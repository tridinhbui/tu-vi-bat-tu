# Horary schools: differences the engine must make selectable or report

Built only from the four public-domain scans in `docs/HORARY-KB.md`: Lilly, *Christian Astrology* (1647, `LILLY`);
Bonatti's *146 Considerations* in Coley's English (1676 first edition `BONATUS_1676`, cited by leaf; Redway reprint 1886
`BONATUS_1886`, cited by page and Consideration number "c"); Ptolemy, *Tetrabiblos*, tr. Ashmand 1822 (`PTOLEMY`). Page
numbers are printed pages. No modern book is used; a modern position is named only as "commonly attributed, not verified
here". Records: `engine/data/horary/bonatti.json`, `ptolemy.json`, and the Lilly files (`lilly_book1.json`,
`tables_lilly.json`).

Three cautions that apply throughout:

- **Ashmand's footnotes are not Ptolemy.** They quote Whalley, Placidus, Moxon, Kepler etc. (orbs, day/night houses,
  "oriental orientality", minor aspects). Nothing below attributes them to Ptolemy.
- **The 1886 Bonatti has an editor's footnotes** (Morrison, Simmonite, Wilson, Pearce) that are not in 1676 and are not
  Bonatti. Notes headed "Note by Lilly" in 1886 are printed in italic, without that heading, on the 1676 leaves checked.
- **Ptolemy gives no horary rules.** The `ptolemy` school is a dignity/aspect variant, not a way of judging questions.

Engine defaults below assume the product's primary school is Lilly; the `bonatti` and `ptolemy` schools switch only the
items listed.

## 1. Triplicity rulers

| Triplicity | Lilly p.104-105 | Ptolemy (Ashmand) pp.44-45 | Bonatti |
|---|---|---|---|
| Fire | Sun day, Jupiter night | Sun day, Jupiter night; Mars expressly excluded | no table |
| Earth | Venus day, Moon night | Venus day, Moon night | no table |
| Air | Saturn day, Mercury night | Saturn day, Mercury night | no table |
| Water | **Mars day and night**, "according to Ptolomy and Naibod" (p.105) | **Venus day, Moon night, "together with Mars"** (p.45) | implies Mars has triplicity in Pisces (c005, p.4) |

- Lilly attributes his Mars-only water triplicity to Ptolemy; Ashmand's Ptolemy does not say that. Both are read from the
  page images.
- **No participating (third) ruler** is printed by Lilly or by Ashmand's Ptolemy.
- **Bonatti implies a scheme none of these sources prints.** c005 (p.4, checked on 1676 leaf 27) says Saturn "in the 4 last
  degrees of Aries or Gemini" has "a Term and a Triplicity". Saturn ruling the Gemini triplicity agrees with Lilly and
  Ptolemy. Saturn ruling the triplicity of Aries (fire) agrees with neither. A three-ruler (Dorothean) scheme with Saturn
  in fire is commonly attributed to the Arabic tradition Bonatti follows. That is **not verified here**.
- **Engine default:** lilly school: Lilly p.104 (water Mars/Mars). ptolemy school: Ashmand (water Venus/Moon with Mars as
  co-ruler, giving Mars triplicity dignity by day and by night). bonatti school: Lilly's table, with a reported flag "c005
  implies Saturn has triplicity in Aries (participating ruler, not tabulated in our sources)". Reason: Bonatti prints no
  table, and Lilly's is the only full table we have that matches Bonatti's water example.

## 2. Terms (bounds)

Three tables are available, all read from page images:

- **Lilly p.104**, "according to Ptolomy" (`tables_lilly.json`).
- **Ashmand p.53**, Ptolemy's own terms (`ptolemy.json` `terms_ptolemaic`). Seven signs have two readings stacked in one
  cell: Taurus, Cancer, Leo, Libra, Scorpio, Capricorn, Pisces.
- **Ashmand p.49**, the Egyptian terms (`terms_egyptian`). The planet totals 57/79/66/82/76 check against the text.

How Lilly's "Ptolomy" table compares with Ashmand's Ptolemaic table:

