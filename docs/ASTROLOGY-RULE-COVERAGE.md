# Astrology rule coverage (2026-10-18)

This document says what the engine computes, from which source, and what it interprets.

- **Status vocabulary.** *verified* means the cited page says it. *convention* means a common formula with no page in the three Tử Vi books. *NEEDS SOURCE* and *NEEDS DECISION* are as in INTERPRETATION-ENGINE-AUDIT.md.
- **Abbreviations.** KL = Tử Vi Khảo Luận; TH = Tử Vi Thực Hành; TT = Tử Vi Đẩu Số Toàn Thư; ZZ = 八字真宗; TVH = Thiệu Vĩ Hoa, *Dự Đoán Theo Tứ Trụ*; TTT = Trích Thiên Tủy.

## 1. Tử Vi: calculation

| Item | Source | Status | Note |
|---|---|---|---|
| Mệnh, Thân, Cục, 14 chính tinh | KL, TH (golden tests incl. 5 KL worked charts) | verified | |
| Tả Hữu, Xương Khúc, Khôi Việt, Lộc Tồn, Kình Đà, Thiên Mã, Hỏa Linh, Không Kiếp, Thiên Không, Đào Hồng Hỷ, Tuần Triệt | KL pp.26-36, TH pp.19-27 | verified | |
| Three rings (Thái Tuế, Lộc Tồn / Bác Sĩ, Trường Sinh) | KL, TH | verified | KL pp.33-34 Trường Sinh variant not disclosed (TV-12) |
| Tứ Hóa (natal) | KL pp.36, 196-197; TH | verified | Canh and Nhâm disputes not shown in the UI (TV-4/5) |
| ~30 "unverified" aux stars (Khốc Hư, Long Phượng, Cô Quả, Hình Riêu, Thai Tọa, Quang Quý…) | printed in KL pp.26-36 and TH pp.19-27 (TV-9) | formula convention in code | Thiên Quý **fixed** (TV-1); Lưu Hà matches neither book (TV-2, NEEDS DECISION); no rule uses these stars |
| Quốc Ấn, Đường Phù, Phong Cáo, Giải Thần, Thai Phụ | KL / TH print them (TV-9) | not placed | could be placed and golden-tested |
| Chính tinh brightness | TH pp.29-48 (default), TT (selectable) | verified per school | KL pp.74-115 table missing (TV-3) |
| Aux brightness | TT `dignity_minor.json`; TH work in progress elsewhere | partial | never invented; empty cells stay empty |
| Đại hạn start and direction | TH p.27 | verified | |
| Tiểu hạn | TH p.27 | verified (TH) | KL pp.39-40 differ for âm-stem births (TV-6, NEEDS DECISION) |
| Lưu Thái Tuế, Tang Môn, Bạch Hổ, Khốc, Hư, Lộc Tồn, Kình, Đà, Mã | KL pp.41-42 (TH p.114 same list) | verified (**this branch**) | lưu Khôi/Việt: convention, experimental only |
| Lưu Tứ Hóa | none of KL/TH/TT | convention, positions only (**this branch**) | |
| Đại hạn Tứ Hóa | none | convention, NEEDS SOURCE | |
| Lưu Tuần/Triệt | TH p.114 | not implemented | |
| Lưu nguyệt Tử Vi | KL p.41 (monthly palace) | not implemented | |
| Mệnh chủ / Thân chủ | not in KL/TH/TT | convention, NEEDS SOURCE | Tý/Ngọ Thân chủ differs between schools |

### Aux-star registry (sub-audit, as found on 6c10cf5)

Columns: formula in code (file:line) · source and page · golden test · positional notes in sources · brightness table in repo (source) · rules using the star · UI class (util.js:43-44), and whether that class is sourced.
"Both" means KL and TH print the same formula. "TH-grp" means the star's block in the TH pp.18-26 layout grouping (cát = items 3-25, hung = items 26-39).

