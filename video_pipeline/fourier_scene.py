from manim import *
import numpy as np
import timings

C_TITLE = YELLOW
C_AXIS = WHITE
C_GRAY = GRAY_B
C_SIN = BLUE_C
C_SQUARE = ORANGE
C_H1 = BLUE_C       # 基波
C_H3 = GREEN_C      # 3次谐波
C_H5 = RED_C        # 5次谐波
C_H7 = PURPLE_C     # 7次谐波
C_H9 = TEAL_C       # 9次谐波
C_HIGH = GOLD_E     # 更高次
C_SYNTH = ORANGE    # 合成波
C_SPECT = YELLOW    # 频谱
C_LABEL = LIGHT_GRAY

def fourier_series(x, max_k):
    """方波的傅里叶级数逼近，max_k为最大奇数次"""
    s = np.zeros_like(x)
    for k in range(1, max_k + 1, 2):
        s += (4.0 / (k * np.pi)) * np.sin(k * x)
    return s


class FourierScene(Scene):
    def construct(self):
        durs = timings.SEGMENT_DURATIONS
        is_pause = timings.SEGMENT_IS_PAUSE
        n = len(durs)

        def anims(*plays, idx=None):
            used = 0.0
            for angs, rt in plays:
                if angs is not None and len(angs) > 0:
                    self.play(*angs, run_time=rt)
                else:
                    self.wait(rt)
                used += rt
            if idx is not None:
                rem = durs[idx] - used if idx < n else 0.5
                if rem > 0:
                    self.wait(rem)

        # ================================================================
        # 坐标系（全局复用）
        # ================================================================
        axes = Axes(
            x_range=[0, 2 * PI, PI / 2],
            y_range=[-1.8, 1.8, 0.5],
            x_length=10,
            y_length=4.5,
            axis_config={"color": C_AXIS, "stroke_width": 1.5},
        )
        axes.center().shift(DOWN * 0.2)

        # 自定义刻度标签（避免 LaTeX 依赖）
        xticks = VGroup()
        for val, label in [(PI / 2, "π/2"), (PI, "π"), (3 * PI / 2, "3π/2"), (2 * PI, "2π")]:
            p = axes.coords_to_point(val, 0)
            t = Text(label, font_size=16, color=C_GRAY)
            t.next_to(p, DOWN, buff=0.1)
            xticks.add(t)
        yticks = VGroup()
        for val, label in [(-1, "-1"), (1, "1")]:
            p = axes.coords_to_point(0, val)
            t = Text(label, font_size=16, color=C_GRAY)
            t.next_to(p, LEFT, buff=0.15)
            yticks.add(t)

        # ================================================================
        # 标题
        # ================================================================
        title = Text("傅里叶变换", font_size=64, color=C_TITLE, weight=BOLD)
        title.move_to(UP * 2.8)
        subtitle = Text("从波形到频率的神奇之旅", font_size=28, color=C_GRAY)
        subtitle.next_to(title, DOWN, buff=0.3)

        # 缩小版标题（左上角）
        title_corner = title.copy().scale(0.45).move_to(UP * 3.0 + LEFT * 5.8)
        sub_corner = subtitle.copy().scale(0.45).next_to(title_corner, DOWN, buff=0.08, aligned_edge=LEFT)

        # ================================================================
        # 数学图形对象（预创建）
        # ================================================================

        # 正弦波
        sin_graph = axes.plot(lambda x: np.sin(x), color=C_SIN, stroke_width=4)

        # 方波（用傅里叶级数高次逼近）
        sq_graph = axes.plot(lambda x: fourier_series(x, 51), color=C_SQUARE, stroke_width=4)

        # 频率和振幅标注
        freq_line = DashedLine(
            axes.coords_to_point(PI, -1.5), axes.coords_to_point(PI, 1.5),
            color=C_LABEL, stroke_width=1.5
        )
        freq_label = Text("周期 T", font_size=22, color=C_LABEL)
        freq_label.next_to(axes.coords_to_point(PI, -1.7), DOWN, buff=0.05)

        amp_arrow = Arrow(
            axes.coords_to_point(0.4, 0), axes.coords_to_point(0.4, 1),
            color=C_LABEL, stroke_width=2, buff=0
        )
        amp_label = Text("振幅 A", font_size=22, color=C_LABEL)
        amp_label.next_to(amp_arrow.get_start(), LEFT, buff=0.2)

        # 谐波曲线（叠加过程用）
        h1 = axes.plot(lambda x: np.sin(x), color=C_H1, stroke_width=4)
        h3 = axes.plot(lambda x: (4 / (3 * PI)) * np.sin(3 * x), color=C_H3, stroke_width=2.5)
        h5 = axes.plot(lambda x: (4 / (5 * PI)) * np.sin(5 * x), color=C_H5, stroke_width=2.5)
        h7 = axes.plot(lambda x: (4 / (7 * PI)) * np.sin(7 * x), color=C_H7, stroke_width=2.5)

        # 各阶合成波
        synth_1 = axes.plot(lambda x: fourier_series(x, 1), color=C_SYNTH, stroke_width=4)
        synth_3 = axes.plot(lambda x: fourier_series(x, 3), color=C_SYNTH, stroke_width=4)
        synth_5 = axes.plot(lambda x: fourier_series(x, 5), color=C_SYNTH, stroke_width=4)
        synth_7 = axes.plot(lambda x: fourier_series(x, 7), color=C_SYNTH, stroke_width=4)
        synth_9 = axes.plot(lambda x: fourier_series(x, 9), color=C_SYNTH, stroke_width=4)
        synth_21 = axes.plot(lambda x: fourier_series(x, 21), color=C_SYNTH, stroke_width=4)

        # 频谱条
        n_bars = 9
        bar_vals = [(4.0 / ((2 * k + 1) * PI)) for k in range(n_bars)]
        bar_max = bar_vals[0]
        bar_width = 0.35
        bars = VGroup()
        bar_labels = VGroup()
        for i, v in enumerate(bar_vals):
            freq_hz = 2 * i + 1
            h = v / bar_max * 3.0  # 最大高度3.0
            bar = Rectangle(width=bar_width, height=h, color=C_SPECT, fill_color=C_SPECT, fill_opacity=0.8, stroke_width=1)
            bar.move_to(RIGHT * (i - n_bars / 2) * 0.55 + DOWN * 1.2 + UP * h / 2)
            bars.add(bar)
            lbl = Text(str(freq_hz), font_size=14, color=C_GRAY)
            lbl.next_to(bar, DOWN, buff=0.05)
            bar_labels.add(lbl)

        # 频谱坐标文字
        spect_title = Text("频谱", font_size=32, color=C_TITLE, weight=BOLD)
        spect_title.next_to(bars, UP, buff=0.4)
        ax_label_x = Text("频率 →", font_size=18, color=C_GRAY)
        ax_label_x.next_to(bar_labels, DOWN, buff=0.15)
        ax_label_y = Text("幅度", font_size=18, color=C_GRAY).rotate(PI / 2)
        ax_label_y.next_to(bars, LEFT, buff=0.3)

        # ================================================================
        # 段0：标题
        # ================================================================
        anims(
            ([Write(title)], 1.2),
            ([FadeIn(subtitle, shift=UP)], 0.8),
            idx=0,
        )

        # ================================================================
        # 段1：标题缩小→左上角，创建坐标系，画正弦波
        # ================================================================
        label_grp = VGroup()
        anims(
            ([Transform(title, title_corner),
              FadeOut(subtitle),
              FadeIn(sub_corner)], 0.4),
            ([Create(axes), FadeIn(xticks), FadeIn(yticks)], 1.2),
            ([Create(sin_graph)], 1.5),
            idx=1,
        )

        # ================================================================
        # 段2：标注频率和振幅
        # ================================================================
        anims(
            ([Create(freq_line), Write(freq_label)], 1.0),
            ([GrowArrow(amp_arrow), Write(amp_label)], 1.0),
            idx=2,
        )

        # ================================================================
        # 段3：方波
        # ================================================================
        old_graphs = VGroup(sin_graph, freq_line, freq_label, amp_arrow, amp_label)
        anims(
            ([FadeOut(old_graphs)], 0.4),
            ([Create(sq_graph)], 1.5),
            idx=3,
        )

        # ================================================================
        # 段4：[pause:1.2]
        # ================================================================
        anims(idx=4)

        # ================================================================
        # 段5：核心发现
        # ================================================================
        disc_text = Text("任何复杂波形\n都能拆成不同频率的正弦波", font_size=34, color=C_TITLE, weight=BOLD, line_spacing=0.5)
        disc_text.move_to(RIGHT * 3.5 + UP * 0.5)
        disc_box = SurroundingRectangle(disc_text, color=C_TITLE, buff=0.15, stroke_width=2, corner_radius=0.08)
        # 方波保持
        anims(
            ([Write(disc_text), Create(disc_box)], 1.5),
            idx=5,
        )

        # ================================================================
        # 段6：基波
        # ================================================================
        # 清除方波和文字
        wave_text = Text("基波：最低频的正弦波", font_size=26, color=C_H1, weight=BOLD)
        wave_text.move_to(DOWN * 2.6)

        anims(
            ([FadeOut(VGroup(sq_graph, disc_text, disc_box))], 0.4),
            ([Create(h1)], 1.5),
            ([Write(wave_text)], 0.6),
            idx=6,
        )

        # ================================================================
        # 段7：逐步叠加谐波
        # ================================================================
        # 用 Transform 连续更新合成波，每次先显示新的谐波
        wave_text2 = Text("加上更高频率的正弦波……", font_size=22, color=C_GRAY)
        wave_text2.next_to(wave_text, DOWN, buff=0.15, aligned_edge=LEFT)

        # 复制 h1 作为合成波初始（因为 h1 也是 sin(x)）
        synth_current = h1.copy().set_color(C_SYNTH)
        synth_current.set_stroke(width=5)
        self.add(synth_current)  # 添加到场景但不通过 anims

        anims(
            ([Write(wave_text2)], 0.4),
            # 加 3 次谐波
            ([FadeIn(h3), Transform(synth_current, synth_3)], 1.2),
            # 加 5 次谐波
            ([FadeIn(h5), Transform(synth_current, synth_5)], 1.2),
            # 加 7 次谐波
            ([FadeIn(h7), Transform(synth_current, synth_7)], 1.0),
            idx=7,
        )

        # ================================================================
        # 段8："离方波更近一步"
        # ================================================================
        closer_text = Text("每多一个正弦波，\n波形就离方波更近一步", font_size=26, color=C_GRAY, weight=BOLD, line_spacing=0.4)
        closer_text.next_to(wave_text2, DOWN, buff=0.15, aligned_edge=LEFT)

        # 再加 9 次谐波
        h9 = axes.plot(lambda x: (4 / (9 * PI)) * np.sin(9 * x), color=C_H9, stroke_width=2)
        anims(
            ([Write(closer_text)], 0.5),
            ([FadeIn(h9), Transform(synth_current, synth_9)], 1.2),
            idx=8,
        )

        # ================================================================
        # 段9：[pause:0.8]
        # ================================================================
        all_harmonics = VGroup(h1, h3, h5, h7, h9)
        all_wave_texts = VGroup(wave_text, wave_text2, closer_text)
        anims(idx=9)

        # ================================================================
        # 段10：完美拼出方波！
        # ================================================================
        # 清除各谐波曲线，保留合成波进行变换
        perfect_text = Text("完美拼出方波！", font_size=44, color=C_TITLE, weight=BOLD)
        perfect_text.move_to(UP * 2.0)

        anims(
            ([FadeOut(all_harmonics)], 0.3),
            ([Transform(synth_current, synth_21)], 2.0),
            ([Write(perfect_text)], 0.8),
            idx=10,
        )

        # ================================================================
        # 段11：[pause:1.8]
        # ================================================================
        anims(idx=11)

        # ================================================================
        # 段12：傅里叶级数
        # ================================================================
        fs_text = Text("傅里叶级数：\n任何周期函数都能写成\n一系列正弦波的加权和", font_size=30, color=C_TITLE, weight=BOLD, line_spacing=0.5)
        fs_text.move_to(UP * 0.5)

        anims(
            ([FadeOut(VGroup(all_wave_texts, perfect_text))], 0.3),
            ([FadeIn(fs_text)], 1.5),
            idx=12,
        )

        # ================================================================
        # 段13：频谱
        # ================================================================
        # 清除当前画面，切到频谱
        freq_text = Text("傅里叶变换：\n时间域 → 频率域", font_size=30, color=C_TITLE, weight=BOLD, line_spacing=0.5)
        freq_text.move_to(UP * 2.5)

        anims(
            ([FadeOut(VGroup(synth_current, axes, xticks, yticks, fs_text))], 0.4),
            ([FadeIn(freq_text)], 0.8),
            # 逐个出现频谱条
            ([FadeIn(spect_title)], 0.5),
            idx=13,
        )

        # 逐个显示频谱条
        for i, (bar, lbl) in enumerate(zip(bars, bar_labels)):
            rt = 0.15
            a = []
            if i == 0:
                a.append(FadeIn(bar, shift=UP * 0.5))
            else:
                a.append(FadeIn(bar, shift=UP * 0.5))
                a.append(FadeIn(lbl))
            # 不能用 anims()，需要在段13内部手动播放
            self.play(*a, run_time=rt)
            self.wait(0.05)
        self.play(FadeIn(ax_label_x), FadeIn(ax_label_y), run_time=0.3)
        # 补足段13剩余时间
        used_13 = 1.7 + 0.15 * 9 + 0.05 * 9 + 0.3  # ≈ 4.1s
        rem_13 = durs[13] - used_13 if 13 < n else 0
        if rem_13 > 0:
            self.wait(rem_13)

        # ================================================================
        # 段14：频谱标注说明
        # ================================================================
        spect_note = Text("每个尖峰代表一个频率成分\n高度代表该频率的幅度", font_size=26, color=C_LABEL, line_spacing=0.5)
        spect_note.move_to(DOWN * 2.5)

        lbl_all = VGroup(ax_label_x, ax_label_y)

        anims(
            ([Write(spect_note)], 1.5),
            idx=14,
        )

        # ================================================================
        # 段15：[pause:1.0]
        # ================================================================
        all_spect = VGroup(spect_title, bars, bar_labels, lbl_all, spect_note)
        anims(idx=15)

        # ================================================================
        # 段16：应用
        # ================================================================
        apps = VGroup(
            Text("音频压缩（MP3）", font_size=26, color=WHITE),
            Text("图像处理（JPEG）", font_size=26, color=WHITE),
            Text("WiFi 通信", font_size=26, color=WHITE),
            Text("心电图分析", font_size=26, color=WHITE),
        )
        apps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        apps.move_to(ORIGIN)

        app_title = Text("无处不在的傅里叶变换", font_size=36, color=C_TITLE, weight=BOLD)
        app_title.next_to(apps, UP, buff=0.4, aligned_edge=LEFT)

        anims(
            ([FadeOut(VGroup(freq_text, all_spect))], 0.4),
            ([Write(app_title)], 0.8),
            ([Write(apps[0])], 0.5),
            ([Write(apps[1])], 0.5),
            ([Write(apps[2])], 0.5),
            ([Write(apps[3])], 0.5),
            idx=16,
        )

        # ================================================================
        # 段17：结尾互动
        # ================================================================
        end_text = Text("你还见过哪些用傅里叶变换的地方？", font_size=44, color=C_TITLE, weight=BOLD)
        end_text.move_to(UP * 0.3)
        sub_text = Text("在评论区说说吧", font_size=26, color=C_GRAY)
        sub_text.next_to(end_text, DOWN, buff=0.5)

        anims(
            ([FadeOut(VGroup(app_title, apps))], 0.5),
            ([Write(end_text)], 1.0),
            ([FadeIn(sub_text, shift=UP)], 0.5),
            idx=17,
        )
