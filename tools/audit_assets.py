#!/usr/bin/env python3
"""核对注册表、防爆档位、防辐射标签，并统计资源缺口。

  python3 tools/audit_assets.py            缺资源只提示，不算失败（B0 阶段资源还没做）
  python3 tools/audit_assets.py --strict   缺资源也算失败（收尾用）

HBM 的防爆标签按爆炸抗性分档，阈值取自 NTM-Continuum TagCategories.BLAST_TIERS：
large_explosion 70 / nuclear 200 / obsidian 1200。
"""
import json
import math
import re
import subprocess
import sys
from collections import Counter
from itertools import product

from npp_blocks import (ATLAS_SIZES, EQUIPMENT_IDS, EQUIPMENT_SOURCE, MOD_ID, ROOT,
                        equipment_catalog, parse_blocks, parse_surfaces, parse_tiers)

HBM_BLAST = {"large_explosion": 70.0, "nuclear": 200.0, "obsidian": 1200.0}
TIER_MUST_REACH = {"STANDARD": None, "REINFORCED": "large_explosion", "SHIELD": "nuclear", "CONTAINMENT": "obsidian"}
EXPECTED_TOTAL = 97
EXPECTED_KINDS = {"full": 39, "slab": 22, "stairs": 18, "panel": 12, "wallbox": 1, "equipment": 5}

RES = ROOT / "src/main/resources"
errors = []
notes = []


def fail(msg):
    errors.append(msg)


def audit_panel_shape(bid, assets):
    """按 MC BlockModelRotation 的负角度旋转模型，核对碰撞箱与支撑侧。"""
    source = (ROOT / "src/main/java/com/example/sheepnpp/block/PanelBlock.java").read_text(encoding="utf-8")
    boxes = {name.lower(): [float(v.strip()) for v in values.split(",")]
             for name, values in re.findall(r"SHAPE_(\w+)\s*=\s*Block\.box\(([^)]+)\)", source)}
    state = json.loads((assets / f"blockstates/{bid}.json").read_text(encoding="utf-8"))
    for key, variant in state["variants"].items():
        direction = key.removeprefix("facing=")
        model = json.loads((assets / f"models/{variant['model'].split(':')[1]}.json").read_text(encoding="utf-8"))
        element = model["elements"][0]
        x_angle = math.radians(-variant.get("x", 0))
        y_angle = math.radians(-variant.get("y", 0))
        points = []
        for x, y, z in product(*zip(element["from"], element["to"])):
            x, y, z = x - 8, y - 8, z - 8
            y, z = y * math.cos(x_angle) - z * math.sin(x_angle), y * math.sin(x_angle) + z * math.cos(x_angle)
            x, z = x * math.cos(y_angle) + z * math.sin(y_angle), -x * math.sin(y_angle) + z * math.cos(y_angle)
            points.append((x + 8, y + 8, z + 8))
        bounds = [round(min(p[i] for p in points), 5) for i in range(3)]
        bounds += [round(max(p[i] for p in points), 5) for i in range(3)]
        if bounds != boxes[direction]:
            fail(f"{bid} {direction}: 模型边界 {bounds} 与碰撞箱 {boxes[direction]} 不一致")
        axis, positive = {"down": (1, True), "up": (1, False), "north": (2, True),
                          "south": (2, False), "west": (0, True), "east": (0, False)}[direction]
        if bounds[axis] != (12 if positive else 0) or bounds[axis + 3] != (16 if positive else 4):
            fail(f"{bid} {direction}: 板体未紧贴支撑侧")