| Star(s) | Formula (code) | Source / page | Golden test | Positional notes in sources | Brightness table (repo) | Used by rules? | UI class / sourced? |
|---|---|---|---|---|---|---|---|
| Tả Phụ / Hữu Bật | tuvi.py:227-228 (Thìn+m−1 / Tuất−(m−1)) | Both: KL p.26, TH p.19 | test_book_examples (book charts), oracle_tuvi_independent | Tứ mộ đắc (TH p.51) | dignity_aux_th.json (TH p.51) | yes (many packs) | cát / TH-grp cát ✓ |
| Văn Xương / Văn Khúc | tuvi.py:229-230 | Both: KL p.27, TH p.19 | test_book_examples, oracle | Ngọ Tuất hãm, etc. | aux_th (TH p.50), minor (TT pp.41,43) | yes | cát / ✓ |
| Thiên Khôi / Việt | tuvi.py:238-239, KHOI_VIET:66 | Both: KL p.30, TH p.19 (Canh Tân Ngọ Dần) | test_khoi_viet_verse_p19 | – | NONE | yes | cát / ✓ |
| Lộc Tồn | tuvi.py:232, LOC_TON:65 | Both: KL p.28, TH p.21 | test_loc_ton_kinh_da_p24 | – | NONE | yes | cát / ✓ |
| Thiên Mã (by year) | tuvi.py:241 | Both: KL pp.31-32, TH p.21 | test_year_branch_stars_pp21_23 | Tỵ Dần đắc (TH p.52) | aux_th (TH p.52; only Tỵ, Dần) | yes | **neutral** / TH-grp cát → mismatch |
| Kình Dương / Đà La | tuvi.py:233-234 | Both: KL p.29, TH p.24 | test_loc_ton_kinh_da_p24 | Tứ mộ miếu (TT) | minor (TT pp.50-51) only, fallback under TH (TV-15) | yes | hung / ✓ |
| Hỏa / Linh | tuvi.py:242-243, HOA_START/LINH_START:88-89 | Both: KL p.27 (table), TH p.25 (direction by âm dương nam nữ) | test_hoa_linh_p25 (male and female) | Hỏa: Dần Ngọ Tuất miếu (TT) | Hỏa: minor (TT p.52). Linh: NONE | yes | hung / ✓ |
| Địa Không / Kiếp | tuvi.py:244-245 | Both: KL p.27, TH p.24-25 | test_dia_kiep_khong_p24_25 | – | NONE | yes | hung / ✓ |
| Thiên Không | tuvi.py:250 (Thái Tuế + 1) | Both: KL p.30, TH p.25 | test_year_branch_stars_pp21_23 | – | NONE | yes | hung / ✓ |
| Đào Hoa / Hồng Loan / Thiên Hỷ | tuvi.py:246-249 | Both: KL p.31, TH p.23 (TH's Mùi example contradicts its own rule; KL's Ất Mão example gives Hồng Loan Tý, consistent with the rule) | test_year_branch_stars_pp21_23 | – | NONE | yes | Hồng, Hỷ cát; **Đào neutral** (TH-grp cát) |
| Thiên Khốc / Hư | aux_stars.py:38-39 | Both: KL p.32, TH p.25 | none (self-test only: test_sample_positions_1990, mirror test) | Hư sits with Tuế Phá (KL p.32) | NONE | no | hung / TH-grp hung ✓ |
| Thiên Hình / Thiên Riêu (Diêu) / Thiên Y | aux_stars.py:53-55 | Both: KL p.26, TH p.25 | none (self-test) | – | NONE | Thiên Hình: synthesis/structures.py:211 | Hình, Riêu hung; **Y cát** but TH-grp hung → mismatch |
| Cô Thần / Quả Tú | aux_stars.py:42-44 | Both: KL p.32, TH p.25 | none (self-test) | Cô always tứ sinh, Quả tứ mộ (KL p.32) | NONE | no (BaZi shensha.json is a separate system) | hung / TH-grp hung ✓ |
| Thiên Đức / Nguyệt Đức | aux_stars.py:64-65 | Both: KL pp.30-31 (Thiên Đức with Phúc Đức of the Thái Tuế ring), TH p.24 | none | – | NONE | no | cát / TH-grp cát ✓ |
| Long Trì / Phượng Các | aux_stars.py:40-41 | Both: KL p.31, TH p.20 | none (self-test) | – | NONE | no | cát / TH-grp cát ✓ |
| Tam Thai / Bát Tọa | aux_stars.py:67-68 | Both: KL pp.27-28, TH pp.19-20 | none | mirror pair | NONE | no | cát / ✓ |
| Ân Quang / Thiên Quý | aux_stars.py:69-70 | Both: KL p.28, TH p.19. Thiên Quý formula was wrong (TV-1), **fixed in this branch** | none | mirror pair | NONE | no | cát / ✓ |
| Thiên Quan / Thiên Phúc | aux_stars.py:22-23,45-46 | Both: KL p.29 table, TH pp.23-24 (all 10 stems match code) | none | – | NONE | no | cát / TH-grp cát ✓ |
| Hoa Cái | aux_stars.py:30,60 | Both: KL p.31, TH p.23 | none | always tứ mộ | NONE | no | cát / TH-grp cát ✓ |
| Thiên Giải / Địa Giải | aux_stars.py:56-57 | Both: KL p.26, TH p.24 | none | – | NONE | no | cát / TH-grp cát ✓ |
| Giải Thần | NOT PLACED | Both: sits with Phượng Các (KL p.31, TH p.20) | – | – | NONE | no | cát (unused) |
| Lưu Hà | aux_stars.py:24,63 | KL p.29 vs TH p.26 **disagree (TV-2); code matches neither** | none | – | NONE | no | hung / TH-grp hung ✓ |
| Kiếp Sát | aux_stars.py:31,61 | Both: KL p.31, TH p.26 | none | always tứ sinh | NONE | no | hung / ✓ |
| Phá Toái | aux_stars.py:62 | Both: KL p.31, TH p.26 | none | always Tỵ, Dậu or Sửu | NONE | no | hung / ✓ |
| Thiên Thương / Thiên Sứ | aux_stars.py:49-50 (Nô Bộc / Tật Ách) | Both: KL p.36, TH p.26 (no gender variant in these books) | none (self-test) | fixed palaces | NONE | no | hung / TH-grp hung ✓ |
| Thiên La / Địa Võng | aux_stars.py:51-52 | KL p.36 | none (self-test) | fixed Thìn / Tuất | NONE | no | hung / not in TH list |
| Đẩu Quân | aux_stars.py:58 | Both: KL p.32 ("tiểu Thái tuế"), TH p.25 ("Nguyệt tướng") | none | – | NONE | no | **neutral** / TH-grp hung → mismatch |
| Thiên Tài / Thiên Thọ | aux_stars.py:47-48 | Both: KL p.32, TH p.24 (worked example) | none | KL p.195 (meaning) | NONE | no | cát / TH-grp cát ✓ |
| Quốc Ấn | NOT PLACED | Both: Lộc Tồn + 8 (KL p.29, TH p.22) | – | – | NONE | no | cát (unused) |
| Đường Phù | NOT PLACED | Both: Lộc Tồn + 5 (KL p.29, TH p.22) | – | – | NONE | no | cát (unused) |
| Phong Cáo (and Thai Phụ) | NOT PLACED | Both: Khúc − 2 / Khúc + 2 (KL p.27, TH p.19) | – | – | NONE | no | cát; util.js spells "Thái Phụ" (typo) |

