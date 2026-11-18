#!/usr/bin/env python3
"""贴图重绘管线：16x16 字符矩阵 -> Blockbench 渲染 -> 写回仓库 PNG。

用法：
    # 1) 生成需要发送给 Blockbench MCP 的 payload（矩阵 + 调色板）
    python3 tools/texture_pipeline.py build <spec.json> <payload.json>

    # 2) 校验仓库里的 PNG 是否与 spec 一致（渲染后自检）
    python3 tools/texture_pipeline.py verify <spec.json>

    # 3) 体检现有贴图：列出边框硬边、噪声、缺色层等问题
    python3 tools/texture_pipeline.py audit [texdir]

    # 4) 接缝对比度检测：平铺后边界是否出现贯穿的亮线/暗线
    python3 tools/texture_pipeline.py seams [texdir]

spec.json 结构：
{
  "wall_concrete_polished_white": {
    "palette": {"A": "#e8e6e0", "B": "#d6d4ce", ...},
    "rows": [
      "AAAAAAAAAAAAAAA",
      ...共 16 行，每行 16 个字符...
    ]
  }
}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from npp_blocks import ATLAS_SIZES, MOD_ID, parse_blocks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEX_DIR = ROOT / f"src/main/resources/assets/{MOD_ID}/textures/block"


def atlas_names() -> set[str]:
    """Independent model atlases are audited by audit_assets.py, outside the 16x16 spec."""
    return set(ATLAS_SIZES)


def check_atlas_sizes(tex_dir: Path) -> int:
    """Only the explicit six atlas ids may bypass the 16px texture checks."""
    from PIL import Image

    failures = 0
    for name, size in ATLAS_SIZES.items():
        path = tex_dir / f"{name}.png"
        if not path.exists():
            print(f"FAIL atlas {name}: file missing")
            failures += 1
            continue
        with Image.open(path) as image:
            if image.size != size:
                print(f"FAIL atlas {name}: size {image.size}, expected {size}")
                failures += 1
    return failures


def spec_texture_files(tex_dir: Path) -> list[Path]:
    return [path for path in sorted(tex_dir.glob("*.png")) if path.stem not in atlas_names()]


def panel_names() -> set[str]:
    """薄板贴图（四边斜角边框，不平铺）：直接取自 ModBlocks.java 的 panel(...) 注册。"""
    return {b["id"] for b in parse_blocks() if b["kind"] == "panel"}


# --------------------------------------------------------------------------
# 矩阵 -> 像素
# --------------------------------------------------------------------------
def parse_color(value: str) -> tuple[int, int, int, int]:
    """'#rrggbb' -> (r,g,b,255)；支持 '#rrggbbaa'。"""
    v = value.lstrip("#")
    if len(v) == 6:
        r, g, b = (int(v[i:i + 2], 16) for i in (0, 2, 4))
        return r, g, b, 255
    if len(v) == 8:
        r, g, b, a = (int(v[i:i + 2], 16) for i in (0, 2, 4, 6))
        return r, g, b, a
    raise ValueError(f"bad color: {value!r}")


def matrix_to_pixels(spec: dict) -> list[list[tuple[int, int, int, int]]]:
    """把 16x16 字符矩阵展开成 RGBA 像素网格。'.' 表示透明。"""
    palette = {k: parse_color(v) for k, v in spec["palette"].items()}
    rows = spec["rows"]
    if len(rows) != 16:
        raise ValueError(f"expected 16 rows, got {len(rows)}")
    grid = []
    for row in rows:
        if len(row) != 16:
            raise ValueError(f"expected 16 chars, got {len(row)!r}")
        grid.append([
            (0, 0, 0, 0) if ch == "." else palette[ch] for ch in row
        ])
    return grid


# --------------------------------------------------------------------------
# build: 生成 Blockbench payload
# --------------------------------------------------------------------------
def cmd_build(spec_path: Path, out_path: Path) -> None:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    payload = {}
    for name, entry in spec.items():
        grid = matrix_to_pixels(entry)
        # 扁平化成 RGBA 字节序列，供 Blockbench 侧直接灌 ImageData
        flat = []
        for row in grid:
            for px in row:
                flat.extend(px)
        payload[name] = {
            "width": 16,
            "height": 16,
            "rgba": flat,
        }
    out_path.write_text(json.dumps(payload), encoding="utf-8")
    print(f"payload -> {out_path}  ({len(payload)} textures)")


# --------------------------------------------------------------------------
# verify: 校验磁盘 PNG 与 spec 是否一致
# --------------------------------------------------------------------------
def cmd_verify(spec_path: Path) -> int:
    from PIL import Image

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    failures = check_atlas_sizes(TEX_DIR)
    if len(spec) != 52:
        print(f"FAIL spec count: expected 52, got {len(spec)}")
        failures += 1
    expected = {path.stem for path in spec_texture_files(TEX_DIR)}
    if set(spec) != expected:
        print(f"FAIL spec coverage: missing={sorted(expected - set(spec))}, extra={sorted(set(spec) - expected)}")
        failures += 1
    for name, entry in spec.items():
        path = TEX_DIR / f"{name}.png"
        if not path.exists():
            print(f"FAIL {name}: file missing")
            failures += 1
            continue
        expect = matrix_to_pixels(entry)
        img = Image.open(path).convert("RGBA")
        if img.size != (16, 16):
            print(f"FAIL {name}: size {img.size}")
            failures += 1
            continue
        bad = 0
        for y in range(16):
            for x in range(16):
                if img.getpixel((x, y)) != expect[y][x]:
                    bad += 1
        if bad:
            print(f"FAIL {name}: {bad}/256 pixels differ")
            failures += 1
        else:
            print(f"ok   {name}")
    print(f"\n{len(spec) - failures}/{len(spec)} match")
    return 1 if failures else 0


# --------------------------------------------------------------------------
# audit: 体检现有贴图
# --------------------------------------------------------------------------
def cmd_audit(tex_dir: Path) -> int:
    from PIL import Image

    # 薄板类：四边都有设计好的斜角边框（外暗 -> 本色 -> 亮，见 texture_spec.bevel_frame），
    # 本来就不像整方块那样平铺，因此整体豁免硬边判定。
    # particle_chip 是破坏粒子小碎屑，本来就是透明底上的一个色块。
    NOT_TILED = {"particle_chip", *panel_names()}

    def col_profile(img, x):
        return [img.getpixel((x, y)) for y in range(16)]

    def row_profile(img, y):
        return [img.getpixel((x, y)) for x in range(16)]

    def is_periodic(profile, others):
        """边缘整列/整行单色时，若与某个内部等距位置完全一致，说明图案本身是
        周期的（例：钢格栅每 4px 一循环），平铺后接缝连续，不算硬边。"""
        return any(profile == o for o in others)

    print(f"{'texture':30} {'colors':>6} {'lumSpan':>8} {'border':>7}  verdict")
    print("-" * 72)
    files = spec_texture_files(tex_dir)
    failures = check_atlas_sizes(tex_dir)
    for path in files:
        img = Image.open(path).convert("RGBA")
        if img.size != (16, 16):
            print(f"FAIL {path.stem}: size {img.size}")
            failures += 1
            continue
        px = list(img.get_flattened_data())
        opaque = [p for p in px if p[3] > 8]
        if not opaque:
            print(f"{path.stem:30} {'-':>6} {'-':>8} {'-':>7}  EMPTY")
            failures += 1
            continue
        uniq = len(set(opaque))
        lums = [0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2] for p in opaque]
        span = max(lums) - min(lums)

        # 边框硬边判定（R2）：
        # 只有当"整行/整列单色"且该颜色与内部主色明显不同时，才是真硬边。
        # 边缘本来就是本色（如混凝土大面本色）属于正常可平铺结构。
        from collections import Counter
        interior = [img.getpixel((x, y)) for y in range(1, 15) for x in range(1, 15)]
        dominant = Counter(interior).most_common(1)[0][0]
        dom_lum = 0.2126 * dominant[0] + 0.7152 * dominant[1] + 0.0722 * dominant[2]

        # 从不平铺的贴图整体豁免（薄板/窗框/粒子碎片）
        skip_all = path.stem in NOT_TILED

        edges = []
        if not skip_all:
            edge_defs = [
                ("row0", row_profile(img, 0)),
                ("row15", row_profile(img, 15)),
                ("col0", col_profile(img, 0)),
                ("col15", col_profile(img, 15)),
            ]
            for label, prof in edge_defs:
                if len(set(prof)) != 1:
                    continue
                edge_rgb = list(prof)[0]
                edge_lum = (0.2126 * edge_rgb[0] + 0.7152 * edge_rgb[1]
                            + 0.0722 * edge_rgb[2])
                if abs(edge_lum - dom_lum) <= 12:
                    continue
                # 周期性格栅等：边缘与内部等距位置完全一致 -> 平铺接缝连续
                if label.startswith("row"):
                    others = [row_profile(img, y) for y in (4, 8, 12)]
                else:
                    others = [col_profile(img, x) for x in (4, 8, 12)]
                if is_periodic(prof, others):
                    continue
                edges.append(label)

        issues = []
        if uniq >= 8 and span < 60:
            issues.append("NOISE")
        if edges:
            issues.append("HARD-EDGE")
        # FLAT 只在色少且亮度跨度也小的时候才是问题；
        # 高对比纯几何（警示条黄黑、纯白灯面）色少是正常的。
        if uniq <= 3 and span < 30:
            issues.append("FLAT")
        verdict = " ".join(issues) if issues else "ok"
        failures += bool(issues)
        print(f"{path.stem:30} {uniq:>6} {span:>8.1f} {','.join(edges) or '-':>7}  {verdict}")
    return 1 if failures or not files else 0


def cmd_seams(tex_dir: Path) -> int:
    """接缝对比度检测（R2 的量化版）。

    平铺后，方块边界两侧的像素差（接缝差）如果明显大于贴图内部相邻像素差，
    就会在游戏里表现为一条贯穿地面的亮线/暗线。
    判定：接缝差 <= 内部最大相邻差 + 2 视为连续。
    """
    from PIL import Image

    def lum(p):
        return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]

    NOT_TILED = {"particle_chip", *panel_names()}

    print(f"{'texture':30} {'seamMax':>8} {'innerMax':>9}  verdict")
    print("-" * 66)
    files = spec_texture_files(tex_dir)
    failures = check_atlas_sizes(tex_dir)
    for path in files:
        if path.stem in NOT_TILED:
            continue
        img = Image.open(path).convert("RGBA")
        if img.size != (16, 16):
            print(f"FAIL {path.stem}: size {img.size}")
            failures += 1
            continue
        seam = []
        inner = []
        for y in range(16):
            a, b = img.getpixel((15, y)), img.getpixel((0, y))
            if a[3] > 8 and b[3] > 8:
                seam.append(abs(lum(a) - lum(b)))
            for x in range(15):
                p, q = img.getpixel((x, y)), img.getpixel((x + 1, y))
                if p[3] > 8 and q[3] > 8:
                    inner.append(abs(lum(p) - lum(q)))
        for x in range(16):
            a, b = img.getpixel((x, 15)), img.getpixel((x, 0))
            if a[3] > 8 and b[3] > 8:
                seam.append(abs(lum(a) - lum(b)))
            for y in range(15):
                p, q = img.getpixel((x, y)), img.getpixel((x, y + 1))
                if p[3] > 8 and q[3] > 8:
                    inner.append(abs(lum(p) - lum(q)))
        if not seam or not inner:
            print(f"{path.stem:30} {'-':>8} {'-':>9}  skip")
            continue
        s_max, i_max = max(seam), max(inner)
        verdict = "接缝连续" if s_max <= i_max + 2 else "接缝跳变"
        failures += s_max > i_max + 2
        print(f"{path.stem:30} {s_max:>8.1f} {i_max:>9.1f}  {verdict}")
    return 1 if failures or not files else 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "build":
        if len(sys.argv) != 4:
            print("usage: texture_pipeline.py build <spec.json> <payload.json>")
            return 1
        cmd_build(Path(sys.argv[2]), Path(sys.argv[3]))
        return 0
    if cmd == "verify":
        if len(sys.argv) != 3:
            print("usage: texture_pipeline.py verify <spec.json>")
            return 1
        return cmd_verify(Path(sys.argv[2]))
    if cmd == "audit":
        target = Path(sys.argv[2]) if len(sys.argv) > 2 else TEX_DIR
        return cmd_audit(target)
    if cmd == "seams":
        target = Path(sys.argv[2]) if len(sys.argv) > 2 else TEX_DIR
        return cmd_seams(target)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
