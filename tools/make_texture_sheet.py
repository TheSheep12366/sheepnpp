#!/usr/bin/env python3
"""Build per-family contact sheets of the mod's block textures for visual review.

Usage: python3 tools/make_texture_sheet.py <out.png> <group|all> [zoom] [texdir]
Groups: plant, rbmk, pwr, cc, eo, all；其他字符串按名称子串匹配

可选第 4 个参数 texdir：指定贴图目录。用于把"改动前"的旧贴图目录也拼成
同规格印样表，配合 GLM Vision 做 before/after 对比。
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TEX_DIR = ROOT / "src/main/resources/assets/sheepnpp/textures/block"

GROUPS = {
    "plant": ["plant_", "particle_"],
    "rbmk": ["rbmk_"],
    "pwr": ["pwr_"],
    "cc": ["cc_"],
    "eo": ["eo_"],
}


def pick(group: str, tex_dir: Path) -> list[Path]:
    files = sorted(tex_dir.glob("*.png"))
    if group == "all":
        return files
    prefixes = GROUPS.get(group)
    if prefixes is None:
        return [f for f in files if group in f.stem]
    return [f for f in files if any(f.stem.startswith(p) for p in prefixes)]


def main() -> None:
    out = Path(sys.argv[1])
    group = sys.argv[2] if len(sys.argv) > 2 else "all"
    zoom = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    tex_dir = Path(sys.argv[4]) if len(sys.argv) > 4 else TEX_DIR
    files = pick(group, tex_dir)
    cols = max(1, min(4, len(files)))
    cell = 16 * zoom
    label_h = 18
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (cell + 4), rows * (cell + label_h + 4)), (18, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        img = Image.open(f).convert("RGBA").resize((cell, cell), Image.NEAREST)
        bg = Image.new("RGBA", (cell, cell), (96, 96, 102, 255))
        bg.alpha_composite(img)
        x = (i % cols) * (cell + 4)
        y = (i // cols) * (cell + label_h + 4)
        sheet.paste(bg.convert("RGB"), (x, y))
        draw.text((x + 2, y + cell + 2), f.stem, fill=(225, 225, 230))
    sheet.save(out)
    print(f"{out} {sheet.size} n={len(files)}")


if __name__ == "__main__":
    main()
