#!/usr/bin/env python3
"""从 ModBlocks.java 生成方块标签。

  python3 tools/gen_tags.py          写入 src/main/resources/data/...
  python3 tools/gen_tags.py --check  只比对磁盘，不一致则退出码 1

生成：
  minecraft:mineable/pickaxe、mineable/axe
  minecraft:needs_stone_tool / needs_iron_tool / needs_diamond_tool
  hbm:radiation_resistant        NTM-Continuum 把这个标签里的方块当辐射密封墙；只放满格
"""
import json
import sys

from npp_blocks import MOD_ID, ROOT, parse_blocks, parse_surfaces, parse_tiers

DATA = ROOT / "src/main/resources/data"


def build():
    tiers = parse_tiers()
    surfaces = parse_surfaces()
    blocks = parse_blocks()

    tags = {
        "minecraft/tags/blocks/mineable/pickaxe.json": [],
        "minecraft/tags/blocks/mineable/axe.json": [],
        "minecraft/tags/blocks/needs_stone_tool.json": [],
        "minecraft/tags/blocks/needs_iron_tool.json": [],
        "minecraft/tags/blocks/needs_diamond_tool.json": [],
        "hbm/tags/blocks/radiation_resistant.json": [],
    }
    blast_tiers = {"large_explosion": 70, "nuclear": 200, "obsidian": 1200}
    for kind in ("blocks", "items"):
        for tag in ("blast_resistant", *(f"blast_resistant/{t}" for t in blast_tiers)):
            tags[f"hbm/tags/{kind}/{tag}.json"] = []
    for b in blocks:
        name = f"{MOD_ID}:{b['id']}"
        tool, _ = surfaces[b["surface"]]
        if tool in ("pickaxe", "axe"):
            tags[f"minecraft/tags/blocks/mineable/{tool}.json"].append(name)
        if tool == "pickaxe":
            tool_tier = tiers[b["tier"]][2]
            if tool_tier != "none":
                tags[f"minecraft/tags/blocks/needs_{tool_tier}_tool.json"].append(name)
        if b["rad"]:
            tags["hbm/tags/blocks/radiation_resistant.json"].append(name)
        resistance = tiers[b["tier"]][1]
        for kind in ("blocks", "items"):
            for tier, threshold in blast_tiers.items():
                if resistance >= threshold:
                    tags[f"hbm/tags/{kind}/blast_resistant/{tier}.json"].append(name)
            if resistance >= 70:
                tags[f"hbm/tags/{kind}/blast_resistant.json"].append(name)

    return {path: {"replace": False, "values": sorted(values)} for path, values in tags.items()}


def main():
    check = "--check" in sys.argv
    stale = []
    for rel, content in build().items():
        text = json.dumps(content, indent=2) + "\n"
        path = DATA / rel
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"wrote {rel}  ({len(content['values'])} entries)")
    if check:
        for rel in stale:
            print(f"STALE {rel}")
        sys.exit(1 if stale else 0)


if __name__ == "__main__":
    main()
