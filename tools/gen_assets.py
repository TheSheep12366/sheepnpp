#!/usr/bin/env python3
"""按 ModBlocks.java 的注册表生成方块资源：blockstate / 方块模型 / 物品模型 / 配方 / 战利品 / 语言。

只为“贴图已存在”的材质组生成（textures/block/<group>.png），所以分批做贴图就分批出资源。
满格、半砖、台阶共用 <group>.png；薄板用自己的 <id>.png。

  python3 tools/gen_assets.py

台阶 blockstate 直接取自原版模板 tools/vanilla_templates/stone_brick_stairs.json，只换模型名，
不手抄旋转表。
"""
import json
import shutil
import sys

from npp_blocks import EQUIPMENT_SOURCE, MOD_ID, ROOT, equipment_catalog, parse_blocks

RES = ROOT / "src/main/resources"
ASSETS = RES / f"assets/{MOD_ID}"
DATA = RES / f"data/{MOD_ID}"
TEX = ASSETS / "textures/block"
PARTICLE = f"{MOD_ID}:block/particle_chip"
WALLBOX_SOURCE = ROOT / "prototypes/distribution_box"

# 材质组 id -> (中文名, 英文名)。半砖/台阶/薄板的后缀由 SUFFIX 统一追加。
NAMES = {
    "floor_heavy_load": ("重载承压地板", "Heavy Load Floor"),
    "floor_turbine_hall": ("汽机大厅防滑甲板", "Turbine Hall Deck"),
    "floor_equipment_room": ("设备间检修地板", "Equipment Room Access Floor"),
    "floor_maintenance_tread": ("检修菱纹踏板", "Maintenance Tread Floor"),
    "floor_decontamination_ceramic": ("去污陶瓷地板", "Decontamination Ceramic Floor"),
    "distribution_box": ("壁挂配电箱", "Wall-Mounted Distribution Box"),
    "plant_concrete": ("清水混凝土", "Fair-Faced Concrete"),
    "plant_concrete_painted": ("涂装混凝土", "Painted Concrete"),
    "plant_lead": ("铅板", "Lead Plate"),
    "plant_hazard": ("黄黑警示块", "Hazard Stripe"),
    "plant_grating": ("钢格栅", "Steel Grating"),
    "plant_epoxy": ("去污地坪", "Decontamination Flooring"),
    "plant_ceiling": ("厂房吊顶板", "Plant Ceiling Panel"),
    "plant_tray": ("电缆桥架", "Cable Tray"),
    "plant_vent": ("通风百叶", "Ventilation Louver"),
    "plant_trefoil": ("辐射标识板", "Radiation Sign Panel"),
    "rbmk_shield": ("RBMK 生物屏蔽", "RBMK Biological Shield"),
    "rbmk_graphite": ("RBMK 石墨砌块", "RBMK Graphite Block"),
    "rbmk_steel_green": ("RBMK 灰绿钢板", "RBMK Green Steel Plate"),
    "rbmk_channel": ("RBMK 通道端面", "RBMK Channel Plate"),
    "rbmk_channel_cover": ("RBMK 通道盖板", "RBMK Channel Cover"),
    "rbmk_panel_mint": ("RBMK 薄荷面板", "RBMK Mint Panel"),
    "rbmk_upper_bio_shield": ("RBMK 上生物屏蔽", "RBMK Upper Biological Shield"),
    "rbmk_lower_bio_shield": ("RBMK 下生物屏蔽", "RBMK Lower Biological Shield"),
    "rbmk_serpentinite_shield": ("RBMK 蛇纹石屏蔽", "RBMK Serpentinite Shield"),
    "rbmk_borated_concrete": ("RBMK 硼混凝土", "RBMK Borated Concrete"),
    "rbmk_lead_brick": ("RBMK 铅砖", "RBMK Lead Brick"),
    "rbmk_laminated_shield": ("RBMK 复合屏蔽", "RBMK Laminated Shield"),
    "rbmk_support_steel": ("RBMK 支撑钢", "RBMK Structural Support Steel"),
    "rbmk_support_base": ("RBMK 支撑基座", "RBMK Support Base"),
    "rbmk_refuelling_rail": ("RBMK 换料轨道装饰块", "RBMK Refuelling Rail Decor"),
    "rbmk_crane_girder": ("RBMK 吊车梁", "RBMK Crane Girder"),
    "pwr_containment": ("PWR 安全壳混凝土", "PWR Containment Concrete"),
    "pwr_liner": ("PWR 不锈钢衬里", "PWR Stainless Steel Liner"),
    "pwr_liner_white": ("PWR 涂白内衬", "PWR White-Painted Liner"),
    "pwr_deck": ("PWR 汽机甲板", "PWR Turbine Deck"),
    "pwr_cladding": ("PWR 保温覆层", "PWR Insulation Cladding"),
    "pwr_panel_white": ("PWR 白面板", "PWR White Panel"),
    "cc_wall_white": ("主控室白色墙板", "Control Room White Wall Panel"),
    "cc_wall_grey": ("主控室灰色吸音墙板", "Control Room Grey Acoustic Wall Panel"),
    "cc_wall_console": ("主控室控制台面板墙", "Control Room Console Wall"),
    "cc_floor_dark": ("主控室深色防静电地板", "Control Room Dark Antistatic Floor"),
    "cc_floor_light": ("主控室浅色防静电地板", "Control Room Light Antistatic Floor"),
    "cc_light_white": ("主控室纯白灯", "Control Room Pure White Light"),
    "cc_light_white_panel": ("主控室纯白灯板", "Control Room Pure White Light Panel"),
    "cc_ceiling": ("主控室吸音吊顶板", "Control Room Acoustic Ceiling Panel"),
    "eo_wall_beige": ("办公室米白涂料墙", "Office Beige Painted Wall"),
    "eo_wall_wood": ("办公室浅木饰面板", "Office Light Wood Veneer"),
    "eo_floor_carpet": ("办公室灰蓝地毯", "Office Blue-Grey Carpet Floor"),
    "eo_floor_tile": ("办公室浅色地砖", "Office Light Floor Tile"),
    "eo_ceiling": ("办公室矿棉吊顶板", "Office Mineral Fibre Ceiling Panel"),
    "eo_light_panel": ("办公室暖白灯板", "Office Warm White Light Panel"),
}
SUFFIX = {"full": ("", ""), "slab": ("半砖", " Slab"), "stairs": ("台阶", " Stairs"), "panel": ("", ""), "wallbox": ("", ""), "equipment": ("", "")}