def audit_wallbox(b, assets):
    """Check the preserved prototype and rotate every element against Java's wall-touching bounds."""
    bid = b["id"]
    prototype = ROOT / f"prototypes/{bid}"
    model_path = assets / f"models/block/{bid}.json"
    state_path = assets / f"blockstates/{bid}.json"
    if not model_path.exists() or not state_path.exists():
        fail(f"{bid}: missing wallbox model/state")
        return
    model = json.loads(model_path.read_text(encoding="utf-8"))
    if model_path.read_bytes() != (prototype / f"{bid}.json").read_bytes():
        fail(f"{bid}: model must preserve the prototype exactly")
    atlas = assets / f"textures/block/{bid}.png"
    if not atlas.exists() or atlas.read_bytes() != (prototype / f"{bid}.png").read_bytes():
        fail(f"{bid}: atlas differs from prototype")
    if len(model.get("elements", [])) != 28:
        fail(f"{bid}: expected 28 elements")
    if model.get("textures") != {"0": f"{MOD_ID}:block/{bid}", "particle": "minecraft:block/light_gray_concrete"}:
        fail(f"{bid}: incorrect atlas or particle reference")
    if (b["tier"], b["surface"], b["rad"], b["light"]) != ("STANDARD", "METAL", False, 0):
        fail(f"{bid}: expected STANDARD/METAL, no radiation shielding or light")
    source = (ROOT / "src/main/java/com/example/sheepnpp/block/WallMountedDistributionBoxBlock.java").read_text(encoding="utf-8")
    compact = re.sub(r"\s+", "", source)
    # Static guardrails for placement, support, shape dispatch, rotation and mirroring.
    required = ["extends Block", "BlockStateProperties.HORIZONTAL_FACING", "context.getClickedFace()",
                "if (!face.getAxis().isHorizontal())", "setValue(FACING, face)",
                "state.canSurvive(context.getLevel(), context.getClickedPos()) ? state : null",
                "pos.relative(facing.getOpposite())", "isFaceSturdy(level, supportPos, facing)",
                "direction == state.getValue(FACING).getOpposite() && !state.canSurvive(level, pos)",
                "return Blocks.AIR.defaultBlockState()", "rotation.rotate(state.getValue(FACING))",
                "state.rotate(mirror.getRotation(state.getValue(FACING)))"]
    for token in required:
        if re.sub(r"\s+", "", token) not in compact:
            fail(f"{bid}: missing Java wall-mount contract: {token}")
    boxes = {name.lower(): [float(v.strip()) for v in values.split(",")]
             for name, values in re.findall(r"SHAPE_(\w+)\s*=\s*Block\.box\(([^)]+)\)", source)}
    variants = json.loads(state_path.read_text(encoding="utf-8"))["variants"]
    rotations = {"north": 0, "east": 90, "south": 180, "west": 270}
    if set(variants) != {f"facing={d}" for d in rotations}:
        fail(f"{bid}: expected exactly four horizontal states")
    for direction, angle in rotations.items():
        variant = variants.get(f"facing={direction}", {})
        if variant != {"model": f"{MOD_ID}:block/{bid}", "y": angle}:
            fail(f"{bid} {direction}: incorrect model rotation")
        points = []
        radians = math.radians(-angle)
        for element in model["elements"]:
            if element.get("rotation", {}).get("angle", 0) != 0:
                fail(f"{bid}: audit expects unrotated prototype elements")
            for face in element["faces"].values():
                if face["texture"] != "#0" or any(not 0 <= uv <= 16 for uv in face["uv"]):
                    fail(f"{bid}: invalid atlas face reference/UV")
            for x, y, z in product(*zip(element["from"], element["to"])):
                x, z = x - 8, z - 8
                points.append((x * math.cos(radians) + z * math.sin(radians) + 8,
                               y, -x * math.sin(radians) + z * math.cos(radians) + 8))
        bounds = [round(min(p[i] for p in points), 5) for i in range(3)]
        bounds += [round(max(p[i] for p in points), 5) for i in range(3)]
        if bounds != boxes.get(direction):
            fail(f"{bid} {direction}: model bounds {bounds} != Java {boxes.get(direction)}")
        if f"case{direction.upper()}->SHAPE_{direction.upper()}" not in compact:
            fail(f"{bid} {direction}: incorrect shape dispatch")
        axis, wall = {"north": (2, 16), "east": (0, 0), "south": (2, 0), "west": (0, 16)}[direction]
        if bounds[axis + (3 if wall == 16 else 0)] != wall:
            fail(f"{bid} {direction}: back does not touch support wall")
    if boxes.get("north") != [1.8, 0.5, 9.2, 14.2, 14.9, 16]:
        fail(f"{bid}: incorrect north prototype bounds")
    recipe_dir = RES / f"data/{MOD_ID}/recipes"
    recipe_path = recipe_dir / f"{bid}.json"
    if recipe_path.exists():
        recipe = json.loads(recipe_path.read_text(encoding="utf-8"))

        def grids(data):
            if data.get("type") != "minecraft:crafting_shaped":
                return set()
            rows = data["pattern"]
            while rows and not rows[0].strip():
                rows = rows[1:]
            while rows and not rows[-1].strip():
                rows = rows[:-1]
            columns = [x for row in rows for x, char in enumerate(row) if char != " "]
            if not columns:
                return set()
            grid = tuple(tuple(json.dumps(data["key"][char], sort_keys=True) if char != " " else ""
                               for char in row[min(columns):max(columns) + 1]) for row in rows)
            return {grid, tuple(tuple(reversed(row)) for row in grid)}

        ingredients = {value.get("item") for value in recipe.get("key", {}).values()}
        if ingredients != {"minecraft:iron_ingot", "minecraft:redstone", "minecraft:iron_nugget"}:
            fail(f"{bid}: expected iron ingot, redstone and iron nugget recipe")
        if recipe.get("result") != {"item": f"{MOD_ID}:{bid}", "count": 1}:
            fail(f"{bid}: incorrect recipe output")
        own_grids = grids(recipe)
        if not own_grids:
            fail(f"{bid}: expected shaped recipe")
        for other in recipe_dir.glob("*.json"):
            if other != recipe_path and own_grids & grids(json.loads(other.read_text(encoding="utf-8"))):
                fail(f"{bid}: recipe conflicts with {other.stem}")
    loot_path = RES / f"data/{MOD_ID}/loot_tables/blocks/{bid}.json"
    if loot_path.exists():
        loot = json.loads(loot_path.read_text(encoding="utf-8"))
        if loot.get("pools", [{}])[0].get("entries") != [{"type": "minecraft:item", "name": f"{MOD_ID}:{bid}"}]:
            fail(f"{bid}: loot must drop its own BlockItem")


