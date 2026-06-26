"""
一条龙自媒体视频生成管线 v2
用法:
  python pipeline.py --scene <scene.py> --scene-name <SceneClass> --narration <narration.txt> --topic "选题"

旁白文件格式（使用 --- 分隔每个分镜段落）:
  第一段旁白文字（对应动画场景的第一段）
  ---
  第二段旁白文字
  ---
  第三段旁白文字

流程:
  1. 解析旁白分段 -> 每段独立生成 TTS -> 测量每段时长
  2. 自动生成 timings.py（含每段秒数、每段文字）
  3. Manim 场景 import timings，按每段时长驱动 run_time / wait
  4. 拼接所有 TTS 片段为完整音频
  5. 根据分段时间轴生成 ASS 字幕（描边样式、无背景框）
  6. ffmpeg 合成：视频 + 音频 + 烧录字幕
"""

import argparse
import asyncio
import os
import re
import subprocess
import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
TTS_VOICE = "zh-CN-XiaoxiaoNeural"
TTS_RATE = "+5%"
MANIM_QUALITY = "h"

QUALITY_MAP = {
    "h": ("1080p60", 60, "1920:1080"),
    "m": ("720p30", 30, "1280:720"),
    "l": ("480p15", 15, "854:480"),
    "k": ("2160p60", 60, "3840:2160"),
}
VIDEO_RES = QUALITY_MAP[MANIM_QUALITY][2]
VIDEO_FPS = QUALITY_MAP[MANIM_QUALITY][1]

SEGMENT_SEP = re.compile(r"^\s*---\s*$", re.MULTILINE)
PAUSE_MARK = re.compile(r"^\s*\[pause:([\d.]+)\]\s*$")


def _find_exe(name: str) -> str:
    base = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    )
    if os.path.isdir(base):
        for entry in os.listdir(base):
            p = os.path.join(base, entry, "bin", f"{name}.exe")
            if os.path.isfile(p):
                return p
    return name


def get_env() -> dict:
    env = os.environ.copy()
    extras = []
    miktex = os.path.expandvars(r"%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64")
    if os.path.isdir(miktex):
        extras.append(miktex)
    ffmpeg_base = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    )
    if os.path.isdir(ffmpeg_base):
        for e in os.listdir(ffmpeg_base):
            bd = os.path.join(ffmpeg_base, e, "bin")
            if os.path.isdir(bd):
                extras.append(bd)
                break
    if extras:
        env["PATH"] = os.pathsep.join(extras) + os.pathsep + env.get("PATH", "")
    return env


# ============================================================
# 1. 解析旁白分段（支持 [pause:X.X] 静音停顿标记）
# ============================================================
def parse_narration(narration_file: str) -> list[dict]:
    """返回 list of dict: {"text": str, "is_pause": bool, "duration": float|None}
       普通段落 text 为旁白文字；pause 段落 text="[pause]"，duration 为秒数。"""
    raw = Path(narration_file).read_text(encoding="utf-8").strip()
    raw_segments = [s.strip() for s in SEGMENT_SEP.split(raw) if s.strip()]
    if not raw_segments:
        raise ValueError("旁白文件为空或没有有效段落")
    segs = []
    for s in raw_segments:
        m = PAUSE_MARK.match(s)
        if m:
            segs.append({"text": "[pause]", "is_pause": True, "duration": float(m.group(1))})
        else:
            segs.append({"text": s, "is_pause": False, "duration": None})
    return segs


# ============================================================
# 2. 每段生成音频（TTS 或静音）并测量时长
# ============================================================
def _generate_silence(duration: float, output_path: Path, env: dict, ffprobe: str, ffmpeg: str) -> float:
    """用 ffmpeg 生成指定时长的静音 mp3，返回实际时长"""
    subprocess.run(
        [ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
         "-t", str(duration), "-c:a", "libmp3lame", "-b:a", "192k", str(output_path)],
        capture_output=True, check=True, env=env,
    )
    r = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(output_path)],
        capture_output=True, text=True, env=env,
    )
    return float(r.stdout.strip())


