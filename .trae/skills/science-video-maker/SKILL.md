---
name: "science-video-maker"
description: "Generates complete self-media videos (animation + TTS + subtitles) from a topic using Manim + edge-tts + ffmpeg. Invoke when user asks to make a science/educational explainer video from a topic or script."
---

# Science Video Maker - 科普短视频一条龙生成

You are a professional educational video creator. When the user gives you a topic (e.g. "勾股定理", "傅里叶变换", "囚徒困境"), you will generate a complete short video with animated visuals, AI voiceover, and burned-in subtitles — fully automatically.

## Tech Stack (pre-installed)

| Tool | Purpose | Version |
|------|---------|---------|
| Manim (Community) | Math/animation engine | 0.20.x |
| edge-tts | Free Microsoft neural TTS (Chinese voice zh-CN-XiaoxiaoNeural) | latest |
| FFmpeg | Video compositing, subtitle burn-in, silence generation | 8.x |

All assets live in: `d:\KaiFa\test\video_pipeline\`
- Pipeline script: `pipeline.py`
- Output dir: `output/`
- Working dir: `output/work/`

## Workflow (MUST follow exactly — 5 phases)

### Phase 1: Plan the video

Given the user's topic, plan:
1. **Target duration**: 60–120 seconds (short video for Douyin/Bilibili; proofs/derivations need time)
2. **Number of segments**: 10–20 segments (shorter segments = better sync + clearer step-by-step)
3. **Content outline**: Plan the narrative arc before writing narration
4. **Visual metaphor**: Choose appropriate animation patterns (see "Animation Patterns")

**Pacing principle**: 
- For derivations/proofs, one logical step per segment
- Dense algebra → break into 2–3 segments with short pauses
- After a key reveal or important visual, add a `[pause:X.X]` segment (1.0–2.0s) for viewers to absorb
- Introduce ONE new concept per segment; never introduce two things at once

#### 🎯 文案核心原则（基于百万播放科普UP主研究）:

**黄金结构公式（60-120s短视频）：**
| 时间 | 环节 | 功能 |
|------|------|------|
| 0-5s | **钩子（Hook）** | 反常识/数据冲击/痛点共鸣，瞬间抓住注意力 |
| 5-15s | **设问/冲突** | 建立认知缺口，让观众产生"为什么？"的好奇 |
| 15-45s | **知识拆解** | 信息降维，3步法则，每个新概念用比喻拉回日常 |
| 45-55s | **Wow Moment** | 颠覆认知的结论/视觉高潮/神转折 |
| 55-60s | **结尾点睛** | 金句收尾 + 互动引导 |

**钩子（Hook）三大公式：**
- ✅ 反常识型：「你相信吗？一个汉堡就能判断哪个国家物价贵」
- ✅ 数据冲击型：「同一个iPhone，在土耳其卖两千美元，在中国只要六千块——差了三倍」
- ✅ 痛点共鸣型：「每次出国旅游都不知道去哪划算？这条视频帮你省一半预算」

**文案写作铁律：**
1. **前3秒定生死**：第一句必须是钩子，不能是"今天我们来介绍..."等废话
2. **每30秒一个"哇点"**：让观众忍不住发出"哇"的时刻——惊人数据、反直觉结论、视觉震撼
3. **专业术语出现必解释**：每30秒不超过2个术语。出现术语时立即跟一句人话解释（"这叫巴拉萨-萨缪尔森效应——简单说就是：越高效的国家货币越强"）
4. **类比优先于定义**：用生活化比喻代替学术定义。"汇率就像两个国家之间的价格翻译器"优先于"汇率是两种货币的兑换比率"
5. **场景化提问**：不从定义开始，从生活场景切入。"你有没有想过，为什么去日本买iPhone比在国内便宜？"
6. **信息密度节奏**：每40秒1-2个新信息点。不要把一堆信息塞在一个段落里
7. **结尾金句 + 行动号召**：最后一句要让观众记住并想互动

**三位一体原则（视频质量的生命线）：**
- 🎯 **TTS（配音）** 说到的内容 → 🎬 **画面/动画** 必须同步展示 → 📝 **字幕** 必须同时出现
- ❌ 禁止：TTS在说A，画面还在显示B；字幕出现时画面还没变
- ❌ 禁止：同一时间出现两个不相关的动画，导致视觉拥挤
- ❌ 禁止：前一段的残留文字还没有消失，下一段的新文字就出现了
- ✅ **内容清理机制（CRITICAL）**：每段必须用一个 `current` 变量追踪当前屏幕上的内容组。下一段开始时先 `FadeOut(current)` 再写新内容，保证前一段所有元素彻底消失。
  ```python
  # 每段都这样写：
  s0 = VGroup(t0, ...)       # 本段所有内容
  anims(([Write(t0)], ...), idx=0)
  current = s0               # 记录为 current

  s1 = VGroup(k1, ...)       # 下一段内容
  anims(([FadeOut(current), Write(k1)], 0.3), ...)  # 先清再写
  current = s1               # 更新 current
  ```
- ✅ **动画文字 = 关键词而非完整句子**：字幕已承载完整信息，动画中的文字只需提取核心关键词（5-15字）。TTS读全句，屏幕显示重点，两者互补不重复。
  - ❌ 坏例子：动画显示"一个国家制造业效率越高，全社会工资就越高，服务价格就越贵"
  - ✅ 好例子：动画显示"制造业高效 → 全社会高薪 → 服务价格高 → 货币强势"
- ✅ **段落间不留残余**：pause 段不更新 `current`（保留画面内容），但非 pause 段必须 FadeOut 旧内容。绝对不允许两段内容同时出现在屏幕上。
- ✅ 每个anims(idx=N)调用内，所有动画的run_time总和 ≤ durs[N]（旁白时长），保证音画同步

**优秀科普文案结构模板（可直接套用）：**
```
[钩子] 你知道吗？【惊人事实/反常识问题】
[设问] 为什么会这样？
[比喻] 这就像【生活化类比】...
[拆解] 第一步...第二步...第三步...
[高潮] 所以最终结论是【颠覆认知的结果】！
[应用] 知道这个能帮你【实用价值】
[结尾] 【金句】+ 你遇到过类似的情况吗？评论区聊聊
```

### Phase 2: Write narration file with MANDATORY 3-round self-review

Create a text file `<topic>.txt` in `video_pipeline/` directory. Format:
```
第一段旁白（开场）
---
第二段旁白
---
[pause:1.5]
---
第三段旁白（继续推导）
```

#### Narration syntax:
- `---` on its own line separates segments
- `[pause:X.X]` on its own line inserts X seconds of silence (no subtitle, no TTS) for thinking time
- Each speaking segment: 3–12 seconds of speech (~8–35 Chinese characters)
- Use natural spoken Chinese
- Math terms in speech: "a的平方" not "a²"; "二分之一ab" not "½ab"; "开根号" not "√"
- **⚠️ CRITICAL — TTS数字字母混合问题**：edge-tts对数字读中文、字母读英文。因此旁白中**禁止出现数字+字母混写**（如 "2ab"，会被读成"二 a b"）。必须写完整中文，如 "两倍的ab"、"三个x"、"5Hz"写成"五赫兹"
- End with an interactive question to encourage comments

#### ⚠️ MANDATORY 3-Round Narration Review (before writing any Manim code):

After drafting narration, you MUST perform three rounds of self-review, revising the narration file each time:

**Round 1 — Comprehension Check**:
- Read each segment aloud mentally
- Could a 12-year-old understand every sentence?
- Are there any unexplained terms or undefined variables?
- Is every pronoun unambiguous?
- Fix: add definitions, remove jargon, clarify references

**Round 2 — Step-by-Step Gradualness Check**:
- Walk through the logic flow: does each step follow from the previous one?
- Are there any "leaps" where the narration assumes knowledge the viewer hasn't been given?
- For mathematical proofs: is every algebraic manipulation narrated? (e.g., "两边减2ab" not just "化简得到")
- Are visuals described before they're referenced? ("先画一个正方形" before saying "它的面积是...")
- Fix: insert additional segments for missing steps, add transition phrases ("接下来", "现在", "你看")

**Round 3 — Pacing & Pause Check**:
- After an important visual is revealed: is there a pause for the viewer to look at it?
- After a key equation appears: is there silence (0.5–1.5s) before the next statement?
- Before the final result/dramatic reveal: is there a 1.5–2.0s build-up pause?
- Are any segments too dense (more than 30 characters)? If so, split them.
- Fix: add `[pause:X.X]` segments, split overly long segments

Document (in your thinking) what you changed in each round. Only proceed to Phase 3 after all three rounds are complete.

### Phase 3: Write Manim scene (`<topic>_scene.py`)

Create a Manim Scene file in `video_pipeline/`. The scene MUST:

1. **Import timings** at the top: `import timings`
2. **Read segment durations**: `durs = timings.SEGMENT_DURATIONS`, `is_pause = timings.SEGMENT_IS_PAUSE`
3. **Use the `anims()` helper pattern** to ensure each segment's total run_time matches TTS duration:

```python
from manim import *
import timings

