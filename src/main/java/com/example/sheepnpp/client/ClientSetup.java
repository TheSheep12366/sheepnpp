package com.example.sheepnpp.client;

import com.example.sheepnpp.SheepNpp;
import com.example.sheepnpp.registry.ModBlocks;
import net.minecraft.client.renderer.ItemBlockRenderTypes;
import net.minecraft.client.renderer.RenderType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

/** 贴图含透明像素的方块（Surface.GRATING）走 cutout 渲染层。 */
@Mod.EventBusSubscriber(modid = SheepNpp.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ClientSetup {
    private ClientSetup() {}

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            RenderType cutout = RenderType.cutout();
            ModBlocks.CUTOUT.forEach(block -> ItemBlockRenderTypes.setRenderLayer(block.get(), cutout));
        });
    }
}