No aux brightness table was invented. Every "NONE" in the brightness column is a real gap in the repo; KL and TH have prose for some of these stars (e.g. Kình tứ mộ).

---


## 2. Tử Vi: interpretation layers (what the engine reasons about)

| Layer | Implemented | Source of the method | Gaps |
|---|---|---|---|
| Bản cung | yes (dossier layer 1) | calculation + brightness tables | aux brightness partial |
| Đồng cung / xung chiếu / hội chiếu / giáp | yes (role-typed facts, dossier layer 2) | TT p.17 (terminology) | rules that read "tam phương" as one bag remain (RL-10) |
| Chủ / khách | yes | TT pp.17-18 | the "cường nhược" weighing is described, not computed (no criterion for "chủ mạnh") |
| Vô chính diệu borrowing | yes, explicit | TT p.18; KL pp.141-142 (Tuần/Triệt in an empty palace) | rules are not re-run with borrowed stars (no source says borrowed = own) |
| Tuần/Triệt | qualifier on every reading of the palace | KL p.141 | effect on chiếu stars: school-dependent, open |
| Named configurations | rule-recognised + name-only + TT p.18 thành phá (Mệnh, Thân) | packs; TT p.18 | 9 qualifiers only; experimental breakers unsourced |
| Disqualifiers / qualifiers | `data/qualifiers.json` (9) | KL pp.140-142, 197; TT p.20 | extend page by page |
| Mệnh–Thân–Cục | facts + KL/TH chart-level rules | KL pp.238-246, TH pp.74-76 | |
| Đại hạn / tiểu hạn | structural activation + KL pp.233-236 Mệnh-gặp-vận | KL, TH pp.115-117 | KL vận rules are not in the review system (RL-12) |
| Lưu niên | lưu Thái Tuế + nine lưu stars | KL pp.41-42 | no verified readings for lưu stars in a palace |
| Synthesis | conditional, no score | this design | no practitioner review |

