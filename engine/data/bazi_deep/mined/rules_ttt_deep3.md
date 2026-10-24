# Trích Thiên Tủy (bản dịch Việt, Nhậm Thiết Tiều bình giảng): DEEP-3 mining, 2026-10-24

Pages read from the PDF text layer (committed as ttt_pNNN.txt): Phần I pp.59-78 (Bát Cách, Thể Dụng, Tinh Thần, Nguyệt Lệnh, Sinh Thời,
Suy Vượng, Trung Hòa), pp.101-112 (Thanh Khí, Trọc Khí, Chân Thần, Giả Thần, Cương Nhu, Thuận Nghịch); Phần II pp.130-132 (Con Cái, already
committed), pp.143-148 (Hà Tri, already committed), pp.161-170 (Tài Đức, Phấn Ức, Ân Oán, Nhàn Thần), pp.183-201 (Thuận/Phản/Chiến/Hợp cục,
Quân/Thần/Mẫu/Tử tượng), pp.229-233 (Tuế Vận).

Columns: page | quote (substring of ttt_pNNN.txt, whitespace-insensitive) | chart condition | judgement | flag → where it went.
Flags: '-' usable; SENSITIVE (death, lifespan, illness, injury, child number / sex, no wife / no child, divorce, prison, sexual vice) with the
reason; VAGUE (needs a judgement call the facts cannot make); METHOD (a principle, no chart verdict: goes to hyky.json / thanh_pha.json, not to a
rule); LUCK (about a luck pillar or a year against its luck pillar: needs facts the kin layer does not compute); DUP (same condition and verdict as
a rule already packed). "→ R:<id>" = packed as a rule, "→ H:<key>" = in hyky.json, "→ T:<key>" = in thanh_pha.json.

## Bát Cách, Thể Dụng, Nguyệt Lệnh, Suy Vượng (pp.59-76)

