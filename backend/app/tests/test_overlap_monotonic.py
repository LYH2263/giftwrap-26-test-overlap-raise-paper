"""折边抬升单调回归 —— 断言助手与用例模块。

覆盖点：
1. 书型盒、方形盒各在两档严格更大的 overlap 下连续取 paper_m2：
   单调非降且至少严格上升一次，未乘折边的 box_surface 全程不变；
2. overlap=0 与负 overlap 各一条失败用例，断言消息互不相同；
3. 跨模块链：算纸落库 -> 调大全局 overlap -> 用纸档详情与列表摘要均不回刷，
   同时走全局系数的新算结果单调抬升（新算/历史双链都覆盖）。

盒型样例、overlap 档位与隔离夹具见 box_fixtures.py。
"""
import pytest

from app.engines.wrap_math import paper_area
from box_fixtures import BOXES, OVERLAP_STEPS


# ---------- 断言助手 ----------

def assert_monotone_non_decreasing(values, label):
    for prev, curr in zip(values, values[1:]):
        assert curr >= prev, (
            f"{label}：overlap 抬升后 paper_m2 不得回落，得到 {values}"
        )


def assert_strictly_rises(values, label):
    assert any(curr > prev for prev, curr in zip(values, values[1:])), (
        f"{label}：两档严格更大的 overlap 中至少应有一次 paper_m2 严格上升，得到 {values}"
    )


def assert_surface_unchanged(surfaces, expected, label):
    assert all(s == expected for s in surfaces), (
        f"{label}：box_surface 是未乘折边的表面积，不应随 overlap 变化，得到 {surfaces}"
    )
    assert len(set(surfaces)) == 1, (
        f"{label}：不同 overlap 档位下 box_surface 必须完全一致，得到 {surfaces}"
    )


def assert_paper_m2_persisted(payload, saved_m2, source):
    assert payload["result"]["paper_m2"] == saved_m2, (
        f"{source}：全局 overlap 调大后历史用纸档被回刷，"
        f"期望落库值 {saved_m2}，实际 {payload['result']['paper_m2']}"
    )


# ---------- 单调回归：两组盒型 ----------

@pytest.mark.parametrize("box", BOXES, ids=[b["name"] for b in BOXES])
def test_paper_m2_monotone_with_strict_rise(box):
    results = [
        paper_area(box["length"], box["width"], box["height"], overlap)
        for overlap in OVERLAP_STEPS
    ]
    values = [r["paper_m2"] for r in results]

    assert_monotone_non_decreasing(values, box["name"])
    assert_strictly_rises(values, box["name"])
    assert_surface_unchanged(
        [r["box_surface"] for r in results], box["expected_surface"], box["name"]
    )


def test_overlap_steps_are_strictly_larger():
    # 守卫夹具数据：基准之上必须有两档严格更大的 overlap
    assert OVERLAP_STEPS[1] > OVERLAP_STEPS[0], "第一档 overlap 未严格大于基准档"
    assert OVERLAP_STEPS[2] > OVERLAP_STEPS[1], "第二档 overlap 未严格大于第一档"


# ---------- 非法 overlap 失败用例（消息各不相同） ----------

def test_zero_overlap_rejected():
    book = BOXES[0]
    with pytest.raises(ValueError) as exc:
        paper_area(book["length"], book["width"], book["height"], 0)
    assert "overlap must be positive" in str(exc.value), (
        "overlap=0 属于非法折边系数，算纸必须显式拒绝而不是返回零用纸"
    )


def test_negative_overlap_rejected():
    square = BOXES[1]
    with pytest.raises(ValueError) as exc:
        paper_area(square["length"], square["width"], square["height"], -0.1)
    assert "overlap must be positive" in str(exc.value), (
        "负 overlap 会算出负用纸面积，算纸必须显式拒绝而不是参与乘法"
    )


# ---------- 跨模块链：算纸落库 -> 调全局系数 -> 历史不回刷，新算抬升 ----------

def test_saved_run_not_recomputed_after_global_overlap_rises(isolated_client):
    # 1) 以较小 overlap 经算纸接口落库一条用纸档
    saved = isolated_client.post(
        "/api/estimate",
        json={"box_id": 1, "overlap": 1.05, "wrap_style": "cross", "save": True, "note": "单调回归"},
    )
    assert saved.status_code == 200, saved.text
    saved_m2 = saved.json()["paper_m2"]
    run_id = saved.json()["run_id"]
    assert run_id is not None, "save=True 时必须返回落库 run_id"

    # 2) 经设置接口把全局 overlap 调大
    bumped = isolated_client.post("/api/settings", json={"overlap": 1.50})
    assert bumped.status_code == 200, bumped.text
    assert float(bumped.json()["overlap"]) == 1.50

    # 3a) 单调新算链：不带 overlap 的新算走全局新系数，用纸必须严格抬升
    fresh = isolated_client.get("/api/estimate", params={"box_id": 1})
    assert fresh.status_code == 200, fresh.text
    assert fresh.json()["paper_m2"] > saved_m2, (
        f"全局 overlap 调大后新算用纸应抬升：落库 {saved_m2}，新算 {fresh.json()['paper_m2']}"
    )

    # 3b) 历史不回刷链 —— 用纸档详情
    detail = isolated_client.get(f"/api/runs/{run_id}")
    assert detail.status_code == 200, detail.text
    assert_paper_m2_persisted(detail.json(), saved_m2, "用纸档详情")

    # 3c) 历史不回刷链 —— 列表摘要
    listing = isolated_client.get("/api/runs")
    assert listing.status_code == 200, listing.text
    rows = [item for item in listing.json()["items"] if item["id"] == run_id]
    assert rows, "落库用纸档必须出现在列表摘要中"
    assert_paper_m2_persisted(rows[0], saved_m2, "用纸档列表摘要")