def recipe_grids(data):
    if data.get("type") != "minecraft:crafting_shaped":
        return set()
    rows = data["pattern"]
    occupied = [(x, y) for y, row in enumerate(rows) for x, char in enumerate(row) if char != " "]
    if not occupied:
        return set()
    x0, y0 = (min(p[i] for p in occupied) for i in (0, 1))
    x1, y1 = (max(p[i] for p in occupied) for i in (0, 1))
    grid = tuple(tuple(json.dumps(data["key"][char], sort_keys=True) if char != " " else ""
                       for char in row[x0:x1 + 1]) for row in rows[y0:y1 + 1])
    return {grid, tuple(tuple(reversed(row)) for row in grid)}


def audit_equipment(b, assets):
    bid = b["id"]
    try:
        entry = equipment_catalog()[bid]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        fail(f"{bid}: invalid/missing prototype catalog: {exc}")
        return
    for key in ("mount", "bounds", "tier"):
        if b[key] != entry[key]:
            fail(f"{bid}: Java {key} does not match catalog")
    if b["rad"] or b["light"] or b["surface"] != "METAL":
        fail(f"{bid}: equipment must be non-sealing, unlit METAL decoration")
    model_path = assets / f"models/block/{bid}.json"
    atlas_path = assets / f"textures/block/{bid}.png"
    state_path = assets / f"blockstates/{bid}.json"
    for path, extension in ((model_path, "json"), (atlas_path, "png")):
        prototype = EQUIPMENT_SOURCE / f"{bid}.{extension}"
        if not path.exists() or not prototype.exists() or path.read_bytes() != prototype.read_bytes():
            fail(f"{bid}: {extension} must match prototype byte-for-byte")
    if not model_path.exists() or not state_path.exists():
        return
    model = json.loads(model_path.read_text(encoding="utf-8"))
    textures = model.get("textures", {})
    if textures.get("particle") != "minecraft:block/gray_concrete":
        fail(f"{bid}: expected vanilla gray_concrete particle")
    atlas_keys = {key for key, value in textures.items() if value == f"{MOD_ID}:block/{bid}"}
    if not atlas_keys or any(value != f"{MOD_ID}:block/{bid}" for key, value in textures.items() if key != "particle"):
        fail(f"{bid}: incorrect atlas reference")
    elements = model.get("elements", [])
    if not 5 <= len(elements) <= 25 or len({tuple(e.get("from", []) + e.get("to", [])) for e in elements}) < 4:
        fail(f"{bid}: expected 5-25 elements with at least four distinct cuboids")
    points = []
    for element in elements:
        if not element.get("faces"):
            fail(f"{bid}: element has no faces")
        for face in element.get("faces", {}).values():
            if face.get("texture", "").removeprefix("#") not in atlas_keys:
                fail(f"{bid}: face does not reference its atlas")
            if len(face.get("uv", [])) != 4 or any(not 0 <= uv <= 16 for uv in face.get("uv", [])):
                fail(f"{bid}: invalid atlas UV")
        for corner in product(*zip(element["from"], element["to"])):
            point = list(corner)
            rotation = element.get("rotation", {})
            if rotation.get("angle", 0):
                axis = "xyz".index(rotation["axis"])
                a, c = ((1, 2), (2, 0), (0, 1))[axis]
                origin = rotation.get("origin", [8, 8, 8])
                angle = math.radians(rotation["angle"])
                u, v = point[a] - origin[a], point[c] - origin[c]
                scale = 1 / math.cos(angle) if rotation.get("rescale") else 1
                point[a] = origin[a] + (u * math.cos(angle) - v * math.sin(angle)) * scale
                point[c] = origin[c] + (u * math.sin(angle) + v * math.cos(angle)) * scale
            points.append(point)
    if not points:
        fail(f"{bid}: empty geometry")
        return
    variants = json.loads(state_path.read_text(encoding="utf-8"))["variants"]
    rotations = {"north": 0, "east": 90, "south": 180, "west": 270}
    if set(variants) != {f"facing={d}" for d in rotations}:
        fail(f"{bid}: expected exactly four horizontal variants")
    x0, y0, z0, x1, y1, z1 = b["bounds"]
    expected = {"north": b["bounds"], "east": [16-z1, y0, x0, 16-z0, y1, x1],
                "south": [16-x1, y0, 16-z1, 16-x0, y1, 16-z0],
                "west": [z0, y0, 16-x1, z1, y1, 16-x0]}
    for direction, angle in rotations.items():
        if variants.get(f"facing={direction}") != {"model": f"{MOD_ID}:block/{bid}", "y": angle}:
            fail(f"{bid} {direction}: incorrect model rotation")
        theta = math.radians(angle)
        rotated = [(8 + (x-8)*math.cos(theta) - (z-8)*math.sin(theta), y,
                    8 + (x-8)*math.sin(theta) + (z-8)*math.cos(theta)) for x, y, z in points]
        bounds = [round(min(p[i] for p in rotated), 5) for i in range(3)]
        bounds += [round(max(p[i] for p in rotated), 5) for i in range(3)]
        if bounds != expected[direction]:
            fail(f"{bid} {direction}: model bounds {bounds} != Java profile {expected[direction]}")
        axis, index = {"north": (2, 5), "east": (0, 0), "south": (2, 2), "west": (0, 3)}[direction]
        if b["mount"] == "floor":
            if bounds[1] != 0:
                fail(f"{bid}: floor model must touch the block below")
        elif bounds[index] != (16 if index == axis + 3 else 0):
            fail(f"{bid} {direction}: wall model back must touch its support")
    recipe_dir = RES / f"data/{MOD_ID}/recipes"
    recipe_path = recipe_dir / f"{bid}.json"
    if recipe_path.exists():
        recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
        grids = recipe_grids(recipe)
        if not grids or recipe.get("result") != {"item": f"{MOD_ID}:{bid}", "count": 1}:
            fail(f"{bid}: expected shaped recipe producing one matching BlockItem")
        for other in recipe_dir.glob("*.json"):
            if other != recipe_path and grids & recipe_grids(json.loads(other.read_text(encoding="utf-8"))):
                fail(f"{bid}: recipe conflicts with {other.stem}")
    loot_path = RES / f"data/{MOD_ID}/loot_tables/blocks/{bid}.json"
    if loot_path.exists():
        loot = json.loads(loot_path.read_text(encoding="utf-8"))
        if loot.get("pools", [{}])[0].get("entries") != [{"type": "minecraft:item", "name": f"{MOD_ID}:{bid}"}]:
            fail(f"{bid}: loot must drop its own BlockItem")
    for lang, key in (("zh_cn", "name_zh"), ("en_us", "name_en")):
        path = assets / f"lang/{lang}.json"
        if path.exists() and json.loads(path.read_text(encoding="utf-8")).get(f"block.{MOD_ID}.{bid}") != entry[key]:
            fail(f"{bid}: {lang} name differs from catalog")