### Rule coverage (sub-audit, 6c10cf5)

### Verified rules and firing per palace (400-chart sweep, verified cards after merge)

| Palace | Rules (all / verified) | Charts with ≥1 card | Median cards | Mean |
|---|---|---|---|---|
| Mệnh | 676 / 598 | 100% | 22 | 23.3 |
| Tài Bạch | 114 / 96 | 92% | 3 | 3.4 |
| Quan Lộc | 93 / 78 | 87% | 2 | 2.6 |
| Thiên Di | 89 / 78 | 100% | 4 | 4.2 |
| Phu Thê | 77 / 55 | 89% | 2 | 2.7 |
| Phúc Đức | 77 / 64 | 93% | 2 | 2.7 |
| Điền Trạch | 65 / 55 | 83% | 2 | 2.4 |
| Nô Bộc | 55 / 48 | 79% | 1 | 1.6 |
| Phụ Mẫu | 45 / 35 | 88% | 2 | 2.2 |
| Tử Tức | 14 / **9** | 76% (60% from one rule) | 1 | 1.1 |
| Huynh Đệ | 9 / **6** | 56% | 1 | 0.7 |
| Tật Ách | 1 / **1** | 88% (that one rule) | 1 | 0.9 |
| chart-level | 12 / 12 | 100% | 1 | 1.0 |

Mệnh holds 52% of the verified rules and 47% of a chart's cards. Tật Ách, Huynh Đệ and Tử Tức are effectively unread. Their high "charts with ≥1 card" figures come from the generic rules in RL-1, RL-9 and RL-11.

### Stars in verified rule conditions (98 stars appear in charts; 65 are used)

