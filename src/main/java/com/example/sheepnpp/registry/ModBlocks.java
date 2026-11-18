package com.example.sheepnpp.registry;

import com.example.sheepnpp.SheepNpp;
import com.example.sheepnpp.block.EquipmentBlock;
import com.example.sheepnpp.block.EquipmentProfile;
import com.example.sheepnpp.block.PanelBlock;
import com.example.sheepnpp.block.Surface;
import com.example.sheepnpp.block.Tier;
import com.example.sheepnpp.block.WallMountedDistributionBoxBlock;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * 全部方块的注册表。每个注册写成单行调用，tools/gen_tags.py 和 tools/audit_assets.py 直接解析这些行，
 * 所以改格式前先看那两个脚本。
 *
 * <pre>
 * family(id, tier, surface, color, radSealed, slab, stairs)   满格 + 可选半砖/台阶，后两者为 id_slab / id_stairs
 * full(id, tier, surface, color, light, radSealed)            仅满格
 * panel(id, tier, surface, color, light, ceilingOnly)         4px 薄板
 * wallbox(id, tier, surface, color)                         Wall-mounted box
 * </pre>
 *
 * radSealed 只对满格有意义：进入 hbm:radiation_resistant 标签。半砖、台阶、薄板不密封，
 * 因为 HBM 的辐射分区把整格当墙，缝隙会被凭空封死。
 */
