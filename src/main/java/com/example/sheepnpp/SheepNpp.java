package com.example.sheepnpp;

import com.example.sheepnpp.registry.ModBlocks;
import com.example.sheepnpp.registry.ModCreativeTabs;
import com.example.sheepnpp.registry.ModItems;
import com.mojang.logging.LogUtils;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;

/** Sheep's Nuclear Plant Decor。内容规划见 docs/PLAN.md。 */
@Mod(SheepNpp.MOD_ID)
public class SheepNpp {
    public static final String MOD_ID = "sheepnpp";
    public static final Logger LOGGER = LogUtils.getLogger();

    public SheepNpp() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();

        ModBlocks.BLOCKS.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModCreativeTabs.CREATIVE_MODE_TABS.register(modBus);
    }
}
