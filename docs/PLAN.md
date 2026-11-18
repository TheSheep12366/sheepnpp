# Sheep's Nuclear Plant Decor（羊's 核电站装饰方块）计划书

> 版本：v1.2（2026-11-14）
> 状态：0.1.2 新增 15 建筑块与 5 立体模型，全部 97 个注册项资源已落地，运行时效果待用户自行验证
> 平台：**Minecraft 1.20.1 / Forge 47.4.28 / Java 17 / Gradle 8.8**（与 `001` 同一套已缓存 userdev）
> 贴图做法：沿用 [`001/docs/TEXTURE_PIPELINE.md`](../../001/docs/TEXTURE_PIPELINE.md)，不另起一套画法
> 建筑形态：**满格方块 / 半砖 / 台阶 / 薄板**；0.1.1 新增首个静态立体装饰：壁挂配电箱

“RMBK” 按反应堆型号记为 **RBMK**（大功率通道式石墨沸水堆）。方块 ID 前缀用 `rbmk_`。

---

## 1. 定位与风格

纯装饰模组。用现代工业与现代办公的材质，把 **RBMK 厂房、PWR 厂房、主控室、工程师办公区** 搭出来。

**“现代”的具体含义**（所有贴图必须满足，不满足就重画）：

- 大幅面板 + 细缝，不做小砖块和碎石感。板缝 1px，低对比。
- 哑光为主。高光只出现在不锈钢和灯面，窄而克制。
- 色板低饱和，饱和色只给警示条、三叶符、状态点。
- 不做做旧、污渍、锈迹、裂纹。
- 满格方块遵守 R1–R7，细颗粒是原版混凝土那种 1px、±3 级。

四个区域靠色调分开，并排放在一起也能认出来：

| 区域 | 前缀 | 色调 | 用途 |
|---|---|---|---|
| 共用厂房 | `plant_` | 冷灰混凝土、警示黄、铅灰 | 两种堆型通用的结构、地面、桥架 |
| RBMK 厂房 | `rbmk_` | 暖灰屏蔽层、近黑石墨、灰绿钢板、薄荷控制面板 | 堆厅、屏蔽墙、通道层 |
| PWR 厂房 | `pwr_` | 冷灰安全壳、冷银衬里、暖白内衬、蓝灰甲板 | 安全壳、辅助厂房、汽机厅 |
| 主控室 | `cc_` | 白、浅灰、深灰、纯白灯面 | 控制室墙地顶、灯光 |
| 工程师办公室 | `eo_` | 米白、浅木、灰蓝地毯、浅色地砖 | 办公、会议、走廊 |

### 明确不做

- 管道、控制棒、燃料组件、压力容器、汽轮机、泵、阀门
- 多方块结构、方块实体、辐射 / 热量 / 流体 / 能量的本体逻辑
- 门、窗、栏杆、梯子、按钮、压力板、家具（都要自定义或半自定义模型）
- 动画、GeckoLib
- 对 HBM 的**编译期**依赖（见第 3 节）

玻璃留到以后，本轮不注册。

---

## 2. 技术基线

| 项 | 值 |
|---|---|
| Minecraft | 1.20.1（`[1.20.1,1.21)`） |
| Forge | 47.4.28（`[47,)`） |
| Java | 17 |
| Gradle | wrapper 8.8（从 `001` 复用） |
| 映射 | official / 1.20.1 |
| modId | `sheepnpp` |
| 包名 | `com.example.sheepnpp` |
| 显示名 | Sheep's Nuclear Plant Decor / 羊's 核电站装饰方块 |
| 创造标签 | 一个：`sheepnpp.building` |
| 构建 | `./gradlew build`，无头机不跑 `runClient` |
| 代理 | `192.168.0.78:10808`，只通过命令行 `-D` 传给 Gradle，不写进仓库 |

---

## 3. NTM-Continuum（HBM）适配

