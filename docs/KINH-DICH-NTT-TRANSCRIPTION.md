# Kinh Dịch, Ngô Tất Tố: transcription of the 64 quẻ

Book id `KD`: `KINH DỊCH TRỌN BỘ.PDF` (666 PDF pages). The PDF is an image scan; its only text is a download watermark.

| What | Where |
|---|---|
| Data | `engine/data/kinh_dich/ntt/<King Wen number>.json` (64 files) |
| Page text | `engine/data/kinh_dich/ntt/pages.txt` (601 printed pages, `=== p.N` per page) |
| Hán differences from 周易, and checked Vietnamese misprints | `engine/data/kinh_dich/ntt/misprints.json` |
| Tools | `tools/kinh_dich_ntt.py` (assemble, checks, finalize); `tools/book_text.py` / `tools/show_page.py` (book id `KD`) |
| Tests | `engine/tests/test_kinh_dich_ntt.py`; fixture `engine/tests/fixtures/zhouyi_han_segments.json` (zh.wikisource 周易, revids inside) |

## The scan

**Page offset is not constant.** I read the running head of all 666 pages. Blank pages were dropped from the scan, so the offset steps up:

| PDF pages | printed page |
|---|---|
| 1–57 | PDF + 2 |
| 58 | PDF + 3 |
| 59–361 | PDF + 4 |
| 362–660 | PDF + 5 |
| 661–666 | PDF + 6 |

- Printed pages 60, 62, 366 and 666 are not in the scan. All four are blank pages around the title pages and the end of the text.
- `book_text.pdf_page("KD", printed)` does the mapping, and `show_page.py KD <page> --image DIR` renders a page.

**What the book contains:**
- Thượng kinh: title page p.61, Kiền from p.63. Ly ends on p.364.
- Hạ kinh: title page p.365, Hàm from p.367. Vị Tế ends on p.665.
- Mục lục: pp.667–669. The quẻ start pages below are taken from it.
- **The end matter (Hệ từ, Thuyết quái, Tự quái, Tạp quái) is not in this book.** The Mục lục stops at Vị Tế, and the text ends on p.665.

**Page map:**

| # | quẻ | 卦 | printed pages | segments | verified |
|---|---|---|---|---|---|
| 1 | Kiền | 乾 | 63–100 | 54 | 49 |
| 2 | Khôn | 坤 | 101–119 | 29 | 29 |
| 3 | Truân | 屯 | 120–129 | 16 | 15 |
| 4 | Mông | 蒙 | 130–140 | 19 | 19 |
| 5 | Nhu | 需 | 141–149 | 17 | 17 |
| 6 | Tụng | 訟 | 150–159 | 17 | 17 |
| 7 | Sư | 師 | 160–169 | 17 | 17 |
| 8 | Ty | 比 | 170–179 | 16 | 15 |
| 9 | Tiểu Súc | 小畜 | 180–188 | 18 | 18 |
| 10 | Lý | 履 | 189–195 | 16 | 15 |
| 11 | Thái | 泰 | 196–205 | 16 | 14 |
| 12 | Bĩ | 否 | 206–212 | 16 | 14 |
| 13 | Đồng Nhân | 同人 | 213–221 | 20 | 20 |
| 14 | Đại Hữu | 大有 | 222–229 | 16 | 15 |
| 15 | Khiêm | 謙 | 230–237 | 16 | 16 |
| 16 | Dự | 豫 | 238–245 | 19 | 19 |
| 17 | Tùy | 隨 | 246–254 | 18 | 17 |
| 18 | Cổ | 蠱 | 255–263 | 19 | 18 |
| 19 | Lâm | 臨 | 264–271 | 16 | 15 |
| 20 | Quán | 觀 | 272–279 | 18 | 18 |
| 21 | Phệ hạp | 噬嗑 | 280–288 | 19 | 19 |
| 22 | Bí | 賁 | 289–297 | 20 | 18 |
| 23 | Bác | 剝 | 298–304 | 18 | 15 |
| 24 | Phục | 復 | 305–313 | 20 | 19 |
| 25 | Vô Vọng | 无妄 | 314–322 | 18 | 17 |
| 26 | Đại Súc | 大畜 | 323–331 | 19 | 18 |
| 27 | Di | 頤 | 332–340 | 17 | 16 |
| 28 | Đại Quá | 大過 | 341–348 | 19 | 19 |
| 29 | Tập Khảm | 坎 | 349–357 | 17 | 16 |
| 30 | Ly | 離 | 358–364 | 18 | 18 |
| 31 | Hàm | 咸 | 367–376 | 17 | 17 |
| 32 | Hằng | 恒 | 377–385 | 21 | 21 |
| 33 | Độn | 遯 | 386–393 | 19 | 18 |
| 34 | Đại Tráng | 大壯 | 394–401 | 17 | 17 |
| 35 | Tấn | 晉 | 402–409 | 16 | 16 |
| 36 | Minh Di | 明夷 | 410–419 | 18 | 18 |
| 37 | Gia Nhân | 家人 | 420–427 | 16 | 16 |
| 38 | Khuê | 睽 | 428–437 | 18 | 18 |
| 39 | Kiển | 蹇 | 438–446 | 19 | 18 |
| 40 | Giải | 解 | 447–456 | 20 | 19 |
| 41 | Tổn | 損 | 457–467 | 20 | 20 |
| 42 | Ích | 益 | 468–478 | 21 | 21 |
| 43 | Quải | 夬 | 479–489 | 20 | 19 |
| 44 | Cấu | 姤 | 490–499 | 20 | 20 |
| 45 | Tụy | 萃 | 500–510 | 22 | 20 |
| 46 | Thăng | 升 | 511–517 | 17 | 17 |
| 47 | Khốn | 困 | 518–528 | 19 | 19 |
| 48 | Tỉnh | 井 | 529–537 | 17 | 16 |
| 49 | Cách | 革 | 538–546 | 19 | 19 |
| 50 | Đỉnh | 鼎 | 547–554 | 17 | 16 |
| 51 | Chấn | 震 | 555–562 | 18 | 16 |
| 52 | Cấn | 艮 | 563–570 | 19 | 19 |
| 53 | Tiệm | 漸 | 571–578 | 20 | 20 |
| 54 | Quy Muội | 歸妹 | 579–587 | 17 | 16 |
| 55 | Phong | 豐 | 588–597 | 19 | 18 |
| 56 | Lữ | 旅 | 598–605 | 17 | 13 |
| 57 | Tốn | 巽 | 606–614 | 17 | 16 |
| 58 | Đoái | 兌 | 614–620 | 16 | 16 |
| 59 | Hoán | 渙 | 621–629 | 18 | 15 |
| 60 | Tiết | 節 | 629–634 | 16 | 15 |
| 61 | Trung Phu | 中孚 | 635–641 | 16 | 14 |
| 62 | Tiểu Quá | 小過 | 642–650 | 21 | 21 |
| 63 | Ký Tế | 既濟 | 651–657 | 18 | 17 |
| 64 | Vị Tế | 未濟 | 658–665 | 16 | 16 |

