# Modrinth 发布资料 / Modrinth Listing Kit

> 版本 / Version: 0.1.2 · Minecraft 1.20.1 · Forge 47.4.28+ · Java 17
> 上传文件 / File: `build/libs/sheepnpp-0.1.2.jar`

---

## 1. 项目设置 / Project Settings

| 字段 | 值 |
|---|---|
| Name | Sheep's Nuclear Plant Decor |
| Slug | `sheepnpp`（与 modId 一致） |
| Project type | Mod |
| Categories | Decoration（主）、Building（可选） |
| Client / Server | Client: required · Server: required |
| Loader | Forge |
| Game version | 1.20.1 |
| Version number | 0.1.2 |
| Release channel | Beta（运行时效果未经游戏内验证，建议先发 Beta） |
| License | MIT（Modrinth 直接选 MIT） |
| Dependencies | 无必需依赖；NTM-Continuum 不在 mods.toml 声明，Modrinth 依赖栏可不填 |

---

## 2. 摘要 / Summary（Modrinth 限 256 字符）

**English**
> Modern industrial decor for Minecraft 1.20.1: RBMK and PWR plant halls, control rooms and engineer offices. 97 blocks with slabs, stairs, panels and static equipment, plus optional NTM-Continuum radiation sealing.

**简体中文**
> 适用于 1.20.1 的现代工业装饰：RBMK / PWR 厂房、主控室、工程师办公室。97 种方块，含半砖、台阶、薄板与静态设备，并可选适配 NTM-Continuum 防辐射。

**双语 / Bilingual**
> 现代核电站装饰 · Modern nuclear plant decor — RBMK/PWR halls, control rooms, offices. 97 blocks, 1.20.1 Forge.

---

## 3. 简介（直接粘贴到 Modrinth 描述）/ Description

### 3.1 English

```markdown
# Sheep's Nuclear Plant Decor

A **pure decoration** mod for building modern nuclear power plants: RBMK reactor halls, PWR containment and turbine halls, main control rooms and engineers' offices.

Large clean panels, thin seams, matte finishes. No rust, no grime, no cracks. Each of the five areas has its own colour language, so builds read clearly even when placed side by side.

## Highlights

- **97 blocks** in one creative tab: 39 full blocks, 22 slabs, 18 stairs, 12 thin panels, 1 distribution box and 5 static equipment models
- **Five themed areas**: Shared Plant, RBMK Hall, PWR Hall, Control Room, Engineer Office
- **Real models, not just cubes**: wall-mounted distribution box, analog control console, channel mimic panel, radiation monitor, fuel channel head, reactor service hatch
- **Thin 4px panels** (ceilings, cable trays, vents, light panels) that attach to walls, floors and ceilings
- **Light sources**: pure-white control room lights (level 15) and warm-white office panels (level 13)
- **Tiered blast resistance** (6 / 80 / 250 / 1200) with tooltips
- Survival crafting recipes for everything
- English and Simplified Chinese included

## Areas

| Area | Style |
|---|---|
| Shared Plant | Cool grey concrete, hazard yellow, lead grey. Floors, cable trays, vents, signs |
| RBMK Hall | Warm grey shielding, near-black graphite, grey-green steel, mint panels. Bio shields, support steel, refuelling rail, crane girder |
| PWR Hall | Cool containment concrete, silver liners, warm white linings, blue-grey deck |
| Control Room | White and grey acoustic walls, antistatic floors, pure white lights |
| Engineer Office | Beige paint, light wood, blue-grey carpet, floor tile, mineral-fibre ceilings |

Plus five industrial floors: Heavy Load, Turbine Hall Deck, Equipment Room Access, Maintenance Tread and Decontamination Ceramic.

## NTM-Continuum (HBM) support — optional

Works with the 1.20.1 Forge version of [NTM-Continuum](https://github.com/Warfactory-Official/NTM-Continuum). HBM is **not required**; the mod loads without it.

- Reinforced materials are added to HBM's blast-resistance tags. Hover a block to see its blast resistance (shown when above 50).
- 19 full-block walls are added to `hbm:radiation_resistant` and show **[Radiation Shielding]**.
- Slabs, stairs, thin panels and equipment are intentionally **not** sealed, so gaps are never treated as airtight walls.
- Some blocks are deliberately mixed: Lead Brick seals radiation but resists little; Structural Support Steel resists blasts but does not seal.

Sealing is a yes/no tag, not a percentage. Block names do not represent real attenuation. Resistance tiers do not guarantee immunity to every special explosion.

## Notes

- Decorative only: no reactor simulation, energy, fluids, radiation measurement, fuel handling or working doors.
- Install on **both client and server**.
- Remove older sheepnpp jars before installing a new one. Do not keep several versions.
- Minecraft 1.20.1 · Forge 47.4.28+ · Java 17. Not for Fabric, NeoForge or other versions.
- The RBMK blocks take visual cues from the real reactor type; material parameters are gameplay abstractions.
```

