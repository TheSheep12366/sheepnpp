# 壁挂配电箱样件

现代工业浅灰配电箱，作为 004 首个立体装饰模型试作。外观已获用户认可，0.1.1 将同一模型与贴图接入正式模组，注册名为 `distribution_box`；本目录保留可编辑源文件。

- 28 个长方体元素，全部位于一格 16×16×16 的范围内。
- 箱体、门板与密封边分层，包含独立铰链、拉手、钥匙孔、三道百叶、绿色指示点、黄色电气标识和两个底部进线口。
- 原型正面朝北（-Z），背部位于 z=16；正式方块根据点击墙面水平旋转，背面贴墙。
- 图集为 32×32 RGBA，其中门板与箱体各使用一个 16×16 区域，五金共用小型色块；没有透明贴图、动画或方块实体。
- Blockbench `check_model` 检查为 0 问题：无漏贴图、越界 UV、退化元素或共面重叠报告。

## 文件

- `distribution_box.bbmodel`：可编辑工程，内含贴图。
- `distribution_box.json`：按 Minecraft 1.20.1 elements 格式导出的模型，包含父模型与 particle 引用。
- `distribution_box.png`：32×32 图集，由 Blockbench 编码和写盘。
- `paint_texture.js`：Blockbench 内的可重复贴图绘制脚本。
- `export_java_1_20_1.js`：Blockbench 内的导出脚本，移除新版编辑器标记并补充材质粒子。

模型中的纹理路径为 `sheepnpp:block/distribution_box`，`tools/gen_assets.py` 从本目录同步模型与图集到正式 assets，并生成四向状态等配套资源。破坏粒子使用原版浅灰混凝土纹理，避免打碎时出现整张图集。

本轮只检查 Blockbench 效果和模型结构，没有启动服务端或客户端。