TAB_ZH, TAB_EN = "羊's 核电站装饰", "Sheep's Nuclear Plant Decor"
TOOLTIPS = {
    "tooltip.sheepnpp.radshield": ("辐射屏蔽", "Radiation Shielding"),
    "tooltip.sheepnpp.blastres": ("爆炸抗性: %s", "Blast Resistance: %s"),
}

# 满格 / 薄板的合成：(图案, 键->物品, 产出数量) 或 ("shapeless", [物品...], 产出数量)。
# 半砖、台阶统一用对应满格：### -> 6 半砖，台阶 4 个。
V = "minecraft:"
RECIPES = {
    "floor_heavy_load": (["IBI", "CCC", "IBI"], {"I": V + "iron_ingot", "B": V + "iron_bars", "C": V + "gray_concrete"}, 6),
    "floor_turbine_hall": (["NNN", "IDI", "III"], {"N": V + "iron_nugget", "I": V + "iron_ingot", "D": V + "blue_dye"}, 6),
    "floor_equipment_room": (["NIN", "CDC", "NIN"], {"N": V + "iron_nugget", "I": V + "iron_ingot", "C": V + "light_gray_concrete", "D": V + "blue_dye"}, 6),
    "floor_maintenance_tread": (["N N", " I ", "N N"], {"N": V + "iron_nugget", "I": V + "iron_ingot"}, 4),
    "floor_decontamination_ceramic": (["QQQ", "DCD", "QQQ"], {"Q": V + "quartz", "D": V + "cyan_dye", "C": V + "white_concrete"}, 8),
    "rbmk_analog_console": (["GGG", "RCR", "III"], {"G": V + "glass_pane", "R": V + "redstone", "C": V + "comparator", "I": V + "iron_ingot"}, 1),
    "rbmk_channel_mimic_panel": (["IGI", "RGR", "INI"], {"I": V + "iron_ingot", "G": V + "glass_pane", "R": V + "redstone", "N": V + "iron_nugget"}, 1),
    "rbmk_radiation_monitor": (["IGI", "RCR", " N "], {"I": V + "iron_ingot", "G": V + "glass", "R": V + "redstone", "C": V + "comparator", "N": V + "iron_nugget"}, 1),
    "rbmk_fuel_channel_head": (["NIN", "IBI", "III"], {"N": V + "iron_nugget", "I": V + "iron_ingot", "B": V + "iron_block"}, 1),
    "rbmk_reactor_service_hatch": (["INI", "BIB", "INI"], {"I": V + "iron_ingot", "N": V + "iron_nugget", "B": V + "iron_bars"}, 1),
    "distribution_box": (["INI", "IRI", "III"], {"I": V + "iron_ingot", "R": V + "redstone", "N": V + "iron_nugget"}, 1),
    "plant_concrete": (["CCC", "CIC", "CCC"], {"C": V + "gray_concrete", "I": V + "iron_ingot"}, 8),
    "plant_concrete_painted": (["CCC", "CDC", "CCC"], {"C": V + "light_gray_concrete", "D": V + "white_dye"}, 8),
    "plant_lead": (["III", "IDI", "III"], {"I": V + "iron_ingot", "D": V + "gray_dye"}, 4),
    "plant_hazard": (["YYY", "YKY", "YYY"], {"Y": V + "yellow_concrete", "K": V + "black_dye"}, 8),
    "plant_grating": (["BB", "BB"], {"B": V + "iron_bars"}, 4),
    "plant_epoxy": (["CCC", "CDC", "CCC"], {"C": V + "gray_concrete", "D": V + "green_dye"}, 8),
    "plant_ceiling": (["CCC"], {"C": V + "white_concrete"}, 6),
    "plant_tray": (["I I", "III"], {"I": V + "iron_ingot"}, 4),
    "plant_vent": (["BBB"], {"B": V + "iron_bars"}, 6),
    "plant_trefoil": ("shapeless", [f"{MOD_ID}:plant_hazard", V + "magenta_dye"], 4),
    "rbmk_shield": (["CCC", "COC", "CCC"], {"C": V + "gray_concrete", "O": V + "obsidian"}, 8),
    "rbmk_graphite": (["CCC", "CKC", "CCC"], {"C": V + "black_concrete", "K": V + "coal"}, 8),
    "rbmk_steel_green": (["III", "IDI", "III"], {"I": V + "iron_ingot", "D": V + "green_dye"}, 4),
    "rbmk_channel": (["III", "IBI", "III"], {"I": V + "iron_ingot", "B": V + "iron_bars"}, 4),
    "rbmk_channel_cover": ("shapeless", [f"{MOD_ID}:rbmk_channel"], 4),
    "rbmk_panel_mint": ("shapeless", [V + "white_concrete", V + "lime_dye"], 4),
    "rbmk_upper_bio_shield": (["ISI", "SBS", "ISI"], {"I": V + "iron_ingot", "S": f"{MOD_ID}:rbmk_shield", "B": V + "iron_bars"}, 4),
    "rbmk_lower_bio_shield": (["SIS", "III", "SIS"], {"I": V + "iron_ingot", "S": f"{MOD_ID}:rbmk_shield"}, 4),
    "rbmk_serpentinite_shield": (["CCC", "CGC", "CCC"], {"C": V + "polished_andesite", "G": V + "green_dye"}, 8),
    "rbmk_borated_concrete": (["CCC", "CQC", "CCC"], {"C": V + "gray_concrete", "Q": V + "quartz"}, 8),
    "rbmk_lead_brick": (["LL", "LL"], {"L": f"{MOD_ID}:plant_lead"}, 4),
    "rbmk_laminated_shield": (["III", "SSS", "LLL"], {"I": V + "iron_ingot", "S": f"{MOD_ID}:rbmk_shield", "L": f"{MOD_ID}:plant_lead"}, 6),
    "rbmk_support_steel": (["III", "IBI", "III"], {"I": V + "iron_ingot", "B": V + "iron_block"}, 4),
    "rbmk_support_base": (["NNN", "ISI", "III"], {"N": V + "iron_nugget", "I": V + "iron_ingot", "S": f"{MOD_ID}:rbmk_shield"}, 4),
    "rbmk_refuelling_rail": (["I I", "IRI", "I I"], {"I": V + "iron_ingot", "R": V + "rail"}, 4),
    "rbmk_crane_girder": (["III", " B ", "III"], {"I": V + "iron_ingot", "B": V + "iron_bars"}, 4),
    "pwr_containment": (["CIC", "IOI", "CIC"], {"C": V + "gray_concrete", "I": V + "iron_ingot", "O": V + "obsidian"}, 8),
    "pwr_liner": (["III", "NNN", "III"], {"I": V + "iron_ingot", "N": V + "iron_nugget"}, 4),
    "pwr_liner_white": ("shapeless", [f"{MOD_ID}:pwr_liner", V + "white_dye"], 1),
    "pwr_deck": (["III", "IDI", "III"], {"I": V + "iron_ingot", "D": V + "blue_dye"}, 4),
    "pwr_cladding": (["LLL"], {"L": f"{MOD_ID}:pwr_liner"}, 6),
    "pwr_panel_white": ("shapeless", [f"{MOD_ID}:pwr_liner_white"], 4),
    "cc_wall_white": (["CCC", "CIC", "CCC"], {"C": V + "white_concrete", "I": V + "iron_ingot"}, 8),
    "cc_wall_grey": (["CCC", "CWC", "CCC"], {"C": V + "light_gray_concrete", "W": V + "light_gray_wool"}, 8),
    "cc_wall_console": (["III", "CRC", "III"], {"I": V + "iron_ingot", "C": V + "gray_concrete", "R": V + "redstone"}, 4),
    "cc_floor_dark": (["CCC", "CRC", "CCC"], {"C": V + "gray_concrete", "R": V + "redstone"}, 8),
    "cc_floor_light": (["CCC", "CRC", "CCC"], {"C": V + "light_gray_concrete", "R": V + "redstone"}, 8),
    "cc_light_white": (["CGC", "GLG", "CGC"], {"C": V + "white_concrete", "G": V + "glass", "L": V + "glowstone"}, 4),
    "cc_light_white_panel": ("shapeless", [f"{MOD_ID}:cc_light_white"], 4),
    "cc_ceiling": (["CWC"], {"C": V + "white_concrete", "W": V + "white_wool"}, 6),
    "eo_wall_beige": ("shapeless", [V + "white_concrete", V + "brown_dye"], 2),
    "eo_wall_wood": (["PPP", "PIP", "PPP"], {"P": V + "birch_planks", "I": V + "iron_nugget"}, 8),
    "eo_floor_carpet": (["WWW", "WDW", "WWW"], {"W": V + "light_gray_wool", "D": V + "blue_dye"}, 8),
    "eo_floor_tile": (["QQ", "QQ"], {"Q": V + "smooth_quartz"}, 4),
    "eo_ceiling": (["WCW"], {"W": V + "white_wool", "C": V + "white_concrete"}, 6),
    "eo_light_panel": (["GGG", "WLW"], {"G": V + "glass", "W": V + "white_concrete", "L": V + "glowstone_dust"}, 4),
}

