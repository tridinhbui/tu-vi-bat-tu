"""Rule expression AST: typed, closed vocabulary. Rule content is DATA — never eval'd code/SQL.

Expression JSON forms:
  {"all": [expr...]} | {"any": [expr...]} | {"not": expr}
  {"fact": "<known fact name>", "operator": "eq|ne|in|not_in|gte|lte|contains", "value": <literal>}
Facts are resolved from a flat dict produced by fact extraction (Phase 3); unknown facts are a
validation error, and a missing fact at run time yields UNKNOWN (three-valued logic), not False.
"""
from __future__ import annotations

from typing import Any

OPERATORS = {"eq", "ne", "in", "not_in", "gte", "lte", "contains"}
MAX_DEPTH = 8
UNKNOWN = None  # three-valued: True / False / None


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
        if expr["fact"] not in known_facts:
            raise RuleError(f"unknown fact {expr['fact']!r}")
        op = expr.get("operator", "eq")
        if op not in OPERATORS:
            raise RuleError(f"unknown operator {op!r}")
        if "value" not in expr:
            raise RuleError("fact condition needs 'value'")
        if op in ("in", "not_in") and not isinstance(expr["value"], list):
            raise RuleError(f"{op} needs a list value")
    else:
        raise RuleError(f"unrecognised expression shape: {sorted(keys)}")


def evaluate(expr: dict, facts: dict[str, Any]) -> bool | None:
    if "all" in expr:
        vals = [evaluate(e, facts) for e in expr["all"]]
        return False if False in vals else (None if None in vals else True)
    if "any" in expr:
        vals = [evaluate(e, facts) for e in expr["any"]]
        return True if True in vals else (None if None in vals else False)
    if "not" in expr:
        v = evaluate(expr["not"], facts)
        return None if v is None else (not v)
    name = expr["fact"]
    if name not in facts:
        return UNKNOWN
    got, want, op = facts[name], expr["value"], expr.get("operator", "eq")
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
    return want in got  # contains