async def generate_segment_audio(segments: list[dict], work_dir: Path) -> tuple[list[Path], list[float]]:
    """为每个段落生成音频：普通段落用 TTS，pause 段落用静音。返回 (音频路径列表, 时长列表)"""
    try:
        import edge_tts
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts"], check=True)
        import edge_tts

    ffprobe = _find_exe("ffprobe")
    ffmpeg = _find_exe("ffmpeg")
    env = get_env()
    audio_paths: list[Path] = []
    durations: list[float] = []

    for i, seg in enumerate(segments):
        ap = work_dir / f"seg_{i:03d}.mp3"
        if seg["is_pause"]:
            d = _generate_silence(seg["duration"], ap, env, ffprobe, ffmpeg)
            durations.append(d)
            audio_paths.append(ap)
            print(f"      段落 {i+1}/{len(segments)}: {d:.2f}s  [停顿]")
        else:
            text = seg["text"]
            comm = edge_tts.Communicate(text=text, voice=TTS_VOICE, rate=TTS_RATE)
            await comm.save(str(ap))
            audio_paths.append(ap)
            r = subprocess.run(
                [ffprobe, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(ap)],
                capture_output=True, text=True, env=env,
            )
            dur = float(r.stdout.strip())
            durations.append(dur)
            print(f"      段落 {i+1}/{len(segments)}: {dur:.2f}s  {text[:30]}...")

    return audio_paths, durations


# ============================================================
# 3. 拼接所有 TTS 片段
# ============================================================
def concat_audio(audio_paths: list[Path], output: Path, env: dict) -> None:
    ffmpeg = _find_exe("ffmpeg")
    list_file = output.parent / "concat_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for p in audio_paths:
            f.write(f"file '{p.as_posix()}'\n")
    subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
         "-c:a", "libmp3lame", "-b:a", "192k", str(output)],
        capture_output=True, check=True, env=env,
    )


# ============================================================
# 4. 生成 timings.py（给 Manim 场景 import 用）
# ============================================================
def write_timings(durations: list[float], segments: list[dict], scene_dir: Path) -> Path:
    """在 Manim 场景所在目录写入 timings.py"""
    lines = [
        "# Auto-generated by pipeline.py — DO NOT EDIT",
        f"TOTAL_SEGMENTS = {len(durations)}",
        "SEGMENT_DURATIONS = [",
    ]
    for d in durations:
        lines.append(f"    {d:.3f},")
    lines.append("]")
    lines.append("SEGMENT_IS_PAUSE = [")
    for seg in segments:
        lines.append(f"    {True if seg['is_pause'] else False},")
    lines.append("]")
    lines.append("SEGMENT_TEXTS = [")
    for seg in segments:
        s = seg["text"]
        escaped = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
        lines.append(f'    "{escaped}",')
    lines.append("]")
    lines.append("")
    # 计算每段的累计起始时间
    cum = []
    t = 0.0
    for d in durations:
        cum.append(t)
        t += d
    lines.append("SEGMENT_STARTS = [")
    for c in cum:
        lines.append(f"    {c:.3f},")
    lines.append("]")
    lines.append(f"TOTAL_DURATION = {t:.3f}")

    tp = scene_dir / "timings.py"
    tp.write_text("\n".join(lines), encoding="utf-8")
    return tp


