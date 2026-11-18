package com.example.sheepnpp.block;

import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.shapes.VoxelShape;

/** North-facing prototype bounds; runtime configuration is entirely self-contained. */
public enum EquipmentProfile {
    RBMK_ANALOG_CONSOLE(Mount.FLOOR, 1, 0, 2, 15, 15, 14),
    RBMK_CHANNEL_MIMIC_PANEL(Mount.WALL, 1, 1, 13, 15, 15, 16),
    RBMK_RADIATION_MONITOR(Mount.WALL, 3, 2, 10, 13, 14, 16),
    RBMK_FUEL_CHANNEL_HEAD(Mount.FLOOR, 2, 0, 2, 14, 8, 14),
    RBMK_REACTOR_SERVICE_HATCH(Mount.WALL, 1, 1, 12, 15, 15, 16);

    public enum Mount { WALL, FLOOR }

    public final Mount mount;
    private final VoxelShape north;
    private final VoxelShape east;
    private final VoxelShape south;
    private final VoxelShape west;

    EquipmentProfile(Mount mount, double x0, double y0, double z0, double x1, double y1, double z1) {
        this.mount = mount;
        north = Block.box(x0, y0, z0, x1, y1, z1);
        east = Block.box(16 - z1, y0, x0, 16 - z0, y1, x1);
        south = Block.box(16 - x1, y0, 16 - z1, 16 - x0, y1, 16 - z0);
        west = Block.box(z0, y0, 16 - x1, z1, y1, 16 - x0);
    }

    public VoxelShape shape(Direction facing) {
        return switch (facing) {
            case NORTH -> north;
            case EAST -> east;
            case SOUTH -> south;
            case WEST -> west;
            default -> throw new IllegalArgumentException("Equipment must face horizontally");
        };
    }
}
