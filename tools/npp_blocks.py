"""解析 ModBlocks.java / Tier.java / Surface.java，给 gen_tags.py 和 audit_assets.py 提供唯一的方块清单。

注册表只在 Java 里维护一份；改 ModBlocks.java 的调用格式前先改这里的正则。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JAVA = ROOT / "src/main/java/com/example/sheepnpp"
MOD_ID = "sheepnpp"

_B = r"(true|false)"
_COMMON = r'"([a-z0-9_]+)",\s*Tier\.(\w+),\s*Surface\.(\w+),\s*MapColor\.(\w+),\s*'
FAMILY = re.compile(r"\bfamily\(" + _COMMON + _B + r",\s*" + _B + r",\s*" + _B + r"\)")
FULL = re.compile(r"\bfull\(" + _COMMON + r"(\d+),\s*" + _B + r"\)")
PANEL = re.compile(r"\bpanel\(" + _COMMON + r"(\d+),\s*" + _B + r"\)")
WALLBOX = re.compile(r'\bwallbox\("([a-z0-9_]+)",\s*Tier\.(\w+),\s*Surface\.(\w+),\s*MapColor\.(\w+)\)')
EQUIPMENT = re.compile(r'\bequipment\(' + _COMMON + r'EquipmentProfile\.(\w+)\)')
EQUIPMENT_SOURCE = ROOT / "prototypes/rbmk_equipment"
EQUIPMENT_IDS = frozenset({
    "rbmk_analog_console", "rbmk_channel_mimic_panel", "rbmk_radiation_monitor",
    "rbmk_fuel_channel_head", "rbmk_reactor_service_hatch",
})
ATLAS_SIZES = {bid: (32, 32) for bid in ("distribution_box", *sorted(EQUIPMENT_IDS))}


def equipment_profiles():
    text = (JAVA / "block/EquipmentProfile.java").read_text(encoding="utf-8")
    return {name: {"mount": mount.lower(), "bounds": [float(v.strip()) for v in values.split(",")]}
            for name, mount, values in re.findall(r"^\s*(RBMK_[A-Z_]+)\(Mount\.(WALL|FLOOR),\s*([\d.,\s]+)\)", text, re.M)}


def equipment_catalog():
    """Prototype metadata is consumed at build time only, never by Minecraft."""
    data = json.loads((EQUIPMENT_SOURCE / "catalog.json").read_text(encoding="utf-8"))
    entries = data if isinstance(data, list) else data["entries"]
    catalog = {entry["id"]: entry for entry in entries}
    if len(catalog) != len(entries) or set(catalog) != EQUIPMENT_IDS:
        raise ValueError("Equipment catalog must contain exactly the five approved unique ids")
    for bid, entry in catalog.items():
        bounds = entry["bounds"]
        if (entry["mount"] not in ("floor", "wall") or len(bounds) != 6
                or not all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 16 for v in bounds)
                or not all(bounds[i] < bounds[i + 3] for i in range(3))
                or entry["tier"] not in ("STANDARD", "REINFORCED", "SHIELD")
                or not entry["name_zh"] or not entry["name_en"]):
            raise ValueError(f"Invalid equipment catalog entry: {bid}")
    return catalog


def parse_enum_numbers(path, enum_name):
    """Tier.java: STANDARD(2.0F, 6.0F, "none") -> {name: (hardness, resistance, toolTier)}"""
    text = path.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'^\s*([A-Z_]+)\(([\d.]+)F,\s*([\d.]+)F,\s*"(\w+)"\)', text, re.M):
        out[m.group(1)] = (float(m.group(2)), float(m.group(3)), m.group(4))
    return out


def parse_surfaces():
    """Surface.java: CONCRETE(SoundType.STONE, "pickaxe", false) -> {name: (tool, open)}"""
    text = (JAVA / "block/Surface.java").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'^\s*([A-Z_]+)\(SoundType\.\w+,\s*"(\w+)",\s*(true|false)\)', text, re.M):
        out[m.group(1)] = (m.group(2), m.group(3) == "true")
    return out


def parse_tiers():
    return parse_enum_numbers(JAVA / "block/Tier.java", "Tier")


def parse_blocks():
    """返回注册顺序的方块列表。kind: full|slab|stairs|panel|wallbox|equipment。"""
    text = (JAVA / "registry/ModBlocks.java").read_text(encoding="utf-8")
    found = []
    for m in FAMILY.finditer(text):
        found.append((m.start(), "family", m.groups()))
    for m in FULL.finditer(text):
        found.append((m.start(), "full", m.groups()))
    for m in PANEL.finditer(text):
        found.append((m.start(), "panel", m.groups()))
    for m in WALLBOX.finditer(text):
        found.append((m.start(), "wallbox", m.groups()))
    for m in EQUIPMENT.finditer(text):
        found.append((m.start(), "equipment", m.groups()))
    found.sort()

    blocks = []
    for _, form, g in found:
        if form == "family":
            gid, tier, surface, color, rad, slab, stairs = g
            base = dict(group=gid, tier=tier, surface=surface, color=color, light=0, ceiling_only=False)
            blocks.append(dict(base, id=gid, kind="full", rad=rad == "true"))
            if slab == "true":
                blocks.append(dict(base, id=gid + "_slab", kind="slab", rad=False))
            if stairs == "true":
                blocks.append(dict(base, id=gid + "_stairs", kind="stairs", rad=False))
        elif form == "full":
            gid, tier, surface, color, light, rad = g
            blocks.append(dict(group=gid, id=gid, kind="full", tier=tier, surface=surface, color=color,
                               light=int(light), rad=rad == "true", ceiling_only=False))
        elif form == "equipment":
            gid, tier, surface, color, profile = g
            blocks.append(dict(group=gid, id=gid, kind="equipment", tier=tier, surface=surface, color=color,
                               light=0, rad=False, ceiling_only=False, profile=profile,
                               **equipment_profiles()[profile]))
        elif form == "wallbox":
            gid, tier, surface, color = g
            blocks.append(dict(group=gid, id=gid, kind="wallbox", tier=tier, surface=surface, color=color,
                               light=0, rad=False, ceiling_only=False))
        else:
            gid, tier, surface, color, light, ceiling = g
            blocks.append(dict(group=gid, id=gid, kind="panel", tier=tier, surface=surface, color=color,
                               light=int(light), rad=False, ceiling_only=ceiling == "true"))
    return blocks