59 | Trước xem có đắc lệnh tháng, sau xem thiên can có thấu lộ, kế tiếp xem sinh vượng để định chân giả, cuối cùng mới đến thủ dụng, phân thanh trọc | order of reading a chart | - | METHOD → H:order
59 | Chánh cách tức gồm đủ ngũ hành sinh khắc thường tình như quan sanh ấn, sát sanh ấn, tài sanh sát, thực chế sát, thực sanh tài, thương quan bội ấn, thương quan sanh tài | list of chính cách | - | METHOD → H:chanh_bien
59 | biến cách nhất định phải tòng khí thế của ngũ hành | list of biến cách (tòng) | - | METHOD → H:chanh_bien
60 | Nhật chủ vượng cần nên chế, suy cần nên tương trợ, ấn vượng tiết quan cần có tài, ấn suy phùng tài nên có kiếp, dụng pháp này không thay đổi | the four standing rules of dụng | dụng by strength | METHOD → H:dung_rules.TTT60
61 | Lại cho rằng tạp khí tài quan cần nên xung thật là hàm hồ | tạp khí need not be clashed | - | METHOD → T:ttt_no_clash_kho
61 | phá cách tổn hại dụng thần, thì có bệnh vậy, ưu sầu nhiều vui mừng ít | cách broken, dụng thần hurt | worries outweigh joys | VAGUE (cách broken = TVH thành bại / geju; not a kin fact) → T:ttt_pha_cach
61 | Nhưng nếu hành vận thích hợp, khử mất kỵ thần, sanh trợ dụng thần giống như người bệnh lâu ngày được thầy thuốc giỏi cứu chữa, không phú cũng quý | luck removes kỵ thần | rescued | LUCK → T:ttt_pha_cach
61 | Không theo cách cục vẫn có thể thủ dụng, không có dụng thần vẫn có thể tìm ở vận trình | no cách / no dụng | dụng from luck | METHOD → H:no_dung
61 | nếu chánh cách dụng chân mà gặp vận hành bội phản, trọn đời có chí mà vất vả | true cách, opposing luck | ambitious but toiling | LUCK → H:luck_principles
62 | Cho nên luận mộ khố gặp xung tất phát thật sai lầm vậy | clash opening a tomb | not a rule for prosperity | METHOD → T:ttt_no_clash_kho
63 | Vượng tất nên ức, nhược tất nên phù | standing rule | - | METHOD → H:dung_rules.TTT63_core
63 | Vượng nên ức nhưng không thể ức, phản lại nên phù; nhược nên phù nhưng không thể phù, phản lại nên ức | extreme charts reverse the rule | - | METHOD → H:dung_rules.TTT63_reverse
63 | Cực cường vượng bị ức mà có hại, tất nên tòng cường mà phù cường; cực nhược được phù, phù mà uổng công vô dụng, tất nên tòng nhược mà ức nhược | extreme → tòng | - | METHOD → H:dung_rules.TTT63_reverse
63 | Nếu như nhật chủ vượng, đề cương hoặc quan hoặc tài hoặc thực thương, đều có thể làm dụng thần; nhật chủ suy, đặc biệt tìm tứ trụ can chi có trợ nhật chủ làm dụng thần | dụng by month command | - | METHOD → H:dung_table.T01
63 | Nhật chủ làm thể, nhật chủ vượng, ấn thụ nhiều, cần phải lấy tài tinh làm dụng thần | DM strong, Ấn many | dụng = Tài | - → R:BT_TTTK_DT01, H:dung_table.T02
63 | nhật chủ vượng, quan sát khinh, cũng lấy tài tinh làm dụng thần | DM strong, Quan Sát light | dụng = Tài | - → R:BT_TTTK_DT02
63 | Nhật chủ vượng, tỉ kiếp nhiều, gánh được tài tinh, lấy thực thương làm dụng thần | DM strong, Tỉ Kiếp many, Tài present | dụng = Thực Thương | - → R:BT_TTTK_DT03
63 | nhật chủ vượng, tỉ kiếp nhiều, mà tài tinh khinh, cũng lấy thực thương làm dụng thần | DM strong, Tỉ Kiếp many, Tài light | dụng = Thực Thương | - → R:BT_TTTK_DT04
63 | Nhật chủ vượng, quan tinh khinh, ấn thụ trọng điệp, lấy tài tinh làm dụng thần | DM strong, Quan light, Ấn heavy | dụng = Tài | - → R:BT_TTTK_DT05
63 | Nhật chủ nhược, thực thương nhiều, lấy ấn thụ làm dụng thần | DM weak, Thực Thương many | dụng = Ấn | - → R:BT_TTTK_DT06
63 | nhật chủ nhược, tài tinh vượng, tất lấy tỉ kiếp làm dụng thần | DM weak, Tài strong | dụng = Tỉ Kiếp | - → R:BT_TTTK_DT07
63 | Nhật chủ cùng quan sát cân bằng, tất lấy thực thương làm dụng thần | DM and Quan Sát balanced | dụng = Thực Thương | VAGUE ('cân bằng' has no measure) → H:dung_table.T09
63 | nhật chủ cùng tài tinh cân bằng, tất lấy ấn thụ làm dụng thần | DM and Tài balanced | dụng = Ấn | VAGUE → H:dung_table.T10
63 | Nếu như tứ trụ can chi tài sát thái vượng, nhật chủ vượng biến thành nhược, cần tìm trợ nhật chủ chế hóa tài sát làm dụng thần | Tài Sát too strong | dụng helps DM | METHOD → H:dung_table.T11
63 | hóa thần thật, tức lấy hóa thần làm thể. Hóa thần có lực, tất lấy hóa thần làm dụng; hóa thần không đủ lực, tất lấy sanh trợ hóa thần làm dụng thần | hóa cách | - | METHOD → H:dung_table.T12
63 | lấy sanh trợ khí tượng làm dụng thần, hoặc lấy thực thương làm dụng thần, hoặc lấy tài tinh làm dụng thần, chỉ không nên dụng quan sát | khúc trực / one-element cách | never Quan Sát | METHOD → H:dung_table.T13
63 | hoặc bị nhàn thần hợp mất, hoặc bị xung làm tổn thương, hoặc bị kỵ thần cướp giật chiếm giữ, hoặc khách thần ngăn trở | dụng thần disabled | - | METHOD → H:dung_disabled
64 | trừ dụng thần, hỉ thần, kỵ thần ra thì còn lại đều là nhàn thần khách thần vậy | role list | - | METHOD → H:roles.nhan
64 | cho nên thiên can dễ xem, địa chi khó suy ra | dụng in a stem vs a branch | - | METHOD → H:dung_position
65 | Có thừa cần nên bớt đi, không đủ cần nên bồi thêm | tinh thần tổn ích | - | METHOD → H:ton_ich
65 | đại khái có thừa quá mức, nếu tổn phản lại kích động phẫn nộ, tất nên thuận theo mà tiết đi | excess: drain, do not control | - | METHOD → H:ton_ich
67 | khí tượng đắc lệnh thì cát lợi, hỉ thần đắc lệnh thì cát lợi | hỉ thần holds the month | auspicious | - → R:BT_TTTK_HK05
67 | Khí tượng, cách cục, dụng thần đều lệ thuộc vào đề cương tháng | month is the key | - | METHOD → H:order
67 | Sau lập xuân 7 ngày mậu thổ nắm lệnh | tư lệnh Dần (already in tu_lenh.json) | - | DUP
67 | thiên can không thấu xuất hỏa thổ mà thấu thủy mộc, thì môn (can) suy địa vượng | Dần month, môn/địa | - | VAGUE (needs the day count into the month for tư lệnh; month-day not a kin fact) → H:mon_dia
70 | nhật chủ không luận hưu tù nguyệt lệnh, chỉ cần tứ trụ hữu căn, liền có thể đảm nhận tài quan thực thương thất sát | rooted DM bears Tài Quan | - | METHOD → H:strength_notes
70 | nhiều can không bằng thông căn nơi địa chi | root > stems | - | METHOD → H:strength_notes
70 | mà không biết hình xung tất thương tổn căn khí | clashing a tomb hurts the root | - | METHOD → T:ttt_no_clash_kho
72 | Nếu ấn thụ trong mệnh cục trọng tứ thành cách tòng cường, thì nhất định chỉ được gặp vận ấn kiếp, không nên gặp vận thực thương | tòng cường luck (translator's note) | - | DUP (tong_roles.json) 
76 | “vượng cực không thể tổn, suy cực không thể sinh” | extreme charts | - | METHOD → H:dung_rules.TTT63_reverse
77 | Tức đắc trung hòa chánh khí, danh lợi làm sao mà không toại được | balanced chart | - | VAGUE ('trung hòa' has no measure) → H:trung_hoa
77 | tài khinh kiếp trọng không có vợ | Tài light, Kiếp heavy | no wife | SENSITIVE (marriage absence) — kept out
77 | chế cường sát nhược không có con | control strong, Sát weak | no child | SENSITIVE (no child) — kept out
77 | quan suy thương quan vượng thiếu danh vị | Quan weak, Thương Quan strong | short of rank | - → R:BT_TTTK_TH01
77 | sát cường chế nhược tiền bạc thiếu thốn | Sát strong, its control (Thực Thương) weak | short of money | - → R:BT_TTTK_TH02
77 | có bệnh rõ ràng mà dễ dàng chọn, không có bệnh mà khó đoán | bệnh / dược | - | METHOD → H:benh_duoc

## Thanh / Trọc, Chân / Giả thần, Thuận Nghịch (pp.101-112)

101 | Như chánh quan cách, thân nhược có ấn, kỵ tài, tài tinh không hiện, có thể thấy ngay là thanh hĩ | CQ cách, DM weak, Ấn, Tài not transparent | clear | - → T:thanh.TTT101a
101 | tất tài sanh quan, quan sanh ấn, ấn sanh nhật chủ | chain Tài→Quan→Ấn→DM | - | - → T:thanh.TTT101a
101 | Như chánh quan cách, thân vượng mừng có tài, mà kỵ ấn thụ, tiếp theo kỵ thương quan | CQ cách, DM strong | - | METHOD → T:thanh.TTT101b
101 | Như thương quan cùng tài tinh cách xa, ngược lại thương quan kế cận quan tinh, tài không đủ lực sanh quan, đến hành vận gặp thương quan, không bần cũng tiện hĩ | Thương next to Quan, Tài far | - | LUCK (verdict tied to a luck) → T:thanh.TTT101b
101 | hỉ thần nên đắc địa phùng sanh, cùng nhật chủ kề cận là cát lợi; kỵ thần nên thất thế lâm tuyệt địa, cùng nhật chủ xa cách thì đẹp vậy | position of hỉ / kỵ | - | - → R:BT_TTTK_HK06, R:BT_TTTK_HK07, H:position
103 | Trong trụ chủ yếu tìm không ra thanh khí, hành vận lại không thể loại trừ trọc khí, tất là bần tiện | trọc + bad luck | - | LUCK → T:troc
103 | Hoặc quan suy hỉ ấn, tài tinh khắc ấn, cách này tài là trọc vậy | Quan weak, Ấn hỉ, Tài next to Ấn | Tài is the turbid one | - → R:BT_TTTK_TR01
103 | Hoặc quan suy hỉ tài, tỉ kiếp tranh tài, cách này kiếp là trọc vậy | Quan weak, Tài hỉ, Tỉ Kiếp next to Tài | Kiếp is the turbid one | - → R:BT_TTTK_TR02
103 | Hoặc tài vượng hỉ kiếp, quan tinh chế kiếp, cách này quan là trọc vậy | Tài strong, Tỉ Kiếp hỉ, Quan next to Tỉ Kiếp | Quan is the turbid one | - → R:BT_TTTK_TR03
103 | Hoặc thân cường sát thiển, thực thương chế sát, cách này thực thương là trọc vậy | DM strong, Sát light, Thực Thương next to Sát | Thực Thương is the turbid one | - → R:BT_TTTK_TR04
103 | tuy thành bại không đều, có nhiều hiểm trở, nhưng ngộ đắc hành vận, khử đi trọc khí, cũng có cơ hội khởi phát | what trọc means | uneven success | - (the verdict of TR01-04) → T:troc
103 | Phàm nhật chủ khô giả, không bần cũng yểu | DM 'khô' | poor or short-lived | SENSITIVE (lifespan) — kept out
103 | dụng thần khô giả, không bần cũng cô độc | dụng 'khô' | poor or lonely | VAGUE ('khô' = rootless and rotten: no fact) — kept out
105 | Nói nhật chủ có dụng thần, nắm lệnh tại đề cương, lại thấu xuất thiên can gọi là tụ đắc chân thần, cuộc đời phú quý hĩ | dụng holds the month and is transparent | prosperous life | - → R:BT_TTTK_CT01
105 | Nhưng nếu kề sát chân thần, hoặc tương khắc tương xung chân thần, hoặc hợp chân thần, ám hóa kỵ thần, chung thân lục đục | giả thần next to and controlling chân thần | lifelong friction | - → R:BT_TTTK_CT02
107 | Hết thảy đều do an hưởng phúc đức, phần nhiều do chân thần đắc dụng; sang nghiệp hưng gia, khó nhọc mà thiếu an nhàn, phần nhiều do giả thần đắc cục | chân vs giả dụng | - | VAGUE ('đắc cục' of a giả thần needs tư lệnh by day) → T:chan_gia
109 | Khắc, tiết, dẫn, tòng bốn chữ nên nghiên cứu kỹ càng | cương / nhu | - | METHOD → H:cuong_nhu
109 | Nói chung đắc thời đương lệnh, tứ trụ không có khắc chế, dụng thực thần thuận theo khí thế, tiết kỳ tinh anh | strong in season, no control | dụng = Thực Thương | - → R:BT_TTTK_DT08
111 | Chỉ có thể thuận theo khí thế mà dẫn thông, cho nên khí lưu hành gặp phú hĩ, nếu miễn cưỡng khắc chế, chọc giận cường thần, chắc chắn gặp phải điều dữ | follow the dominant | - | METHOD → H:dung_rules.TTT111
111 | cho nên chế sát không bằng hóa sát | Sát: transform (Ấn) before control | - | METHOD → H:dung_rules.TTT111

## Con cái (pp.130-132; Phần II ch.2)

130 | Như hỉ thần là Quan tinh, con cái hiền tài | hỉ = Quan (nguyên chú) | children able | - → R:BT_TTTK_CC01
130 | Nay sửa đổi lấy Thực Thương làm con | Nhâm: Thực Thương = children | - | METHOD → schools.json (children star)
130 | Như nhật chủ vượng, không có Ấn thụ, có Thực Thương, tất nhiều con trai | | many sons | SENSITIVE (number / sex) — kept out
130 | Nhật chủ vượng, gặp Ấn thụ, Thực Thương khinh, tất ít con | | few children | SENSITIVE (number)
130 | Nhật chủ vượng, Ấn thụ trọng, Thực Thương khinh, có Tài tinh, dự phòng con nhiều mà hiền | | many, good children | SENSITIVE (number) for 'nhiều'; the 'hiền' half → R:BT_TTTK_CC02 (number not voiced)
130 | Nhật chủ vượng, Ấn nhiều tất không con | | no child | SENSITIVE
130 | Nhật chủ nhược, Thực Thương khinh, không có Tỉ Kiếp, tất không có con | | no child | SENSITIVE
130 | Nhật chủ nhược, Sát trọng, Thực Thương khinh, Tài tàng mà suy nhược, tất nhiều con gái | | many daughters | SENSITIVE (sex)
130 | Nhật chủ nhược, Thất Sát trọng, Thực Thương khinh, có Tỉ Kiếp, con gái nhiều con trai ít | | | SENSITIVE (sex)
130 | Nhật chủ nhược, Quan Sát trọng, không có Ấn Tỉ, tất không có con trai | | | SENSITIVE (sex)
130 | Nhật chủ vượng, Thực Thương khinh, gặp Ấn thụ, gặp Tài tinh, con ít cháu nhiều | | | SENSITIVE (number)
130 | Nhật chủ vượng, Ấn thụ trọng, Quan Sát khinh, có Ấn thụ, gặp Tài, có con tất nghịch | DM strong, Ấn heavy, Quan Sát light, Tài | a child is headstrong | - → R:BT_TTTK_CC03
130 | Lại có nhật chủ vượng, không có Ấn thụ, Thực Thương ẩn, có Quan Sát, tất nhiều con | | | SENSITIVE (number)
131 | Nói chung, thân vượng lấy Tài là con, thân suy lấy Ấn là con | Nhâm's own children star | - | METHOD → schools.json (children star)
132 | trong mệnh con chỉ có 5 số, thủy 1 - hỏa 2 - mộc 3 - kim 4 - thổ 5 vậy | counting children | - | SENSITIVE (number)
132 | phàm dụng thần bát tự là Tử tức tinh | dụng = child star; birth timing | - | SENSITIVE (birth timing) for the timing; principle → schools.json

## Hà Tri (pp.143-148)

143 | Hỉ thần, là phụ dụng thần trợ chủ. Phàm bát tự trước tiên cần phải có hỉ thần, cả đời hữu cát vô hung, cho nên hỉ thần chính là cát thần vậy | role of hỉ | - | METHOD → H:roles.hi
143 | Dụng Quan, nếu thân vượng có thể lấy Tài làm hỉ thần; thân nhược dụng Ấn, rồi sau đó lấy Quan làm hỉ thần | hỉ by dụng | - | METHOD → H:hi_by_dung
143 | không có hỉ thần mà dụng thần đắc lệnh hùng tráng, đại thế kiên cố, tứ trụ an hòa, dụng thần đứng cạnh, không tranh không đố, tức gặp kỵ thần cũng không hung hiểm | dụng holds the month, no hỉ | safe even with kỵ | - → R:BT_TTTK_HK01
143 | Như nguyên cục không có hỷ thần, có kỵ thần (hoặc ám phục hoặc xuất hiện), hoặc đứng sát bên dụng thần, hoặc tranh hoặc đố, hoặc dụng thần không nắm lệnh, hoặc tuế vận dẫn xuất kỵ thần, trợ khởi kỵ thần, giống như quốc gia có gian thần, tư thông giặc ngoại bang, hai mặt giáp công thì hung họa lập tức đến | no hỉ, kỵ next to dụng | trouble | - → R:BT_TTTK_HK02 ('hung họa' voiced as 'dễ gặp trắc trở')
144 | Tài Quan vô khí, dụng thần vô lực, chẳng qua không thể phát đạt được mà thôi, cũng không có hình hung vậy | Tài Quan weak, dụng weak | no rise, no disaster | - → R:BT_TTTK_HK03
144 | Kỵ thần, là thần làm tổn hại dụng thần | role of kỵ | - | METHOD → H:roles.ky
144 | Lấy kỵ thần là bệnh, hỉ thần là dược, bệnh có dược chữa là cát, có bệnh mà không có dược là hung | bệnh / dược | - | METHOD → H:benh_duoc
144 | nếu tuế vận lại không đến phù hỉ ức kỵ, lại không cùng kỵ thần kết thành bè đảng, bất quá cả đời là bình thường, không có chỗ phát đạt mà thôi | kỵ holds the month, no rescue | ordinary life | LUCK → H:luck_principles
145-148 | (thọ / yểu: Tính định Nguyên thần dày; Khí trọc thần khô) | lifespan | - | SENSITIVE (lifespan) — kept out; the definitions of nàn/hỉ/kỵ on p.145 ('chỗ hợp đều là nhàn thần, chỗ hóa đều là dụng thần') → H:roles (definition only)

## Tài Đức, Phấn Ức, Ân Oán, Nhàn Thần (pp.161-170)

161 | hỉ Quan mà Tài có thể sinh Quan; hỉ Tài mà Quan có thể khắc chế Kiếp, kỵ Ấn mà Tài có thể phá Ấn; hỉ Ấn mà Quan có thể sinh Ấn | each hỉ helped by its neighbour | upright, 'phong cách quân tử' | - → R:BT_TTTK_DUC1
161 | hỉ Quan mà lâm Kiếp địa, hỉ Tài mà cư nơi Ấn, kỵ Ấn mà Quan tinh sinh Ấn, hỉ Ấn mà Tài phá Ấn | each hỉ undercut by its neighbour | 'tượng đa năng' | - → R:BT_TTTK_DUC2
161 | Đại để dương ở trong, âm ở ngoài, không kích không kháng là đức thắng tài | yin/yang placement | - | VAGUE (needs a yin/yang reading of the pillars; no fact) — kept out
163 | Nếu thế thuần dương, thân vượng mà Tài Quan vượng, tất là phấn phát; cục thuần âm, thân nhược mà Quan Sát nhiều là nhiều khốn đốn | all-yang / all-yin charts | - | VAGUE (needs an all-yang / all-yin fact) — kept out
163 | chỗ dụng đều đắc khí, hỉ thần đều đắc lực, kỵ thần đều thất thế | open vs depressed chart | - | VAGUE ('đắc khí') → H:phan_uc
163 | Nhưng cục dù âm hối, mà vận đồ phối hợp dương minh, cũng có thể thông suốt | luck reverses | - | LUCK → H:luck_principles
165 | Ân oán, là Hỉ Kỵ vậy | ân / oán | - | METHOD → H:an_oan
165 | Về phần thần đáng ghét, may mắn là ở xa; còn thần yêu thích, gần thì càng thân thiết | distance of kỵ / hỉ | - | - (same as p.101) → R:BT_TTTK_HK06/HK07
167 | Hỉ thần chẳng nên nhiều vậy, một hỉ mà được 10 hỉ; Kỵ thần cũng chẳng nên nhiều vậy, một kị mà bị 10 hại vậy | | - | METHOD → H:roles
167 | Trong tứ trụ ngoài dụng thần, hỉ thần, kỵ thần đều là Nhàn thần | nhàn thần | - | METHOD → H:roles.nhan
167 | Như dụng mộc, mộc có dư, lấy hỏa làm Hỉ thần, lấy kim làm Kỵ thần, lấy thủy làm Cừu thần, lấy thổ làm Nhàn thần; mộc không đủ, lấy thủy làm hỉ thần, thổ làm kỵ thần, lấy kim làm cừu thần, lấy hỏa làm nhàn thần | element map of the five roles | - | METHOD → H:role_map (computable)
167 | được nhàn thần chế hóa hung thần kỵ vật của tuế vận, phụ giúp hỉ dụng cách cục | nhàn thần in a luck | - | LUCK → H:roles.nhan
168 | Hợp mà không hóa, thì giống như bị lưu luyến ràng buộc | tham hợp | - | METHOD → H:hop_xung
169 | Đoạn này chính là đắc dụng phùng xung vậy | xung freeing the DM | - | METHOD → H:hop_xung

## Thuận / Phản / Chiến / Hợp cục, Quân / Thần / Mẫu / Tử (pp.183-201)

183 | là lấy Tòng Nhi cách tối kỵ Ấn vận, kế đến là Quan vận | tòng nhi luck | - | DUP (tong_roles.json Tòng Nhi) → H:tong_luck
185 | Phàm Tòng Nhi cách, hành vận không nghịch, gặp Tài không thể không có phú quý vậy; mà tú khí lưu hành, người tất thông minh xuất chúng, học vấn tinh thông | tòng nhi + Tài | wealth, clever | VAGUE (the kin layer does not know the tòng verdict; tvh_cach does) → H:tong_luck
186 | Quân dựa vào Thần sinh, ý nói Ấn thụ quá vượng vậy | phản cục | Ấn too strong → Tài | METHOD → H:phan_cuc
186 | Phá Ấn mà tựu Tài, là ý phạm thượng, cho nên gọi là Phản cục vậy | | - | METHOD → H:phan_cuc
188 | trong cục Ấn thụ tuy vượng, trong trụ Tài tinh có khí, có thể dụng Tài phá Ấn vậy. Mẫu từ diệt Tử, dẫu có Tài tinh mà vô khí, không thể lấy Tài tinh phá Ấn vậy | Ấn strong: Tài usable only if Tài has qi | - | - → R:BT_TTTK_DT09, R:BT_TTTK_DT10
190 | Mộc vượng thổ nhiều, không có kim không sợ, một khi thấy chữ Canh Thân Tân Dậu, kim khắc mộc, gọi là chồng khỏe mà sợ vợ vậy | phu kiện phạ thê | - | METHOD → H:phan_cuc
191 | Nếu như nhật chủ không kiện, gọi là Tài đa thân nhược, cuối cùng là thân khốn khổ vậy | Tài many, DM weak | hardship | DUP (BT_TVHK_G03 p.521 same condition) — kept out
192 | Thiên chiến còn có thể, Địa chiến gấp như hỏa | stem vs branch clashes | - | METHOD → H:chien_hop
192 | Cho nên thiên can luận là khắc, địa chi nói xung, xung tức là khắc vậy | | - | METHOD → H:chien_hop
194 | Hợp có nên và không nên, không nên hợp nhiều | | - | METHOD → H:chien_hop
194 | Nói chung, hợp nhiều thì không lưu thông, không phấn phát, tuy có tú khí, cũng không được vậy | many combinations | - | VAGUE ('nhiều') → H:chien_hop
197-201 | Quân / Thần / Mẫu / Tử tượng (one-element charts: follow the dominant, avoid the element that provokes it) | | - | METHOD → H:phan_cuc (the title verses are glyph-garbled in the text layer)

## Tuế Vận (pp.229-233)

229 | Phú quý tuy định ở cách cục, cũng phải gắn liền với vận đồ thuận lợi nữa, chỗ gọi là Mệnh tốt không bằng vận tốt vậy | | - | METHOD → H:luck_principles
229 | Cho nên lấy địa chi làm trọng | a luck pillar: branch first | - | METHOD → H:luck_principles
229 | Thà rằng khiến cho thiên can sinh địa chi, không nên địa chi sinh thiên can; thiên can sinh địa chi mà phúc dày, địa chi sinh thiên can mà khí tiết | stem feeds branch | - | LUCK → H:luck_principles
229-230 | cái đầu / tiệt cước | | - | DUP (BT_TTT_CAIDAU_* / BT_TTT_TIETCUOC_* in pack_temporal.json)
230 | Xấu nhất là thiên khắc địa xung | | - | DUP (BT_TTT_THIENKHAC_*)
231 | Chiến là khắc vậy. Như vận Bính năm Canh, là vận khắc Tuế | luck stem controls year stem | - | LUCK → H:luck_year
232 | Xung là phá vậy. Như vận Tý năm Ngọ, gọi là vận xung tuế | | - | LUCK → H:luck_year
232 | Hòa là Hợp vậy | | - | LUCK → H:luck_year
233 | Tốt, là loại tương đồng vậy | | - | LUCK → H:luck_year
