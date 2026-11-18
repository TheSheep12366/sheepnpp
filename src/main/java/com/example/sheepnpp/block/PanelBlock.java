package com.example.sheepnpp.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * 4px 薄板：点击哪个面就吸附在哪个面上。ceilingOnly 的吊顶类只能吸附天花板（点击上方方块的底面）。
 * 吸附面的支撑方块消失时薄板一并破坏。
 *
 * FACING 记录的是被点击的面（贴天花板时为 DOWN），而支撑方块在该面的反方向，所以比较时取 getOpposite()。
 */
public class PanelBlock extends Block {
    public static final DirectionProperty FACING = BlockStateProperties.FACING;

    private static final VoxelShape SHAPE_DOWN = Block.box(0, 12, 0, 16, 16, 16);
    private static final VoxelShape SHAPE_UP = Block.box(0, 0, 0, 16, 4, 16);
    // FACING 是可见面的朝向；板体必须贴在其反方向的支撑方块一侧。
    private static final VoxelShape SHAPE_NORTH = Block.box(0, 0, 12, 16, 16, 16);
    private static final VoxelShape SHAPE_SOUTH = Block.box(0, 0, 0, 16, 16, 4);
    private static final VoxelShape SHAPE_WEST = Block.box(12, 0, 0, 16, 16, 16);
    private static final VoxelShape SHAPE_EAST = Block.box(0, 0, 0, 4, 16, 16);

    private final boolean ceilingOnly;

    public PanelBlock(Properties properties, boolean ceilingOnly) {
        super(properties);
        this.ceilingOnly = ceilingOnly;
        registerDefaultState(stateDefinition.any().setValue(FACING, Direction.DOWN));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        Direction face = context.getClickedFace();
        if (ceilingOnly && face != Direction.DOWN) {
            return null;
        }
        return defaultBlockState().setValue(FACING, face);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return switch (state.getValue(FACING)) {
            case DOWN -> SHAPE_DOWN;
            case UP -> SHAPE_UP;
            case NORTH -> SHAPE_NORTH;
            case SOUTH -> SHAPE_SOUTH;
            case WEST -> SHAPE_WEST;
            case EAST -> SHAPE_EAST;
        };
    }

    @Override
    public BlockState updateShape(BlockState state, Direction direction, BlockState neighborState,
                                  LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
        Direction supportDir = state.getValue(FACING).getOpposite();
        if (direction == supportDir && neighborState.canBeReplaced()) {
            return Blocks.AIR.defaultBlockState();
        }
        return super.updateShape(state, direction, neighborState, level, pos, neighborPos);
    }
}
