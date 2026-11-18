package com.example.sheepnpp.block;

/**
 * 防爆档位。爆炸抗性刻意卡在 NTM-Continuum 的阈值之上：
 * hbm:blast_resistant/large_explosion >= 70，/nuclear >= 200，/obsidian >= 1200。
 * 数值改动前先看 docs/PLAN.md 第 3.1 节，tools/audit_assets.py 会校验。
 */
public enum Tier {
    STANDARD(2.0F, 6.0F, "none"),
    REINFORCED(4.0F, 80.0F, "stone"),
    SHIELD(8.0F, 250.0F, "iron"),
    CONTAINMENT(30.0F, 1200.0F, "diamond");

    public final float hardness;
    public final float resistance;
    /** 工具等级标签后缀：none 不进 needs_* 标签。 */
    public final String toolTier;

    Tier(float hardness, float resistance, String toolTier) {
        this.hardness = hardness;
        this.resistance = resistance;
        this.toolTier = toolTier;
    }
}
