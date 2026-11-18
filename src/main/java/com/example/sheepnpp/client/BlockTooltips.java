package com.example.sheepnpp.client;

import com.example.sheepnpp.SheepNpp;
import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;

/**
 * 悬停提示，格式与 NTM-Continuum 的 BlockTraitTooltips 一致：
 *   [辐射屏蔽]         读 hbm:radiation_resistant 标签，深绿色
 *   爆炸抗性: 250.0    爆炸抗性大于 50 时显示，金色
 *
 * HBM 自己的提示对任何命名空间的“辐射屏蔽”都生效，但“爆炸抗性”只给 hbm 命名空间的方块显示，
 * 所以爆炸抗性这一行始终由本模组补；辐射屏蔽只在没装 HBM 时补，避免重复。
 */
@Mod.EventBusSubscriber(modid = SheepNpp.MOD_ID, value = Dist.CLIENT)
public final class BlockTooltips {
    private static final TagKey<Block> RADIATION_RESISTANT =
            TagKey.create(Registries.BLOCK, new ResourceLocation("hbm", "radiation_resistant"));
    private static final float BLAST_DISPLAY_THRESHOLD = 50.0F;

    private BlockTooltips() {}

    @SubscribeEvent
    public static void onTooltip(ItemTooltipEvent event) {
        if (!(event.getItemStack().getItem() instanceof BlockItem item)) {
            return;
        }
        Block block = item.getBlock();
        if (!SheepNpp.MOD_ID.equals(BuiltInRegistries.BLOCK.getKey(block).getNamespace())) {
            return;
        }

        boolean hbmLoaded = ModList.get().isLoaded("hbm");
        if (!hbmLoaded && block.defaultBlockState().is(RADIATION_RESISTANT)) {
            event.getToolTip().add(Component.literal("[")
                    .append(Component.translatable("tooltip.sheepnpp.radshield"))
                    .append("]")
                    .withStyle(ChatFormatting.DARK_GREEN));
        }

        float resistance = block.getExplosionResistance();
        if (resistance > BLAST_DISPLAY_THRESHOLD) {
            event.getToolTip().add(Component.translatable("tooltip.sheepnpp.blastres", String.valueOf(resistance))
                    .withStyle(ChatFormatting.GOLD));
        }
    }
}
