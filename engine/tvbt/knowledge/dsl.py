"""Rule expression AST: typed, closed vocabulary. Rule content is DATA — never eval'd code/SQL.

Expression JSON forms:
  {"all": [expr...]} | {"any": [expr...]} | {"not": expr}
  {"fact": "<known fact name>", "operator": "eq|ne|in|not_in|gte|lte|contains|not_contains|contains_any|contains_all", "value": <literal>}
Phase-1 additions (all backward compatible):
  {"ref": {"palace": "<role|palace name>", "fact": "<known fact>"}, "operator": ..., "value": ...}
      reads a fact of ANOTHER palace. role is one of self|opp|trine1|trine2|flank_prev|flank_next|nhi_hop (relative to the palace
      being evaluated) or a literal palace name such as "Quan Lộc". Needs a `world` resolver; without one the result is UNKNOWN.
  {"count": [expr...], "operator": "gte|lte|eq|ne", "value": <int>}
      how many of the sub-expressions are True (an UNKNOWN sub-expression makes the count UNKNOWN unless the answer is already decided).
Facts are resolved from a flat dict produced by fact extraction (Phase 3); unknown facts are a
validation error, and a missing fact at run time yields UNKNOWN (three-valued logic), not False.
A fact whose sources disagree is given as alternatives: facts["alt:<name>"] = [v1, v2, ...] (e.g. a CONFLICT star-dignity cell, where one
book reads vượng in its phú and đắc in its prose). A condition on that fact is TRUE when every alternative satisfies it, FALSE when none
does, UNKNOWN otherwise; no reading is ever picked. A null alternative is an unknown reading. The alternatives win over the plain fact.
"""
from __future__ import annotations

from typing import Any, Callable

OPERATORS = {"eq", "ne", "in", "not_in", "gte", "lte", "contains", "not_contains", "contains_any", "contains_all"}
COUNT_OPERATORS = {"eq", "ne", "gte", "lte"}
ROLES = {"self", "opp", "trine1", "trine2", "flank_prev", "flank_next", "nhi_hop"}
MAX_DEPTH = 8
UNKNOWN = None  # three-valued: True / False / None
ALT = "alt:"    # facts[ALT + name]: the disagreeing readings of fact `name` (see the module docstring)


class RuleError(ValueError):
    pass