| Sign | Lilly p.104 | Ashmand p.53 |
|---|---|---|
| Aries, Virgo, Sagittarius, Aquarius | same as Ashmand | single reading |
| Leo | Sat 6, Mer 13, Ven 19, Jup 25, Mars 30 | = the reading the text p.52 requires ("Saturn in Leo") |
| Pisces | Ven 8, Jup 14, Mer 20, Mars 26, Sat 30 | = upper reading (lower: Mars 25, Saturn printed "3", should be 5) |
| Taurus | ... Sat 26, Mars 30 | = lower reading (upper: Sat 24) |
| Cancer | Mars 6, Jup 13, Mer 20, Ven 27, Sat 30 | = lower reading (upper: Mer 13, Jup 20) |
| Capricorn | ... Mars 25, Sat 30 | = lower reading (upper: Sat 25, Mars 30) |
| **Gemini** | Mer 7, Jup 14, Ven 21, **Sat 25, Mars 30** | Mer 7, Jup 13, Ven 20, **Mars 26, Sat 30** (no alternative) |
| **Libra** | Sat 6, Ven 11, **Jup 19, Mer 24**, Mars 30 | Mer 19, Jup 24 **or** Jup 16, Mer 24 |
| **Scorpio** | Mars 6, **Jup 14, Ven 21**, Mer 27, Sat 30 | Ven 14, Jup 21 **or** Jup 13, Ven 21 |

**Ptolemy's own verdict (p.50):** of the two old systems, the Egyptian "seems more to be relied on" than the Chaldean. He
then gives his own terms from an "antient writing" (pp.51-52). He prints no Chaldean table, only the method (8-7-6-5-4
degrees), so the Chaldean terms are not implemented.

**Bonatti's term examples fit Ashmand's Ptolemaic table, not Lilly's and not the Egyptian.** All are from c005, pp.3-4,
checked on 1676 leaves 27-28:

| Bonatti says | Egyptian | Lilly | Ashmand Ptolemaic |
|---|---|---|---|
| Saturn has the 4 last degrees of Aries | 25-30, fails | 26-30, fits | 26-30, fits |
| Saturn has the 4 last degrees of Gemini | 24-30, fails | Mars has 25-30, fails | 26-30, fits |
| Mars has the first 6 degrees of Cancer | 0-7, fails | fits | fits |

Bonatti's remark that the last 6 degrees of Leo belong to Jupiter fits no table: in the Egyptian table Jupiter has the
*first* 6 degrees of Leo. It is recorded as printed and not used.

**Engine default:**

- lilly school: Lilly p.104 (the engine's primary dignity table, and what Lilly's own examples are judged with).
- ptolemy school: Ashmand p.53, upper reading (Leo per p.52). The alternative readings are a sub-option.
- bonatti school: Ashmand p.53, upper reading, `operationalised`. Bonatti prints no table, but his worked degrees agree
  with it in every case we can test and contradict Lilly's Gemini.
- The Egyptian table is offered as an option in every school and is never a default: no source used here prefers it for
  horary, and Ptolemy prefers it only over the Chaldean.

## 3. Exaltations

- Lilly p.104 gives exaltations **with degrees**: Sun 19 Aries, Moon 3 Taurus, North Node 3 Gemini, Jupiter 15 Cancer,
  Mercury 15 Virgo, Saturn 21 Libra, South Node 3 Sagittarius, Mars 28 Capricorn, Venus 27 Pisces.
- Ptolemy (pp.45-46) gives **signs only, and no Nodes**.
- Bonatti uses degree-specific "descensions" (c005, p.3): the Moon in the 3rd degree of Scorpio, the Sun in the 19th degree
  of Libra, Mars in the 28th degree of Cancer. These are the falls opposite Lilly's exaltation degrees.
- All three agree on the sign of each planet's exaltation and fall.
- **Default:** score exaltation and fall by whole sign in every school. Report "at/near the exaltation degree" for the lilly
  and bonatti schools only. Nodes' exaltations are scored only in the lilly school.

## 4. Faces

- Lilly p.104: 10-degree faces (decanates) in Chaldean order, e.g. Aries Mars 10, Sun 20, Venus 30.
- Bonatti: implies decanates. c005 (p.4) gives Mars "a Face" in "the last 10 degrees of Pisces", which matches Lilly's
  Pisces faces (Saturn, Jupiter, Mars).
- Bonatti's weighting (c040, c044): a face (and a triplicity) abates an infortune "very little". A face counts only "assisted
  with another Dignity, which is Hayz or Light".
- Ptolemy (p.54): "proper face" is an aspect relation to the Sun or Moon, not a decanate. He prints no decan table.
- **Default:** decanate faces for the lilly and bonatti schools. In the bonatti school a face counts as a dignity for
  reception only together with another dignity (c044). The ptolemy school scores no face; the aspect-face is reported only.

## 5. Dignity weights and which dignities make a reception

