"""断言助手：折边抬升单调回归的公共断言。

只放断言 helper，不放夹具数据；数据见 overlap_fixtures.py。
"""
import pytest

from app.engines.wrap_math import paper_area


def assert_strictly_increasing(values, message):
    for prev, curr in zip(values, values[1:]):
        assert curr > prev, message


def assert_non_decreasing(values, message):
    for prev, curr in zip(values, values[1:]):
        assert curr >= prev, message


def assert_any_strict_increase(values, message):
    pairs = list(zip(values, values[1:]))
    assert any(curr > prev for prev, curr in pairs), message


def assert_surface_unchanged(results, expected_surface, message):
    surfaces = {r["box_surface"] for r in results}
    assert surfaces == {expected_surface}, message


def assert_overlap_rejected(length, width, height, overlap, fail_message):
    with pytest.raises(ValueError) as exc_info:
        paper_area(length, width, height, overlap)
    assert "overlap must be positive" in str(exc_info.value), fail_message


def assert_run_paper_m2(record, expected_paper_m2, message):
    assert record is not None, message
    assert record["result"]["paper_m2"] == expected_paper_m2, message