# ============================================================
# 5. 生成 ASS 字幕（描边样式，无背景框）
# ============================================================
def format_ass_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def generate_ass_subtitles(segments: list[dict], starts: list[float], durations: list[float],
                           output: Path, video_res: str) -> Path:
    """生成 ASS 字幕文件：白色字+黑色描边，无背景框，底部居中；暂停段不生成字幕"""
    w, h = video_res.split(":")
    w, h = int(w), int(h)

    # Style 配置：
    #   Fontname=Microsoft YaHei 中文字体
    #   Fontsize=52 (1080p)
    #   PrimaryColour=&H00FFFFFF 白色
    #   OutlineColour=&H00000000 黑色描边
    #   BackColour=&H80000000  (不使用，BorderStyle=1 表示描边)
    #   BorderStyle=1: 描边+阴影（非矩形框）
    #   Outline=3, Shadow=1
    #   MarginV=60 距底边距离
    #   Alignment=2 底部居中
    font_size = 52 if h >= 1080 else 36
    margin_v = 70 if h >= 1080 else 45

    ass_header = f"""[Script Info]
Title: Auto-generated subtitles
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,1,2,30,30,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    LEAD_IN = 0.20
    LEAD_OUT = 0.10
    for i, seg in enumerate(segments):
        if seg["is_pause"]:
            continue
        text = seg["text"]
        wrapped = _wrap_text(text, max_chars=22)
        start_t = format_ass_time(starts[i] + LEAD_IN)
        end_t = format_ass_time(starts[i] + durations[i] - LEAD_OUT)
        events.append(f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{wrapped}")

    output.write_text(ass_header + "\n".join(events) + "\n", encoding="utf-8")
    return output


def _wrap_text(text: str, max_chars: int = 22) -> str:
    """按中文字数换行：在标点或最大长度处换行，ASS 用 \\N 表示硬换行。
       避免将句末标点单独留在新行。"""
    text = text.strip()
    lines = []
    current = ""
    break_chars = set("，。！？、；：,.!?;:")
    for i, ch in enumerate(text):
        current += ch
        if ch in break_chars:
            # 若当前行太短，继续积累
            if len(current) < max_chars // 2:
                continue
            # 若下一个字符也是标点，一起带上
            while i + 1 < len(text) and text[i + 1] in break_chars:
                i += 1
                current += text[i]
            lines.append(current)
            current = ""
        elif len(current) >= max_chars:
            # 尽量不在词中间断开；如果当前字符不是标点，向前找最近的标点断开
            lines.append(current)
            current = ""
    if current:
        # 如果剩下的仅为标点，合并到上一行
        if lines and all(c in break_chars or c.isspace() for c in current):
            lines[-1] += current
        else:
            lines.append(current)
    return r"\N".join(lines)


# ============================================================
# 6. 渲染 Manim
# ============================================================
def render_manim(scene_file: str, scene_name: str) -> Path:
    print(f"      正在调用 Manim 渲染引擎...")
    scene_path = Path(scene_file).resolve()
    if not scene_path.exists():
        raise FileNotFoundError(scene_file)

    # 删除旧的 timings.py 让 Manim 用新的
    old_timings = scene_path.parent / "timings.py"
    if old_timings.exists() and not (scene_path.parent / "narration.txt").exists():
        pass  # 会被后面 overwrite

    cmd = [
        sys.executable, "-m", "manim",
        f"-q{MANIM_QUALITY}", "--format", "mp4",
        str(scene_path), scene_name,
    ]
    env = get_env()
    r = subprocess.run(cmd, cwd=str(scene_path.parent), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env)
    if r.returncode != 0:
        print("Manim 渲染失败:")
        print(r.stderr[-3000:])
        raise RuntimeError(f"Manim 渲染失败 ({r.returncode})")

    qdir = QUALITY_MAP[MANIM_QUALITY][0]
    vp = scene_path.parent / "media" / "videos" / scene_path.stem / qdir / f"{scene_name}.mp4"
    if not vp.exists():
        for line in (r.stdout + r.stderr).split("\n"):
            if "File ready at" in line:
                raw = line.split("File ready at")[-1].strip().strip("'\"")
                vp = Path(raw)
                break
    if not vp.exists():
        raise FileNotFoundError(f"找不到 Manim 输出视频: {vp}")
    print(f"      动画视频: {vp}")
    return vp


# ============================================================
# 7. ffmpeg 最终合成：视频+音频+烧录字幕
# ============================================================
def composite_final(video_path: Path, audio_path: Path, ass_path: Path, topic: str) -> Path:
    print(f"[5/5] 合成最终视频（含字幕烧录）...")
    ffmpeg = _find_exe("ffmpeg")
    env = get_env()

    safe = "".join(c for c in topic if c.isalnum() or c in " _-")[:40]
    out = OUTPUT_DIR / f"{safe}_final.mp4"

    # ffmpeg subtitles filter 需要转义路径中的特殊字符（Windows 注意）
    ass_path_escaped = str(ass_path).replace("\\", "/").replace(":", r"\:")

    vf = f"subtitles='{ass_path_escaped}'"

    cmd = [
        ffmpeg, "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-map", "0:v:0", "-map", "1:a:0",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if r.returncode != 0:
        print("ffmpeg 合成失败:")
        print(r.stderr[-2000:])
        raise RuntimeError("ffmpeg 合成失败")
    print(f"      最终视频: {out}")
    return out


# ============================================================
# 主入口
# ============================================================
async def main():
    parser = argparse.ArgumentParser(description="自媒体视频一键生成管线 v2")
    parser.add_argument("--scene", required=True, help="Manim 场景 .py 文件")
    parser.add_argument("--scene-name", required=True, help="Manim 场景类名")
    parser.add_argument("--narration", required=True, help="旁白 .txt 文件（--- 分段）")
    parser.add_argument("--topic", default="video", help="选题名称")
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--video", help="已有视频（配合 --skip-render）")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    work_dir = OUTPUT_DIR / "work"
    work_dir.mkdir(exist_ok=True)
    env = get_env()

    # 1) 解析旁白
    print(f"[1/5] 解析旁白分段...")
    segments = parse_narration(args.narration)
    n_tts = sum(1 for s in segments if not s["is_pause"])
    n_pause = sum(1 for s in segments if s["is_pause"])
    print(f"      共 {len(segments)} 段（{n_tts} 个配音段 + {n_pause} 个停顿段）")

    # 2) 每段音频（TTS 或静音）+ 时长
    print(f"[2/5] 生成段落音频（配音+停顿）...")
    audio_paths, durations = await generate_segment_audio(segments, work_dir)

    # 3) 写入 timings.py（给 Manim 用）
    scene_dir = Path(args.scene).resolve().parent
    timings_path = write_timings(durations, segments, scene_dir)
    print(f"[3/5] 已生成时长配置: {timings_path}")
    for i, (d, seg) in enumerate(zip(durations, segments)):
        tag = "[停顿]" if seg["is_pause"] else seg["text"][:40]
        print(f"      段{i+1}: {d:.2f}s | {tag}")

    # 4) 渲染 Manim
    if args.skip_render:
        video_path = Path(args.video)
        print(f"[4/5] 跳过 Manim 渲染，使用: {video_path}")
    else:
        print(f"[4/5] 渲染 Manim 动画（将按 TTS 时长自适应）...")
        video_path = render_manim(args.scene, args.scene_name)

    # 5) 拼接音频
    full_audio = work_dir / "narration_full.mp3"
    concat_audio(audio_paths, full_audio, env)

    # 6) 生成 ASS 字幕（基于分段起始时间）
    starts = []
    acc = 0.0
    for d in durations:
        starts.append(acc)
        acc += d
    ass_path = work_dir / "subtitles.ass"
    generate_ass_subtitles(segments, starts, durations, ass_path, VIDEO_RES)

    # 7) 合成
    final = composite_final(video_path, full_audio, ass_path, args.topic)

    # 清理 timings.py（避免残留影响后续）
    # 不清理，保留供调试

    size_mb = final.stat().st_size / 1024 / 1024
    total_dur = sum(durations)
    print()
    print("=" * 55)
    print(f"  选题:   {args.topic}")
    print(f"  时长:   {total_dur:.1f} 秒")
    print(f"  段落:   {len(segments)} 段")
    print(f"  输出:   {final}")
    print(f"  大小:   {size_mb:.1f} MB")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