- Lilly pp.101-103, 115: house 5, exaltation 4, triplicity 3, term 2, face 1; detriment -5, fall -4 (see
  `tables_lilly.json`).
- Bonatti gives no numbers, only an order. Perfect reception is "House, Exaltation, or two of the smaller Dignities, which are
  Term, Triplicity, and Face" (c006, p.5; also c011). For abating an infortune (c040, p.22): house, exaltation or term
  "somewhat"; triplicity or face "very little"; hayz least.
- Ptolemy gives no weights.
- **Default:** Lilly's numbers in all schools. In the bonatti school, reception requires house, exaltation, or **two** minor
  dignities together (Bonatti's explicit rule). Reception by a single term, triplicity or face is reported but not counted
  as reception.

## 6. Orbs

- Lilly p.107 prints two columns:

  | Planet | 1st column | 2nd column |
  |---|---|---|
  | Saturn | 10° | 9° |
  | Jupiter | 12° | 9° |
  | Mars | 7°30' | 7° |
  | Sun | 17° | 15° |
  | Venus | 8° | 7° |
  | Mercury | 7° | 7° |
  | Moon | 12°30' | 12° |

  He says "I somtimes use the one, and sometimes the other". Aspects work by the moiety (half) of both planets' orbs (p.107
  example; p.110).
- Bonatti: affliction is judged "according to the quantity of their Orbs" (c016, p.14) but he gives **no values**. His
  timing thresholds are in minutes:
  - separated by 1' means freed, or "fear" only (c016-017);
  - within 51' counts as the present contact (c088);
  - the secret-helper steps run 15'/16'/50' (c009).
- Ptolemy: application "when the distances ... are but trifling" (p.55); **no values**. The orb list in Ashmand's footnote
  on p.55 (Saturn 10, Jupiter 12, Mars 7°30', Sun 17, Venus 8, Mercury 7°30', Moon 12°30') is the translator's.
- **Default:** Lilly's first column with the moiety rule in every school. The bonatti school adds the 1' separation rule
  (c016-017) and reports contacts within 51' as "present" (c088). The ptolemy school states that Ptolemy gives no orbs.

## 7. Combustion, under the beams, cazimi

| | Lilly p.113 | Bonatti | Ptolemy |
|---|---|---|---|
| Combust | within 8°30' of the Sun, **same sign only**; worse when the Sun applies | **15°** before or after (c006, p.5) | nothing |
| Moon combust | as for planets | 15° applying, 12° separating; "escaped" once 5° past (c005, p.3) | phase qualities only (p.23) |
| Under the beams | until 17° | note after c053 (p.25): 12° or less "and yet above 16 minutes" (1676 leaf 62; the 1886 reprint garbles this) | nothing |
| Leaving the beams | beyond 17°, counted "Free from Combustion and Beams" in the p.115 table | 12°-15°, "going from under the Sun's beams" (c053 note); fortified at 12°, more at 15° (c052, c054) | nothing |
| Cazimi | within 17' | within 16' (c053 note); "heart of the Sun ... every star is fortified" (c013) | nothing |
| Degrees of debility | | superiors followed by the Sun: weaker from 15°, extreme from 7° to the heart; inferiors the same when following the Sun (c054, p.26) | |

**Default:** lilly school: Lilly's limits. bonatti school: combust within 12° (c053 note, 16' cazimi), 12°-15° leaving, and
c006's 15° reported as an alternative; for the Moon the c005 asymmetric 15°/12° rule. ptolemy school: Lilly's limits,
labelled "no limit in Ptolemy".

## 8. Void of course

- Lilly p.112: void when separated from a planet "nor doth forthwith, during his being in that Signe, apply to any other"
  (a within-sign test). Lilly p.122: matters go hardly when the Moon is void of course, "yet somewhat she performes" in
  Taurus, Cancer, Sagittarius or Pisces (glyphs checked on the image).
- Bonatti c005, 10th impediment (p.4): "not joined to any planet by body or aspect". He also calls a Moon in a place "where
  she has not any dignity" void ("Feral or Desart").
  - c019 (p.17): the matter will not be accomplished.
  - c062 (p.30): it scarce comes to a good end, unless the Lord of the Ascendant or significator is very strong.
  - c064 (p.30): the Moon in Cancer, Taurus, Sagittarius or Pisces hurts less when void, unless combust. These are the same
    four signs as Lilly.
