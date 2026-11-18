#!/usr/bin/env python3
"""Check the shipped jar, including the loader dependency regression.

An optional dependency with versionRange="" still rejects installed HBM versions.
Tag-only integration must not declare an HBM dependency at all.
"""
import json
import re
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check():
    properties = dict(
        line.split("=", 1) for line in (ROOT / "gradle.properties").read_text().splitlines()
        if line and not line.startswith("#") and "=" in line
    )
    mod_id, version = properties["mod_id"], properties["mod_version"]
    jar = ROOT / f"build/libs/{mod_id}-{version}.jar"
    with zipfile.ZipFile(jar) as archive:
        metadata = archive.read("META-INF/mods.toml").decode("utf-8")
        sections = re.findall(
            r"^\[\[dependencies\.([^\]]+)\]\]\s*\n(.*?)(?=^\[|\Z)",
            metadata, re.MULTILINE | re.DOTALL,
        )
        dependencies = {}
        for owner, body in sections:
            assert owner == mod_id, f"Unexpected dependency owner: {owner}"
            name = re.search(r'^\s*modId\s*=\s*"([^"]+)"', body, re.MULTILINE)
            assert name, "Dependency without a modId"
            assert name[1] not in dependencies, f"Duplicate dependency: {name[1]}"
            dependencies[name[1]] = body
        assert set(dependencies) == {"forge", "minecraft"}, (
            f"Expected only Forge/Minecraft loader dependencies, got {list(dependencies)}"
        )
        for name, body in dependencies.items():
            assert re.search(r"^\s*mandatory\s*=\s*true\s*$", body, re.MULTILINE), name
            assert not re.search(r'^\s*versionRange\s*=\s*""', body, re.MULTILINE), name
        assert f'version="{version}"' in metadata, "Packaged version does not match gradle.properties"
        assert "${" not in metadata, "Unexpanded Gradle placeholder in metadata"

        state = json.loads(archive.read(f"assets/{mod_id}/blockstates/distribution_box.json"))
        expected = {f"facing={d}" for d in ("north", "east", "south", "west")}
        assert set(state["variants"]) == expected, "Wall box must have four facing variants"
        for direction, angle in (("north", 0), ("east", 90), ("south", 180), ("west", 270)):
            variant = state["variants"][f"facing={direction}"]
            assert variant.get("y", 0) == angle and variant.get("x", 0) == 0, (
                f"Wrong wall box rotation for {direction}"
            )
            assert variant["model"] == f"{mod_id}:block/distribution_box", "Wrong wall box model"
        model = json.loads(archive.read(f"assets/{mod_id}/models/block/distribution_box.json"))
        assert len(model["elements"]) == 28, "Unexpected wall box geometry"
        assert model["textures"].get("particle"), "Wall box particle texture is missing"
        png = archive.read(f"assets/{mod_id}/textures/block/distribution_box.png")
        assert png[:8] == b"\x89PNG\r\n\x1a\n", "Invalid wall box PNG"
        assert struct.unpack(">II", png[16:24]) == (32, 32), "Wall box atlas must be 32x32"
        assert png == (ROOT / "prototypes/distribution_box/distribution_box.png").read_bytes(), (
            "Packaged atlas differs from the approved prototype"
        )
        assert f"data/hbm/tags/blocks/radiation_resistant.json" in archive.namelist(), (
            "HBM integration tags must remain packaged"
        )
        # Check the shipped protection combinations, including intentional contrasts.
        radiation = set(json.loads(archive.read("data/hbm/tags/blocks/radiation_resistant.json"))["values"])
        blast = {tier: set(json.loads(archive.read(f"data/hbm/tags/blocks/blast_resistant/{tier}.json"))["values"])
                 for tier in ("large_explosion", "nuclear", "obsidian")}
        examples = {
            "rbmk_upper_bio_shield": (True, (True, True, True)),
            "rbmk_lead_brick": (True, (False, False, False)),
            "rbmk_support_steel": (False, (True, True, True)),
            "rbmk_analog_console": (False, (False, False, False)),
        }
        for bid, (sealed, tiers) in examples.items():
            resource = f"{mod_id}:{bid}"
            archive.getinfo(f"assets/{mod_id}/blockstates/{bid}.json")
            assert (resource in radiation) == sealed, f"Incorrect radiation sealing: {bid}"
            assert tuple(resource in values for values in blast.values()) == tiers, f"Incorrect blast tiers: {bid}"
        files = archive.namelist()
        for folder, suffix, expected_count in (
            (f"assets/{mod_id}/blockstates/", ".json", 97),
            (f"assets/{mod_id}/models/item/", ".json", 97),
            (f"assets/{mod_id}/textures/block/", ".png", 58),
            (f"data/{mod_id}/recipes/", ".json", 97),
            (f"data/{mod_id}/loot_tables/blocks/", ".json", 97),
        ):
            count = sum(name.startswith(folder) and name.endswith(suffix) for name in files)
            assert count == expected_count, f"{folder}: {count}, expected {expected_count}"
    print(f"OK {jar.name}: version={version}; loader dependencies=forge,minecraft; no HBM version gate")
    print("OK wall box: four facing variants, 28 elements, 32x32 atlas; HBM radiation tag retained")
    print("OK RBMK protection contrasts; packaged 97 blocks and 58 textures")


if __name__ == "__main__":
    check()
