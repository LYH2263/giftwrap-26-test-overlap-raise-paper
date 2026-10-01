"""跨模块链：较小折边算纸落库 → 经设置调大全局折边 →
新算单调抬升（单调新算链），历史落库值不被回刷（历史不回刷链）。"""
import pytest

from app import seed
from app.db import connect
from app.repositories import boxes, history, settings_repo
from app.services import estimate_service
from overlap_assertions import assert_run_paper_m2
from overlap_fixtures import (
    BOOK_BOX_GROUP,
    CHAIN_NOTE,
    CHAIN_RAISED_OVERLAP,
    CHAIN_SAVED_OVERLAP,
)


@pytest.fixture()
def isolated_db(tmp_path, monkeypatch):
    """把 app.db 指向临时库并播种，避免触碰真实数据。"""
    db_file = tmp_path / "chain.db"
    monkeypatch.setattr("app.db.DB_PATH", db_file)
    seed.init_db()
    yield db_file


def _set_global_overlap(value):
    c = connect()
    try:
        c.execute(
            "INSERT OR REPLACE INTO settings(key,value) VALUES ('overlap', ?)",
            (str(value),),
        )
        c.commit()
    finally:
        c.close()


def _book_box_id():
    for b in boxes.list_boxes():
        if b["name"] == BOOK_BOX_GROUP["box_name"]:
            return b["id"]
    raise AssertionError("seed 缺少书型盒")


def _save_then_raise():
    """以较小折边算纸落库一条，再经设置把全局折边调大。"""
    box_id = _book_box_id()
    saved = estimate_service.run_estimate(box_id, CHAIN_SAVED_OVERLAP, "cross", True, CHAIN_NOTE)
    assert saved["run_id"] is not None, "落库应返回 run_id"
    _set_global_overlap(CHAIN_RAISED_OVERLAP)
    assert settings_repo.get_overlap() == CHAIN_RAISED_OVERLAP, "全局折边应已被调大"
    return box_id, saved["run_id"], saved["paper_m2"]


def test_new_estimate_lifts_monotonically_after_overlap_raise(isolated_db):
    """单调新算链：全局折边调大后，新算 paper_m2 严格大于落库值。"""
    box_id, run_id, saved_paper = _save_then_raise()
    fresh = estimate_service.run_estimate(box_id, None, "cross", False, "")
    assert fresh["overlap"] == CHAIN_RAISED_OVERLAP, "新算应使用调大后的全局折边"
    assert fresh["paper_m2"] > saved_paper, (
        f"新算 paper_m2 应随折边抬升严格上升: {fresh['paper_m2']} !> {saved_paper}"
    )
    assert fresh["box_surface"] == BOOK_BOX_GROUP["box_surface"], (
        "新算的未乘折边表面积字段不应变化"
    )


def test_saved_run_not_refreshed_after_overlap_raise(isolated_db):
    """历史不回刷链：全局折边调大后，详情与列表摘要仍为落库值。"""
    box_id, run_id, saved_paper = _save_then_raise()
    detail = history.get_run(run_id)
    assert_run_paper_m2(detail, saved_paper, "详情读取：历史用纸 paper_m2 不得被全局折边回刷")
    summaries = [r for r in history.list_runs() if r["id"] == run_id]
    assert summaries, "列表摘要应包含已落库的算纸记录"
    assert_run_paper_m2(summaries[0], saved_paper, "列表摘要：历史用纸 paper_m2 仍为落库值")