## The data

Each quẻ file has this shape:

```
{number, name_vi, name_han, source: "KD", translator, heading, pages: [first, last],
 segments: [{kind, hao?, dung?, han, am, nghia, trinh_di, chu_hy, other_commentary?, printed_labels?, footnotes?,
             order, page, page_end?, absent?, status, status_reason?}]}
```

- **`kind`**: `intro` (the GIẢI NGHĨA before the first LỜI KINH; no Hán), `thoan`, `thoan_truyen`, `dai_tuong`, `hao` (with `hao` 1–6), `tieu_tuong` (with `hao`, or `dung: true` for the tượng of 用九/用六), `dung`, `van_ngon`.
- **One LỜI KINH block is one segment.** A Thoán truyện, a tiểu tượng or a lời quẻ printed as several blocks gives several segments of the same kind, for example Phục's lời quẻ and Phong's tiểu tượng 4.
- **Verbatim text.** Misprints, the book's spelling and tone placement, and its punctuation are kept. Paragraphs are separated by `\n`.
  - Italics are not kept.
  - Drawings are `[hình]`.
  - Unreadable characters are `[?]`. One `[?]` on p.455 stands for a whole printed line lost in the scan.
- **Labels.** A label printed differently from the standard one is kept in `printed_labels`. The book often prints "Bản nghĩa của Trình Di" for Trình Di's Truyện, and sometimes "Dịch âm" over the Dịch nghĩa.
- **Unlabelled paragraphs** are `other_commentary` with an empty label. Lời bàn của Tiên Nho and other named comments are also in `other_commentary`, with their printed label.
- **Order.** `order` gives the order of the layers as printed.
- **Footnotes.** Footnote marks are `[^<page>.<n>]` in the text, and the matching note is in `footnotes`. A note that runs over a page is joined.
- **Absent layers.** `absent` lists layers the book really omits. Each was checked on the image:

| quẻ | where | missing |
|---|---|---|
| 16 | tiểu tượng 4, p.244 | no GIẢI NGHĨA |
| 28 | tiểu tượng 5, p.347 | Trình Di's note on the tượng is printed, but there is no LỜI KINH line before it |
| 32 | Thoán truyện block 剛上而柔下…, p.378 | no Dịch nghĩa |