### 3.2 简体中文

```markdown
# 羊's 核电站装饰方块

一个**纯装饰**模组，用来搭建现代核电站：RBMK 堆厅、PWR 安全壳与汽机厅、主控室和工程师办公室。

大幅面板、细缝、哑光表面。没有锈迹、污渍和裂纹。五个区域各有一套色调，并排摆放也能一眼分清。

## 特色

- **97 个方块**，集中在一个创造标签页：39 满格、22 半砖、18 台阶、12 薄板、1 壁挂配电箱、5 个静态设备模型
- **五大区域**：共用厂房、RBMK 厂房、PWR 厂房、主控室、工程师办公室
- **有真实造型，不只是方块**：壁挂配电箱、苏式模拟仪控台、通道布置图屏、辐射监测箱、燃料通道头、反应堆检修舱盖
- **4px 薄板**（吊顶、电缆桥架、通风百叶、灯板）可贴墙、地面、天花板
- **光源**：主控室纯白灯（亮度 15）、办公室暖白灯板（亮度 13）
- **四档爆炸抗性**（6 / 80 / 250 / 1200），悬停可见
- 全部方块有生存合成配方
- 自带简体中文与英文

## 区域

| 区域 | 风格 |
|---|---|
| 共用厂房 | 冷灰混凝土、警示黄、铅灰。地坪、电缆桥架、百叶、标识板 |
| RBMK 厂房 | 暖灰屏蔽层、近黑石墨、灰绿钢板、薄荷面板。生物屏蔽、支撑钢、换料轨道、吊车梁 |
| PWR 厂房 | 冷灰安全壳、冷银衬里、暖白内衬、蓝灰甲板 |
| 主控室 | 白色与灰色吸音墙板、防静电地板、纯白灯 |
| 工程师办公室 | 米白涂料墙、浅木饰面、灰蓝地毯、地砖、矿棉吊顶 |

另有 5 种工业地板：重载承压、汽机大厅防滑甲板、设备间检修、检修菱纹踏板、去污陶瓷。

## NTM-Continuum（HBM）适配——可选

可配合 1.20.1 Forge 版 [NTM-Continuum](https://github.com/Warfactory-Official/NTM-Continuum) 使用。**不需要 HBM**，没有它也能正常加载。

- 强化材质加入 HBM 的防爆分类标签；爆炸抗性大于 50 的方块，悬停显示“爆炸抗性”。
- 19 种满格墙体加入 `hbm:radiation_resistant`，并显示 **[辐射屏蔽]**。
- 半砖、台阶、薄板和设备**刻意不密封**，避免有缝隙的构件被当成密闭墙。
- 部分方块故意做成偏科：铅衬砌块能密封但抗爆弱；承重钢构抗爆强但不密封。

密封是“是 / 否”的标签，没有百分比，名称也不代表真实材料的衰减率。抗性档位不代表对所有特殊爆炸免疫。

## 说明

- 仅作装饰：没有反应堆模拟、能量、流体、辐射测量、燃料处理，也没有可开关的门。
- 联机时**服务端与客户端都要安装**。
- 更新前请先删除旧的 sheepnpp jar，不要同时保留多个版本。
- 适用于 Minecraft 1.20.1 · Forge 47.4.28+ · Java 17。不支持 Fabric、NeoForge 及其他版本。
- RBMK 方块的外观取自真实堆型；材质参数属于游戏内抽象设定。
```

### 3.3 双语合并版 / Bilingual (single page)

