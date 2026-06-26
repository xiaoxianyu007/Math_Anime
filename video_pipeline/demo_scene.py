"""
勾股定理 - 赵爽弦图证明 v3
- 逐步推导，无跳步
- 弦图上标注 a、b、c 三边长度
- 代数化简逐条动画演示
- 使用 timings.py 中的 SEGMENT_DURATIONS 和 SEGMENT_IS_PAUSE 自适应时长
"""
from manim import *
import timings

# ============================================================
# 几何参数（3-4-5 三角形缩放：a=1.5, b=2.0, c=2.5）
# 大正方形边长 a+b=3.5
# 整体居中偏左，右侧留公式区
# ============================================================
A_LEG = 1.5
B_LEG = 2.0
C_HYP = 2.5
SIDE_SUM = A_LEG + B_LEG  # 3.5

SHIFT_X = -SIDE_SUM / 2 - 1.4   # -3.15（弦图更靠左，给右侧公式留足空间）
SHIFT_Y = -0.5 - SIDE_SUM / 2   # -2.25

def P(x, y):
    return np.array([x + SHIFT_X, y + SHIFT_Y, 0])


class GouGuTheorem(Scene):
    def construct(self):
        durs = timings.SEGMENT_DURATIONS
        is_pause = timings.SEGMENT_IS_PAUSE
        n = len(durs)

        C_TITLE = YELLOW
        C_A = BLUE
        C_B = GREEN
        C_C = RED
        C_TRI = ORANGE
        C_SQ = WHITE
        C_FORMULA = YELLOW
        C_HL = YELLOW

        def budget(i):
            return durs[i] if i < n else 2.0

        def anims(*plays, idx=None):
            """plays: 每项是 (animation_list_or_None, run_time)。None 表示纯等待。"""
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

        # ============================================================
        # 段1：开场标题
        # ============================================================
        title = Text("勾 股 定 理", font_size=72, color=C_TITLE, weight=BOLD)
        title.move_to(UP * 2.6)
        subtitle = Text("Pythagorean Theorem", font_size=28, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.2)

        anims(
            ([Write(title), FadeIn(subtitle, shift=DOWN)], 1.8),
            idx=0,
        )

        # ============================================================
        # 段2：画直角三角形 + 直角标记
        # ============================================================
        tri_center = LEFT * 3.0 + DOWN * 0.0
        dA = tri_center + DOWN * 0.9 + LEFT * 0.9
        dB = tri_center + DOWN * 0.9 + RIGHT * 1.1
        dC = tri_center + UP * 0.9 + LEFT * 0.9

        triangle = Polygon(dA, dB, dC, color=C_TRI, stroke_width=4)
        triangle.set_fill(C_TRI, opacity=0.2)
        rt_mark = RightAngle(Line(dA, dB), Line(dA, dC), length=0.28, color=WHITE, stroke_width=3)

        anims(
            ([FadeOut(subtitle),
              title.animate.scale(0.55).to_corner(UL, buff=0.3)], 0.8),
            ([Create(triangle)], 1.2),
            ([Create(rt_mark)], 0.5),
            idx=1,
        )

        # ============================================================
        # 段3：解释直角边和斜边（高亮对应的边）
        # ============================================================
        side_a_line = Line(dA, dC, color=C_A, stroke_width=8)
        side_b_line = Line(dA, dB, color=C_B, stroke_width=8)
        side_c_line = Line(dB, dC, color=C_C, stroke_width=8)

        t_leg = Text("直角边", font_size=24, color=WHITE)
        t_hyp = Text("斜边", font_size=24, color=WHITE)
        t_leg.next_to(dA, LEFT, buff=0.4)
        t_hyp.move_to((dB + dC) / 2 + UR * 0.55)

        anims(
            ([Create(side_a_line), Create(side_b_line)], 1.0),
            ([FadeIn(t_leg)], 0.4),
            ([FadeOut(t_leg), Create(side_c_line)], 0.8),
            ([FadeIn(t_hyp)], 0.4),
            idx=2,
        )

        # ============================================================
        # 段4：标注 a, b, c 字母
        # ============================================================
        # 移除临时高亮线和标签，换成正式字母标签
        lbl_a = Text("a", font_size=32, color=C_A, weight=BOLD).move_to((dA + dC) / 2 + LEFT * 0.35)
        lbl_b = Text("b", font_size=32, color=C_B, weight=BOLD).move_to((dA + dB) / 2 + DOWN * 0.35)
        lbl_c = Text("c", font_size=32, color=C_C, weight=BOLD).move_to((dB + dC) / 2 + UR * 0.3)

        anims(
            ([FadeOut(VGroup(side_a_line, side_b_line, side_c_line, t_hyp))], 0.3),
            ([Write(lbl_a), Write(lbl_b)], 0.6),
            ([Write(lbl_c)], 0.5),
            idx=3,
        )

        # ============================================================
        # 段5：陈述定理 a²+b²=c²
        # ============================================================
        formula = Text("a² + b² = c²", font_size=56, color=C_FORMULA, weight=BOLD)
        formula.move_to(RIGHT * 3.8 + DOWN * 0.0)
        fbox = SurroundingRectangle(formula, color=C_FORMULA, buff=0.2, stroke_width=2, corner_radius=0.1)

        anims(
            ([Write(formula)], 1.2),
            ([Create(fbox)], 0.6),
            idx=4,
        )

        # ============================================================
        # 段6：过渡到赵爽弦图（保留小公式在右上角）
        # ============================================================
        small_f = formula.copy().scale(0.5)
        small_f.to_corner(UR, buff=0.5)
        small_f.set_y(title.get_y())

        zhao_title = Text("赵爽弦图", font_size=44, color=C_TITLE, weight=BOLD)
        zhao_title.move_to(UP * 2.0)

        anims(
            ([FadeOut(VGroup(triangle, rt_mark, lbl_a, lbl_b, lbl_c, fbox)),
              Transform(formula, small_f)], 0.9),
            ([Write(zhao_title)], 1.0),
            idx=5,
        )

        # ============================================================
        # 段7：画大正方形
        # ============================================================
        big_sq = Polygon(
            P(0, 0), P(SIDE_SUM, 0), P(SIDE_SUM, SIDE_SUM), P(0, SIDE_SUM),
            color=C_SQ, stroke_width=3,
        )
        side_label_bottom = Text("a + b", font_size=24, color=WHITE)
        side_label_bottom.next_to(Line(P(0,0), P(SIDE_SUM,0)), DOWN, buff=0.15)
        side_label_left = Text("a+b", font_size=22, color=WHITE)
        side_label_left.next_to(Line(P(0,0), P(0,SIDE_SUM)), LEFT, buff=0.15)

        anims(
            ([FadeOut(zhao_title)], 0.4),
            ([Create(big_sq)], 1.3),
            ([Write(side_label_bottom), Write(side_label_left)], 0.6),
            idx=6,
        )

        # ============================================================
        # 段8：放入四个三角形
        # ============================================================
        t_bl = Polygon(P(0,0), P(B_LEG,0), P(0,A_LEG), color=C_TRI, stroke_width=2)
        t_bl.set_fill(C_TRI, opacity=0.75)
        t_br = Polygon(P(SIDE_SUM,0), P(B_LEG,0), P(SIDE_SUM,B_LEG), color=C_TRI, stroke_width=2)
        t_br.set_fill(C_TRI, opacity=0.75)
        t_tr = Polygon(P(SIDE_SUM,SIDE_SUM), P(SIDE_SUM,B_LEG), P(A_LEG,SIDE_SUM), color=C_TRI, stroke_width=2)
        t_tr.set_fill(C_TRI, opacity=0.75)
        t_tl = Polygon(P(0,SIDE_SUM), P(A_LEG,SIDE_SUM), P(0,A_LEG), color=C_TRI, stroke_width=2)
        t_tl.set_fill(C_TRI, opacity=0.75)
        triangles = VGroup(t_bl, t_br, t_tr, t_tl)

        anims(
            ([FadeOut(side_label_bottom), FadeOut(side_label_left)], 0.3),
            ([FadeIn(t_bl)], 0.5),
            ([FadeIn(t_br)], 0.5),
            ([FadeIn(t_tr)], 0.5),
            ([FadeIn(t_tl)], 0.5),
            idx=7,
        )

        # ============================================================
        # 段9：在弦图上标注 a、b、c（关键！每条边都标）
        # ============================================================
        # 四个三角形的 a, b 边标签（每个三角形都标短边a和长边b）
        # 只标两个代表位置即可，避免太乱：bl三角形的水平边b、垂直边a；
        # 另外在斜边c上标c
        def lbl_on_line(p1, p2, text, color, offset_dir=RIGHT*0.25+UP*0.15, size=24):
            mid = (p1 + p2) / 2
            return Text(text, font_size=size, color=color, weight=BOLD).move_to(mid + offset_dir)

        # 底部三角形(bl)：水平边(0,0)-(B_LEG,0)=b，垂直边(0,0)-(0,A_LEG)=a
        lbl_b1 = lbl_on_line(P(0,0), P(B_LEG,0), "b", C_B, DOWN*0.25, 22)
        lbl_a1 = lbl_on_line(P(0,0), P(0,A_LEG), "a", C_A, LEFT*0.25, 22)
        # 顶部三角形(tl)：a边在顶(A_LEG,SIDE_SUM)-(0,SIDE_SUM)是水平的... 实际(0,SIDE_SUM)-(A_LEG,SIDE_SUM)=b水平
        # 重新理清四个三角形的a,b边：
        # t_bl: vertices (0,0)[直角], (B_LEG,0), (0,A_LEG)
        #       水平边 (0,0)-(B_LEG,0) 长度 B_LEG=b，垂直边 (0,0)-(0,A_LEG) 长度 A_LEG=a
        # t_br: vertices (SIDE_SUM,0)[直角], (B_LEG,0), (SIDE_SUM,B_LEG)
        #       水平边 (B_LEG,0)-(SIDE_SUM,0) 长度 A_LEG=a，垂直边 (SIDE_SUM,0)-(SIDE_SUM,B_LEG) 长度 B_LEG=b
        # t_tr: vertices (SIDE_SUM,SIDE_SUM)[直角], (SIDE_SUM,B_LEG), (A_LEG,SIDE_SUM)
        #       水平边 (A_LEG,SIDE_SUM)-(SIDE_SUM,SIDE_SUM) 长度 B_LEG=b，垂直边 (SIDE_SUM,B_LEG)-(SIDE_SUM,SIDE_SUM) 长度 A_LEG=a
        # t_tl: vertices (0,SIDE_SUM)[直角], (A_LEG,SIDE_SUM), (0,A_LEG)
        #       水平边 (0,SIDE_SUM)-(A_LEG,SIDE_SUM) 长度 A_LEG=a，垂直边 (0,A_LEG)-(0,SIDE_SUM) 长度 B_LEG=b

        # 右侧三角形(tr)的垂直边a (SIDE_SUM,B_LEG)-(SIDE_SUM,SIDE_SUM)
        lbl_a2 = lbl_on_line(P(SIDE_SUM,B_LEG), P(SIDE_SUM,SIDE_SUM), "a", C_A, RIGHT*0.25, 22)
        # 底部三角形(br)的水平边a (B_LEG,0)-(SIDE_SUM,0) = a
        lbl_a3 = lbl_on_line(P(B_LEG,0), P(SIDE_SUM,0), "a", C_A, DOWN*0.25, 22)
        # 顶部左侧三角形(tl)的水平边a (0,SIDE_SUM)-(A_LEG,SIDE_SUM)
        lbl_a4 = lbl_on_line(P(0,SIDE_SUM), P(A_LEG,SIDE_SUM), "a", C_A, UP*0.25, 22)
        # 右侧三角形的水平边b (A_LEG,SIDE_SUM)-(SIDE_SUM,SIDE_SUM) = b
        lbl_b2 = lbl_on_line(P(A_LEG,SIDE_SUM), P(SIDE_SUM,SIDE_SUM), "b", C_B, UP*0.25, 22)
        # 左侧三角形垂直边b (0,A_LEG)-(0,SIDE_SUM) = b
        lbl_b3 = lbl_on_line(P(0,A_LEG), P(0,SIDE_SUM), "b", C_B, LEFT*0.25, 22)
        # 右侧三角形垂直边b (SIDE_SUM,0)-(SIDE_SUM,B_LEG) = b
        lbl_b4 = lbl_on_line(P(SIDE_SUM,0), P(SIDE_SUM,B_LEG), "b", C_B, RIGHT*0.25, 22)

        a_labels = VGroup(lbl_a1, lbl_a2, lbl_a3, lbl_a4)
        b_labels = VGroup(lbl_b1, lbl_b2, lbl_b3, lbl_b4)

        # 斜边标签（只标一个即可，代表所有斜边都是c）
        V1 = P(B_LEG, 0)
        V2 = P(SIDE_SUM, B_LEG)
        V3 = P(A_LEG, SIDE_SUM)
        V4 = P(0, A_LEG)
        c_sq = Polygon(V1, V2, V3, V4, color=C_C, stroke_width=3)
        hyp_lbl = Text("c", font_size=22, color=C_C, weight=BOLD)
        hyp_mid = (V1 + V2) / 2
        hyp_lbl.move_to(hyp_mid + DR * 0.25)

        anims(
            ([FadeIn(a_labels), FadeIn(b_labels)], 1.0),
            ([], 0.3),
            ([Create(c_sq), Write(hyp_lbl)], 1.0),
            idx=8,
        )

        # ============================================================
        # 段10：[pause:1.2] 让观众观察弦图
        # ============================================================
        anims(
            idx=9,
        )

        # ============================================================
        # 段11：中间区域是空的
        # ============================================================
        c_sq.set_fill(C_C, opacity=0.0)  # 先不填色，只轮廓
        # 用一个脉动效果提示中间区域
        pulse = c_sq.copy().set_stroke(C_HL, width=6)
        anims(
            ([FadeIn(pulse)], 0.4),
            ([], 0.3),
            ([FadeOut(pulse)], 0.4),
            idx=10,
        )

        # ============================================================
        # 段12：中间是c²正方形（填色+面积标签）
        # ============================================================
        c_sq.set_fill(C_C, opacity=0.4)
        c_center = (V1 + V2 + V3 + V4) / 4
        c2_label = Text("c²", font_size=40, color=C_C, weight=BOLD).move_to(c_center)

        anims(
            ([c_sq.animate.set_fill(C_C, opacity=0.4)], 0.8),
            ([FadeOut(hyp_lbl), Write(c2_label)], 0.8),
            idx=11,
        )

        # ============================================================
        # 段13-17：代数推导（右侧逐条显示公式）
        # 公式区在右侧，x ≈ 3.2（弦图左移后有充足空间）
        # ============================================================
        FX = 3.4
        FY_START = 2.3
        fs = 25
        fs_big = 30

        # 段13：大正方形面积 = (a+b)²
        eq1 = Text("大正方形面积 = (a+b)²", font_size=fs, color=WHITE)
        eq1.move_to(RIGHT * FX + UP * FY_START)
        anims(
            ([Write(eq1)], 1.2),
            idx=12,
        )

        # 段14：= 4×三角形 + c² = 4×½ab + c² = 2ab + c²
        eq2a = Text("= 4 × 三角形面积 + c²", font_size=fs, color=WHITE)
        eq2a.next_to(eq1, DOWN, buff=0.22, aligned_edge=LEFT)
        eq2b = Text("= 4 × (1/2)ab + c²", font_size=fs, color=WHITE)
        eq2b.next_to(eq2a, DOWN, buff=0.16, aligned_edge=LEFT)
        eq2c = Text("= 2ab + c²", font_size=fs, color=WHITE)
        eq2c.next_to(eq2b, DOWN, buff=0.16, aligned_edge=LEFT)
        anims(
            ([Write(eq2a)], 1.0),
            ([], 0.2),
            ([Write(eq2b)], 1.0),
            ([], 0.2),
            ([Write(eq2c)], 1.0),
            idx=13,
        )

        # 段15：得到 (a+b)² = 2ab + c²
        eq3 = Text("得到：(a+b)² = 2ab + c²", font_size=fs_big, color=C_HL, weight=BOLD)
        eq3.next_to(eq2c, DOWN, buff=0.30, aligned_edge=LEFT)
        box3 = SurroundingRectangle(eq3, color=C_HL, buff=0.1, stroke_width=2, corner_radius=0.08)
        anims(
            ([Write(eq3)], 1.0),
            ([Create(box3)], 0.5),
            idx=14,
        )

        # 段16：展开左边 a²+2ab+b² = 2ab+c²（用 VGroup 拼接，方便高亮 2ab）
        eq4_label = Text("展开左边：", font_size=fs-2, color=GRAY_B)
        eq4_label.next_to(eq3, DOWN, buff=0.30, aligned_edge=LEFT)
        # 用分段 Text 拼接，便于精确高亮 2ab
        t_a2 = Text("a²", font_size=fs_big, color=WHITE, weight=BOLD)
        t_plus1 = Text(" + ", font_size=fs_big, color=WHITE, weight=BOLD)
        t_2ab_l = Text("2ab", font_size=fs_big, color=C_A, weight=BOLD)
        t_plus2 = Text(" + ", font_size=fs_big, color=WHITE, weight=BOLD)
        t_b2 = Text("b²", font_size=fs_big, color=WHITE, weight=BOLD)
        t_eq = Text(" = ", font_size=fs_big, color=WHITE, weight=BOLD)
        t_2ab_r = Text("2ab", font_size=fs_big, color=C_A, weight=BOLD)
        t_plus3 = Text(" + ", font_size=fs_big, color=WHITE, weight=BOLD)
        t_c2 = Text("c²", font_size=fs_big, color=WHITE, weight=BOLD)
        eq4b = VGroup(t_a2, t_plus1, t_2ab_l, t_plus2, t_b2, t_eq, t_2ab_r, t_plus3, t_c2)
        eq4b.arrange(RIGHT, buff=0.05, aligned_edge=DOWN)
        eq4b.next_to(eq4_label, DOWN, buff=0.15, aligned_edge=LEFT)
        # 初始时 2ab 为白色（与其他一致），段17再变色+划线
        t_2ab_l.set_color(WHITE)
        t_2ab_r.set_color(WHITE)

        anims(
            ([Write(eq4_label)], 0.5),
            ([Write(eq4b)], 1.5),
            idx=15,
        )

        # 段17：两边减去 2ab（高亮两个 2ab，然后划掉）
        # 用 ShowPassingFlash 或颜色变化 + 划线
        strike_l = Line(t_2ab_l.get_left() + LEFT*0.05, t_2ab_l.get_right() + RIGHT*0.05,
                        color=RED, stroke_width=5)
        strike_r = Line(t_2ab_r.get_left() + LEFT*0.05, t_2ab_r.get_right() + RIGHT*0.05,
                        color=RED, stroke_width=5)
        anims(
            ([t_2ab_l.animate.set_color(C_A),
              t_2ab_r.animate.set_color(C_A)], 0.5),
            ([Create(strike_l), Create(strike_r)], 0.6),
            ([], 0.3),
            idx=16,
        )

        # ============================================================
        # 段18：[pause:1.8] 思考停顿
        # ============================================================
        anims(
            idx=17,
        )

        # ============================================================
        # 段19：揭示结论 a²+b²=c²！
        # ============================================================
        # 所有代数公式 + 右上角公式 + 顶部标题（统一淡出，突出最终结论）
        all_algebra = VGroup(eq1, eq2a, eq2b, eq2c, eq3, box3,
                             eq4_label, eq4b, strike_l, strike_r)
        header_group = VGroup(title, formula)

        conclude = Text("千古名定理，得证！", font_size=44, color=C_TITLE, weight=BOLD)
        conclude.move_to(UP * 2.5)

        # 弦图极淡化为背景
        dim_group = VGroup(big_sq, t_bl, t_br, t_tr, t_tl, c_sq, c2_label,
                           a_labels, b_labels)

        # 最终公式从右侧推导位置移到屏幕正中央
        eq_final = Text("a² + b² = c²", font_size=64, color=C_FORMULA, weight=BOLD)
        eq_final.move_to(RIGHT * 1.5 + DOWN * 0.3)
        box_final = SurroundingRectangle(eq_final, color=C_FORMULA, buff=0.25, stroke_width=3, corner_radius=0.12)
        arrow = Arrow(eq4b.get_bottom() + DOWN*0.1, eq_final.get_top() + UP*0.1,
                      color=C_HL, buff=0.15, stroke_width=4)

        anims(
            ([GrowArrow(arrow)], 0.4),
            ([Write(eq_final), Create(box_final)], 0.9),
            # 先淡出公式和箭头
            ([FadeOut(VGroup(all_algebra, arrow, header_group))], 0.3),
            # 弦图淡化 + 公式移到中央 + 标题淡入
            ([dim_group.animate.set_opacity(0.15),
              eq_final.animate.move_to(ORIGIN + DOWN * 0.1),
              box_final.animate.move_to(ORIGIN + DOWN * 0.1),
              FadeIn(conclude, shift=DOWN)], 1.0),
            idx=18,
        )

        # ============================================================
        # 段20：结尾互动
        # ============================================================
        end_text = Text("你还知道其他证明方法吗？", font_size=44, color=C_C, weight=BOLD)
        end_text.move_to(UP * 0.3)
        sub_text = Text("欢迎在评论区分享你的答案", font_size=26, color=GRAY_B)
        sub_text.next_to(end_text, DOWN, buff=0.5)

        anims(
            ([FadeOut(VGroup(dim_group, c2_label, title, formula, conclude,
                            eq_final, box_final, c_sq))], 0.8),
            ([Write(end_text)], 1.0),
            ([FadeIn(sub_text, shift=UP)], 0.5),
            idx=19,
        )
