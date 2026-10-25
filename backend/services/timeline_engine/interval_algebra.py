from datetime import datetime, date
from typing import Tuple
from .models import AllenRelation

def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def compute_interval_relation(
    start_a_str: str,
    end_a_str: str,
    start_b_str: str,
    end_b_str: str
) -> AllenRelation:
    """
    Computes the exact Allen Temporal Interval Relation between Interval A [s_a, e_a] and Interval B [s_b, e_b].
    """
    s_a = parse_date(start_a_str)
    e_a = parse_date(end_a_str) if end_a_str else s_a
    s_b = parse_date(start_b_str)
    e_b = parse_date(end_b_str) if end_b_str else s_b

    # Defensive check: ensure start <= end
    if s_a > e_a:
        s_a, e_a = e_a, s_a
    if s_b > e_b:
        s_b, e_b = e_b, s_b

    if s_a == s_b and e_a == e_b:
        return AllenRelation.EQUALS

    if e_a < s_b:
        return AllenRelation.BEFORE

    if s_a > e_b:
        return AllenRelation.AFTER

    if e_a == s_b:
        return AllenRelation.MEETS

    if s_a == e_b:
        return AllenRelation.MET_BY

    if s_a < s_b and e_a > s_b and e_a < e_b:
        return AllenRelation.OVERLAPS

    if s_b < s_a and e_b > s_a and e_b < e_a:
        return AllenRelation.OVERLAPPED_BY

    if s_a > s_b and e_a < e_b:
        return AllenRelation.DURING

    if s_b > s_a and e_b < e_a:
        return AllenRelation.CONTAINS

    if s_a == s_b and e_a < e_b:
        return AllenRelation.STARTS

    if s_a == s_b and e_b < e_a:
        return AllenRelation.STARTED_BY

    if s_a > s_b and e_a == e_b:
        return AllenRelation.FINISHES

    if s_b > s_a and e_a == e_b:
        return AllenRelation.FINISHED_BY

    # Fallback to before/after
    return AllenRelation.BEFORE if e_a <= s_b else AllenRelation.AFTER