```markdown
# Sheep's Nuclear Plant Decor · 羊's 核电站装饰方块

**EN** — A pure decoration mod for building modern nuclear plants: RBMK and PWR halls, control rooms and engineers' offices.
**中文** — 纯装饰模组，用于搭建现代核电站：RBMK / PWR 厂房、主控室、工程师办公室。

## Features · 特色

- **97 blocks / 97 种方块**: 39 full · 22 slabs · 18 stairs · 12 thin panels · 1 distribution box · 5 equipment models
  39 满格 · 22 半砖 · 18 台阶 · 12 薄板 · 1 配电箱 · 5 设备模型
- **5 areas / 5 大区域**: Shared Plant 共用厂房 · RBMK 厂房 · PWR 厂房 · Control Room 主控室 · Engineer Office 工程师办公室
- **Static 3D equipment / 立体静态设备**: distribution box 配电箱, analog console 仪控台, mimic panel 图屏, radiation monitor 辐射监测箱, fuel channel head 燃料通道头, service hatch 检修舱盖
- **Lights / 光源**: pure white (15) 纯白灯 · warm white (13) 暖白灯板
- **Blast tiers / 爆炸抗性四档**: 6 / 80 / 250 / 1200
- **Survival recipes / 全部可生存合成**
- **Languages / 语言**: English, 简体中文

## NTM-Continuum (HBM) — optional · 可选

| EN | 中文 |
|---|---|
| HBM is not required. | 不需要 HBM。 |
| Reinforced blocks join HBM blast-resistance tags. | 强化方块加入 HBM 防爆标签。 |
| 19 full-block walls join `hbm:radiation_resistant` and show [Radiation Shielding]. | 19 种满格墙体加入防辐射标签，并显示 [辐射屏蔽]。 |
| Slabs, stairs, panels and equipment are not sealed. | 半砖、台阶、薄板、设备不密封。 |
| Sealing is yes/no, with no attenuation percentage. | 密封为是/否判定，没有衰减百分比。 |

## Notes · 说明

- Decorative only: no reactor logic, energy, fluids or radiation measurement. / 仅装饰，无反应堆、能量、流体、辐射测量逻辑。
- Install on client **and** server. / 服务端与客户端都需安装。
- Remove old sheepnpp jars before updating. / 更新前删除旧版 jar。
- Minecraft 1.20.1 · Forge 47.4.28+ · Java 17.
```

---

## 4. 更新日志 / Changelog（Modrinth 版本说明）

### English
```markdown
## 0.1.2
- Added 10 RBMK building blocks: upper / lower biological shield, serpentinite shield, borated concrete, lead brick, laminated shield, support steel, support base, refuelling rail, crane girder
- Added 5 industrial floors
- Added 5 static 3D equipment models: analog control console, channel mimic panel, radiation monitor, fuel channel head, reactor service hatch
- Added 6 full-block radiation-sealing materials (19 in total)

## 0.1.1
- Added wall-mounted distribution box
- Removed the HBM load dependency that rejected installed HBM 1.0.5. HBM support now works through tags only.

## 0.1.0
- Initial release (do not install together with newer versions)
```

### 简体中文
```markdown
## 0.1.2
- 新增 10 个 RBMK 建筑方块：上/下生物屏蔽、蛇纹石屏蔽、硼混凝土、铅砖、复合屏蔽、支撑钢、支撑基座、换料轨道、吊车梁
- 新增 5 种工业地板
- 新增 5 个静态立体设备：苏式模拟仪控台、通道布置图屏、辐射监测箱、燃料通道头、反应堆检修舱盖
- 新增 6 个可密封辐射的满格材质（共 19 个）

## 0.1.1
- 新增壁挂配电箱
- 移除会拒绝已安装 HBM 1.0.5 的加载依赖，HBM 适配改为仅靠标签

## 0.1.0
- 初始版本（请勿与新版同时安装）
```

---

## 5. 上传前核对 / Pre-upload Checklist

- [ ] 图标 512×512 PNG（建议用印样表或配电箱截图；工程里目前没有现成图标，需要游戏内截图）
- [ ] 至少 3 张截图：RBMK 堆厅、主控室、办公室（需要在游戏里截取）
- [ ] 描述里的 HBM 效果尚未在游戏内验证，先发 Beta，并在页面保留“未验证”的措辞
- [ ] `0.1.0` 已知会触发 HBM 版本报错，不要上传该版本
- [ ] 许可证为 MIT，整合包可自由使用
- [ ] 源码链接填 GitHub 仓库地址，Issues 填其 `/issues`
- [ ] 许可证改为 MIT 后需重新构建 jar（`bash tools/check_release.sh`），SHA-256 会变化，以新 jar 为准
- [ ] SHA-256（0.1.2）：`04823d01e076dd7e33f1d43732e711ce29c44ac5ab0680ada2135ceb952dde85`

---

## 6. 语言文件说明 / Localization

- `assets/sheepnpp/lang/en_us.json`、`zh_cn.json` 各 100 条，键完全对应（方块 97 + 创造标签 1 + 悬停提示 2）。
- 文件由 `tools/gen_assets.py` 生成；若改译名，请改生成器再重新构建，否则会被覆盖。
- 悬停提示：`tooltip.sheepnpp.blastres`（爆炸抗性 / Blast Resistance）、`tooltip.sheepnpp.radshield`（辐射屏蔽 / Radiation Shielding）。