def audit_equipment_java():
    source = (ROOT / "src/main/java/com/example/sheepnpp/block/EquipmentBlock.java").read_text(encoding="utf-8")
    compact = re.sub(r"\s+", "", source)
    required = ["extends Block", "BlockStateProperties.HORIZONTAL_FACING", "facing = face",
                "!face.getAxis().isHorizontal()", "face != Direction.UP",
                "context.getHorizontalDirection().getOpposite()",
                "state.canSurvive(context.getLevel(), context.getClickedPos()) ? state : null",
                "state.getValue(FACING).getOpposite() : Direction.DOWN",
                "pos.relative(support)", "isFaceSturdy(level, supportPos, support.getOpposite())",
                "direction == supportDirection(state) && !state.canSurvive(level, pos)",
                "return Blocks.AIR.defaultBlockState()", "getCollisionShape(",
                "return profile.shape(state.getValue(FACING))", "rotation.rotate(state.getValue(FACING))",
                "state.rotate(mirror.getRotation(state.getValue(FACING)))"]
    for token in required:
        if re.sub(r"\s+", "", token) not in compact:
            fail(f"EquipmentBlock missing placement/shape/support contract: {token}")
    if "EntityBlock" in source or "BlockEntity" in source or "extends HorizontalDirectionalBlock" in source:
        fail("EquipmentBlock must be a plain Block without a block entity")
    profile = re.sub(r"\s+", "", (ROOT / "src/main/java/com/example/sheepnpp/block/EquipmentProfile.java").read_text(encoding="utf-8"))
    for token in ("north=Block.box(x0,y0,z0,x1,y1,z1)",
                  "east=Block.box(16-z1,y0,x0,16-z0,y1,x1)",
                  "south=Block.box(16-x1,y0,16-z1,16-x0,y1,16-z0)",
                  "west=Block.box(z0,y0,16-x1,z1,y1,16-x0)"):
        if token not in profile:
            fail(f"EquipmentProfile rotation formula changed: {token}")
    for direction in ("NORTH", "EAST", "SOUTH", "WEST"):
        if f"case{direction}->{direction.lower()}" not in profile:
            fail(f"EquipmentProfile incorrect {direction} shape dispatch")