public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, SheepNpp.MOD_ID);

    /** 进入“建筑”创造标签页的方块（保序）。 */
    public static final List<Supplier<Block>> BUILDING_TAB = new ArrayList<>();
    /** 贴图含透明像素的方块，客户端走 cutout 渲染层。 */
    public static final List<Supplier<Block>> CUTOUT = new ArrayList<>();

    public record Family(RegistryObject<Block> block, RegistryObject<Block> slab, RegistryObject<Block> stairs) {}

    // ---- 共用厂房 plant_ ---------------------------------------------------
    public static final Family PLANT_CONCRETE = family("plant_concrete", Tier.SHIELD, Surface.CONCRETE, MapColor.STONE, true, true, true);
    static { family("plant_concrete_painted", Tier.REINFORCED, Surface.PLASTER, MapColor.COLOR_LIGHT_GRAY, true, true, true); }
    static { family("plant_lead", Tier.SHIELD, Surface.METAL, MapColor.METAL, true, true, true); }
    static { family("plant_hazard", Tier.STANDARD, Surface.PLASTER, MapColor.COLOR_YELLOW, false, true, true); }
    static { family("plant_grating", Tier.STANDARD, Surface.GRATING, MapColor.METAL, false, true, true); }
    static { family("plant_epoxy", Tier.STANDARD, Surface.PLASTER, MapColor.COLOR_GREEN, false, true, true); }
    static { panel("plant_ceiling", Tier.STANDARD, Surface.PLASTER, MapColor.SNOW, 0, true); }
    static { panel("plant_tray", Tier.STANDARD, Surface.GRATING, MapColor.METAL, 0, false); }
    static { panel("plant_vent", Tier.STANDARD, Surface.METAL, MapColor.METAL, 0, false); }
    static { panel("plant_trefoil", Tier.STANDARD, Surface.METAL, MapColor.COLOR_YELLOW, 0, false); }

    // ---- RBMK 厂房 rbmk_ ---------------------------------------------------
    static { family("rbmk_shield", Tier.CONTAINMENT, Surface.CONCRETE, MapColor.TERRACOTTA_GRAY, true, true, true); }
    static { family("rbmk_graphite", Tier.SHIELD, Surface.CONCRETE, MapColor.COLOR_BLACK, true, true, true); }
    static { family("rbmk_steel_green", Tier.REINFORCED, Surface.METAL, MapColor.TERRACOTTA_GREEN, true, true, true); }
    static { family("rbmk_channel", Tier.REINFORCED, Surface.METAL, MapColor.METAL, true, true, true); }
    static { panel("rbmk_channel_cover", Tier.STANDARD, Surface.METAL, MapColor.METAL, 0, false); }
    static { panel("rbmk_panel_mint", Tier.STANDARD, Surface.PLASTER, MapColor.COLOR_LIGHT_GREEN, 0, false); }

    static { full("rbmk_upper_bio_shield", Tier.CONTAINMENT, Surface.METAL, MapColor.METAL, 0, true); }
    static { full("rbmk_lower_bio_shield", Tier.CONTAINMENT, Surface.METAL, MapColor.METAL, 0, true); }
    static { full("rbmk_serpentinite_shield", Tier.SHIELD, Surface.CONCRETE, MapColor.TERRACOTTA_GREEN, 0, true); }
    static { full("rbmk_borated_concrete", Tier.SHIELD, Surface.CONCRETE, MapColor.TERRACOTTA_GRAY, 0, true); }
    static { full("rbmk_lead_brick", Tier.STANDARD, Surface.METAL, MapColor.COLOR_GRAY, 0, true); }
    static { full("rbmk_laminated_shield", Tier.CONTAINMENT, Surface.METAL, MapColor.METAL, 0, true); }
    static { full("rbmk_support_steel", Tier.CONTAINMENT, Surface.METAL, MapColor.TERRACOTTA_GREEN, 0, false); }
    static { full("rbmk_support_base", Tier.SHIELD, Surface.METAL, MapColor.COLOR_GRAY, 0, false); }
    static { full("rbmk_refuelling_rail", Tier.SHIELD, Surface.METAL, MapColor.METAL, 0, false); }
    static { full("rbmk_crane_girder", Tier.REINFORCED, Surface.METAL, MapColor.TERRACOTTA_GREEN, 0, false); }

    // ---- PWR 厂房 pwr_ -----------------------------------------------------
    static { family("pwr_containment", Tier.CONTAINMENT, Surface.CONCRETE, MapColor.COLOR_LIGHT_GRAY, true, true, true); }
    static { family("pwr_liner", Tier.REINFORCED, Surface.METAL, MapColor.METAL, true, true, true); }
    static { family("pwr_liner_white", Tier.REINFORCED, Surface.PLASTER, MapColor.SNOW, true, true, true); }
    static { family("pwr_deck", Tier.REINFORCED, Surface.METAL, MapColor.COLOR_LIGHT_BLUE, false, true, true); }
    static { panel("pwr_cladding", Tier.STANDARD, Surface.METAL, MapColor.METAL, 0, false); }
    static { panel("pwr_panel_white", Tier.STANDARD, Surface.PLASTER, MapColor.SNOW, 0, false); }

    // ---- 主控室 cc_ --------------------------------------------------------
    static { family("cc_wall_white", Tier.REINFORCED, Surface.PLASTER, MapColor.SNOW, true, true, true); }
    static { family("cc_wall_grey", Tier.REINFORCED, Surface.PLASTER, MapColor.COLOR_LIGHT_GRAY, true, true, true); }
    static { full("cc_wall_console", Tier.REINFORCED, Surface.PLASTER, MapColor.COLOR_GRAY, 0, true); }
    static { family("cc_floor_dark", Tier.STANDARD, Surface.PLASTER, MapColor.COLOR_GRAY, false, true, false); }
    static { family("cc_floor_light", Tier.STANDARD, Surface.PLASTER, MapColor.COLOR_LIGHT_GRAY, false, true, false); }
    static { full("cc_light_white", Tier.STANDARD, Surface.LAMP, MapColor.SNOW, 15, false); }
    static { panel("cc_light_white_panel", Tier.STANDARD, Surface.LAMP, MapColor.SNOW, 15, false); }
    static { panel("cc_ceiling", Tier.STANDARD, Surface.PLASTER, MapColor.SNOW, 0, true); }

    // ---- 工程师办公室 eo_ --------------------------------------------------
    static { family("eo_wall_beige", Tier.STANDARD, Surface.PLASTER, MapColor.SAND, false, true, true); }
    static { family("eo_wall_wood", Tier.STANDARD, Surface.WOOD, MapColor.WOOD, false, true, true); }
    static { family("eo_floor_carpet", Tier.STANDARD, Surface.CARPET, MapColor.COLOR_LIGHT_BLUE, false, true, false); }
    static { family("eo_floor_tile", Tier.STANDARD, Surface.CONCRETE, MapColor.COLOR_LIGHT_GRAY, false, true, false); }
    static { panel("eo_ceiling", Tier.STANDARD, Surface.PLASTER, MapColor.SNOW, 0, true); }
    static { panel("eo_light_panel", Tier.STANDARD, Surface.LAMP, MapColor.SNOW, 13, false); }

    public static final RegistryObject<Block> DISTRIBUTION_BOX = wallbox("distribution_box", Tier.STANDARD, Surface.METAL, MapColor.COLOR_LIGHT_GRAY);

    static { full("floor_heavy_load", Tier.SHIELD, Surface.METAL, MapColor.COLOR_GRAY, 0, false); }
    static { full("floor_turbine_hall", Tier.REINFORCED, Surface.METAL, MapColor.COLOR_LIGHT_BLUE, 0, false); }
    static { full("floor_equipment_room", Tier.REINFORCED, Surface.METAL, MapColor.COLOR_LIGHT_GRAY, 0, false); }
    static { full("floor_maintenance_tread", Tier.STANDARD, Surface.METAL, MapColor.METAL, 0, false); }
    static { full("floor_decontamination_ceramic", Tier.STANDARD, Surface.CONCRETE, MapColor.COLOR_LIGHT_BLUE, 0, false); }

    static { equipment("rbmk_analog_console", Tier.STANDARD, Surface.METAL, MapColor.COLOR_GRAY, EquipmentProfile.RBMK_ANALOG_CONSOLE); }
    static { equipment("rbmk_channel_mimic_panel", Tier.STANDARD, Surface.METAL, MapColor.COLOR_LIGHT_GRAY, EquipmentProfile.RBMK_CHANNEL_MIMIC_PANEL); }
    static { equipment("rbmk_radiation_monitor", Tier.STANDARD, Surface.METAL, MapColor.COLOR_LIGHT_GRAY, EquipmentProfile.RBMK_RADIATION_MONITOR); }
    static { equipment("rbmk_fuel_channel_head", Tier.SHIELD, Surface.METAL, MapColor.METAL, EquipmentProfile.RBMK_FUEL_CHANNEL_HEAD); }
    static { equipment("rbmk_reactor_service_hatch", Tier.REINFORCED, Surface.METAL, MapColor.COLOR_GRAY, EquipmentProfile.RBMK_REACTOR_SERVICE_HATCH); }

    private ModBlocks() {}

    private static BlockBehaviour.Properties props(Tier tier, Surface surface, MapColor color, int light) {
        BlockBehaviour.Properties props = BlockBehaviour.Properties.of()
                .mapColor(color)
                .strength(tier.hardness, tier.resistance)
                .sound(surface.sound);
        if (surface.tool.equals("pickaxe")) {
            props.requiresCorrectToolForDrops();
        }
        if (surface.open) {
            props.noOcclusion();
        }
        if (light > 0) {
            props.lightLevel(state -> light);
        }
        return props;
    }

    private static Family family(String id, Tier tier, Surface surface, MapColor color,
                                 boolean radSealed, boolean slab, boolean stairs) {
        RegistryObject<Block> base = register(id, surface, () -> new Block(props(tier, surface, color, 0)));
        RegistryObject<Block> slabBlock = slab
                ? register(id + "_slab", surface, () -> new SlabBlock(props(tier, surface, color, 0))) : null;
        RegistryObject<Block> stairsBlock = stairs
                ? register(id + "_stairs", surface,
                        () -> new StairBlock(() -> base.get().defaultBlockState(), props(tier, surface, color, 0))) : null;
        return new Family(base, slabBlock, stairsBlock);
    }

    private static RegistryObject<Block> full(String id, Tier tier, Surface surface, MapColor color,
                                              int light, boolean radSealed) {
        return register(id, surface, () -> new Block(props(tier, surface, color, light)));
    }

    private static RegistryObject<Block> panel(String id, Tier tier, Surface surface, MapColor color,
                                               int light, boolean ceilingOnly) {
        return register(id, surface,
                () -> new PanelBlock(props(tier, surface, color, light).noOcclusion(), ceilingOnly));
    }

    private static RegistryObject<Block> wallbox(String id, Tier tier, Surface surface, MapColor color) {
        return register(id, surface,
                () -> new WallMountedDistributionBoxBlock(props(tier, surface, color, 0).noOcclusion()));
    }

    private static RegistryObject<Block> equipment(String id, Tier tier, Surface surface, MapColor color,
                                                    EquipmentProfile profile) {
        return register(id, surface,
                () -> new EquipmentBlock(props(tier, surface, color, 0).noOcclusion()
                        .isRedstoneConductor((state, level, pos) -> false)
                        .isSuffocating((state, level, pos) -> false)
                        .isViewBlocking((state, level, pos) -> false), profile));
    }

    private static RegistryObject<Block> register(String id, Surface surface, Supplier<Block> factory) {
        RegistryObject<Block> block = BLOCKS.register(id, factory);
        ModItems.ITEMS.register(id, () -> new BlockItem(block.get(), new Item.Properties()));
        BUILDING_TAB.add(block);
        if (surface.open) {
            CUTOUT.add(block);
        }
        return block;
    }
}