- Ptolemy: nothing.
- **Default:** Lilly's within-sign definition for both schools, with the four-sign mitigation. Bonatti never states the
  sign limit. c069 ("If she join not to any in or from the Sign in which she is, take ... the next Sign") supports it
  indirectly. The bonatti school also reports the "feral" (Moon peregrine) flag separately, never as VOC.

## 9. Radicality and when not to judge

| Test | Lilly pp.121-123 | Bonatti |
|---|---|---|
| Hour ruler | radical when the Lord of the hour and the Lord of the Ascendant are of one triplicity, the same planet, or of the same nature | not radical unless they are the same, of the same triplicity, or of the same complexion as the Ascendant (c007, p.7). c143 (p.69): the signs where the two lords stand are of the same triplicity or complexion |
| Early/late Ascendant | 0-2° rising (especially signs of short ascension) or 27-29° rising: not safe | Ascendant "very near the end of one sign and beginning of another" means the querent is testing or not serious (c007, p.6); "if the Ascendant shall be the end of any Sign, the Question is not Radical" (c143, p.69). **No degrees given** |
| Moon | late degrees, especially Gemini, Scorpio, Capricorn; "as some say" Via Combusta, the last 15° of Libra and first 15° of Scorpio | Via Combusta, 15 Libra to 15 Scorpio, is the 9th impediment of the Moon (c005; 1676 leaf 28), not a bar to judgment |
| 7th house | cusp or lord afflicted: the judgment gives small content | Lord of the 7th afflicted: "defer judgment if you can" (c065, p.30) |
| Saturn | in the 1st (especially retrograde) or in the 7th (Alkindus) | no equivalent |
| Lord of the Ascendant combust | question will not take | no equivalent as a radicality test |
| Fortunes = infortunes | defer judgment | do not receive the question (c007, case 4); "indifferency", neither gain nor loss (c083) |
| Sun on the MC line | | astrologer does not know whether the Sun has left the MC line (c007, case 3) |

**Default:** compute every test of the active school and **report** them as cautions ("the books say not to judge"). Never
silently refuse. Bonatti's sign-boundary test has no degree: the engine uses the first or last 1° of the sign
(`bonatti.c007`, operationalised) and does not borrow Lilly's 0-2° / 27-29°.

## 10. House cusps, angularity, house system

- Lilly p.33: a planet "within five degrees of the Cusp of any house" counts in the house whose cusp it is nearest.
- Bonatti, c058 (pp.27-28), checked on 1676 leaves 65-67:
  - a planet up to 5° before the Ascendant is in the angle ("Zael ... Ptolomy ... with whom I agree");
  - Bonatti's own experience is 5° after the cusp; more than that is cadent.
- Bonatti, c059 (p.28): Zael allows 15° after an angle; "Ptolomy seems to intimate" 5° before or 25° after.
- The note printed after c059 (headed "Note by Lilly" in 1886) says a planet belongs to a house anywhere between its cusps,
  "in the House, not in the Sign, because sometimes the same House comprehends more than one Sign". That is a quadrant-house
  system, not whole signs.
- Ptolemy (Ashmand p.57): strength is greatest in or succedent to the MC, then on or succedent to the horizon. He gives no
  cusp orb.
- House system: only Lilly names one, and only for nativities: "To erect a Scheame of heaven by the Tables of
  Regiomontanus" (p.519, Book III). Bonatti and Ashmand's Ptolemy name none (Placidus appears only in Ashmand's footnotes).
- **Default:** Regiomontanus cusps. A planet within 5° before a cusp counts in that house (Lilly and Bonatti agree on the 5°
  before). Angular strength is graded by distance from the cusp (Bonatti c081). Whole-sign houses are not offered as a
  default by any source here. Bonatti's house system is **not verified**; he only implies quadrant houses.

## 11. Orientality and sect

**Relation to the Sun:**

- Lilly p.114: superiors are oriental from their conjunction with the Sun to the opposition (rising before the Sun).
  Mercury and Venus are oriental when in fewer degrees of the Sun's sign, or in the sign before.
- Bonatti c052, c054, c056: superiors are strong when rising in the morning before the Sun, from 12° (more at 15°).
  Inferiors are strong when they appear in the evening after sunset. A planet given virtue that is a superior and oriental,
  or an inferior and occidental, "shall be strong and fit to perfect".
- Ptolemy pp.22, 56: oriental (matutine) strengthens **every** planet; no superior/inferior split. Oriental, swift and direct
  is strongest.

**Quadrant "orientality":**

- Ptolemy p.22: from the Ascendant to the Midheaven and from the West to the lower heaven, a planet is oriental and
  masculine.
