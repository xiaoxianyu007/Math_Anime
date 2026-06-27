"""
量子计算与稀释制冷机
- 国产ez-Q F1500下线，量子计算需要极低温
- 15 segments (indices 0-14)
- 2 pause segments (indices 4, 10)
"""
from manim import *
import timings


class QuantumScene(Scene):
    def construct(self):
        durs = timings.SEGMENT_DURATIONS
        is_pause = timings.SEGMENT_IS_PAUSE
        n = len(durs)

        C_TITLE = YELLOW
        C_GREEN = GREEN
        C_RED = RED
        C_GOLD = GOLD
        C_GRAY = GRAY_B
        C_WHITE = WHITE
        C_BLUE = BLUE_D
        C_CYAN = TEAL

        def budget(i):
            return durs[i] if i < n else 2.0

        def anims(*plays, idx=None):
            """plays: (animation_list_or_None, run_time) tuples. None = pure wait."""
            used = 0.0
            for angs, rt in plays:
                if angs:
                    self.play(*angs, run_time=rt)
                else:
                    self.wait(rt)
                used += rt
            if idx is not None:
                rem = budget(idx) - used
                if rem > 0:
                    self.wait(rem)

        current = None

        # ============================================================
        # Segment 0: 开场标题 - 钩子
        # ============================================================
        title = Text("量子计算到底有多冷？", font_size=60, color=C_TITLE, weight=BOLD)
        title.move_to(UP * 2.6)
        sub = Text("比太空深处冷几十倍！", font_size=32, color=C_BLUE)
        sub.next_to(title, DOWN, buff=0.3)

        # 雪花/温度图标
        snow = Text("❄", font_size=48, color=C_CYAN)
        snow.move_to(DOWN * 0.5)

        s0 = VGroup(title, sub, snow)
        anims(([Write(title)], 0.6), ([FadeIn(sub, shift=DOWN)], 0.5),
              ([FadeIn(snow, scale=0.5)], 0.4), idx=0)
        current = s0

        # ============================================================
        # Segment 1: 稀释制冷机介绍
        # ============================================================
        s1_title = Text("稀释制冷机", font_size=44, color=C_GOLD, weight=BOLD)
        s1_title.move_to(UP * 2.5)
        s1_desc = Text("实现极端低温的关键设备", font_size=28, color=C_WHITE)
        s1_desc.next_to(s1_title, DOWN, buff=0.3)

        # 简化设备图示：矩形 + 管道
        fridge = Rectangle(width=2.0, height=3.0, color=C_CYAN, stroke_width=3)
        fridge.move_to(DOWN * 0.3)
        pipe1 = Line(fridge.get_top(), fridge.get_top() + UP * 0.6, color=C_GRAY, stroke_width=4)
        pipe2 = Line(fridge.get_bottom(), fridge.get_bottom() + DOWN * 0.6, color=C_GRAY, stroke_width=4)
        fridge_label = Text("稀释制冷机", font_size=20, color=C_CYAN)
        fridge_label.next_to(fridge, DOWN, buff=0.15)

        s1 = VGroup(s1_title, s1_desc, fridge, pipe1, pipe2, fridge_label)
        anims(([FadeOut(current)], 0.3),
              ([Write(s1_title)], 0.5),
              ([FadeIn(s1_desc, shift=UP)], 0.4),
              ([Create(fridge), Create(pipe1), Create(pipe2)], 1.2),
              ([Write(fridge_label)], 0.4), idx=1)
        current = s1

        # ============================================================
        # Segment 2: 国产ez-Q F1500下线
        # ============================================================
        c2_title = Text("国产突破！", font_size=44, color=C_GREEN, weight=BOLD)
        c2_title.move_to(UP * 2.5)
        c2_name = Text("ez-Q F1500 正式下线", font_size=36, color=C_TITLE, weight=BOLD)
        c2_name.next_to(c2_title, DOWN, buff=0.3)
        c2_flag = Text("性能国际领先", font_size=28, color=C_GREEN)
        c2_flag.next_to(c2_name, DOWN, buff=0.25)

        # 奖杯/五角星图标
        star = Text("★", font_size=48, color=C_GOLD)
        star.move_to(DOWN * 0.5)

        s2 = VGroup(c2_title, c2_name, c2_flag, star)
        anims(([FadeOut(current)], 0.3),
              ([Write(c2_title)], 0.5),
              ([Write(c2_name)], 0.7),
              ([FadeIn(c2_flag, shift=UP)], 0.5),
              ([FadeIn(star, scale=0.5)], 0.5), idx=2)
        current = s2

        # ============================================================
        # Segment 3: 核心参数
        # ============================================================
        param_items = VGroup()
        p1 = VGroup(
            Text("100", font_size=38, color=C_TITLE, weight=BOLD),
            Text(" 毫开尔文", font_size=28, color=C_WHITE),
            Text("  制冷量 1700 微瓦", font_size=28, color=C_GREEN, weight=BOLD),
        )
        p1.arrange(RIGHT, buff=0.05)
        p1.move_to(UP * 1.2)
        p1_sub = Text("全球顶尖水平", font_size=24, color=C_GRAY)
        p1_sub.next_to(p1, DOWN, buff=0.25)
        param_items.add(p1, p1_sub)

        # 数值强调框
        box1 = SurroundingRectangle(p1, color=C_GOLD, buff=0.15, stroke_width=2, corner_radius=0.08)
        arrow_up = Text("↑ 国际领先", font_size=24, color=C_GREEN)
        arrow_up.next_to(box1, RIGHT, buff=0.3)

        # 温度计动画
        thermo_body = Line(UP * 1.8, DOWN * 0.8, color=C_GRAY, stroke_width=6)
        thermo_body.move_to(RIGHT * 4.5)
        thermo_bulb = Circle(radius=0.25, color=C_GRAY, stroke_width=4)
        thermo_bulb.move_to(thermo_body.get_bottom())
        thermo_fill = Line(thermo_body.get_bottom(), thermo_body.get_bottom() + UP * 0.1,
                           color=C_CYAN, stroke_width=8)
        thermo_label = Text("极低温", font_size=16, color=C_GRAY)
        thermo_label.next_to(thermo_body, UP, buff=0.1)

        param_group = VGroup(p1, p1_sub, box1, arrow_up, thermo_body, thermo_bulb, thermo_fill, thermo_label)

        anims(([FadeOut(current)], 0.3),
              ([FadeIn(p1, shift=DOWN)], 1.0),
              ([Create(box1)], 0.5),
              ([Write(p1_sub), FadeIn(arrow_up)], 0.6),
              ([Create(thermo_body), Create(thermo_bulb)], 0.5),
              ([Create(thermo_fill), Write(thermo_label)], 0.4), idx=3)
        current = param_group

        # ============================================================
        # Segment 4: PAUSE
        # ============================================================
        # Hold current frame, no animations
        anims(idx=4)

        # ============================================================
        # Segment 5: 极限低温 5.42毫开尔文
        # ============================================================
        ext_title = Text("极限低温", font_size=44, color=C_TITLE, weight=BOLD)
        ext_title.move_to(UP * 2.5)
        ext_val = Text("5.42 毫开尔文", font_size=52, color=C_CYAN, weight=BOLD)
        ext_val.move_to(UP * 0.8)
        ext_note = Text("只比绝对零度高 0.00542°C", font_size=26, color=C_GRAY)
        ext_note.next_to(ext_val, DOWN, buff=0.25)

        # 接近绝对零度的视觉 - 用数字线
        num_line = Line(LEFT * 4, RIGHT * 4, color=C_GRAY, stroke_width=3)
        num_line.move_to(DOWN * 0.8)
        zero_label = Text("绝对零度", font_size=20, color=C_GRAY)
        zero_label.move_to(LEFT * 3.8 + DOWN * 0.8)
        small_tick = Line(LEFT * 3.8, LEFT * 3.8 + UP * 0.3, color=C_GRAY, stroke_width=2)
        # 5.42mK标记 - 非常接近0
        mk_tick = Line(RIGHT * 3.5, RIGHT * 3.5 + UP * 0.3, color=C_CYAN, stroke_width=3)
        mk_label = Text("5.42mK", font_size=18, color=C_CYAN)
        mk_label.move_to(RIGHT * 3.5 + UP * 0.5)

        s5 = VGroup(ext_title, ext_val, ext_note, num_line, zero_label, small_tick, mk_tick, mk_label)
        anims(([FadeOut(current)], 0.3),
              ([Write(ext_title)], 0.5),
              ([Write(ext_val)], 0.8),
              ([FadeIn(ext_note, shift=UP)], 0.5),
              ([Create(num_line), Create(small_tick)], 0.5),
              ([Create(mk_tick), Write(mk_label)], 0.5), idx=5)
        current = s5

        # ============================================================
        # Segment 6: 解释毫开尔文和绝对零度
        # ============================================================
        s6_title = Text("温度单位换算", font_size=36, color=C_TITLE, weight=BOLD)
        s6_title.move_to(UP * 2.5)

        def_box = Rectangle(width=5.0, height=1.8, color=C_GRAY, stroke_width=2)
        def_box.move_to(UP * 0.2)
        line1 = Text("1 毫开尔文 = 千分之一开尔文", font_size=26, color=C_WHITE)
        line1.move_to(UP * 0.6)
        line2 = Text("绝对零度 = -273.15°C", font_size=26, color=C_BLUE, weight=BOLD)
        line2.next_to(line1, DOWN, buff=0.3)
        line3 = Text("= 0 开尔文（K）", font_size=26, color=C_GRAY)
        line3.next_to(line2, DOWN, buff=0.15)

        temp_scale = Line(LEFT * 4, RIGHT * 4, color=C_GRAY, stroke_width=2)
        temp_scale.move_to(DOWN * 1.5)
        left_t = Text("0 K\n(-273.15°C)", font_size=18, color=C_CYAN)
        left_t.move_to(LEFT * 4 + DOWN * 1.5)
        right_t = Text("室温 300K", font_size=18, color=C_GRAY)
        right_t.move_to(RIGHT * 4 + DOWN * 1.5)
        arrow_mark = Arrow(LEFT * 4 + UP * 0.2, RIGHT * 4 + UP * 0.2, color=C_GRAY, stroke_width=2)

        s6 = VGroup(s6_title, def_box, line1, line2, line3, temp_scale, left_t, right_t, arrow_mark)
        anims(([FadeOut(current)], 0.3),
              ([Write(s6_title)], 0.5),
              ([Create(def_box)], 0.4),
              ([Write(line1)], 0.6),
              ([Write(line2)], 0.6),
              ([Write(line3)], 0.4),
              ([Create(temp_scale), Create(arrow_mark)], 0.5),
              ([Write(left_t), Write(right_t)], 0.5), idx=6)
        current = s6

        # ============================================================
        # Segment 7: 为什么量子计算需要低温
        # ============================================================
        s7_title = Text("为什么需要这么冷？", font_size=40, color=C_TITLE, weight=BOLD)
        s7_title.move_to(UP * 2.5)

        # 量子比特示意
        qbox = Square(side_length=1.2, color=C_CYAN, stroke_width=3)
        qbox.move_to(LEFT * 3 + DOWN * 0.3)
        q_label = Text("量子比特", font_size=20, color=C_CYAN)
        q_label.next_to(qbox, DOWN, buff=0.15)
        q_inner = Circle(radius=0.3, color=C_GOLD, stroke_width=3)
        q_inner.move_to(qbox.get_center())

        # 温度警告
