package com.example.sheepnpp.block;

import net.minecraft.world.level.block.SoundType;

/** 表面材质：决定脚步声、挖掘工具，以及是否有镂空（影响遮挡与渲染层）。 */
public enum Surface {
    CONCRETE(SoundType.STONE, "pickaxe", false),
    METAL(SoundType.METAL, "pickaxe", false),
    GRATING(SoundType.METAL, "pickaxe", true),
    PLASTER(SoundType.STONE, "pickaxe", false),
    LAMP(SoundType.GLASS, "pickaxe", false),
    WOOD(SoundType.WOOD, "axe", false),
    CARPET(SoundType.WOOL, "none", false);

    public final SoundType sound;
    /** 挖掘工具标签：pickaxe / axe / none（不进 mineable 标签，徒手挖）。 */
    public final String tool;
    /** 贴图含透明像素：noOcclusion + cutout 渲染层。 */
    public final boolean open;

    Surface(SoundType sound, String tool, boolean open) {
        this.sound = sound;
        this.tool = tool;
        this.open = open;
    }
}
