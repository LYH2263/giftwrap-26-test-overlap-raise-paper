"""夹具数据：折边抬升单调回归共用的盒型分组、折边档位与跨模块链常量。

只放数据，不放断言；断言助手见 overlap_assertions.py。
"""

# 全局基准折边系数（与 app.config.DEFAULT_OVERLAP 一致）
BASE_OVERLAP = 1.15

# 书型盒组：基准档 + 两档严格更大的折边
BOOK_BOX_GROUP = {
    "group": "书型盒",
    "box_name": "书型盒",  # 与 seed 中的盒名一致，跨模块链按名查库
    "length": 0.30,
    "width": 0.20,
    "height": 0.15,
    # 2*(0.30*0.20 + 0.30*0.15 + 0.20*0.15)，未乘折边的表面积
    "box_surface": 0.27,
    "overlaps": (BASE_OVERLAP, 1.30, 1.50),
}

# 方形盒组：基准档 + 两档严格更大的折边
SQUARE_BOX_GROUP = {
    "group": "方形盒",
    "box_name": "方形礼盒",
    "length": 0.25,
    "width": 0.25,
    "height": 0.10,
    # 2*(0.25*0.25 + 0.25*0.10 + 0.25*0.10)
    "box_surface": 0.225,
    "overlaps": (BASE_OVERLAP, 1.25, 1.40),
}

BOX_GROUPS = (BOOK_BOX_GROUP, SQUARE_BOX_GROUP)

# 跨模块链：先以较小折边算纸落库，再经设置把全局折边调大
CHAIN_SAVED_OVERLAP = BASE_OVERLAP
CHAIN_RAISED_OVERLAP = 1.60
CHAIN_NOTE = "折边抬升回归-落库"