PANEL_FACING = {
    "down": {},
    "east": {"x": 90, "y": 270},
    "north": {"x": 270},
    "south": {"x": 90},
    "up": {"x": 180},
    "west": {"x": 90, "y": 90},
}


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ref(name):
    return f"{MOD_ID}:block/{name}"


def stairs_blockstate(base):
    template = json.loads((ROOT / "tools/vanilla_templates/stone_brick_stairs.json").read_text(encoding="utf-8"))
    mapping = {
        "minecraft:block/stone_brick_stairs_inner": ref(base + "_inner"),
        "minecraft:block/stone_brick_stairs_outer": ref(base + "_outer"),
        "minecraft:block/stone_brick_stairs": ref(base),
    }
    variants = {}
    for key, value in template["variants"].items():
        value = dict(value)
        value["model"] = mapping[value["model"]]
        variants[key] = value
    return {"variants": variants}


def gen_models(b):
    bid, group, kind = b["id"], b["group"], b["kind"]
    tex = f"{MOD_ID}:block/{bid if kind == 'panel' else group}"
    box = {"bottom": tex, "top": tex, "side": tex}

    if kind == "full":
        write(ASSETS / f"models/block/{bid}.json", {"parent": "minecraft:block/cube_all", "textures": {"all": tex}})
        write(ASSETS / f"blockstates/{bid}.json", {"variants": {"": {"model": ref(bid)}}})
        write(ASSETS / f"models/item/{bid}.json", {"parent": ref(bid)})

    elif kind == "slab":
        write(ASSETS / f"models/block/{bid}.json", {"parent": "minecraft:block/slab", "textures": box})
        write(ASSETS / f"models/block/{bid}_top.json", {"parent": "minecraft:block/slab_top", "textures": box})
        write(ASSETS / f"blockstates/{bid}.json", {"variants": {
            "type=bottom": {"model": ref(bid)},
            "type=double": {"model": ref(group)},
            "type=top": {"model": ref(bid + "_top")},
        }})
        write(ASSETS / f"models/item/{bid}.json", {"parent": ref(bid)})

    elif kind == "stairs":
        write(ASSETS / f"models/block/{bid}.json", {"parent": "minecraft:block/stairs", "textures": box})
        write(ASSETS / f"models/block/{bid}_inner.json", {"parent": "minecraft:block/inner_stairs", "textures": box})
        write(ASSETS / f"models/block/{bid}_outer.json", {"parent": "minecraft:block/outer_stairs", "textures": box})
        write(ASSETS / f"blockstates/{bid}.json", stairs_blockstate(bid))
        write(ASSETS / f"models/item/{bid}.json", {"parent": ref(bid)})

    elif kind in ("wallbox", "equipment"):
        # Preserve prototype geometry, UVs, display transforms and vanilla particles byte-for-byte.
        target = ASSETS / f"models/block/{bid}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        source = EQUIPMENT_SOURCE if kind == "equipment" else WALLBOX_SOURCE
        shutil.copyfile(source / f"{bid}.json", target)
        TEX.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / f"{bid}.png", TEX / f"{bid}.png")
        write(ASSETS / f"blockstates/{bid}.json", {"variants": {
            f"facing={direction}": {"model": ref(bid), "y": angle}
            for direction, angle in (("north", 0), ("east", 90), ("south", 180), ("west", 270))
        }})
        write(ASSETS / f"models/item/{bid}.json", {"parent": ref(bid)})

    else:  # panel
        side = {"texture": "#all", "uv": [0, 12, 16, 16]}
        face = {"texture": "#all", "uv": [0, 0, 16, 16]}
        write(ASSETS / f"models/block/{bid}.json", {
            "parent": "minecraft:block/block",
            "textures": {"all": tex, "particle": PARTICLE},
            "elements": [{
                "from": [0, 12, 0], "to": [16, 16, 16],
                "faces": {"down": face, "up": face, "north": side, "south": side, "west": side, "east": side},
            }],
        })
        write(ASSETS / f"blockstates/{bid}.json", {"variants": {
            f"facing={d}": dict({"model": ref(bid)}, **rot) for d, rot in PANEL_FACING.items()
        }})
        write(ASSETS / f"models/item/{bid}.json", {"parent": ref(bid)})