def validate(expr: Any, known_facts: set[str], depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        raise RuleError("expression too deep")
    if not isinstance(expr, dict) or not expr:
        raise RuleError(f"expression must be a non-empty object: {expr!r}")
    keys = set(expr)
    if keys == {"all"} or keys == {"any"}:
        items = expr.get("all", expr.get("any"))
        if not isinstance(items, list) or not items:
            raise RuleError("all/any need a non-empty list")
        for e in items:
            validate(e, known_facts, depth + 1)
    elif keys == {"not"}:
        validate(expr["not"], known_facts, depth + 1)
    elif "fact" in keys and keys <= {"fact", "operator", "value"}:
        _check_fact(expr["fact"], known_facts)
        _check_operator(expr)
    elif "ref" in keys and keys <= {"ref", "operator", "value"}:
        ref = expr["ref"]
        if not isinstance(ref, dict) or set(ref) != {"palace", "fact"} or not isinstance(ref["palace"], str) or not ref["palace"]:
            raise RuleError(f"ref needs exactly {{palace, fact}}: {ref!r}")
        _check_fact(ref["fact"], known_facts)
        _check_operator(expr)
    elif "count" in keys and keys <= {"count", "operator", "value"}:
        items = expr["count"]
        if not isinstance(items, list) or not items:
            raise RuleError("count needs a non-empty list")
        if expr.get("operator", "eq") not in COUNT_OPERATORS or not isinstance(expr.get("value"), int):
            raise RuleError("count needs operator in eq|ne|gte|lte and an integer value")
        for e in items:
            validate(e, known_facts, depth + 1)
    else:
        raise RuleError(f"unrecognised expression shape: {sorted(keys)}")


def _check_fact(name: str, known_facts: set[str]) -> None:
    if name not in known_facts and not any(k.endswith("*") and name.startswith(k[:-1]) for k in known_facts):
        raise RuleError(f"unknown fact {name!r}")


def _check_operator(expr: dict) -> None:
    op = expr.get("operator", "eq")
    if op not in OPERATORS:
        raise RuleError(f"unknown operator {op!r}")
    if "value" not in expr:
        raise RuleError("fact condition needs 'value'")
    if op in ("in", "not_in", "contains_any", "contains_all") and not isinstance(expr["value"], list):
        raise RuleError(f"{op} needs a list value")


def resolve_palace(target: str, facts: dict[str, Any]) -> str | None:
    """Palace NAME a ref points to: a role (relative to the palace whose facts are `facts`) or a literal palace name."""
    if target in ROLES:
        names = facts.get("palace.rel_names")
        return names.get(target) if isinstance(names, dict) else None
    return target


def _compare(got: Any, op: str, want: Any) -> bool | None:
    try:
        if op == "eq":
            return got == want
        if op == "ne":
            return got != want
        if op == "in":
            return got in want
        if op == "not_in":
            return got not in want
        if op == "gte":
            return got >= want
        if op == "lte":
            return got <= want
        if op == "contains":
            return want in got
        if op == "not_contains":
            return want not in got
        if op == "contains_any":
            return any(w in got for w in want)
        if op == "contains_all":
            return all(w in got for w in want)
    except TypeError:
        return UNKNOWN          # incomparable value (e.g. None >= 2): treat as unknown, never as False
    raise RuleError(f"unknown operator {op!r}")


SRC_DIGNITY = "palace.dignity@"   # palace.dignity@<school>.<star>: the star's brightness in the table of the rule's own book


def _own_book_dignity(facts: dict[str, Any], name: str) -> tuple[str, Any]:
    """A rule from Thực Hành, Toàn Thư or Khảo Luận tests brightness in its own book's table (audit 2026-10-23). The cell is looked up in the
    shared dignity KB for the palace's branch; a cell that book leaves empty (or unverified) falls back to the table the chart was drawn with
    (palace.dignity.<star>), which is what the reading then rests on."""
    school, star = name[len(SRC_DIGNITY):].split(".", 1)
    from .. import dignity as dg   # local import: the DSL stays importable without the KB
    br = facts.get("palace.branch")
    try:
        lv = dg.dignity(star, br, school) if br else None
    except ValueError:
        lv = None
    return (name, lv) if lv else (f"palace.dignity.{star}", None)


def _leaf(facts: dict[str, Any], name: str, op: str, want: Any) -> bool | None:
    # a fact given outright (a hand-built test palace) is used as given
    if name.startswith(SRC_DIGNITY) and name not in facts:
        name, lv = _own_book_dignity(facts, name)
        if lv is not None:
            return _compare(lv, op, want)
    alts = facts.get(ALT + name)
    if isinstance(alts, list):
        vals = [UNKNOWN if a is None else _compare(a, op, want) for a in alts]
        if not vals or UNKNOWN in vals:
            return UNKNOWN
        return True if all(vals) else (False if not any(vals) else UNKNOWN)
    if name not in facts:
        return UNKNOWN
    return _compare(facts[name], op, want)


def evaluate(expr: dict, facts: dict[str, Any], world: Callable[[str], dict[str, Any] | None] | None = None) -> bool | None:
    """world(palace_name) -> that palace's facts (or None). Only needed for `ref` conditions."""
    if "all" in expr:
        vals = [evaluate(e, facts, world) for e in expr["all"]]
        return False if False in vals else (None if None in vals else True)
    if "any" in expr:
        vals = [evaluate(e, facts, world) for e in expr["any"]]
        return True if True in vals else (None if None in vals else False)
    if "not" in expr:
        v = evaluate(expr["not"], facts, world)
        return None if v is None else (not v)
    if "count" in expr:
        vals = [evaluate(e, facts, world) for e in expr["count"]]
        yes, unk, op, want = vals.count(True), vals.count(None), expr.get("operator", "eq"), expr["value"]
        lo, hi = yes, yes + unk               # the true count lies in [lo, hi]; answer only if every value in the range agrees
        answers = {_compare(n, op, want) for n in range(lo, hi + 1)}
        return answers.pop() if len(answers) == 1 else UNKNOWN
    if "ref" in expr:
        if world is None:
            return UNKNOWN
        name = resolve_palace(expr["ref"]["palace"], facts)
        other = world(name) if name else None
        if other is None:
            return UNKNOWN
        return _leaf(other, expr["ref"]["fact"], expr.get("operator", "eq"), expr["value"])
    return _leaf(facts, expr["fact"], expr.get("operator", "eq"), expr["value"])


def leaves(expr: dict, facts: dict[str, Any] | None = None) -> list[tuple[str | None, str]]:
    """All (palace name or None, fact name) a condition reads. For role refs the palace is resolved through `facts` when given."""
    if "fact" in expr:
        return [(None, expr["fact"])]
    if "ref" in expr:
        return [(resolve_palace(expr["ref"]["palace"], facts or {}) or expr["ref"]["palace"], expr["ref"]["fact"])]
    key = "count" if "count" in expr else next(iter(expr))
    sub = expr[key] if isinstance(expr[key], list) else [expr[key]]
    return [x for e in sub for x in leaves(e, facts)]