class MyScene(Scene):
    def construct(self):
        durs = timings.SEGMENT_DURATIONS
        is_pause = timings.SEGMENT_IS_PAUSE
        n = len(durs)

        def anims(*plays, idx=None):
            """plays: list of (animation_list_or_None, run_time) tuples.
               None means pure wait. idx=None means no auto-wait at end."""
            used = 0.0
            for angs, rt in plays:
                if angs:
                    self.play(*angs, run_time=rt)
                else:
                    self.wait(rt)
                used += rt
            if idx is not None:
                rem = durs[idx] - used if idx < n else 0.5
                if rem > 0:
                    self.wait(rem)

        # Example:
        # Segment 0: Title
        title = Text("标题", font_size=72, color=YELLOW)
        anims(([Write(title)], 1.5), idx=0)

        # Pause segment (no animations, just wait):
        anims(idx=3)  # automatically waits full durs[3] seconds
```

#### Critical animation rules:

- **ONE segment per narration beat**: Do NOT combine two narration segments' visuals into one anims() call
- **Pause segments**: For `[pause:X.X]` segments, call `anims(idx=i)` with no plays — this holds the current frame for the pause duration
- **Label everything**: When a variable/object is introduced in narration, its label MUST appear visually at that moment or before
- **Step-by-step algebra**: Each algebraic manipulation gets its own segment with its own Write()/animation — never write 3 equations in one segment
- **Visual first, then text**: When narration says "画一个正方形", show Create(square) in that segment. Don't pre-draw it.
- **Title at top**: Main title at UP*2.6–2.8, then scale to corner after intro
- **Consistent colors**: YELLOW=titles/results/highlights, BLUE=a/left elements, GREEN=b/positive, RED=c/key result, ORANGE=shapes, WHITE=normal text
- **Layout bounds**: Keep figures within [-6.5, 6.5] × [-3.2, 3.2] (leaving bottom for subtitles, sides for margin)
- **Font sizes**: Titles 60–72pt, body equations 26–34pt, labels 22–30pt
- **Avoid LaTeX**: Use `Text()` with Unicode (², √, π, ∞, ×, ÷, →) instead of `MathTex()` to avoid MiKTeX dependency
- **Avoid "∴" and "½" symbols**: "∴" renders poorly in Manim Pango; use Chinese "所以：" or "得到：" instead. "½" may render as "1/2"; use "(1/2)" for clarity
- **No background rectangles** on regular text (subtitles are burned by FFmpeg already)
- **Subtitle clear zone**: Keep bottom 1.2 units free of critical content
- **Final segment**: Interactive question centered, with secondary text below
- **Highlight key results**: Use SurroundingRectangle or color pulse for the final answer

#### Animation Patterns by Domain:

**Math/Physics/Chemistry proofs (RECOMMENDED)**:
- Geometric proofs: Build the figure step by step (each element in its own segment)
- Label sides/angles WHEN they are named in narration (not all at once)
- Algebraic derivations: One equation per segment, use color highlighting for the term being manipulated
- Use `ShowPassingFlash` or pulse effect to draw attention to key areas
- Reference implementation: `demo_scene.py` (赵爽弦图 proof with a/b/c labels and step-by-step algebra)

---

### Phase 3.5: Code Self-Review by Sub-Agent (MANDATORY)

After writing the Manim scene code, you MUST launch a **Task subagent** (type=`general_purpose_task`) to review your own code BEFORE running the pipeline.

Write a detailed task prompt to the subagent that includes:

1. **The full path of the scene file** to review
2. **The narration file path** (for context on segment count and timings)
3. **The exact review checklist** the subagent must check:

#### Code Review Checklist

| # | Check | Description |
|---|-------|-------------|
| 1 | **anims() index alignment** | Every `anims(idx=N)` call must correspond to segment index N. No skipped indices, no duplicate indices. The total segments in code must match `len(SEGMENT_DURATIONS)` in timings. |
| 2 | **Pause segment handling** | For segments where `is_pause[i] = True`, the code must call `anims(idx=i)` with **no animation plays** — just a pure wait. |
| 3 | **Timing bounds** | The sum of `run_time` values inside each `anims(idx=N)` call must not exceed `durs[N]`. If sum > durs[N], the last animations will be cut off. |
| 4 | **Object lifecycle** | Objects used in `Transform()` must already exist in the scene. `FadeOut` must use objects that were previously added. No dangling references. |
| 5 | **Coordinate bounds** | Visual elements must stay within [-6.5, 6.5] × [-3.5, 3.5]. No text or shapes off-screen. |
| 6 | **Font & encoding safety** | No LaTeX/MathTex. No emoji in `Text()`. No unsupported Unicode characters. |
| 7 | **Variable scope** | All Manim objects referenced in `anims()` calls are defined before the call. Check for typos in variable names. |
| 8 | **Color consistency** | Colors match the convention: YELLOW=highlights/titles, BLUE=a/base, GREEN=b, RED=c/results, ORANGE=shapes/synthesis, WHITE=normal. |
| 9 | **Subtitle clear zone** | Bottom 1.2 units of the frame contain no critical visual content. |
| 10 | **Narration-visual sync** | Each segment's animation matches what the narration says in that segment. If narration says "画一个正方形", the code draws a square in that segment. |

The subagent must read the scene file, check each item in the checklist, and **return a list of specific issues found** (or "✅ all clear" if none). Each issue must include the exact line number and a suggested fix.

After receiving the subagent's report:
- If issues found: fix them, **then launch another review cycle** (up to max 2 cycles)
- If ✅ all clear: proceed to Phase 4

> ⚠️ Do NOT skip this phase even for simple scenes. Most bugs in Manim scenes come from index misalignment and timing overruns.

### Phase 4: Run the pipeline

Execute in terminal at `d:\KaiFa\test\video_pipeline\`:

```powershell
python pipeline.py --scene <topic>_scene.py --scene-name <SceneClassName> --narration <topic>.txt --topic "<topic_name>"
```

The pipeline automatically:
1. Parses narration → splits by `---` → detects `[pause:X.X]` markers
2. Generates TTS for speaking segments, generates silent audio for pause segments
3. Measures each audio clip duration (TTS clips via ffprobe, pauses use specified duration)
4. Writes `timings.py` with `SEGMENT_DURATIONS`, `SEGMENT_IS_PAUSE`, `SEGMENT_TEXTS`
5. Renders Manim animation
6. Concatenates all audio (TTS + silence)
7. Generates ASS subtitles (pause segments produce NO subtitle line)
8. FFmpeg composites: video + audio + burned-in subtitles → final MP4

Final output: `output/<topic>_final.mp4`

#### Animation Patterns by Domain:

**Economics/Sociology concepts**:
- `Circle(radius=0.1)` for people/agents/particles — group with VGroup for swarm effects
- `Arrow()` for flows/causality/transactions
- `BarChart`/`Axes` for statistical data
- Stick figures: compose from `Line` (body, arms, legs) + `Circle` (head) — keep VERY simple
- Text cards for concept names (FadeIn center)

**Processes/Algorithms**:
- `Square`/`Rectangle` for nodes/blocks in a flow
- `Arrow`/`Line` for connections
- `Transform()` for state changes
- `Circumscribe()` for emphasis on active step

**History/Narrative/Concept explanations**:
- Primarily text animations (Write, FadeIn) with simple icons
- Use VGroup for text cards with title + bullet points
- Simple shape metaphors (e.g., circles for ideas, arrows for influence)

### Phase 5: Multi-point Frame Verification (REQUIRED — at least 2 rounds)

After generation, you MUST verify quality:

1. **Duration check**: Video duration should approximately equal total narration duration (±0.3s)
2. **Frame extraction**: Use ffmpeg to extract frames at key points:
   ```powershell
   # Extract frames at timestamps t=3,8,15,25,40,55,... (at segment boundaries and key moments)
   ffmpeg -ss <t> -i output/<topic>_final.mp4 -frames:v 1 output/frames/f_<t>.png
   ```
3. **Visually inspect each frame** for:
   - All elements within frame bounds (no cutoff)
   - Labels are correct and positioned next to what they label
   - Colors match convention (a=blue, b=green, c=red etc.)
   - Equations are readable and mathematically correct
   - No overlapping text
   - Subtitles don't cover important visuals
   - Pause segments show a stable, complete frame (not half-drawn)
4. **Check pauses**: At pause timestamps, verify no subtitle appears (clean silence)
5. **Mathematical accuracy**: Double-check all formulas, labels, geometry coordinates
6. **Fix issues, delete `media/` and `output/work/seg_*.mp3`**, re-run pipeline
7. **Repeat verification** until clean

## Key Files (reference)

- `pipeline.py` — Main orchestrator
- `demo_scene.py` — Reference: 勾股定理 赵爽弦图 (20 segments with pauses, a/b labels, step-by-step algebra)
- `demo_narration.txt` — Reference narration with `[pause:X.X]` markers
- `timings.py` — Auto-generated; provides `SEGMENT_DURATIONS`, `SEGMENT_IS_PAUSE`, `SEGMENT_STARTS`

## Narration Segment Types available in timings.py

| Variable | Type | Description |
|----------|------|-------------|
| `SEGMENT_DURATIONS` | list[float] | Duration of each segment in seconds |
| `SEGMENT_IS_PAUSE` | list[bool] | True if segment is a `[pause:X.X]` silence |
| `SEGMENT_TEXTS` | list[str] | Text of each segment (`"[pause]"` for pauses) |
| `SEGMENT_STARTS` | list[float] | Cumulative start time of each segment |
| `TOTAL_DURATION` | float | Total video duration |

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| TTS and video out of sync | Each `anims()` call uses `idx=N` for exactly one segment; sum of run_time in that call must be ≤ durs[N] |
| Two anims() calls for same idx | BUG! Combine into ONE `anims(idx=N)` call with multiple play tuples |
| Subtitles appear during pause | Pause segments are detected by `[pause:X.X]` marker — ensure marker is exact format, on its own line |
| Subtitles have background box | Subtitles use BorderStyle=1 (outline only); NEVER add background rects in Manim |
| Objects go off-screen | Coordinates must stay within [-6.5,6.5] × [-3.2,3.2]; reduce SHIFT offsets |
| LaTeX errors | Use `Text()` with Unicode (², ½, √, π, ∴, →, ×, ÷) |
| Font issues with Chinese | Use `Text()` not `Tex()` — Pango renders Microsoft YaHei |
| Labels missing on figures | Add labels WHEN the object is introduced, matching the narration segment |
| Algebra appears too fast | Split into multiple segments: one for "=" connection, one for expansion, one for cancellation — use pauses between |
| Formula chain goes off bottom | Reduce font size to 24–26pt, compress buff between equations to 0.18, start higher (UP*2.2) |

## Domain Feasibility

- **Math/Physics/Chemistry (RECOMMENDED)**: Manim's strength — formulas, geometry, equations, geometric proofs
- **Economics/Sociology**: Use dot/ball metaphors (Circle=agent), charts, arrow flows, text cards
- **History/Narrative**: Text animations + simple icons, clean and readable
- **3D**: Avoid unless essential; 3D Manim scenes are much more complex
- **火柴人/stick figures**: Compose from basic shapes (Circle head + Line limbs), but keep minimal

## Quality Standard — Final Checklist

Before declaring done, verify ALL:
- [ ] 3 rounds of narration self-review completed (comprehension, gradualness, pacing)
- [ ] Audio/video synchronized (±0.3s)
- [ ] Subtitles: white with black outline, NO background box, NO subtitles during pauses
- [ ] All visual elements within frame bounds
- [ ] Labels appear when their concept is introduced in narration
- [ ] Geometric figures have ALL relevant sides/elements labeled (not just the final answer)
- [ ] Mathematical/scientific content FACTUALLY CORRECT (formulas, labels, arithmetic, geometry)
- [ ] Algebraic derivations: each step narrated and shown separately
- [ ] Key results highlighted (SurroundingRectangle, color, or size emphasis)
- [ ] Strategic pauses before/after key reveals (1–2s silence)
- [ ] Ends with interactive question/CTA
- [ ] Narration is natural spoken Chinese (no unexplained jargon)
- [ ] Frame inspection passed on at least 6–8 key timestamps
- [ ] 1080p, smooth animation
