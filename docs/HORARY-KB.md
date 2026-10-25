# Horary knowledge base (engine/data/horary)

Chiêm tinh vấn sự (horary) is a traditional interpretive practice. Nothing here is evidence that it predicts events: the
astronomy is exact and checkable, the judgments are the tradition's own rules, reported as such.

## Sources (only public-domain scans with a clear provenance)

| key | work | copy | use |
|---|---|---|---|
| `LILLY` | William Lilly, *Christian Astrology* (London, 1647), Books I–II | Wellcome Library, archive.org `b30338724`, Public Domain Mark | primary school of the engine |
| `BONATUS_1886` | Guido Bonatti, *146 Considerations*, tr. Henry Coley in *Anima Astrologiae* (1676), Redway reprint 1886 | archive.org `b24884054`, PD Mark | second school; cross-check |
| `BONATUS_1676` | same, first edition | archive.org `b30335735`, PD Mark | image check only (OCR unusable) |
| `PTOLEMY` | Ptolemy, *Tetrabiblos*, tr. J. M. Ashmand (1822) | archive.org `b29293066`, PD Mark | dignity scheme / aspect theory cross-check |

Not consulted (copyrighted, no licensed copy available to the project): John Frawley, *The Horary Textbook* (2005); Olivia
Barclay, *Horary Astrology Rediscovered* (1990); B. Dykes' translation of Bonatti's *Book of Astronomy* (2007). No rule cites
them; where a rule is known to be read differently by modern authors, the record says only "modern reading, not verified
from the text" and is never `classical`.

Page tool: `python tools/horary/sources.py text|image|find|check` (see its docstring). The printed page number is the
citation; `check` re-reads every quote from the scan and fails when it is not on its page.

## Record schema

Every file is `{ "meta": {...}, "rules": [ ... ] }` (tables may add `"tables": {...}` with their own `sources`).

```jsonc
{
  "id": "lilly.voc.definition",          // stable; code and traces refer to it
  "category": "moon",                    // radicality | dignity_essential | dignity_accidental | aspect | perfection | denial |
                                         // reception | sun | motion | moon | house | significator | topic | timing | lost_object | method
  "title_en": "Void of course",
  "title_vi": "Trăng vô hành (void of course)",
  "statement_en": "A planet is void of course when ...",       // faithful paraphrase of the source
  "statement_vi": "...",                                         // Vietnamese, same content, no added claim
  "conditions": "when it applies: ... (operational, what the engine tests)",
  "exceptions": ["Lilly: the Moon VOC in Taurus, Cancer, Sagittarius or Pisces performs somewhat ..."],  // each with its own source if it has one
  "effect": "definition",                // definition | table | warning | caution_radicality | testimony_for | testimony_against |
                                         // modifies | timing_method | significator_assignment
  "school": "lilly",                     // lilly | bonatti | ptolemy
  "status": "classical",                 // classical (stated in the source) | operationalised (source + an engine choice the source
                                         // leaves open, explained in `engine_choice`) | disputed (sources disagree: `dispute`)
  "engine_choice": "...",                // only when status = operationalised
  "dispute": "...",                      // only when status = disputed: who says what, with sources
  "sources": [ { "work": "LILLY", "page": 112, "quote": "verbatim from the scan, old spelling kept, <= ~40 words" } ],
  "example": "a worked case from the source, or a constructed configuration the test-suite checks (say which)"
}
```

Rules about health, death, lawsuits' outcomes, pregnancy and similar are recorded only as `effect: "warning"` boundary notes
(the product does not judge them).