def gen_loot(b):
    entry = {"type": "minecraft:item", "name": f"{MOD_ID}:{b['id']}"}
    if b["kind"] == "slab":
        entry["functions"] = [
            {"function": "minecraft:set_count", "count": 2.0, "add": False,
             "conditions": [{"condition": "minecraft:block_state_property",
                             "block": f"{MOD_ID}:{b['id']}", "properties": {"type": "double"}}]},
            {"function": "minecraft:explosion_decay"},
        ]
    write(DATA / f"loot_tables/blocks/{b['id']}.json", {
        "type": "minecraft:block",
        "pools": [{
            "rolls": 1.0,
            "entries": [entry],
            **({} if b["kind"] == "slab" else {"conditions": [{"condition": "minecraft:survives_explosion"}]}),
        }],
    })


def gen_recipe(b):
    bid, group, kind = b["id"], b["group"], b["kind"]
    path = DATA / f"recipes/{bid}.json"
    if kind == "slab":
        write(path, {"type": "minecraft:crafting_shaped", "pattern": ["XXX"],
                     "key": {"X": {"item": f"{MOD_ID}:{group}"}},
                     "result": {"item": f"{MOD_ID}:{bid}", "count": 6}})
    elif kind == "stairs":
        write(path, {"type": "minecraft:crafting_shaped", "pattern": ["X  ", "XX ", "XXX"],
                     "key": {"X": {"item": f"{MOD_ID}:{group}"}},
                     "result": {"item": f"{MOD_ID}:{bid}", "count": 4}})
    else:
        spec = RECIPES[bid]
        if spec[0] == "shapeless":
            write(path, {"type": "minecraft:crafting_shapeless",
                         "ingredients": [{"item": i} for i in spec[1]],
                         "result": {"item": f"{MOD_ID}:{bid}", "count": spec[2]}})
        else:
            pattern, key, count = spec
            write(path, {"type": "minecraft:crafting_shaped", "pattern": pattern,
                         "key": {k: {"item": v} for k, v in key.items()},
                         "result": {"item": f"{MOD_ID}:{bid}", "count": count}})