## How it was made

1. **Transcribers.** Subagents transcribed from page images rendered at zoom 2.0, with high-zoom strips and boxes for diacritics and Hán. Each worked on 5–11 pages, one file per printed page. The brief was "copy, never correct; never guess (`[?]`); no other copy of the text".
2. **Assembly.** The page files are joined into segments by `tools/kinh_dich_ntt.py`.
3. **Differences seen on the image.** Every difference found by the checks below was looked at on the page image by a separate agent. Its verdict was one of: the print shows ours, shows the other text, shows neither, or is unclear.
4. **Corrections.** Our transcription errors were then corrected in the page files: 36 corrections in all, every one a single character or a glyph.
5. **Spot checks.** I checked a sample of the image verdicts myself (pp.68, 81, 143, 149, 156, 244, 347, 373, 378). All agreed with the adjudicators.

## Check: 9 Wikisource quẻ, blind (CER gate)

vi.wikisource has 9 quẻ of this translation: Kiền, Khôn, Truân, Mông, Nhu, Tụng, Sư, Hàm, Hằng. The transcribers of those pages had not seen it.

**Raw difference from Wikisource.** This is before looking at the print. Text is compared with tone placement normalised (hoà = hòa), and footnote marks and drawings are left out.

| layer | chars | edits | raw CER |
|---|---|---|---|
| all text in book order | 192,584 | 1,571 | 0.82% |
| Dịch âm | 14,263 | 128 | 0.90% |
| Dịch nghĩa | 18,323 | 248 | 1.35% |
| Trình Di | 77,900 | 2,631 | 3.38%* |
| Chu Hy | 42,588 | 894 | 2.10%* |

\*The per-layer figures for Trình Di and Chu Hy also count paragraphs that the two texts file under different labels.

**After looking at the print.** All 818 differences were checked on the image:

| outcome | count |
|---|---|
| the print agrees with our transcription (Wikisource is a different or corrected text) | 794 |
| our transcription errors (`ờ`/`ợ`, `ằ`/`ầ`, `ễ`/`ẽ`, `ồ`/`ổ`, `ì`/`i`, `ớ`/`ó` …; 12 edited characters), all corrected | 11 |
| our `[?]` marks (some readable at high zoom and filled in, others left) | 12 |
| unclear | 1 |

- **CER of the procedure: 12 / 192,584 = 0.006%.** The gate is ≤ 0.5%, so it passed.
- The procedure was not changed. The other 55 quẻ were done the same way.
- The 794 differences are this printing's own readings: its misprints and its wording. Examples: "kính thật" where Wikisource has "kính thận", "Lời tượng… mây", a whole clause of 不見是而無悶 missing in the Dịch nghĩa on p.81, and "Bản nghĩa của Trình Di" over a Chu-Hy-like note on p.156.

## Check (a): Hán against zh.wikisource 周易, all 64 quẻ

The Hán of each segment kind is joined and compared with the fixture.
- Punctuation is ignored.
- Glyph variants of one character (無/无, 說/説, 黃/黄, 恆/恒, 內/内 …) are normalised; the list is `VARIANTS` in the tool.
- Different characters are not normalised.
- The 彖曰/象曰/文言曰 labels and the 初九-type hào labels are dropped. The lời quẻ name is handled the same way in both texts.

**Results:**
- 293 segment groups differ from 周易. After corrections they hold 383 differences seen on the print, plus 4 open (below).
- First round: 403 character-level differences, each looked up on the image. Verdicts: 374 print = ours, 18 ours wrong, 9 neither, 2 unclear.
  - The 18 + 9 were `[?]` marks that could be read at high zoom (豶, 遯, 牖, 禴, 繻, 禦, 遲, 簣, 瀳 …) or wrong glyph forms (决→決, 洌→冽, 愼→慎). All were corrected and re-checked.
- `misprints.json` records each group: the book's text, the 周易 text, and every difference with what the print shows.
- **The book has many Hán misprints.** These are copied as printed, not fixed:

| book prints | 周易 has | where |
|---|---|---|
| 象曰 | 彖曰 (Thoán truyện) | throughout |
| 長子師師 | 長子帥師 | Sư |
| 在失中吉 | 在師中吉 | Sư |
| 至寇至 | 致寇至 | Nhu |
| 君子飲食宴樂 | (without 以) | Nhu |
| 出下出泉 | 山下出泉 | Mông |
| 大月 | 大有 | Đại Hữu |
| 六無之吉 | 六五之吉 | Phong |
| 遯恒 | 遯亨 | Độn |
| 遇于之吉 | 遇雨之吉 | Khuê |

**Four differences remain open**, and their segments are `unverified`:

| page | what | reading |
|---|---|---|
| 96 | Kiền Văn ngôn | a smudged punctuation mark before 曰 |
| 198 | Thái hào 1 | the character after 以其 is a solid blot (周易 has 彙) |
| 208 | Bĩ hào 1 | same blot (彙) |
| 537 | Tỉnh hào 6 | a glyph ⿰儿危, not in Unicode as printed (周易 has 勿) |

## Check (b): structure

The test checks, for every quẻ:
- every hào 1–6 and every tiểu tượng 1–6 is present;
- there is a lời quẻ, a Thoán truyện and a Đại tượng;
- dụng and Văn ngôn appear only in Kiền and Khôn;
- pages run in order and lie inside the quẻ's Mục lục range;
- no layer is empty, except those in `absent`.

All 64 quẻ pass.

## Check (c): independent second transcription of a random 10%

- **Sample.** 61 printed pages were drawn with `random.seed(20261025)` from the 601 text pages; they are listed in `.kd_work/sample_pass2.txt`.
- **Blind.** They were transcribed again by different agents that never saw the first transcription.
- **Raw result.** The two transcriptions differ in 53 places over 103,497 characters (tags kept, notes dropped, spaces inside Hán lines ignored).

Every one of the 53 was looked up on the image: the first transcription was right in 30, the second in 21, neither in 2 (the print
had a third reading). So on these 61 pages the first transcription had **23 errors in 103,497 characters (0.022%)**, all corrected:
- **10 Vietnamese letters.** One pattern matters: in 4 of them the first transcriber silently *corrected a misprint*. The print has "nền", "vĩ", "ngốn", "Ngô"; the transcriber typed "nên", "vì", "ngón", "Ngộ". The other 6 are tone or letter misreadings ("thể", "tế" ×2, "Đương", "cắm", "nới").
- **7 Hán.**
  - 弧 typed for the printed 孤 (×2). The print is a misprint, and the transcriber normalised it.
  - 象 typed for the printed 彖 (×2).
  - 說 typed for 説 (×3). This is a glyph form only, so the 周易 check cannot see it.
- **3 `[?]` marks** that the image check could read: 胾, a comma, and "ê".
- **1 punctuation mark** (":" printed, "." typed), **1 block boundary** (p.539), and the γ-like broken glyph on p.286.
The second transcription had more errors than the first (30 of the 53).

A separate check by readers of the text (the Kinh Dịch module session) flagged 152 places in the Vietnamese layers of the 55 quẻ that
look wrong ("trí giống nhau", "Kiêu sự nhún", "lợi vở sự"…). A random 30 were looked up on the image: **all 30 are printed so** (book
misprints, kept), none was a transcription error. They are listed under `vietnamese` in `misprints.json`; the other 122 were not looked up.

**A note on the second pass.** Three second-pass agents stopped partway because they doubted the rights to the 2012 reprint. They were told the owner's decision and resumed:
- Ngô Tất Tố died in 1954.
- vi.wikisource hosts this translation as public domain.
- The footnotes are the translator's own; they appear in the Wikisource text too.

## Status

A segment is `verified` when all of these hold:
- (a) its Hán equals 周易, or each difference was seen on the print;
- (b) its quẻ passes the structure check;
- it has no `[?]`;
- each of its pages that is in the second-pass sample has its differences settled on the image.

Otherwise it is `unverified`, and `status_reason` says why.

Now: **1149 of 1199 segments verified, 50 unverified** — 50 because they keep a `[?]` (4 of them also hold one of the open Hán
places below). Every page of the 61-page sample agrees after settlement; all 64 quẻ pass (b).

## Not verified, and limits

- **`[?]` marks.** 50 segments keep a `[?]`: blots, broken letters, or a tone mark that cannot be read. One whole printed line on p.455 is lost in the scan.
- **The 4 open Hán places** listed in check (a).
- **Vietnamese layers of the 55 non-Wikisource quẻ.**
  - Only the 10% sample was transcribed twice; elsewhere they rest on one transcription.
  - Measured error rates: 0.006% against Wikisource (9 quẻ, every difference seen on the print) and 0.022% against the second transcription (61 random pages).
  - The main remaining risk is a misprint that a transcriber silently normalised (see check c). Such a place reads correctly but differs from the print.
  - A `verified` status on those segments means checks (a)–(b) passed. It does not mean a second reading of every Vietnamese word.
- **Formatting.** Italic and bold are not kept. Curly and straight quotes are written as the transcribers saw them.
- **Variant Hán glyphs.** Some were written in their standard form when the scan could not show the difference (黄/黃, 説/說). Clearly different glyphs were copied as printed: 劳, 晋, 戸, 瀳, 簣.