- Bonatti c008 (p.8): from the cusp of the 10th to the cusp of the Ascendant, and from the 4th to the 7th, are masculine
  quarters.
- Read in the direction of the daily motion, these are the same two quadrants (houses 10-12 and 4-6). That reading is the
  engine's.

**Sect:** Ptolemy pp.22-23 has Saturn diurnal and Mars nocturnal, with Mercury by matutine/vespertine. Bonatti c008 and
c047 agree (Mercury listed in both groups).

**Default:** the lilly and bonatti schools split by superior/inferior as above. The ptolemy school uses "matutine = strong"
for all planets. Sect ("light", c047) is scored only in the bonatti school, where Bonatti uses it as a strength.

## 12. Benefics, malefics, the luminaries

- Ptolemy p.21: Jupiter, Venus **and the Moon** are benefic; the Sun and Mercury are common.
- Bonatti c050 (p.24) counts "Jupiter, Venus, the Sun or Moon" as fortunes that can rescue. c013: the Sun is a fortune by
  aspect (not opposition) and an infortune by conjunction. c014: Mercury and the Moon take the nature of the planet they
  join.
- Lilly: not compared here; see the lilly records.
- **Default:** per school as stated. The engine never counts the Sun's conjunction as benefic (combustion).

## 13. How a matter is perfected or destroyed

These differences change verdicts:

- **Separation by one minute** (Bonatti c016-017): a benefic aspect just separated by 1' gives hope but no perfection; a
  malefic just separated gives fear but escape. Lilly treats a planet as not wholly separated until it is past the moiety of
  the orbs (p.110). Default: lilly school: Lilly. bonatti school: Bonatti's 1' rule.
- **Application across a sign boundary** (c031): perfects only with reception in the new sign and no interposed contact. A
  bodily conjunction cuts off an aspect, never the reverse. Lilly's prohibition (pp.110-111) is the closest rule; the
  sign-change and reception condition is Bonatti's alone.
- **Planet in the 30th degree** (c030): past 29°01' it acts in the next sign. Not compared with Lilly.
- **Significator and Moon both more than 25° from the angles**: no perfection (c096), journeys excepted. Bonatti only.
- **Lord of the prior new or full Moon in an angle of the matter** (c070); tie-break by the prior syzygy, then the Moon
  (c069). Bonatti only.
- **Translation** (c098) shows a go-between described by the translator's house. Lilly's definition (p.111) supplies the
  mechanics, which Bonatti's list (c003-004) names without defining.
- **Projections** (c140, c144, c146) are Bonatti only. They are auxiliary testimonies, never the verdict.

## 14. Timing

- Bonatti c071 (p.33; 1676 leaf 74): the unit comes from the significator's region of the figure:
  - Ascendant to 12th: days or hours;
  - 12th to 10th: half weeks;
  - 10th to 7th: months or weeks;
  - 7th to 4th: years;
  - 4th to Ascendant: half years.
- Bonatti gives no count of units. The 1886 footnote with "degrees = days/weeks/months" is the editor's (absent in 1676).
- Lilly p.110: count the degrees to perfection, with units by sign modality.
- **Default:** lilly school: Lilly's count. bonatti school: report c071's unit next to Lilly's count, labelled.

## 15. Could NOT be verified

- Bonatti's triplicity scheme (participating ruler) and his term table. Inferred only from the c005 examples.
- Bonatti's house system.
- What Bonatti means by "Novenarium" and "Duodenarium" of the Moon (c087, c089). Coley does not define them; their reading
  as ninth-part and twelfth-part is commonly attributed, not verified here.
- "Hayz" in Bonatti (named in c040, c044, c046, never defined by Coley). Lilly defines hayz (p.113); applying Lilly's
  definition to Bonatti is an engine choice, not verified.
- The azimene, pitted, smoky and dark degrees in Bonatti's Moon list (c005, items 14-17). He refers to "Tables commonly in
  most Books" and prints none.
- Bonatti's fixed-star longitudes (c099-100). Not image-checked and not used.
- Which reading of the seven double cells in Ashmand's Ptolemaic terms is right. Neither the scan nor the text decides,
  except Leo.
- Whether Lilly's "Ptolomy" terms in Gemini, Libra and Scorpio come from a different edition of Ptolemy. Not determinable
  from these scans.
- Who wrote the italic notes that the 1886 reprint heads "Note by Lilly". No heading is visible on the 1676 leaves checked
  (25, 62, 67, 85).
