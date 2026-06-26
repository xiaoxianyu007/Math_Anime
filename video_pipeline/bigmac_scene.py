from manim import *
import timings

C_TITLE = YELLOW
C_W = WHITE
C_G = GRAY_B
C_GOLD = GOLD_E
C_R = RED_C
C_GRN = GREEN_C
C_O = ORANGE
C_P = PURPLE_C


class BigMacScene(Scene):
    def construct(self):
        durs = timings.SEGMENT_DURATIONS
        is_pause = timings.SEGMENT_IS_PAUSE
        n = len(durs)

        def anims(*plays, idx=None):
            used = 0.0
            for angs, rt in plays:
                if angs and len(angs) > 0:
                    self.play(*angs, run_time=rt)
                else:
                    self.wait(rt)
                used += rt
            if idx is not None:
                rem = durs[idx] - used if idx < n else 0.5
                if rem > 0:
                    self.wait(rem)

        # 角标
        corner = Text("一个汉堡看懂全世界", font_size=22, color=C_TITLE, weight=BOLD)
        corner.move_to(UP * 3.2 + LEFT * 5.8)

        # 当前段的内容组（用于清理）
        current = VGroup()
        def next_seg(new_grp, plays_and_idx):
            """先 FadeOut 旧内容，再执行动画"""
            nonlocal current
            if current:
                # 旧内容消失 + 新动画同步进行
                for plays, idx in plays_and_idx:
                    all_anims = [FadeOut(current)]
                    for a in plays:
                        all_anims.extend(a if isinstance(a, list) else [a])
                    self.play(*all_anims, run_time=0.3)
                    break  # 只取第一个 play 来做过渡
            # 剩余的 plays
            offset = 1 if current else 0
            for plays, idx in plays_and_idx[offset:]:
                if plays and len(plays) > 0:
                    self.play(*plays, run_time=0.5)
                else:
                    self.wait(0.5)
            current = new_grp

        # ================================================================
        # 段0：Hook — 三条价格条
        # ================================================================
        t0 = Text("一个汉堡 价格差三倍", font_size=44, color=C_TITLE, weight=BOLD)
        t0.move_to(UP * 2.5)

        def price_bar(label, w, col, pos, val):
            lbl = Text(label, font_size=22, color=col).move_to(LEFT * 5 + UP * pos)
            bar = Rectangle(width=w, height=0.45, color=col, fill_color=col, fill_opacity=0.75)
            bar.move_to(LEFT * 1.2 + UP * pos).align_to(LEFT * 4.0, LEFT)
            p = Text(val, font_size=18, color=C_W, weight=BOLD).next_to(bar, RIGHT, buff=0.12)
            return VGroup(lbl, bar, p)

        ch = price_bar("瑞士", 7.0, C_R, 1.2, "$7.99")
        za = price_bar("南非", 2.3, C_GRN, 0.3, "$2.78")
        cn = price_bar("中国", 3.0, C_O, -0.6, "$3.52")

        s0 = VGroup(t0, ch, za, cn)
        anims(([Write(t0)], 0.6), ([Write(ch)], 0.6), ([Write(za)], 0.6), ([Write(cn)], 0.6), idx=0)
        current = s0

        # ================================================================
        # 段1：巨无霸指数 — 关键词
        # ================================================================
        k1 = Text("巨无霸指数", font_size=44, color=C_TITLE, weight=BOLD).move_to(UP * 1.5)
        k1a = Text("全球同款商品比价 → 判断汇率高低", font_size=28, color=C_W).move_to(DOWN * 0.3)
        s1 = VGroup(k1, k1a)
        anims(([FadeOut(current), Write(k1)], 0.3), ([Write(k1a)], 0.5), idx=1)
        current = s1

        # ================================================================
        # 段2：中国数据 — 关键词
        # ================================================================
        k2 = Text("中国 被低估 39%", font_size=46, color=C_O, weight=BOLD).move_to(UP * 1.0)
        k2a = Text("3.52 美元 vs 美国 5.79 美元", font_size=28, color=C_W).move_to(DOWN * 0.3)
        s2 = VGroup(k2, k2a)
        anims(([FadeOut(current), Write(k2)], 0.3), ([Write(k2a)], 0.5), idx=2)
        current = s2

        # ================================================================
        # 段3：日本数据 — 关键词
        # ================================================================
        k3 = Text("日本 被低估 46%", font_size=46, color=C_R, weight=BOLD).move_to(UP * 1.0)
        k3a = Text("购买力翻倍  相当于打五折", font_size=30, color=C_GRN, weight=BOLD).move_to(DOWN * 0.3)
        s3 = VGroup(k3, k3a)
        anims(([FadeOut(current), Write(k3)], 0.3), ([Write(k3a)], 0.5), idx=3)
        current = s3

        # ================================================================
        # 段4：[pause:1.2] — 保留画面
        # ================================================================
        anims(idx=4)

        # ================================================================
        # 段5：设问 — 关键词
        # ================================================================
        k5 = Text("为什么有些货币天生就强？", font_size=38, color=C_TITLE, weight=BOLD).move_to(UP * 0.8)
        k5a = Text("瑞士法郎  挪威克朗  美元", font_size=28, color=C_W).move_to(DOWN * 0.5)
        s5 = VGroup(k5, k5a)
        anims(([FadeOut(current), Write(k5)], 0.3), ([Write(k5a)], 0.5), idx=5)
        current = s5

        # ================================================================
        # 段6：巴拉萨效应 — 箭头链条
        # ================================================================
        k6t = Text("巴拉萨-萨缪尔森效应", font_size=34, color=C_TITLE, weight=BOLD).move_to(UP * 2.0)

        a1 = Arrow(LEFT * 3.5, LEFT * 0.5, color=C_GRN, stroke_width=3)
        a2 = Arrow(LEFT * 0.5, RIGHT * 1.2, color=C_GRN, stroke_width=3)
        a3 = Arrow(RIGHT * 1.2, RIGHT * 3.8, color=C_GRN, stroke_width=3)

        l1 = Text("制造业高效", font_size=22, color=C_GRN).move_to(LEFT * 5)
        l2 = Text("全社会高薪", font_size=22, color=C_O).move_to(LEFT * 1.5 + UP * 0.2)
        l3 = Text("服务价格高", font_size=22, color=C_P).move_to(RIGHT * 1.0)
        l4 = Text("货币强势", font_size=22, color=C_R, weight=BOLD).move_to(RIGHT * 4.0)

        chain = VGroup(a1, a2, a3, l1, l2, l3, l4).move_to(DOWN * 0.2)
        k6f = Text("越高效 → 理发越贵 → 货币越强", font_size=20, color=C_G).move_to(DOWN * 1.8)
        s6 = VGroup(k6t, chain, k6f)
        anims(
            ([FadeOut(current), Write(k6t)], 0.3),
            ([Write(l1)], 0.3), ([GrowArrow(a1), Write(l2)], 0.4),
            ([GrowArrow(a2), Write(l3)], 0.4), ([GrowArrow(a3), Write(l4)], 0.4),
            ([Write(k6f)], 0.4), idx=6,
        )
        current = s6

        # ================================================================
        # 段7：瑞士例子
        # ================================================================
        k7 = Text("瑞士：年薪百万  vs  理发几百", font_size=34, color=C_GOLD, weight=BOLD).move_to(UP * 1.0)
        k7a = Text("程序员高薪 → 理发师也要涨薪 → 物价全涨", font_size=26, color=C_W).move_to(DOWN * 0.5)
        k7b = Text("→ 货币自然强", font_size=28, color=C_TITLE, weight=BOLD).move_to(DOWN * 1.5)
        s7 = VGroup(k7, k7a, k7b)
        anims(([FadeOut(current), Write(k7)], 0.3), ([Write(k7a)], 0.5), ([Write(k7b)], 0.4), idx=7)
        current = s7

        # ================================================================
        # 段8：[pause:1.0] — 保留画面
        # ================================================================
        anims(idx=8)

        # ================================================================
        # 段9：旅游价值洼地
        # ================================================================
        k9 = Text("货币被低估 = 旅游价值洼地", font_size=34, color=C_TITLE, weight=BOLD).move_to(UP * 1.0)
        k9a = Text("日本：教科书级案例", font_size=30, color=C_GRN, weight=BOLD).move_to(DOWN * 0.3)
        k9b = Text("汇率是最好的促销券", font_size=28, color=C_GOLD, weight=BOLD).move_to(DOWN * 1.3)
        s9 = VGroup(k9, k9a, k9b)
        anims(([FadeOut(current), Write(k9)], 0.3), ([Write(k9a)], 0.4), ([Write(k9b)], 0.4), idx=9)
        current = s9

        # ================================================================
        # 段10：日本旅游数据
        # ================================================================
        k10 = Text("2025年 访日游客 4260 万", font_size=42, color=C_R, weight=BOLD).move_to(UP * 1.0)
        k10a = Text("同比增长 16%  创历史新高", font_size=28, color=C_GRN).move_to(UP * 0.0)
        k10b = Text("中国游客 910 万 占 21%", font_size=26, color=C_W).move_to(DOWN * 0.8)
        k10c = Text("汇率贬值 + 购物红利 = 大爆发", font_size=26, color=C_GOLD, weight=BOLD).move_to(DOWN * 1.8)
        s10 = VGroup(k10, k10a, k10b, k10c)
        anims(([FadeOut(current), Write(k10)], 0.3), ([Write(k10a)], 0.4), ([Write(k10b)], 0.4), ([Write(k10c)], 0.4), idx=10)
        current = s10

        # ================================================================
        # 段11：[pause:0.8] — 保留画面
        # ================================================================
        anims(idx=11)

        # ================================================================
        # 段12：iPhone价差
        # ================================================================
        k12 = Text("同款 iPhone 价差两倍", font_size=36, color=C_TITLE, weight=BOLD).move_to(UP * 1.5)
        k12a = Text("土耳其 $2,182", font_size=28, color=C_R, weight=BOLD).move_to(LEFT * 1.5 + UP * 0.2)
        k12b = Text("中国 $840", font_size=28, color=C_GRN, weight=BOLD).move_to(LEFT * 1.5 + DOWN * 0.5)
        k12c = Text("差 2.6 倍", font_size=26, color=C_TITLE, weight=BOLD).move_to(RIGHT * 2.5 + UP * 0.2)
        s12 = VGroup(k12, k12a, k12b, k12c)
        anims(([FadeOut(current), Write(k12)], 0.3), ([Write(k12a), Write(k12b)], 0.5), ([Write(k12c)], 0.3), idx=12)
        current = s12

        # ================================================================
        # 段13：三层过滤
        # ================================================================
        k13 = Text("三层过滤", font_size=40, color=C_TITLE, weight=BOLD).move_to(UP * 1.5)
        k13a = Text("1. 汇率换算", font_size=26, color=C_W).move_to(UP * 0.3)
        k13b = Text("2. 关税 + 增值税", font_size=26, color=C_W).move_to(DOWN * 0.4)
        k13c = Text("3. 品牌定价策略", font_size=26, color=C_W).move_to(DOWN * 1.1)
        k13d = Text("土耳其：汇率崩 + 50% 奢侈税 = 全球最贵", font_size=20, color=C_R).move_to(DOWN * 2.0)
        s13 = VGroup(k13, k13a, k13b, k13c, k13d)
        anims(([FadeOut(current), Write(k13)], 0.3), ([Write(k13a)], 0.4), ([Write(k13b)], 0.4), ([Write(k13c)], 0.4), ([Write(k13d)], 0.4), idx=13)
        current = s13

        # ================================================================
        # 段14：汇率幻觉 — 现象
        # ================================================================
        k14 = Text("汇率幻觉：土耳其", font_size=38, color=C_R, weight=BOLD).move_to(UP * 1.5)
        k14a = Text("里拉暴跌 90%", font_size=40, color=C_TITLE, weight=BOLD).move_to(UP * 0.3)
        k14b = Text("可乐 → 34 元", font_size=36, color=C_R, weight=BOLD).move_to(DOWN * 0.5)
        k14c = Text("为什么？", font_size=28, color=C_TITLE, weight=BOLD).move_to(DOWN * 1.5)
        s14 = VGroup(k14, k14a, k14b, k14c)
        anims(([FadeOut(current), Write(k14)], 0.3), ([Write(k14a)], 0.4), ([Write(k14b)], 0.4), ([Write(k14c)], 0.3), idx=14)
        current = s14

        # ================================================================
        # 段15：汇率幻觉 — 原因
        # ================================================================
        k15 = Text("景区有自己的定价体系", font_size=34, color=C_TITLE, weight=BOLD).move_to(UP * 1.0)
        k15a = Text("欧元定价  两套价签  月月涨价", font_size=28, color=C_W).move_to(UP * 0.0)
        k15b = Text("贬值九成 ≠ 便宜九成", font_size=32, color=C_TITLE, weight=BOLD).move_to(DOWN * 1.0)
        s15 = VGroup(k15, k15a, k15b)
        anims(([FadeOut(current), Write(k15)], 0.3), ([Write(k15a)], 0.4), ([Write(k15b)], 0.4), idx=15)
        current = s15

        # ================================================================
        # 段16：[pause:1.2] — 保留画面
        # ================================================================
        anims(idx=16)

        # ================================================================
        # 段17：总结 — 5条关键词
        # ================================================================
        k17t = Text("一张汉堡 看懂世界", font_size=38, color=C_TITLE, weight=BOLD).move_to(UP * 1.8)

        items = VGroup(
            Text("巨无霸指数 → 汇率高低", font_size=22, color=C_GRN),
            Text("劳动效率 → 货币强弱", font_size=22, color=C_O),
            Text("汇率 → 旅游折扣", font_size=22, color=C_GOLD),
            Text("三层过滤 → 品牌价差", font_size=22, color=C_P),
            Text("汇率幻觉 → 贬值≠便宜", font_size=22, color=C_R),
        )
        items.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        items.next_to(k17t, DOWN, buff=0.3, aligned_edge=LEFT)
        items.move_to(ORIGIN + LEFT * 0.5)

        s17 = VGroup(k17t, items)
        anims(([FadeOut(current), Write(k17t)], 0.3), idx=17)
        for item in items:
            self.play(Write(item), run_time=0.3)
        used = 0.3 + 5 * 0.3
        rem = durs[17] - used
        if rem > 0:
            self.wait(rem)
        current = s17

        # ================================================================
        # 段18：结尾
        # ================================================================
        end_t = Text("你还知道哪些全球化指标？", font_size=40, color=C_TITLE, weight=BOLD).move_to(UP * 0.3)
        end_sub = Text("在评论区说说吧", font_size=26, color=C_G).next_to(end_t, DOWN, buff=0.5)
        s18 = VGroup(end_t, end_sub)
        anims(([FadeOut(current), Write(end_t)], 0.3), ([FadeIn(end_sub, shift=UP)], 0.4), idx=18)
