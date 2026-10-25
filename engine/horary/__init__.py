"""Horary astrology (chiêm tinh vấn sự) for Thiên Bàn: a chart for the moment a question is received, judged by the rules of
traditional horary (William Lilly, Christian Astrology 1647, as primary school; Bonatti's Considerations as second school).

Kept apart from engine/western (natal astrology): it reuses only western's astronomy (ephemeris, time resolution, angles and
house formulas, zodiac arithmetic). No natal rule is used to judge a question. No LLM is called at any point: the chart is
computed, the judgment is rule-based and every conclusion carries the planets, houses, aspects, rule ids and book pages it
rests on. The astronomy is exact and checkable; the judgments are the tradition's, which no scientific test has shown to
predict events. See docs/HORARY-KB.md and docs/HORARY-ENGINE.md.
"""
