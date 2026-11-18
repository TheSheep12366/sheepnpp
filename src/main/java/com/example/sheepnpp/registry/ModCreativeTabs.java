package com.example.sheepnpp.registry;

import com.example.sheepnpp.SheepNpp;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/** 全部方块归在“建筑”一个标签页。 */
public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, SheepNpp.MOD_ID);

    public static final RegistryObject<CreativeModeTab> BUILDING = CREATIVE_MODE_TABS.register("building",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.sheepnpp.building"))
                    .icon(() -> new ItemStack(ModBlocks.PLANT_CONCRETE.block().get()))
                    .displayItems((parameters, output) -> ModBlocks.BUILDING_TAB.forEach(b -> output.accept(b.get())))
                    .build());

    private ModCreativeTabs() {}
}
