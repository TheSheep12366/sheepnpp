#!/usr/bin/env python3
"""贴图美术规范与矩阵生成器（Sheep's Nuclear Plant Decor）。

规则沿用 001/docs/TEXTURE_PIPELINE.md 的 R1~R7：
  R1 颗粒是 1px 逐像素细噪声、调色板只差 ±3 级（原版混凝土做法）；禁止 2~3px 高对比团块
  R2 满格方块四边可平铺：不得有整行/整列与内部明显不同的硬边
  R3 薄板四边对称斜角边框，下边框带兼作侧脸断面
  R4 图案提供材质身份
  R5 透明镂空用 '.'（alpha=0），只有格栅和桥架允许
  R6 结构性噪点成簇或 1px 点状
  R7 薄板模型声明 particle（particle_chip）

“现代”的约束：大幅面板 + 1px 低对比细缝、哑光、低饱和；饱和色只给警示、三叶符和少量状态点。

用法：
  python3 tools/texture_spec.py            写 tools/texture_spec.json
  python3 tools/texture_spec.py --ascii    同时把每张贴图按字符打印出来，人工核对
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "tools/texture_spec.json"
N = 16


def hash01(x: int, y: int, seed: int) -> float:
    """确定性哈希：同一个 (x, y, seed) 永远得到同一个 0~1 的值，重跑得到同一张图。"""
    n = (x * 374761393 + y * 668265263 + seed * 2246822519) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


class Grid:
    """16x16 字符画布。'.' 表示透明。"""

    def __init__(self, fill: str = ".") -> None:
        self.cells = [[fill] * N for _ in range(N)]

    def set(self, x: int, y: int, ch: str) -> None:
        if 0 <= x < N and 0 <= y < N:
            self.cells[y][x] = ch

    def rect(self, x: int, y: int, w: int, h: int, ch: str) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, ch)

    def frame(self, x: int, y: int, w: int, h: int, ch: str) -> None:
        for xx in range(x, x + w):
            self.set(xx, y, ch)
            self.set(xx, y + h - 1, ch)
        for yy in range(y, y + h):
            self.set(x, yy, ch)
            self.set(x + w - 1, yy, ch)

    def hline(self, y: int, x0: int, x1: int, ch: str) -> None:
        for x in range(x0, x1 + 1):
            self.set(x, y, ch)

    def vline(self, x: int, y0: int, y1: int, ch: str) -> None:
        for y in range(y0, y1 + 1):
            self.set(x, y, ch)

    def grain(self, ch_up: str, ch_down: str, seed: int,
              p_up: float = 0.25, p_down: float = 0.25) -> None:
        """逐像素细颗粒（R1）。必须配合极窄调色板：B/C 只差 ±3 级。"""
        for y in range(N):
            for x in range(N):
                h = hash01(x, y, seed)
                if h < p_up:
                    self.set(x, y, ch_up)
                elif h < p_up + p_down:
                    self.set(x, y, ch_down)

    def grit(self, ch: str, positions: list[tuple[int, int]]) -> None:
        """零星 1px 颗粒（骨料 / 针点 / 螺栓）。"""
        for x, y in positions:
            self.set(x, y, ch)

    def stamp(self, x: int, y: int, rows: list[str], mapping: dict[str, str]) -> None:
        """把小图案盖到画布上。图案里的 ' ' 不动，其余字符经 mapping 换成色位。"""
        for dy, row in enumerate(rows):
            for dx, c in enumerate(row):
                if c != " ":
                    self.set(x + dx, y + dy, mapping.get(c, c))

    def rows(self) -> list[str]:
        return ["".join(r) for r in self.cells]


# 通道端面的圆盖：D 环 / C 盖面 / B 高光。6x6，四角空出。
DISC = [
    " DDDD ",
    "DCCCCD",
    "DCBCCD",
    "DCCCCD",
    "DCCCCD",
    " DDDD ",
]


# --------------------------------------------------------------------------
# 满格材质
# --------------------------------------------------------------------------
def solid(kind: str, seed: int = 7) -> Grid:
    """色位约定：A 本色 / B 高光(+3) / C 阴影(-3) / D 深 / E、F 为各材质自带的辅助色。"""
    g = Grid("A")

    if kind == "formwork":
        # 清水混凝土：细颗粒 + 一道水平模板缝（row 8）+ 四枚拉杆孔。模板缝在内部，不触及平铺边。
        g.grain("B", "C", seed, 0.26, 0.26)
        g.hline(8, 0, 15, "E")
        g.grit("D", [(4, 4), (11, 4), (4, 12), (11, 12)])

    elif kind == "painted":
        # 涂装混凝土：几乎无颗粒的哑光漆面 + 一道 V 形凹缝（暗线 + 亮线）。
        g.grain("B", "C", seed, 0.12, 0.12)
        g.hline(7, 0, 15, "D")
        g.hline(8, 0, 15, "E")
        g.grit("D", [(3, 2), (12, 12)])

    elif kind == "lead":
        # 铅板：整块平面 + 短边斜线收口（不围死一圈）+ 四角螺栓。
        g.grain("B", "C", seed, 0.12, 0.12)
        for x in range(1, 15):
            g.set(x, 0, "B")
            g.set(x, 15, "C")
        for y in range(1, 15):
            g.set(0, y, "B")
            g.set(15, y, "C")
        g.grit("D", [(3, 3), (12, 3), (3, 12), (12, 12)])

    elif kind == "hazard":
        # 黄黑警示：45° 斜条，两色，无渐变。
        for y in range(N):
            for x in range(N):
                g.set(x, y, "Y" if ((x + y) // 4) % 2 == 0 else "K")

    elif kind == "grate":
        # 钢格栅：4px 周期格阵，承重条 + 格孔；每格中心 2x2 透空（R5）。
        for y in range(N):
            for x in range(N):
                if x % 4 == 0 or y % 4 == 0:
                    g.set(x, y, "B" if (y % 4 == 0 and x % 4 != 0) else "A")
                else:
                    g.set(x, y, "D")
        for oy in range(0, N, 4):
            for ox in range(0, N, 4):
                g.rect(ox + 1, oy + 1, 2, 2, ".")

    elif kind == "epoxy":
        # 去污地坪：近乎均质的树脂涂层 + 极细暗颗粒 + 沿斜线分布的 1px 微反光。
        g.grain("B", "C", seed, 0.0, 0.12)
        g.grit("B", [(5, 3), (6, 4), (7, 5), (8, 6), (9, 7)])
        g.grit("D", [(2, 11), (12, 2), (6, 13)])

    elif kind == "shield":
        # RBMK 生物屏蔽：偏暖深灰重混凝土，骨料明显多于普通混凝土，一道竖向浇筑缝。
        g.grain("B", "C", seed, 0.28, 0.28)
        g.grit("E", [(2, 3), (6, 10), (11, 6), (13, 13), (4, 14), (10, 1)])
        g.grit("D", [(5, 6), (12, 10), (9, 13), (1, 8), (14, 3)])
        g.vline(7, 0, 15, "F")

    elif kind == "graphite":
        # RBMK 石墨砌块：近黑，2x2 砌块（十字缝 = 暗线 + 紧邻的受光线）+ 1px 晶点。
        g.grain("B", "C", seed, 0.22, 0.22)
        g.grit("E", [(3, 3), (11, 2), (5, 12), (13, 10), (2, 9), (10, 13)])
        g.hline(8, 0, 15, "F")
        g.vline(8, 0, 15, "F")
        g.hline(7, 0, 15, "D")
        g.vline(7, 0, 15, "D")

    elif kind == "steel_green":
        # RBMK 灰绿钢板：哑光漆 + 一道竖向板缝（暗线 + 亮线）+ 四枚螺栓。
        g.grain("B", "C", seed, 0.12, 0.12)
        g.vline(7, 0, 15, "D")
        g.vline(8, 0, 15, "E")
        g.grit("D", [(3, 3), (12, 3), (3, 12), (12, 12)])

    elif kind == "channel":
        # RBMK 通道端面：金属板面 + 2x2 圆盖阵列（平面贴图，不做凹陷模型）。
        g.grain("B", "C", seed, 0.10, 0.10)
        for ox, oy in [(1, 1), (9, 1), (1, 9), (9, 9)]:
            g.stamp(ox, oy, DISC, {"D": "D", "C": "E", "B": "F"})

    elif kind == "containment":
        # 冷灰安全壳：干净大板，仅一道内部浅浇筑缝，不围边。
        g.grain("B", "C", seed, 0.20, 0.20)
        g.hline(8, 0, 15, "D")

    elif kind == "liner":
        # 冷银衬里：低振幅短拉丝 + 1px 竖缝，窄高光留在缝边。
        g.grain("B", "C", seed, 0.12, 0.12)
        for x, y in [(2, 3), (10, 5), (4, 11), (11, 13)]:
            g.hline(y, x, x + 2, "B")
        g.vline(7, 0, 15, "D")
        g.vline(8, 0, 15, "E")

    elif kind == "liner_white":
        # 暖白哑光内衬：细颗粒 + 单条浅竖缝，无金属高光。
        g.grain("B", "C", seed, 0.10, 0.10)
        g.vline(7, 0, 15, "D")

    elif kind == "deck":
        # 蓝灰甲板：大面保持连续，四角螺栓各用暗点和克制的受光点。
        g.grain("B", "C", seed, 0.16, 0.16)
        for x, y in [(3, 3), (12, 3), (3, 12), (12, 12)]:
            g.set(x, y, "D")
            g.set(x, y - 1, "E")

    elif kind == "cc_white":
        g.grain("B", "C", seed, 0.10, 0.10)
        g.frame(0, 0, N, N, "E")
        g.hline(8, 1, 14, "D")

    elif kind == "acoustic":
        g.grain("B", "C", seed, 0.10, 0.10)
        g.vline(7, 0, 15, "E")
        # Opaque pinholes on a regular acoustic panel, never cutout.
        for y in range(2, N, 4):
            for x in range(2, N, 4):
                g.set(x, y, "D")

    elif kind == "console":
        g.grain("B", "C", seed, 0.08, 0.08)
        g.vline(7, 0, 15, "D")
        g.hline(8, 0, 15, "D")
        g.hline(4, 2, 5, "E")
        g.hline(12, 10, 13, "E")
        # Only two status pixels (2/256); slots carry the panel identity.
        g.set(4, 6, "F")
        g.set(12, 10, "G")

    elif kind == "antistatic":
        g.grain("B", "C", seed, 0.14, 0.14)
        g.frame(0, 0, N, N, "D")
        g.grit("E", [(3, 3), (12, 3), (3, 12), (12, 12)])

    elif kind == "white_light":
        g.grain("B", "C", seed, 0.06, 0.06)
        g.frame(0, 0, N, N, "D")

    elif kind == "beige":
        g.grain("B", "C", seed, 0.18, 0.18)
        g.grit("D", [(3, 5), (10, 2), (12, 12), (6, 10)])

    elif kind == "office_wood":
        g.grain("B", "C", seed, 0.10, 0.10)
        # Fine straight veneer, with no knots or rustic plank borders.
        for x in (3, 11):
            g.vline(x, 0, 15, "D")
        for x, y, length in [(1, 2, 4), (5, 9, 4), (8, 3, 5), (13, 10, 3)]:
            g.vline(x, y, y + length - 1, "E")
        for x, y in [(2, 9), (6, 3), (10, 12), (14, 5)]:
            g.vline(x, y, y + 2, "F")

    elif kind == "carpet":
        g.grain("B", "C", seed, 0.24, 0.24)
        # Sparse single-pixel tufts keep the carpet soft and unpatterned.
        g.grit("D", [(2, 3), (9, 6), (5, 12), (13, 10)])

    elif kind == "office_tile":
        g.grain("B", "C", seed, 0.08, 0.08)
        g.frame(0, 0, N, N, "D")

    else:
        raise ValueError(f"unknown solid kind: {kind}")
    return g


# --------------------------------------------------------------------------
# RBMK building full cubes
# --------------------------------------------------------------------------
def floor_solid(kind: str, seed: int) -> Grid:
    """Original opaque floor patterns, with quiet +/-3 RGB grain beneath the structure."""
    g = Grid("A")
    g.grain("B", "C", seed, 0.12, 0.12)
    if kind == "heavy_load":
        for x in (3, 11):
            g.vline(x, 0, 15, "D")
            g.vline(x + 1, 0, 15, "E")
        g.hline(8, 0, 15, "D")
        g.grit("F", [(2, 3), (10, 3), (2, 12), (10, 12)])
    elif kind == "turbine_hall":
        for y in (2, 6, 10, 14):
            for x in (2, 10):
                g.hline(y, x, x + 3, "E")
                g.hline(y + 1, x, x + 3, "D")
    elif kind == "equipment_room":
        g.frame(2, 2, 12, 12, "D")
        g.vline(7, 3, 12, "F")
        for x, y in ((3, 3), (12, 3), (3, 12), (12, 12)):
            g.set(x, y, "E")
            g.set(x, y + 1, "D")
    elif kind == "maintenance_tread":
        # Repeating short raised diagonals, no clustered noise or grime patches.
        for y in (1, 9):
            for x in (1, 9):
                for step in range(3):
                    g.set(x + step, y + step, "E")
                    g.set(x + step, y + step + 1, "D")
                    g.set(x + 4 + step, y + 3 - step, "E")
                    g.set(x + 4 + step, y + 4 - step, "D")
    elif kind == "decontamination_ceramic":
        g.vline(7, 0, 15, "D")
        g.hline(7, 0, 15, "D")
        g.hline(6, 0, 15, "B")
    else:
        raise ValueError(f"unknown floor kind: {kind}")
    return g


def rbmk_solid(kind: str, seed: int) -> Grid:
    """Opaque full cubes: quiet 1px grain under distinct industrial structures."""
    g = Grid("A")
    g.grain("B", "C", seed, 0.18, 0.18)
    if kind == "upper_bio_shield":
        for x in (3, 11):
            g.vline(x, 0, 15, "E")
            for y in (4, 12):
                g.stamp(x - 2, y - 2, DISC, {"D": "D", "C": "A", "B": "F"})
    elif kind == "lower_bio_shield":
        g.rect(6, 0, 4, 16, "E")
        g.rect(0, 6, 16, 4, "E")
        g.vline(6, 0, 15, "F")
        g.hline(6, 0, 15, "F")
        g.grit("D", [(7, 3), (3, 7), (12, 7), (7, 12)])
    elif kind == "serpentinite_shield":
        g.grit("D", [(2, 3), (10, 4), (6, 9), (13, 13), (4, 14)])
        g.grit("E", [(5, 2), (12, 7), (3, 11), (9, 14)])
    elif kind == "borated_concrete":
        g.grit("D", [(1, 6), (7, 3), (12, 10), (5, 13)])
        g.grit("E", [(4, 4), (10, 1), (14, 6), (8, 11), (2, 14)])
    elif kind == "lead_brick":
        for y, x in ((3, 4), (11, 12)):
            g.hline(y, 0, 15, "D")
            g.hline(y + 1, 0, 15, "E")
            for yy in range(y - 7, y):
                g.set(x, yy % N, "D")
    elif kind == "laminated_shield":
        for y in (3, 11):
            g.hline(y, 0, 15, "D")
            g.hline(y + 1, 0, 15, "E")
            g.hline(y + 2, 0, 15, "F")
        g.grit("D", [(3, 8), (12, 8)])
    elif kind == "support_steel":
        for x in (3, 10):
            g.rect(x, 0, 3, 16, "E")
            g.vline(x, 0, 15, "F")
            g.vline(x + 2, 0, 15, "D")
        g.hline(8, 0, 15, "E")
        g.grit("D", [(4, 4), (11, 12)])
    elif kind == "support_base":
        g.frame(2, 2, 12, 12, "E")
        g.rect(5, 5, 6, 6, "E")
        g.hline(5, 5, 10, "F")
        for x, y in ((3, 3), (12, 3), (3, 12), (12, 12)):
            g.rect(x, y, 2, 2, "D")
            g.set(x, y, "F")
    elif kind == "refuelling_rail":
        for y in (4, 12):
            g.hline(y, 0, 15, "E")
        for x in (3, 11):
            g.rect(x, 0, 3, 16, "D")
            g.vline(x + 1, 0, 15, "F")
            g.vline(x + 2, 0, 15, "E")
    elif kind == "crane_girder":
        for y in (3, 11):
            g.rect(0, y, 16, 2, "E")
            g.hline(y, 0, 15, "F")
        for x in range(4, 12):
            g.set(x, x - 1, "D")
        g.grit("D", [(2, 4), (13, 4), (2, 12), (13, 12)])
    else:
        raise ValueError(f"unknown RBMK solid kind: {kind}")
    return g


# --------------------------------------------------------------------------
# 薄板：四边对称斜角边框 + 8x8 内区（R3）
# --------------------------------------------------------------------------
def bevel_frame(g: Grid, tones: list[str], band: int) -> None:
    for i in range(band):
        g.hline(i, 0, 15, tones[i])
        g.hline(15 - i, 0, 15, tones[i])
    for y in range(band, 16 - band):
        for i in range(band):
            g.set(i, y, tones[i])
            g.set(15 - i, y, tones[i])


def trefoil(g: Grid, x0: int, y0: int, ch: str) -> None:
    """8x8 辐射三叶符：中心圆盘 + 三片叶（一片朝上、两片朝下），叶间空隙 30°/150°/270°。

    8x8 太小，逐像素判圆会让叶片断开，所以每个像素做 8x8 超采样，覆盖率 >= 0.4 才点亮。
    朝向选“一叶朝上”：另一种朝向（一叶朝下）在 8x8 下会读成一张脸。
    """
    sub = 8
    for dy in range(8):
        for dx in range(8):
            hit = 0
            for sy in range(sub):
                for sx in range(sub):
                    vx = dx + (sx + 0.5) / sub - 4.0
                    vy = -(dy + (sy + 0.5) / sub - 4.0)
                    d = math.hypot(vx, vy)
                    if d <= 1.0:
                        hit += 1
                    elif 1.8 <= d <= 4.0:
                        ang = math.degrees(math.atan2(vy, vx)) % 360
                        if not any(abs((ang - gap + 180) % 360 - 180) < 20 for gap in (30, 150, 270)):
                            hit += 1
            if hit / (sub * sub) >= 0.4:
                g.set(x0 + dx, y0 + dy, ch)


def plate(kind: str) -> Grid:
    """色位：A 面 / B 高光 / C 中间 / D 暗部 / E 边框主体 / F 边框外沿暗 / G 边框内沿亮。"""
    g = Grid("A")
    band = 4
    x0 = y0 = band
    x1 = y1 = 15 - band

    if kind == "ceiling":
        # 吊顶板：平整内区 + 对角两枚螺丝。
        for sx, sy in [(x0, y0), (x1 - 1, y1 - 1)]:
            g.rect(sx, sy, 2, 2, "D")
            g.set(sx, sy, "B")
    elif kind == "tray":
        # 电缆桥架：边框即两侧纵梁，内区是两根横档，档间透空（R5）。
        g.rect(x0, y0, 8, 8, ".")
        for y in (y0 + 1, y0 + 5):
            g.hline(y, x0, x1, "E")
            g.hline(y + 1, x0, x1, "C")
    elif kind == "vent":
        # 通风百叶：每片 = 受光亮线 + 暗缝。
        for y in range(y0, y1 + 1, 2):
            g.hline(y, x0, x1, "B")
            g.hline(y + 1, x0, x1, "D")
    elif kind == "trefoil":
        # 辐射标识板：黄底 + 三叶符。
        trefoil(g, x0, y0, "D")
    elif kind == "cover":
        # 通道盖板：金属面 + 居中的 6x6 圆盖。
        g.stamp(x0 + 1, y0 + 1, DISC, {"D": "D", "C": "C", "B": "B"})
    elif kind == "slot":
        # 薄荷控制面板：一条居中的暗槽 + 下沿受光线。
        g.hline(y0 + 3, x0 + 1, x1 - 1, "D")
        g.hline(y0 + 4, x0 + 1, x1 - 1, "B")
    elif kind == "cladding":
        # 保温覆层：中央横向搭接缝，四周仍留给统一的断面边框。
        g.grain("B", "C", 89, 0.12, 0.12)
        g.hline(y0 + 3, x0, x1, "D")
        g.hline(y0 + 4, x0, x1, "B")
    elif kind == "white_slot":
        # 白面板：内区短竖槽，与满格涂白内衬的贯通板缝区分。
        g.grain("B", "C", 97, 0.10, 0.10)
        g.vline(x0 + 3, y0 + 1, y1 - 1, "D")
    elif kind == "cc_ceiling":
        g.grain("B", "C", 137, 0.10, 0.10)
        g.hline(y0 + 3, x0, x1, "D")
        g.grit("D", [(5, 5), (9, 5), (5, 9), (9, 9)])
    elif kind == "office_ceiling":
        g.grain("B", "C", 139, 0.18, 0.18)
        g.vline(x0 + 3, y0, y1, "D")
        g.grit("C", [(5, 5), (9, 6), (6, 9), (10, 10)])
    elif kind == "diffuser":
        # The palette alone sets neutral white versus warm office white.
        g.grain("B", "C", 149, 0.08, 0.08)
    else:
        raise ValueError(f"unknown plate kind: {kind}")

    bevel_frame(g, ["F", "E", "E", "G"], band)
    return g


def plate_palette(face: str, hi: str, lo: str, deep: str,
                  housing: str, hdark: str, hlight: str) -> dict:
    return {"A": face, "B": hi, "C": lo, "D": deep,
            "E": housing, "F": hdark, "G": hlight}


def speck() -> Grid:
    """破坏粒子：中央 4x4 碎屑，其余透明（R7，思路同原版 redstone_dust_dot）。"""
    g = Grid(".")
    for y, row in enumerate(["AABB", "ABBC", "BBCC", "CCCC"]):
        for x, c in enumerate(row):
            g.set(6 + x, 6 + y, c)
    return g


# --------------------------------------------------------------------------
# 组装 spec
# --------------------------------------------------------------------------
def build_spec() -> dict:
    spec: dict = {}

    def add(name: str, palette: dict, g: Grid) -> None:
        spec[name] = {"palette": palette, "rows": g.rows()}

    # ===== 共用厂房 plant_ =====
    add("plant_concrete",
        {"A": "#8d8f91", "B": "#909294", "C": "#8a8c8e", "D": "#747678", "E": "#7f8183"},
        solid("formwork", seed=11))
    add("plant_concrete_painted",
        {"A": "#b3b5b7", "B": "#b6b8ba", "C": "#b0b2b4", "D": "#9fa1a3", "E": "#c2c4c6"},
        solid("painted", seed=23))
    add("plant_lead",
        {"A": "#586470", "B": "#626e7a", "C": "#4f5964", "D": "#3d454e"},
        solid("lead", seed=37))
    add("plant_hazard",
        {"Y": "#e0b01f", "K": "#1d1e20"},
        solid("hazard"))
    add("plant_grating",
        {"A": "#6b7279", "B": "#8b9299", "D": "#33393f"},
        solid("grate"))
    add("plant_epoxy",
        {"A": "#76847a", "B": "#808f85", "C": "#727f76", "D": "#6c786f"},
        solid("epoxy", seed=61))

    add("plant_ceiling",
        plate_palette("#dcdedf", "#eff0f1", "#c3c6c8", "#a6aaad", "#c3c6c8", "#a6aaad", "#eff0f1"),
        plate("ceiling"))
    add("plant_tray",
        plate_palette("#8d9399", "#b9bec3", "#7a8087", "#5a6066", "#9aa0a6", "#6c7278", "#b9bec3"),
        plate("tray"))
    add("plant_vent",
        plate_palette("#c3c6c9", "#dfe1e3", "#a2a6aa", "#7a7f84", "#b8bbbe", "#8b9095", "#e6e8ea"),
        plate("vent"))
    add("plant_trefoil",
        plate_palette("#e0b01f", "#f0c93a", "#c89a18", "#b0307a", "#c89a18", "#8a6c12", "#f0c93a"),
        plate("trefoil"))

    # ===== RBMK rbmk_ =====
    add("rbmk_shield",
        {"A": "#6a665f", "B": "#6d6962", "C": "#67635c", "D": "#575450",
         "E": "#7a766f", "F": "#5e5a54"},
        solid("shield", seed=41))
    add("rbmk_graphite",
        {"A": "#252320", "B": "#2a2824", "C": "#211f1c", "D": "#151412",
         "E": "#4a463c", "F": "#312e29"},
        solid("graphite", seed=53))
    add("rbmk_steel_green",
        {"A": "#65756a", "B": "#6a7a6f", "C": "#607065", "D": "#46524a", "E": "#76867b"},
        solid("steel_green", seed=67))
    add("rbmk_channel",
        {"A": "#767c82", "B": "#7b8187", "C": "#70767c", "D": "#4a5056",
         "E": "#5f656b", "F": "#9aa0a6"},
        solid("channel", seed=71))

    add("rbmk_channel_cover",
        plate_palette("#70767c", "#9aa0a6", "#5f656b", "#4a5056", "#6a7076", "#4a5056", "#8f959b"),
        plate("cover"))
    add("rbmk_panel_mint",
        plate_palette("#a8c3b3", "#bdd5c7", "#8fac9a", "#6c8a77", "#8fac9a", "#6c8a77", "#bdd5c7"),
        plate("slot"))

    add("rbmk_upper_bio_shield",
        {"A": "#7a8285", "B": "#7d8588", "C": "#777f82", "D": "#4b5559",
         "E": "#687477", "F": "#9ba5a6"},
        rbmk_solid("upper_bio_shield", seed=173))
    add("rbmk_lower_bio_shield",
        {"A": "#6b7475", "B": "#6e7778", "C": "#687172", "D": "#424c4d",
         "E": "#566463", "F": "#8b9895"},
        rbmk_solid("lower_bio_shield", seed=179))
    add("rbmk_serpentinite_shield",
        {"A": "#525e56", "B": "#556159", "C": "#4f5b53", "D": "#48534c", "E": "#606b60"},
        rbmk_solid("serpentinite_shield", seed=181))
    add("rbmk_borated_concrete",
        {"A": "#898477", "B": "#8c877a", "C": "#868174", "D": "#7e796d", "E": "#938e80"},
        rbmk_solid("borated_concrete", seed=191))
    add("rbmk_lead_brick",
        {"A": "#586574", "B": "#5b6877", "C": "#556271", "D": "#424e5d", "E": "#6a7684"},
        rbmk_solid("lead_brick", seed=193))
    add("rbmk_laminated_shield",
        {"A": "#7f8585", "B": "#828888", "C": "#7c8282", "D": "#535e66",
         "E": "#918b7d", "F": "#a3acab"},
        rbmk_solid("laminated_shield", seed=197))
    add("rbmk_support_steel",
        {"A": "#65796e", "B": "#687c71", "C": "#62766b", "D": "#3e5349",
         "E": "#53695e", "F": "#859a8e"},
        rbmk_solid("support_steel", seed=199))
    add("rbmk_support_base",
        {"A": "#777d7d", "B": "#7a8080", "C": "#747a7a", "D": "#4b5355",
         "E": "#657071", "F": "#99a3a1"},
        rbmk_solid("support_base", seed=211))
    add("rbmk_refuelling_rail",
        {"A": "#6d777b", "B": "#707a7e", "C": "#6a7478", "D": "#465357",
         "E": "#818d90", "F": "#a9b3b4"},
        rbmk_solid("refuelling_rail", seed=223))
    add("rbmk_crane_girder",
        {"A": "#718175", "B": "#748478", "C": "#6e7e72", "D": "#4b5b50",
         "E": "#5c7062", "F": "#92a18f"},
        rbmk_solid("crane_girder", seed=227))

    # ===== PWR pwr_ =====
    add("pwr_containment",
        {"A": "#969ea6", "B": "#99a1a9", "C": "#939ba3", "D": "#8c949c"},
        solid("containment", seed=79))
    add("pwr_liner",
        {"A": "#b2bdc5", "B": "#b5c0c8", "C": "#afbac2", "D": "#a4afb7", "E": "#b9c4cc"},
        solid("liner", seed=83))
    add("pwr_liner_white",
        {"A": "#deded6", "B": "#e1e1d9", "C": "#dbdbd3", "D": "#d3d3cb"},
        solid("liner_white", seed=87))
    add("pwr_deck",
        {"A": "#687d8e", "B": "#6b8091", "C": "#657a8b", "D": "#4f6272", "E": "#7a8d9c"},
        solid("deck", seed=91))
    add("pwr_cladding",
        plate_palette("#b9c1c6", "#bcc4c9", "#b6bec3", "#a6aeb3", "#aeb6bb", "#949ca1", "#c9d1d6"),
        plate("cladding"))
    add("pwr_panel_white",
        plate_palette("#e4e5e1", "#e7e8e4", "#e1e2de", "#c3c6c4", "#cfd2cf", "#afb4b1", "#eff0ec"),
        plate("white_slot"))

    # ===== Control room cc_: neutral whites, subdued greys =====
    add("cc_wall_white",
        {"A": "#e3e3e3", "B": "#e6e6e6", "C": "#e0e0e0", "D": "#d7d7d7", "E": "#e7e7e7"},
        solid("cc_white", seed=101))
    add("cc_wall_grey",
        {"A": "#b5b7b8", "B": "#b8babb", "C": "#b2b4b5", "D": "#9fa1a2", "E": "#abadae"},
        solid("acoustic", seed=103))
    add("cc_wall_console",
        {"A": "#45494c", "B": "#484c4f", "C": "#424649", "D": "#383c3f",
         "E": "#565a5d", "F": "#739b82", "G": "#b29b69"},
        solid("console", seed=107))
    add("cc_floor_dark",
        {"A": "#55585c", "B": "#585b5f", "C": "#525559", "D": "#4d5054", "E": "#494c50"},
        solid("antistatic", seed=109))
    add("cc_floor_light",
        {"A": "#bfc2c4", "B": "#c2c5c7", "C": "#bcbfc1", "D": "#b7babc", "E": "#b3b6b8"},
        solid("antistatic", seed=113))
    # Every tone, including the housing, is RGB-neutral for both cc_ lamps.
    add("cc_light_white",
        {"A": "#fcfcfc", "B": "#ffffff", "C": "#f9f9f9", "D": "#f6f6f6"},
        solid("white_light", seed=127))
    add("cc_light_white_panel",
        plate_palette("#fcfcfc", "#ffffff", "#f9f9f9", "#eeeeee", "#e4e4e4", "#d6d6d6", "#f3f3f3"),
        plate("diffuser"))
    add("cc_ceiling",
        plate_palette("#e4e5e5", "#e7e8e8", "#e1e2e2", "#d0d1d1", "#d9dada", "#c6c7c7", "#eff0f0"),
        plate("cc_ceiling"))

    # ===== Engineer office eo_: beige, fine veneer, soft blue-grey =====
    add("eo_wall_beige",
        {"A": "#e2dfd5", "B": "#e5e2d8", "C": "#dfdcd2", "D": "#dedbd1"},
        solid("beige", seed=151))
    add("eo_wall_wood",
        {"A": "#c7b89e", "B": "#cabba1", "C": "#c4b59b", "D": "#bbac92",
         "E": "#c1b298", "F": "#cdbea4"},
        solid("office_wood", seed=157))
    add("eo_floor_carpet",
        {"A": "#87949e", "B": "#8a97a1", "C": "#84919b", "D": "#83909a"},
        solid("carpet", seed=163))
    add("eo_floor_tile",
        {"A": "#d2d3cf", "B": "#d5d6d2", "C": "#cfd0cc", "D": "#c8c9c5"},
        solid("office_tile", seed=167))
    add("eo_ceiling",
        plate_palette("#e6e4dd", "#e9e7e0", "#e3e1da", "#d6d4cd", "#dcdad3", "#cac8c1", "#f0eee7"),
        plate("office_ceiling"))
    add("eo_light_panel",
        plate_palette("#fcf5e5", "#fff8e8", "#f9f2e2", "#ece5d5", "#e4e0d6", "#d4d0c6", "#f3efe5"),
        plate("diffuser"))

    add("floor_heavy_load",
        {"A": "#737b80", "B": "#767e83", "C": "#70787d", "D": "#596268", "E": "#879196", "F": "#626c72"},
        floor_solid("heavy_load", seed=229))
    add("floor_turbine_hall",
        {"A": "#6b7f8d", "B": "#6e8290", "C": "#687c8a", "D": "#596d7b", "E": "#8294a0"},
        floor_solid("turbine_hall", seed=233))
    add("floor_equipment_room",
        {"A": "#b5bdc0", "B": "#b8c0c3", "C": "#b2babd", "D": "#9ca6ab", "E": "#869298", "F": "#6f8f9e"},
        floor_solid("equipment_room", seed=239))
    add("floor_maintenance_tread",
        {"A": "#858c90", "B": "#888f93", "C": "#82898d", "D": "#737c81", "E": "#9aa3a8"},
        floor_solid("maintenance_tread", seed=241))
    add("floor_decontamination_ceramic",
        {"A": "#c5d9d7", "B": "#c8dcda", "C": "#c2d6d4", "D": "#b1c5c3"},
        floor_solid("decontamination_ceramic", seed=251))

    # ===== 破坏粒子 =====
    add("particle_chip",
        {"A": "#cfcfcc", "B": "#9a9a97", "C": "#6b6b68"},
        speck())

    return spec


def main() -> None:
    spec = build_spec()
    SPEC_PATH.write_text(json.dumps(spec, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"spec -> {SPEC_PATH} ({len(spec)} textures)")
    if "--ascii" in sys.argv:
        for name, entry in spec.items():
            print(f"\n== {name}")
            for row in entry["rows"]:
                print("  " + row)


if __name__ == "__main__":
    main()