- **Chính tinh:** each is used by 67–148 rules (Tử Vi 148, Thiên Cơ 111, Vũ Khúc 108 … Thất Sát 67).
- **Lục cát and lục sát:** 20–67 each (Hữu Bật 67, Tả Phụ 66, Văn Xương 66, Văn Khúc 63; Địa Không 42, Địa Kiếp 41, Kình 40, Hỏa 36, Linh 30, **Đà La 20**).
- **Lộc Tồn 74, Thiên Mã 42, Khôi and Việt 39 each.** "Phúc Đức" scores 64, but that number is inflated by the palace of the same name.
- **Minor stars:** Hồng Loan 21, Đào Hoa 18, Song Hao 12, Thái Tuế 11, Thiên Không 7, Tấu Thư and Tướng Quân 7. Every other minor star is used by ≤6 rules.
- **Unused (33):** Thiên Hình, Thiên Riêu, Thiên Khốc, Thiên Hư, Hoa Cái, Cô Thần, Quả Tú, Long Trì, Phượng Các, Tam Thai, Bát Tọa, Ân Quang, Thiên Quý, Thiên Quan, Thiên Phúc, Thiên Đức, Nguyệt Đức, Long Đức, Thiên Thọ, Thiên Tài, Thiên Y, Thiên La, Địa Võng, Địa Giải, Thiên Giải, Đẩu Quân, Kiếp Sát, Phá Toái, Lưu Hà, Thiên Thương, Thiên Sứ, Tử, Bệnh.
  - Some are cited on pages already encoded: KL p.218's Tử Tức list includes Long Trì, Phượng Các and Thiên/Nguyệt/Long Đức; "Khốc Hư Tí Ngọ" appears at TH p.85 and TT p.159 #109 (it applies to the reference chart's Mệnh).

### Other structural features (verified rules)

| Feature | Count |
|---|---|
| Uses the merged tam phương (own + tam hợp + xung chiếu, prior audit §7.2) | 138 |
| Uses role-typed positions | 42 |
| Tests brightness | 201 |
| Tests branch | 231 |
| Tests gender | 72 |
| Tứ Hóa leaves (no inter-palace Hóa interaction) | 108 |
| Hóa Kỵ as a trigger | 15 |
| Hóa Kỵ as an exclusion | 0 |
| Giáp (flank) | 26 |
| Thân cư (`is_than`) | 5 |
| Cục / Mệnh–Cục relation | 2 |
| Vô chính diệu | 20 (0 with borrowing) |
| Exceptions | 2 |
| `conflictsWith` | 0 |
| Never fire in 2,000 charts | 55 |

---

### Firing rate (verified rules, 400 charts; the 2,000-chart run agrees within ±4 pt)

| Rate | Rule | Effect | Reading (abridged) |
|---|---|---|---|
| 88.0% | TV_KL_CUNG_TAT_ACH_CUOI_DOI | support | về già sung túc, an nhàn |
| 60.5% | TV_KL_CUNG_TU_TUC_PHU_TINH | support | con cái dễ có, khá giả, xinh đẹp |
| 52.0% | TV_TH_CACH_MENH_NGHICH_LY | limit | giờ sinh nghịch lý: độ số kém bớt |
| 48.0% | TV_TH_CACH_MENH_THUAN_LY | support | giờ sinh thuận lý (complement of the row above: 100% of charts get one) |
| 46.8% | TV_KL_CASE_MENH_KHONG_DAC_CHINH | limit | ra đời gặp trở ngại lúc ban đầu |
| 46.2% | TV_KL_CUNG_PHU_MAU_SAO_TOT | support | cha mẹ khá giả, con cái hòa thuận |
| 46.2% | TV_KL_CUNG_PHU_MAU_HUNG | support (sic) | cha mẹ vất vả, chẳng giàu |
| 41.2% | TV_TH_CACH_MENH_MUA_SINH | support | thuận mùa sinh |
| 35.0% | TV_KL_CUNG_PHU_THE_DEP_DOI | support | vợ chồng hòa thuận, đẹp đôi, bền lâu |
| 34.8% | TV_KL_CASE_MENH_TU_CHINH | support | tinh thần trách nhiệm cao (year branch only) |
| 34.0% | TV_TH_VERSE_MENH_TRIET_TUAN / TV_KL_PHU2_TUAN_TRIET / TV_KL_AUX_TUAN_TRIET | support (sic) | thời trẻ vất vả / vui ít buồn nhiều (3 rules, 1 trigger) |
| 34.0% | TV_TH_P2_PHUC_DUC_TT | limit | phúc bị kìm hãm |
| 34.0% | TV_KL_CASE_MENH_TU_MO | limit | phải cố gắng giành chỗ đứng |
| 32.2% | TV_TT_PHU_MENH_PHU_TUONG_DONG_LUONG | support | tính tình hiếu thuận |
| 31.5% | TV_TH_P2_HUYNH_DE_TT | limit | anh em ít, mỗi người một ngả |
| 29.2% | TV_KL_PHU2_BA_KHONG | support (sic) | khó giàu sang |
| 28.5% | TV_KL_CUNG_PHU_THE_TT | support | hôn nhân trong hoàn cảnh đặc biệt |
| 27.8 / 27.3 / 27.0% | TV_KL_MENH_{TU_PHU_VU_TUONG, SAT_PHA_LIEM_THAM, CO_NGUYET_DONG_LUONG} | neutral | star-group classification |
| 27.0% | TV_KL_CT_CNDL | support | hàng trí thức, công bộc |
| 27.0% | TV_KL_CASE_MENH_DAC_CHINH_DUONG | support | đúng chỗ của mình |
| 26.5% | TV_TT_PHU_MENH_SAT_KIEP_THAM | limit | tính tình thất thường |
| 26.2% | TV_KL_CASE_MENH_DAC_CHINH_AM | support | mềm dẻo, khôn khéo |
| 25.8% | TV_TH_AUX_MENH_DH_CHIEU | support | đẹp hơn khi Đào Hồng xung chiếu |
| 25.8% | TV_KL_CT_NHAT_NGUYET_CHIEU | support | thông minh sáng suốt, dễ thành công |