目标：只适配社区高版本 **[NTM-Continuum](https://github.com/Warfactory-Official/NTM-Continuum)**（modId `hbm`，1.20.1-forge 节点，Forge 47.2.30 起）。不支持 1.7.10 / 1.12.2 的旧 HBM。

已读其源码确认两条接口，**都不需要编译依赖 HBM**：

### 3.1 防爆

HBM 使用原版 `Block.getExplosionResistance()`，其材质分类标签按下列阈值划分。本模组通过 `gen_tags.py` 显式生成对应方块及物品标签；不能依赖 HBM 的本体数据生成器自动收录附属方块。

| HBM 标签 | 爆炸抗性阈值 | 含义 |
|---|---|---|
| `hbm:blast_resistant/large_explosion` | ≥ 70 | HBM 大型爆炸抗性分类 |
| `hbm:blast_resistant/nuclear` | ≥ 200 | HBM 核爆抗性分类 |
| `hbm:blast_resistant/obsidian` | ≥ 1200 | 与黑曜石同级 |

本模组设置 `strength(硬度, 抗爆)` 并生成对应分类标签。方块分四档，半砖和台阶通过同一档位参数取得相同抗性。分类阈值不代表所有特殊爆炸的绝对免疫：

| 档位 | 硬度 | 爆炸抗性 | 挖掘 | 命中的 HBM 标签 |
|---|---|---|---|---|
| `STANDARD` | 2.0 | 6 | 镐 | 无 |
| `REINFORCED` | 4.0 | 80 | 镐 + 石质 | `large_explosion` |
| `SHIELD` | 8.0 | 250 | 镐 + 铁质 | + `nuclear` |
| `CONTAINMENT` | 30.0 | 1200 | 镐 + 钻石 | + `obsidian` |

### 3.2 防辐射

HBM 的辐射引擎用泛洪分区，把“辐射密封方块”当成墙。除了它自己的 `IRadResistantBlock` 类，还认**方块标签 `hbm:radiation_resistant`**（源码注释写明供附属使用）。

做法：本模组提供 `data/hbm/tags/blocks/radiation_resistant.json`，列出要密封的方块。没装 HBM 时这个标签没人读，无副作用；装了就自动生效。

规则：

- **只有满格方块**可以进该标签。泛洪分区把整格当墙，半砖、台阶、薄板进去会凭空封死缝隙。
- 半砖、台阶仍然享有防爆（继承抗性），但不防辐射。
- 通透的格栅、桥架、地毯、普通办公装饰不密封。
- 标签文件由 `tools/gen_tags.py` 从 `ModBlocks.java` 生成，不手写。

### 3.3 mods.toml 与版本检查修复

0.1.1 完全移除 HBM 的加载器依赖声明，只保留 Forge 与 Minecraft 必需依赖。HBM 适配依靠标签和可选运行时检测，不需要版本范围或加载顺序约束。

已定位 0.1.0 的报错根因：`mandatory=false` 不会跳过对已安装依赖的版本检查，而 `versionRange=""` 在 Maven `VersionRange.containsVersion(1.0.5)` 中返回 false；空字符串并不表示接受任意版本。已用构建环境中的 Maven 库独立复现，没有启动游戏。

`tools/check_mod_metadata.py` 直接检查最终 jar：依赖只能为 Forge/Minecraft，不允许再出现 HBM 加载限制，同时检查壁挂配电箱的模型、四向状态、图集及 HBM 标签是否打包。

### 3.4 验证方式（先说清楚能验证什么）

悬停提示已实现：爆炸抗性大于 50 时显示金色 `爆炸抗性: 数值`；防辐射满格显示深绿色 `[辐射屏蔽]`。装有 HBM 时屏蔽提示由 HBM 依据标签显示，未安装时由本模组补充；爆炸抗性提示由本模组补充，因为 HBM 的这一行只对自己的命名空间生效。仅完成代码与编译校验，未启动客户端验证悬停画面。

按用户最新要求，不再启动服务端或客户端测试；后续使用资源审计、像素校验和 Gradle 构建。

| 项 | 能否在本机验证 | 做法 |
|---|---|---|
| 抗爆数值 | 能 | `tools/audit_assets.py` 解析 `ModBlocks.java`，核对每档抗性 ≥ 阈值 |
| 标签文件与注册一致 | 能 | 同上，标签内 id 必须全是已注册满格方块 |
| HBM 实际认标签 | **不能**（无头机不跑游戏） | 在能运行客户端的那台电脑上，装 NTM-Continuum，`/give` 方块后看 HBM 的方块特性提示，用爆炸和辐射源实测一次 |

---

## 4. 形态约定

| 形态 | 实现 | 模型 |
|---|---|---|
| 满格 | `Block` | `cube_all` |
| 半砖 | `SlabBlock` | 原版 slab / slab_top |
| 台阶 | `StairBlock` | 原版 stairs / inner / outer |
| 薄板 | 移植 `001` 的 `PanelBlock`（4px，六向吸附） | 元素模型 |

- 同材质的满格、半砖、台阶**共用一张贴图**。
- 满格六面同一张图，本轮不做 side / end 分面。
- 薄板：整张图是大面，四边等宽斜角边框，下边框带兼作侧面（R3）。模型写 `particle`（R7），全模组共用一张 `particle_chip`。
- 贴图含透明像素的才注册 `cutout`，当前只有格栅和桥架。
- 灯：满格灯 15 级；薄板灯 15 / 13 级。灯面贴图自己是亮的，不用 emissive 渲染。

---

## 5. 方块清单（原 77 + 本轮 20）

形态简写：**F** 满格，**S** 半砖，**T** 台阶，**P** 薄板。
“防辐射”列：✔ 表示该材质的**满格**进 `hbm:radiation_resistant`。

### 5.1 共用厂房 `plant_`（22）

| 材质 | ID 前缀 | 形态 | 档位 | 防辐射 | 贴图身份 |
|---|---|---|---|---|---|
| 清水混凝土 | `plant_concrete` | F S T | SHIELD | ✔ | 大幅模板板印 + 1px 细颗粒 + 规则拉杆孔点 |
| 涂装混凝土 | `plant_concrete_painted` | F S T | REINFORCED | ✔ | 浅灰哑光漆 + 一道低对比板缝 |
| 铅板 | `plant_lead` | F S T | SHIELD | ✔ | 冷蓝灰金属板 + 窄缝 + 四角螺栓 |
| 黄黑警示 | `plant_hazard` | F S T | STANDARD | — | 45° 黄黑条，两色 |
| 钢格栅 | `plant_grating` | F S T | STANDARD | — | 格阵，孔用 `.`，`cutout` |
| 去污地坪 | `plant_epoxy` | F S T | STANDARD | — | 灰绿树脂 + 1px 微反光 |
| 吊顶板 | `plant_ceiling` | P（仅天花板） | STANDARD | — | 浅灰，内区两枚螺丝 |
| 电缆桥架 | `plant_tray` | P | STANDARD | — | 内区横档，档间 `.`，`cutout` |
| 通风百叶 | `plant_vent` | P | STANDARD | — | 内区横向百叶缝 |
| 辐射标识板 | `plant_trefoil` | P | STANDARD | — | 黄底三叶符，四边仍是斜角边框 |

### 5.2 RBMK 厂房 `rbmk_`（14）

| 材质 | ID 前缀 | 形态 | 档位 | 防辐射 | 贴图身份 |
|---|---|---|---|---|---|
| 生物屏蔽 | `rbmk_shield` | F S T | CONTAINMENT | ✔ | 偏暖深灰大板，细骨料，和 `plant_concrete` 必须分得开 |
| 石墨砌块 | `rbmk_graphite` | F S T | SHIELD | ✔ | 近黑石墨 + 1px 晶点，规整砌块缝 |
| 灰绿钢板 | `rbmk_steel_green` | F S T | REINFORCED | ✔ | 灰绿哑光漆 + 竖向板缝 + 少量螺栓 |
| 通道端面 | `rbmk_channel` | F S T | REINFORCED | ✔ | 金属底 + 规则孔阵（平面贴图，不做凹陷模型） |
| 通道盖板 | `rbmk_channel_cover` | P | STANDARD | — | 金属面 + 中央螺栓 |
| 薄荷面板 | `rbmk_panel_mint` | P | STANDARD | — | 薄荷漆面板，内区一条暗槽 |

### 5.3 PWR 厂房 `pwr_`（14）

| 材质 | ID 前缀 | 形态 | 档位 | 防辐射 | 贴图身份 |
|---|---|---|---|---|---|
| 安全壳混凝土 | `pwr_containment` | F S T | CONTAINMENT | ✔ | 冷灰大板 + 浅缝，比 RBMK 屏蔽干净 |
| 不锈钢衬里 | `pwr_liner` | F S T | REINFORCED | ✔ | 冷银拉丝 + 窄缝，高光窄 |
| 涂白内衬 | `pwr_liner_white` | F S T | REINFORCED | ✔ | 暖白哑光漆 + 浅板缝 |
| 汽机甲板 | `pwr_deck` | F S T | REINFORCED | — | 蓝灰金属板 + 四角螺栓 |
| 保温覆层 | `pwr_cladding` | P | STANDARD | — | 内区横向接缝 |
| 白面板 | `pwr_panel_white` | P | STANDARD | — | 白面板，内区细槽，和涂白内衬不同图 |

### 5.4 主控室 `cc_`（14）

| 材质 | ID 前缀 | 形态 | 档位 | 防辐射 | 贴图身份 |
|---|---|---|---|---|---|
| 白色墙板 | `cc_wall_white` | F S T | REINFORCED | ✔ | 白色哑光大板，1px 缝，四边留 1px 浅边 |
| 灰色吸音墙板 | `cc_wall_grey` | F S T | REINFORCED | ✔ | 浅灰板面，规则细孔阵（吸音，不透空） |
| 控制台面板墙 | `cc_wall_console` | F | REINFORCED | ✔ | 深灰面板 + 细缝 + 少量状态点，饱和色面积 < 5% |
| 深色地板 | `cc_floor_dark` | F S | STANDARD | — | 深灰防静电面板，四角隐形螺丝 |
| 浅色地板 | `cc_floor_light` | F S | STANDARD | — | 浅灰防静电面板 |
| 纯白灯 | `cc_light_white` | F（发光 15） | STANDARD | — | 整面纯白灯面 + 极淡边框，无色偏 |
| 纯白灯板 | `cc_light_white_panel` | P（发光 15） | STANDARD | — | 白色发光面 + 浅灰斜角边框 |
| 控制室吊顶 | `cc_ceiling` | P（仅天花板） | STANDARD | — | 白色吸音吊顶，细缝 |

### 5.5 工程师办公室 `eo_`（12）

| 材质 | ID 前缀 | 形态 | 档位 | 防辐射 | 贴图身份 |
|---|---|---|---|---|---|
| 米白涂料墙 | `eo_wall_beige` | F S T | STANDARD | — | 米白哑光 + 1px 细颗粒，无缝 |
| 浅木饰面板 | `eo_wall_wood` | F S T | STANDARD | — | 浅色木纹竖向板条，窄缝，现代北欧感 |
| 灰蓝地毯 | `eo_floor_carpet` | F S | STANDARD | — | 灰蓝簇绒，1px 细颗粒，无图案 |
| 浅色地砖 | `eo_floor_tile` | F S | STANDARD | — | 大幅浅灰瓷砖 + 细缝 |
| 办公吊顶 | `eo_ceiling` | P（仅天花板） | STANDARD | — | 白色矿棉板，细缝 |
| 暖白灯板 | `eo_light_panel` | P（发光 13） | STANDARD | — | 暖白发光面，轻微偏黄 |

### 5.6 数量核对

| 项 | 数 |
|---|---|
| 注册方块 | **97** |
| 满格 | 39 |
| 半砖 | 22 |
| 台阶 | 18 |
| 薄板 | 12 |
| 壁挂配电箱 | 1（静态立体模型） |
| RBMK 立体设备 | 5（2 落地、3 壁挂） |
| 本轮新增 | 20（10 RBMK 建筑块 + 5 新地板 + 5 模型） |
| 实际独立贴图 | **58**（52 张 16×16 建筑贴图 + 6 张 32×32 模型图集） |
| 防辐射满格 | 19 |

防辐射满格：原 13 个保留，新增上下生物屏蔽、蛇纹石屏蔽、硼化屏蔽混凝土、铅衬砌块、复合屏蔽夹层，共 19 个。新增地板和所有非满格设备均不密封。以 `gen_tags.py` 生成标签及成品 jar 的保护组合检查为准。

### 5.7 壁挂配电箱（0.1.1）

注册名 `distribution_box`，中文“壁挂配电箱”，沿用用户认可的 28 元素浅灰样件和独立 32×32 图集。模型含门板、铰链、拉手、百叶、电气标识和底部进线口；仅装饰，无方块实体、电力网络或开门动画。

放置朝向由点击墙面决定，使用 `HORIZONTAL_FACING` 的东、南、西、北四个状态：背面贴住反方向支撑墙，正面朝外。模型、碰撞箱和结构旋转同步；不接受地面或天花板放置，失去支撑时掉落。原型正面为 -Z，背部到 z=16。

`STANDARD` 抗性档位，使用镐挖掘，不加入辐射密封标签。破坏粒子使用原版浅灰混凝土材质，不使用整张设备图集。方块拥有独立物品模型、合成配方、战利品、中英名称及创造标签页条目。

### 5.8 RBMK 堆厅扩充（0.1.2）

完整 20 项清单、参考资料、防护组合及原创性约束见 [RBMK_EXPANSION.md](RBMK_EXPANSION.md)。本轮不参考或复制 001/002/003 模组设计。10 个 RBMK 满格、5 个原创地板、5 个真实模型，均有完整资源和合成配方。

仪控台有倾斜台面和独立表盘/拨杆；另外四个模型为通道图屏、辐射监测箱、燃料通道头和手轮检修舱盖。5 个模型均有四向状态和相应碰撞箱。壁挂模型朝点击墙面正向，落地模型朝玩家；不提供电力、燃料、辐射测量或开门功能。

---

## 6. 开工清单

### B0 工程骨架

- [x] 读 NTM-Continuum 源码，确认防爆 / 防辐射接口
- [x] 计划书重写（现代风格、76 个方块、HBM 适配）
- [x] 复制 Gradle / wrapper，改成 `sheepnpp`
- [x] 主类、`ModBlocks`（原建筑 76 个，0.1.1 增至 77 个注册）、`ModItems`、`ModCreativeTabs`、`ClientSetup`
- [x] 移植 `PanelBlock`
- [x] `mods.toml`（仅 Forge/Minecraft 必需依赖，HBM 不声明加载依赖）、`pack.mcmeta`
- [x] `tools/gen_tags.py` 生成挖掘 / 工具等级 / `hbm:radiation_resistant` 标签
- [x] `tools/audit_assets.py` 核对注册、抗性档位、标签
- [x] `./gradlew build` 通过（走代理，首次约 15 分钟，主要是 MCP 环境初始化）

构建命令（代理只走命令行，不写进仓库）：

```bash
./gradlew build --console=plain \
  -Dhttp.proxyHost=192.168.0.78 -Dhttp.proxyPort=10808 \
  -Dhttps.proxyHost=192.168.0.78 -Dhttps.proxyPort=10808 \
  -Dhttp.nonProxyHosts="localhost|127.*|192.168.*"
```

97 个注册方块物品及其资源已全部生成，共 58 张贴图（含粒子和设备图集）。每个方块都有 blockstate、模型、物品模型、配方、战利品及中英名称。

### B1 贴图工具

- [x] 复制 `texture_pipeline.py`、`texture_spec.py`、`blockbench_render_texture.js`、印样表、平铺脚本，改成 `sheepnpp`
- [x] 先跑通 `particle_chip` + `plant_concrete` 一条链路（build → Blockbench → verify）

### B2 共用 `plant_`　B3 RBMK　B4 PWR　B5 主控室 `cc_`　B6 办公室 `eo_`

每批的完成标准相同：

- [x] B2 共用厂房：22 个方块，10 张材质贴图，模型/配方/战利品/中英语言齐全
- [x] B3 RBMK：14 个方块，6 张材质贴图，资源齐全；两批合计 17 张贴图（含粒子），逐像素校验、体检、接缝检测通过
- [x] B4 PWR：14 个方块，6 张材质贴图；模型、状态、配方、战利品和中英语言齐全
- [x] B5 主控室：14 个方块，8 张材质贴图；纯白灯为 15 级光照，中性 RGB 白，不偏蓝黄
- [x] B6 工程师办公室：12 个方块，6 张材质贴图；米白墙、浅木、灰蓝地毯、地砖和 13 级暖白灯板

- [x] 贴图进 `texture_spec.py`，`verify` / `audit` / `seams` 全 ok
- [x] 每个方块成套：blockstate、方块模型、物品模型、配方、战利品、zh_cn、en_us
- [x] 台阶带 inner / outer 模型；薄板带 `particle`
- [x] 印样表目视检查：不同材质、办公区与厂房区的色调可区分

0.1.2 静态验证：建筑贴图 `verify` 为 52/52 像素一致，`audit` 全部 ok，满格横纵接缝连续；6 张 32×32 设备图集单独审计。`audit_assets.py --strict` 严格检查全部 97 个注册项通过，无缺失或孤儿资源。壁挂/落地设备均检查四向模型与碰撞箱及支撑侧，防护组合还会从成品 jar 的标签中核对。没有启动服务端或客户端。

最终构建：`bash tools/check_release.sh` 已全部通过，产物 `build/libs/sheepnpp-0.1.2.jar`。已从成品确认仅含 Forge/Minecraft 加载依赖、97 份方块状态/物品模型/配方/战利品、58 张贴图；铅衬密封弱抗爆、承重钢构强抗爆不密封、生物屏蔽双防护等标签组合均通过成品检查。

SHA-256：`654769a06fe42b1869a9e753bb5fb66f8d1b149823d2a7b93058f746169a0045`。

安装新版时移除旧 sheepnpp jar，不能同时放入多个版本。

MC 工具扫描 409 个资源文件，无孤儿贴图。仅对原版粒子纹理 `minecraft:block/light_gray_concrete` 和 `minecraft:block/gray_concrete` 提出本地资源查找警告；已从 1.20.1 原版 jar 确认两者存在，属于工具未跨命名空间定位原版资源，并非缺失贴图。

旧的 0.1.0 存在空版本范围导致的 HBM 加载报错，应从游戏 `mods` 目录移除，以 0.1.1 替换，不能同时安装两个版本。

Blockbench 贴图存档：`docs/factory_textures.bbmodel`，含 52 张建筑贴图，已保存并关闭项目。6 套设备独立 `.bbmodel` 位于 `prototypes/distribution_box/` 与 `prototypes/rbmk_equipment/`，全部已保存并关闭。新增设备逐一视图检查，`check_model` 最终均为 0 问题。

薄板方向修正：`FACING` 表示可见面，板体位于反方向的支撑侧。已修正南北模型旋转和水平碰撞箱；审计器按原版 `BlockModelRotation` 的负角度计算六向模型边界，逐一与 Java 碰撞箱及支撑侧核对，12 种薄板全部通过。

### B7 收尾

- [x] 注册数 = 97，贴图数 = 58，无孤儿资源
- [x] 完成贴图回读、体检、接缝检测、印样表目视及 Blockbench 存档并关闭；GLM 评审不可用，见校验约定
- [x] 回填第 5.6 节实际数量
- [ ] HBM 运行时效果与悬停画面待用户自行验证（本机不启动服务端或客户端）

### 校验约定

- `bash tools/check_release.sh`：一键运行标签、像素、材质、接缝、全部资源严格审计和离线构建，不启动游戏。
- `python3 tools/audit_assets.py --strict`：严格检查全部 97 个注册项；包括语言键、纯白灯无色偏、薄板六向几何、设备四向几何和安装方式、双半砖掉落和孤儿资源。
- `python3 tools/texture_pipeline.py verify tools/texture_spec.json`：逐像素回读所有已绘贴图。
- `audit` 检查材质颗粒与边框，`seams` 检查横、纵两个方向的平铺接缝。
- `./gradlew build --offline --console=plain`：编译并重新混淆输出 jar，不启动游戏。
- 当前没有 GLM Vision 服务可用，贴图以印样表人工目视、ASCII 图案和像素审计交叉检查，未进行 GLM 评审。

---

## 7. 每个方块要落地的文件

| 文件 | 路径 |
|---|---|
| 注册 | `registry/ModBlocks.java` |
| 方块状态 | `assets/sheepnpp/blockstates/<id>.json` |
| 方块模型 | `assets/sheepnpp/models/block/<id>.json`（台阶另有 inner / outer） |
| 物品模型 | `assets/sheepnpp/models/item/<id>.json` |
| 配方 | `data/sheepnpp/recipes/<id>.json` |
| 战利品 | `data/sheepnpp/loot_tables/blocks/<id>.json` |
| 语言 | `assets/sheepnpp/lang/zh_cn.json`、`en_us.json` |
| 标签 | `tools/gen_tags.py` 生成：`mineable/*`、`needs_*_tool`、`hbm:radiation_resistant` |
