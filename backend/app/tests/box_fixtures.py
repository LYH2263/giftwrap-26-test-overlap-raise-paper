"""折边抬升单调回归 —— 夹具与样例数据模块。

本模块只提供：
1. 两组盒型样例（书型盒、方形盒）与基准之上严格更大的两档 overlap；
2. 与生产 SQLite 库隔离的临时数据库夹具，以及走 ASGI 的 TestClient 夹具。

断言助手与具体用例放在同目录 test_overlap_monotonic.py。
"""
import pytest
from fastapi.testclient import TestClient

from app import config, seed
from app.main import app

# 基准档 1.10 之上，两档严格更大的折边系数
OVERLAP_STEPS = (1.10, 1.20, 1.35)

BOXES = [
    {"name": "书型盒", "length": 0.30, "width": 0.20, "height": 0.15,
     "expected_surface": 0.27},   # 2*(0.06+0.045+0.03)
    {"name": "方形盒", "length": 0.25, "width": 0.25, "height": 0.10,
     "expected_surface": 0.225},  # 2*(0.0625+0.025+0.025)
]


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    """把 DATA_DIR/DB_PATH 指向临时目录并初始化种子数据，避免触碰真实库。"""
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    seed.init_db()
    return tmp_path


@pytest.fixture
def isolated_client(isolated_db):
    """启动事件会在临时库上建表灌种子；退出即连同临时目录一起丢弃。"""
    with TestClient(app) as client:
        yield client
