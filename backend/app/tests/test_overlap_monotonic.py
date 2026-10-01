"""折边抬升单调回归：同一盒型连续抬升折边档位时 paper_m2 单调非降，
且未乘折边的表面积字段保持不变；非法折边（0 / 负）必须被拒绝。"""
from app.engines.wrap_math import paper_area
from overlap_assertions import (
    assert_any_strict_increase,
    assert_non_decreasing,
    assert_overlap_rejected,
    assert_strictly_increasing,
    assert_surface_unchanged,
)
from overlap_fixtures import BOOK_BOX_GROUP, SQUARE_BOX_GROUP


def _paper_sequence(group):
    return [
        paper_area(group["length"], group["width"], group["height"], ov)
        for ov in group["overlaps"]
    ]


def _assert_group_monotonic(group):
    assert_strictly_increasing(
        group["overlaps"], f"{group['group']} 折边档位应严格抬升: {group['overlaps']}"
    )
    results = _paper_sequence(group)
    seq = [r["paper_m2"] for r in results]
    assert_non_decreasing(seq, f"{group['group']} paper_m2 应随折边单调非降: {seq}")
    assert_any_strict_increase(seq, f"{group['group']} 至少出现一次严格上升: {seq}")
    assert_surface_unchanged(
        results,
        group["box_surface"],
        f"{group['group']} 未乘折边的表面积不应随折边档位变化",
    )


def test_book_box_group_monotonic():
    _assert_group_monotonic(BOOK_BOX_GROUP)


def test_square_box_group_monotonic():
    _assert_group_monotonic(SQUARE_BOX_GROUP)


def test_overlap_zero_rejected():
    g = BOOK_BOX_GROUP
    assert_overlap_rejected(
        g["length"], g["width"], g["height"], 0.0,
        "overlap=0 不是合法折边，必须抛出 ValueError",
    )


def test_overlap_negative_rejected():
    g = SQUARE_BOX_GROUP
    assert_overlap_rejected(
        g["length"], g["width"], g["height"], -0.25,
        "负折边系数必须被判定为非法输入",
    )