def audit_textures(blocks, surfaces, textures):
    """贴图与资源的一致性：模型引用的贴图必须存在、透明像素必须与 cutout 注册一致、不能有孤儿贴图。"""
    from PIL import Image

    tex_dir = RES / f"assets/{MOD_ID}/textures/block"
    wanted = {"particle_chip"}
    for b in blocks:
        wanted.add(b["id"] if b["kind"] == "panel" else b["group"])
    for orphan in sorted(textures - wanted):
        fail(f"孤儿贴图 {orphan}.png：没有任何注册方块使用")
    for name in sorted(textures):
        with Image.open(tex_dir / f"{name}.png") as image:
            expected_size = ATLAS_SIZES.get(name, (16, 16))
            if image.size != expected_size:
                fail(f"{name}: 尺寸 {image.size}, expected {expected_size}")

    model_dir = RES / f"assets/{MOD_ID}/models/block"
    for model in sorted(model_dir.glob("*.json")) if model_dir.exists() else []:
        data = json.loads(model.read_text(encoding="utf-8"))
        for value in data.get("textures", {}).values():
            if value.startswith(f"{MOD_ID}:block/") and value.split("/")[-1] not in textures:
                fail(f"模型 {model.name} 引用了不存在的贴图 {value}")

    seen = set()
    for b in blocks:
        name = b["id"] if b["kind"] == "panel" else b["group"]
        if name in seen or name not in textures:
            continue
        seen.add(name)
        img = Image.open(tex_dir / f"{name}.png").convert("RGBA")
        if img.size != ATLAS_SIZES.get(name, (16, 16)):
            continue
        has_hole = any(pixel[3] < 255 for pixel in img.get_flattened_data())
        wants_hole = surfaces[b["surface"]][1]
        if name.startswith("floor_") and not 4 <= len(set(img.get_flattened_data())) <= 7:
            fail(f"{name}: floor texture must use 4-7 colors")
        if has_hole != wants_hole:
            fail(f"{name}: 贴图{'有' if has_hole else '没有'}透明像素，但注册为{'镂空' if wants_hole else '实心'}"
                 f"（Surface.{b['surface']}），cutout 与贴图必须一致")
        if name in ("cc_light_white", "cc_light_white_panel"):
            if any(r != g or g != blue for r, g, blue, alpha in img.get_flattened_data() if alpha):
                fail(f"{name}: 纯白灯的像素必须为中性灰白，不能偏蓝或偏黄")


