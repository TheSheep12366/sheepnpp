#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Verification only: do not regenerate assets or start Minecraft.
python3 tools/gen_tags.py --check
python3 tools/texture_pipeline.py verify tools/texture_spec.json
python3 tools/texture_pipeline.py audit
python3 tools/texture_pipeline.py seams
python3 tools/audit_assets.py --strict
./gradlew build --offline --console=plain
python3 tools/check_mod_metadata.py