def main():
    catalog = equipment_catalog()
    NAMES.update({bid: (entry["name_zh"], entry["name_en"]) for bid, entry in catalog.items()})
    registered = parse_blocks()
    for b in registered:
        if b["kind"] == "equipment":
            entry = catalog[b["id"]]
            if any(b[key] != entry[key] for key in ("mount", "bounds", "tier")):
                sys.exit(f"Equipment catalog/Java mismatch: {b['id']}")
            for suffix in ("json", "png"):
                if not (EQUIPMENT_SOURCE / f"{b['id']}.{suffix}").is_file():
                    sys.exit(f"Missing equipment prototype: {b['id']}.{suffix}")
    blocks = [b for b in registered if b["kind"] in ("wallbox", "equipment")
              or (TEX / f"{b['group'] if b['kind'] != 'panel' else b['id']}.png").exists()]
    missing_names = sorted({b["group"] for b in blocks} - set(NAMES))
    if missing_names:
        sys.exit(f"NAMES 缺少: {missing_names}")
    missing_recipes = sorted({b["id"] for b in blocks if b["kind"] in ("full", "panel", "wallbox", "equipment")} - set(RECIPES))
    if missing_recipes:
        sys.exit(f"RECIPES 缺少: {missing_recipes}")

    zh = {"itemGroup.sheepnpp.building": TAB_ZH}
    en = {"itemGroup.sheepnpp.building": TAB_EN}
    for key, (z, e) in TOOLTIPS.items():
        zh[key], en[key] = z, e

    for b in blocks:
        gen_models(b)
        gen_loot(b)
        gen_recipe(b)
        z, e = NAMES[b["group"]]
        sz, se = SUFFIX[b["kind"]]
        zh[f"block.{MOD_ID}.{b['id']}"] = z + sz
        en[f"block.{MOD_ID}.{b['id']}"] = e + se

    write(ASSETS / "lang/zh_cn.json", zh)
    write(ASSETS / "lang/en_us.json", en)
    print(f"生成 {len(blocks)} 个方块的资源（{len({b['group'] for b in blocks})} 个材质组）")


if __name__ == "__main__":
    main()