def main():
    strict = "--strict" in sys.argv
    blocks = parse_blocks()
    batches = sys.argv[sys.argv.index("--batches") + 1].split(",") if "--batches" in sys.argv else []
    tiers = parse_tiers()
    surfaces = parse_surfaces()
    ids = [b["id"] for b in blocks]

    # 注册表自洽
    for dup, n in Counter(ids).items():
        if n > 1:
            fail(f"重复注册 {dup}")
    for i in ids:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", i):
            fail(f"非法 id {i}")
    if len(blocks) != EXPECTED_TOTAL:
        fail(f"注册数 {len(blocks)}，计划书要求 {EXPECTED_TOTAL}")
    if Counter(b["kind"] for b in blocks) != EXPECTED_KINDS:
        fail(f"方块分类应为 {EXPECTED_KINDS}")
    for b in blocks:
        if b["tier"] not in tiers:
            fail(f"{b['id']}: 未知档位 {b['tier']}")
        if b["surface"] not in surfaces:
            fail(f"{b['id']}: 未知表面 {b['surface']}")

    # 防爆档位：抗性必须达到该档对应的 HBM 阈值，且不能越档
    reached_by_tier = {}
    for name, (_, resistance, _) in tiers.items():
        reached = [t for t, v in HBM_BLAST.items() if resistance >= v]
        reached_by_tier[name] = reached
        want = TIER_MUST_REACH.get(name)
        if want is None:
            if reached:
                fail(f"档位 {name} 抗性 {resistance} 不该命中 HBM 防爆标签，实际命中 {reached}")
        else:
            expect = list(HBM_BLAST)[: list(HBM_BLAST).index(want) + 1]
            if reached != expect:
                fail(f"档位 {name} 抗性 {resistance}：应命中 {expect}，实际 {reached}")

    # 防辐射：只能是满格，且不能是镂空/地毯
    for b in blocks:
        if b["rad"]:
            if b["kind"] != "full":
                fail(f"{b['id']}: 非满格不能防辐射")
            if surfaces[b["surface"]][1] or b["surface"] == "CARPET":
                fail(f"{b['id']}: 镂空或地毯不能密封辐射")
    # 半砖/台阶/薄板与对应满格同档；薄板和灯不该有 rad
    by_group = {b["group"]: b for b in blocks if b["kind"] == "full"}
    for b in blocks:
        if b["kind"] in ("slab", "stairs") and b["group"] not in by_group:
            fail(f"{b['id']}: 找不到对应满格 {b['group']}")

    # 标签文件与注册表一致
    check = subprocess.run([sys.executable, str(ROOT / "tools/gen_tags.py"), "--check"],
                           capture_output=True, text=True)
    if check.returncode != 0:
        fail("标签文件过期，运行 python3 tools/gen_tags.py：" + check.stdout.strip().replace("\n", "; "))
    rad_path = RES / "data/hbm/tags/blocks/radiation_resistant.json"
    if rad_path.exists():
        rad = json.loads(rad_path.read_text(encoding="utf-8"))["values"]
        full_ids = {f"{MOD_ID}:{b['id']}" for b in blocks if b["kind"] == "full"}
        for v in rad:
            if v not in full_ids:
                fail(f"radiation_resistant 含非满格或未注册项 {v}")

    # 资源缺口（B0 只做代码与标签，其余资源按批次补）
    def missing(pattern):
        return [i for i in ids if not (RES / pattern.format(i)).exists()]

    gaps = {
        "blockstates": missing(f"assets/{MOD_ID}/blockstates/{{}}.json"),
        "item models": missing(f"assets/{MOD_ID}/models/item/{{}}.json"),
        "loot tables": missing(f"data/{MOD_ID}/loot_tables/blocks/{{}}.json"),
        "recipes": missing(f"data/{MOD_ID}/recipes/{{}}.json"),
    }
    textures = {p.stem for p in (RES / f"assets/{MOD_ID}/textures/block").glob("*.png")} \
        if (RES / f"assets/{MOD_ID}/textures/block").exists() else set()
    for label, miss in gaps.items():
        (fail if strict and miss else notes.append)(f"缺 {label}: {len(miss)}/{len(ids)}")
    if textures:
        notes.append(f"贴图 {len(textures)} 张")
    if strict:
        if len(textures) != 58:
            fail(f"贴图应为 58 张（52 张 16x16 + 6 张 32x32），实际 {len(textures)}")
        expected_textures = {b["group"] for b in blocks} | {"particle_chip"}
        if textures != expected_textures:
            fail(f"贴图集合不一致：缺少 {sorted(expected_textures - textures)}，多余 {sorted(textures - expected_textures)}")
        paths = [f"assets/{MOD_ID}/blockstates", f"assets/{MOD_ID}/models/item",
                 f"data/{MOD_ID}/recipes", f"data/{MOD_ID}/loot_tables/blocks"]
        for rel in paths:
            extra = {p.stem for p in (RES / rel).glob("*.json")} - set(ids)
            if extra:
                fail(f"{rel} 含孤儿资源 {sorted(extra)}")

    audit_textures(blocks, surfaces, textures)

    # 已交付批次必须完整；其余批次继续报告缺口。
    delivered = blocks if strict else [b for b in blocks if any(b["id"].startswith(p + "_") for p in batches)]
    assets = RES / f"assets/{MOD_ID}"
    languages = [json.loads((assets / f"lang/{lang}.json").read_text(encoding="utf-8"))
                 for lang in ("zh_cn", "en_us")] if delivered else []
    if languages and languages[0].keys() != languages[1].keys():
        fail("中英文语言键不一致")
    if strict and languages:
        expected_keys = {f"block.{MOD_ID}.{bid}" for bid in ids}
        for lang, content in zip(("zh_cn", "en_us"), languages):
            extra = {key for key in content if key.startswith(f"block.{MOD_ID}.")} - expected_keys
            if extra:
                fail(f"{lang} 含孤儿方块名称 {sorted(extra)}")
    for b in delivered:
        bid = b["id"]
        for label, missing_ids in gaps.items():
            if bid in missing_ids:
                fail(f"已交付批次 {bid} 缺少 {label}")
        if b["group"] not in textures:
            fail(f"已交付批次 {bid} 缺少贴图")
        for lang, content in zip(("zh_cn", "en_us"), languages):
            if f"block.{MOD_ID}.{bid}" not in content:
                fail(f"{bid} 缺少 {lang} 名称")
        state_path = assets / f"blockstates/{bid}.json"
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            variants = state["variants"]
            expected = {"full": 1, "slab": 3, "stairs": 40, "panel": 6, "wallbox": 4, "equipment": 4}[b["kind"]]
            if len(variants) != expected:
                fail(f"{bid} 状态变体数应为 {expected}")
            for variant in variants.values():
                model = variant["model"].removeprefix(f"{MOD_ID}:")
                if not (assets / f"models/{model}.json").exists():
                    fail(f"{bid} 引用了缺失模型 {model}")
        if b["kind"] == "wallbox":
            audit_wallbox(b, assets)
        if b["kind"] == "equipment":
            audit_equipment(b, assets)
        if b["kind"] == "panel":
            model_path = assets / f"models/block/{bid}.json"
            if not model_path.exists() or json.loads(model_path.read_text(encoding="utf-8")).get("textures", {}).get("particle") != f"{MOD_ID}:block/particle_chip":
                fail(f"{bid} 缺少薄板粒子贴图引用")
            elif state_path.exists():
                audit_panel_shape(bid, assets)
        if b["kind"] == "slab":
            loot_path = RES / f"data/{MOD_ID}/loot_tables/blocks/{bid}.json"
            if loot_path.exists():
                loot = json.loads(loot_path.read_text(encoding="utf-8"))
                functions = loot["pools"][0]["entries"][0].get("functions", [])
                if not any(f.get("function") == "minecraft:set_count" and f.get("count") == 2
                           and any(c.get("properties", {}).get("type") == "double" and c.get("block") == f"{MOD_ID}:{bid}"
                                   for c in f.get("conditions", [])) for f in functions):
                    fail(f"{bid} 双层半砖必须掉落两个半砖")
    if delivered:
        notes.append(f"{'全量' if strict else '已交付批次 ' + ','.join(batches)}：严格检查 {len(delivered)} 个方块")

    audit_equipment_java()
    if {b["id"] for b in blocks if b["kind"] == "equipment"} != EQUIPMENT_IDS:
        fail("Equipment registrations differ from the explicit atlas whitelist")
    floor_tiers = {"floor_heavy_load": "SHIELD", "floor_turbine_hall": "REINFORCED",
                   "floor_equipment_room": "REINFORCED", "floor_maintenance_tread": "STANDARD",
                   "floor_decontamination_ceramic": "STANDARD"}
    for bid, tier in floor_tiers.items():
        b = next((b for b in blocks if b["id"] == bid), {})
        if (b.get("kind"), b.get("tier"), b.get("rad")) != ("full", tier, False):
            fail(f"{bid}: expected full/{tier}/non-sealing")
    kinds = Counter(b["kind"] for b in blocks)
    rad_count = sum(1 for b in blocks if b["rad"])
    print(f"注册 {len(blocks)}：满格 {kinds['full']}  半砖 {kinds['slab']}  台阶 {kinds['stairs']}  薄板 {kinds['panel']}  壁挂箱 {kinds['wallbox']}  设备 {kinds['equipment']}")
    print(f"防辐射满格 {rad_count}")
    print("档位抗性 -> HBM 标签：" + "  ".join(
        f"{n}={tiers[n][1]:g}->{'/'.join(reached_by_tier[n]) or '-'}" for n in tiers))
    for n in notes:
        print("note:", n)
    for e in errors:
        print("FAIL:", e)
    print("OK" if not errors else f"{len(errors)} 个问题")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
