package com.example.sheepnpp.registry;

import com.example.sheepnpp.SheepNpp;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;

/** 方块物品由 ModBlocks 登记，这里只保留注册器。 */
public final class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, SheepNpp.MOD_ID);

    private ModItems() {}
}
