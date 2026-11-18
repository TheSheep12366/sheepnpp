#!/usr/bin/env python3
"""生成平铺预览图：把同一张贴图按 NxN 平铺，用于检查接缝是否突兀。

用法: python3 tools/texture_tilesheet.py <out.png> <texture_name> [nx] [ny] [zoom]
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEX_DIR = ROOT / "src/main/resources/assets/sheepnpp/textures/block"


def main() -> None:
    out = Path(sys.argv[1])
    name = sys.argv[2]
    nx = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    ny = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    zoom = int(sys.argv[5]) if len(sys.argv) > 5 else 8

    img = Image.open(TEX_DIR / f"{name}.png").convert("RGBA")
    cell = img.width * zoom
    # 细密棋盘底衬：透空贴图的孔洞能显出来，同时底衬自身的明暗块足够小，
    # 不会被误读成"方块之间的接缝"（早先用整格大小的底衬会让评审误判）。
    sq = max(2, cell // 16)
    sheet = Image.new("RGB", (nx * cell, ny * cell))
    for y in range(ny):
        for x in range(nx):
            bg = Image.new("RGBA", (cell, cell), (140, 140, 146, 255))
            for by in range(0, cell, sq):
                for bx in range(0, cell, sq):
                    if ((bx // sq) + (by // sq)) % 2 == 0:
                        continue
                    for yy in range(by, min(by + sq, cell)):
                        for xx in range(bx, min(bx + sq, cell)):
                            bg.putpixel((xx, yy), (112, 112, 118, 255))
            tile = img.resize((cell, cell), Image.NEAREST)
            bg.alpha_composite(tile)
            sheet.paste(bg.convert("RGB"), (x * cell, y * cell))
    sheet.save(out)
    print(f"{out} {sheet.size} {name} {nx}x{ny}")


if __name__ == "__main__":
    main()