- 26 verified rules fire on more than 25% of charts, and about 95 on more than 10%.
- Draft rules with high rates are hidden by the UI: `KL_CUNG_DIEN_TRACH_NGHEO` 62%, `KL_CUNG_TAI_BACH_KHONG_KIEP` 57%, `KL_CUNG_THIEN_DI_QUY_NHAN` 49%, `TV_STRUCT_SAT_PHA_THAM_001` 100%.
- 1,046 of 1,139 verified rules fired at least once in 400 charts.

---


## 3. Bát Tự

| Item | Source | Status |
|---|---|---|
| Pillars, Lập Xuân / jie boundaries, luck start | astronomy (sxtwl/PyEphem), checked at 15:26 vs 15:27 on 2024-02-04 | verified |
| Tàng can, Thập Thần, 12 trường sinh | ZZ pp.7-17, TVH p.342 | verified (golden) |
| Can hợp, 干冲克 (10 pairs, xung/khắc) | ZZ p.20 | verified (**10 pairs from this branch**) |
| Lục hợp, tam hợp, tam hội, lục xung, hại, phá | ZZ pp.19-20 | verified |
| Hình: 三刑 pairwise, 子卯, 自刑 | ZZ pp.19-20 | verified (**pairwise from this branch**) |
| Bán hợp (with the middle branch) | ZZ p.20 | not reported (BZ-14) |
| Hợp vs hóa | TVH pp.336-338 (only adjacent ngũ hợp) | potential only; distance shown |
| Year / luck × natal, including hình | ZZ pp.19-20 | verified (**this branch**) |
| Strength, three tests | ZZ p.27 | implemented with stated operationalisation |
| Strength, 40% rule | TVH pp.331-355 | implemented strictly (no band) |
| Cách cục | `bazi_deep/geju.py` (子平真诠 from memory) | draft; not shown as a conclusion |
| Dụng / Hỷ / Kỵ | TVH điều hậu pp.389-396 (table origin unknown, p.388); phù ức / cách cục draft | not concluded; the điều hậu list is shown as one school's |
| Thần sát, không vong, thai / mệnh / thân cung | ZZ pp.21-22 and tables | computed; no verified interpretation beyond ZZ tables |
| Direct judgements (ZZ pp.51-96) | ZZ | loaded but off (BZ-12) |
| Lưu nguyệt | ZZ p.20 (ngũ hổ độn) | pillars only |

## 4. Not covered on purpose

- Death, illness, prison, accident and adultery lines in the books.
- Child counts and gender.
- Calamity thần sát (关煞, 天罗地网…).
- "Năm xung năm tuổi" lore: TT pp.106-107 itself calls it unfounded.
