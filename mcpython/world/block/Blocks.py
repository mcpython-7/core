from mcpython.world.block.Block import Block
from mcpython.world.block.BlockManagement import BLOCK_REGISTRY
from mcpython.world.block.ChiseledBookshelf import ChiseledBookshelf
from mcpython.world.block.FenceBlock import FenceBlock
from mcpython.world.block.FenceGate import FenceGate
from mcpython.world.block.LogBlock import LogBlock
from mcpython.world.block.SingleBlockStateBlock import SingleBlockStateBlock
from mcpython.world.block.SlabBlock import SlabBlock
from mcpython.world.block.StairsBlocks import StairsBlock
from mcpython.world.block.FallingBlock import FallingBlock
from mcpython.world.block.WallBlock import WallBlock

# fmt: off

STONE = BLOCK_REGISTRY.register_lazy("minecraft:stone", lambda: Block().register_block_item())
GRANITE = BLOCK_REGISTRY.register_lazy("minecraft:granite", lambda: Block().register_block_item())
POLISHED_GRANITE = BLOCK_REGISTRY.register_lazy("minecraft:polished_granite", lambda: Block().register_block_item())
DIORITE = BLOCK_REGISTRY.register_lazy("minecraft:diorite", lambda: Block().register_block_item())
POLISHED_DIORITE = BLOCK_REGISTRY.register_lazy("minecraft:polished_diorite", lambda: Block().register_block_item())
ANDESITE = BLOCK_REGISTRY.register_lazy("minecraft:andesite", lambda: Block().register_block_item())
POLISHED_ANDESITE = BLOCK_REGISTRY.register_lazy("minecraft:polished_andesite", lambda: Block().register_block_item())
GRASS_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:grass_block", lambda: SingleBlockStateBlock("snowy=false").register_block_item())
DIRT = BLOCK_REGISTRY.register_lazy("minecraft:dirt", lambda: Block().register_block_item())
COARSE_DIRT = BLOCK_REGISTRY.register_lazy("minecraft:coarse_dirt", lambda: Block().register_block_item())
PODZOL = BLOCK_REGISTRY.register_lazy("minecraft:podzol", lambda: SingleBlockStateBlock("snowy=false").register_block_item())
COBBLESTONE = BLOCK_REGISTRY.register_lazy("minecraft:cobblestone", lambda: Block().register_block_item())

OAK_PLANKS = BLOCK_REGISTRY.register_lazy("minecraft:oak_planks", lambda: Block().register_block_item())
SPRUCE_PLANKS = BLOCK_REGISTRY.register_lazy("minecraft:spruce_planks", lambda: Block().register_block_item())
BIRCH_PLANKS = BLOCK_REGISTRY.register_lazy("minecraft:birch_planks", lambda: Block().register_block_item())
JUNGLE_PLANKS = BLOCK_REGISTRY.register_lazy("minecraft:jungle_planks", lambda: Block().register_block_item())
ACACIA_PLANKS = BLOCK_REGISTRY.register_lazy("minecraft:acacia_planks", lambda: Block().register_block_item())
DARK_OAK_PLANKS = BLOCK_REGISTRY.register_lazy("minecraft:dark_oak_planks", lambda: Block().register_block_item())
MANGROVE_PLANKS = BLOCK_REGISTRY.register_lazy("minecraft:mangrove_planks", lambda: Block().register_block_item())
BAMBOO_PLANKS = BLOCK_REGISTRY.register_lazy("minecraft:bamboo_planks", lambda: Block().register_block_item())
BAMBOO_MOSAIC = BLOCK_REGISTRY.register_lazy("minecraft:bamboo_mosaic", lambda: Block().register_block_item())

# saplings

BEDROCK = BLOCK_REGISTRY.register_lazy("minecraft:bedrock", lambda: Block().set_breakable(False).register_block_item())

SAND = BLOCK_REGISTRY.register_lazy("minecraft:sand", lambda: FallingBlock().register_block_item())
RED_SAND = BLOCK_REGISTRY.register_lazy("minecraft:red_sand", lambda: FallingBlock().register_block_item())
GRAVEL = BLOCK_REGISTRY.register_lazy("minecraft:gravel", lambda: FallingBlock().register_block_item())

GOLD_ORE = BLOCK_REGISTRY.register_lazy("minecraft:gold_ore", lambda: Block().register_block_item())
DEEPSLATE_GOLD_ORE = BLOCK_REGISTRY.register_lazy("minecraft:deepslate_gold_ore", lambda: Block().register_block_item())
IRON_ORE = BLOCK_REGISTRY.register_lazy("minecraft:iron_ore", lambda: Block().register_block_item())
DEEPSLATE_IRON_ORE = BLOCK_REGISTRY.register_lazy("minecraft:deepslate_iron_ore", lambda: Block().register_block_item())
COAL_ORE = BLOCK_REGISTRY.register_lazy("minecraft:coal_ore", lambda: Block().register_block_item())
DEEPSLATE_COAL_ORE = BLOCK_REGISTRY.register_lazy("minecraft:deepslate_coal_ore", lambda: Block().register_block_item())
NETHER_GOLD_ORE = BLOCK_REGISTRY.register_lazy("minecraft:nether_gold_ore", lambda: Block().register_block_item())

OAK_LOG = BLOCK_REGISTRY.register_lazy("minecraft:oak_log", lambda: LogBlock().register_block_item())
SPRUCE_LOG = BLOCK_REGISTRY.register_lazy("minecraft:spruce_log", lambda: LogBlock().register_block_item())
BIRCH_LOG = BLOCK_REGISTRY.register_lazy("minecraft:birch_log", lambda: LogBlock().register_block_item())
JUNGLE_LOG = BLOCK_REGISTRY.register_lazy("minecraft:jungle_log", lambda: LogBlock().register_block_item())
ACACIA_LOG = BLOCK_REGISTRY.register_lazy("minecraft:acacia_log", lambda: LogBlock().register_block_item())
DARK_OAK_LOG = BLOCK_REGISTRY.register_lazy("minecraft:dark_oak_log", lambda: LogBlock().register_block_item())
MANGROVE_LOG = BLOCK_REGISTRY.register_lazy("minecraft:mangrove_log", lambda: LogBlock().register_block_item())
MANGROVE_ROOTS = BLOCK_REGISTRY.register_lazy("minecraft:mangrove_roots", lambda: Block().register_block_item())
MUDDY_MANGROVE_ROOTS = BLOCK_REGISTRY.register_lazy("minecraft:muddy_mangrove_roots", lambda: LogBlock().register_block_item())

STRIPPED_OAK_LOG = BLOCK_REGISTRY.register_lazy("minecraft:stripped_oak_log", lambda: LogBlock().register_block_item())
STRIPPED_SPRUCE_LOG = BLOCK_REGISTRY.register_lazy("minecraft:stripped_spruce_log", lambda: LogBlock().register_block_item())
STRIPPED_BIRCH_LOG = BLOCK_REGISTRY.register_lazy("minecraft:stripped_birch_log", lambda: LogBlock().register_block_item())
STRIPPED_JUNGLE_LOG = BLOCK_REGISTRY.register_lazy("minecraft:stripped_jungle_log", lambda: LogBlock().register_block_item())
STRIPPED_ACACIA_LOG = BLOCK_REGISTRY.register_lazy("minecraft:stripped_acacia_log", lambda: LogBlock().register_block_item())
STRIPPED_DARK_OAK_LOG = BLOCK_REGISTRY.register_lazy("minecraft:stripped_dark_oak_log", lambda: LogBlock().register_block_item())
STRIPPED_MANGROVE_LOG = BLOCK_REGISTRY.register_lazy("minecraft:stripped_mangrove_log", lambda: LogBlock().register_block_item())

OAK_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:oak_wood", lambda: LogBlock().register_block_item())
SPRUCE_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:spruce_wood", lambda: LogBlock().register_block_item())
BIRCH_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:birch_wood", lambda: LogBlock().register_block_item())
JUNGLE_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:jungle_wood", lambda: LogBlock().register_block_item())
ACACIA_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:acacia_wood", lambda: LogBlock().register_block_item())
DARK_OAK_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:dark_oak_wood", lambda: LogBlock().register_block_item())
MANGROVE_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:mangrove_wood", lambda: LogBlock().register_block_item())

STRIPPED_OAK_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:stripped_oak_wood", lambda: LogBlock().register_block_item())
STRIPPED_SPRUCE_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:stripped_spruce_wood", lambda: LogBlock().register_block_item())
STRIPPED_BIRCH_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:stripped_birch_wood", lambda: LogBlock().register_block_item())
STRIPPED_JUNGLE_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:stripped_jungle_wood", lambda: LogBlock().register_block_item())
STRIPPED_ACACIA_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:stripped_acacia_wood", lambda: LogBlock().register_block_item())
STRIPPED_DARK_OAK_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:stripped_dark_oak_wood", lambda: LogBlock().register_block_item())
STRIPPED_MANGROVE_WOOD = BLOCK_REGISTRY.register_lazy("minecraft:stripped_mangrove_wood", lambda: LogBlock().register_block_item())

# leaves

SPONGE_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:sponge", lambda: Block().register_block_item())
WET_SPONGE_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:wet_sponge", lambda: Block().register_block_item())

GLASS = BLOCK_REGISTRY.register_lazy("minecraft:glass", lambda: Block().register_block_item())

LAPIS_ORE = BLOCK_REGISTRY.register_lazy("minecraft:lapis_ore", lambda: Block().register_block_item())
DEEPSLATE_LAPIS_ORE = BLOCK_REGISTRY.register_lazy("minecraft:deepslate_lapis_ore", lambda: Block().register_block_item())
LAPIS_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:lapis_block", lambda: Block().register_block_item())

# dispenser

SANDSTONE = BLOCK_REGISTRY.register_lazy("minecraft:sandstone", lambda: Block().register_block_item())
CHISELED_SANDSTONE = BLOCK_REGISTRY.register_lazy("minecraft:chiseled_sandstone", lambda: Block().register_block_item())
CUT_SANDSTONE = BLOCK_REGISTRY.register_lazy("minecraft:cut_sandstone", lambda: Block().register_block_item())

# note block, beds, rails, sticky piston, cobweb, grass, gern, dead bush
# seagrass, tall seagrass, piston, piston head

WHITE_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:white_wool", lambda: Block().register_block_item())
ORANGE_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:orange_wool", lambda: Block().register_block_item())
MAGENTA_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:magenta_wool", lambda: Block().register_block_item())
LIGHT_BLUE_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:light_blue_wool", lambda: Block().register_block_item())
YELLOW_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:yellow_wool", lambda: Block().register_block_item())
LIME_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:lime_wool", lambda: Block().register_block_item())
PINK_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:pink_wool", lambda: Block().register_block_item())
GRAY_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:gray_wool", lambda: Block().register_block_item())
LIGHT_GRAY_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:light_gray_wool", lambda: Block().register_block_item())
CYAN_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:cyan_wool", lambda: Block().register_block_item())
PURPLE_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:purple_wool", lambda: Block().register_block_item())
BLUE_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:blue_wool", lambda: Block().register_block_item())
BROWN_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:brown_wool", lambda: Block().register_block_item())
GREEN_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:green_wool", lambda: Block().register_block_item())
RED_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:red_wool", lambda: Block().register_block_item())
BLACK_WOOL = BLOCK_REGISTRY.register_lazy("minecraft:black_wool", lambda: Block().register_block_item())

# moving piston, flowers, mushrooms

GOLD_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:gold_block", lambda: Block().register_block_item())
IRON_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:iron_block", lambda: Block().register_block_item())

BRICKS = BLOCK_REGISTRY.register_lazy("minecraft:bricks", lambda: Block().register_block_item())
TNT = BLOCK_REGISTRY.register_lazy("minecraft:tnt", lambda: Block().register_block_item())
BOOKSHELF = BLOCK_REGISTRY.register_lazy("minecraft:bookshelf", lambda: Block().register_block_item())
CHISELED_BOOKSHELF = BLOCK_REGISTRY.register_lazy("minecraft:chiseled_bookshelf", lambda: ChiseledBookshelf().register_block_item())

MOSSY_COBBLESTONE = BLOCK_REGISTRY.register_lazy("minecraft:mossy_cobblestone", lambda: Block().register_block_item())
OBSIDIAN = BLOCK_REGISTRY.register_lazy("minecraft:obsidian", lambda: Block().register_block_item())

# torch, fire, soul fire, spawner

OAK_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:oak_stairs", lambda: StairsBlock().register_block_item())

# chest, redstone wire

DIAMOND_ORE = BLOCK_REGISTRY.register_lazy("minecraft:diamond_ore", lambda: Block().register_block_item())
DEEPSLATE_DIAMOND_ORE = BLOCK_REGISTRY.register_lazy("minecraft:deepslate_diamond_ore", lambda: Block().register_block_item())
DIAMOND_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:diamond_block", lambda: Block().register_block_item())

# wheat, farmland, furnace
# signs, oak door, ladder, rail

COBBLESTONE_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:cobblestone_stairs", lambda: StairsBlock().register_block_item())

# wall signs, hanging signs
# lever, stone pressure plate, iron door, wood pressure plate

REDSTONE_ORE = BLOCK_REGISTRY.register_lazy("minecraft:redstone_ore", lambda: Block().register_block_item())
DEEPSLATE_REDSTONE_ORE = BLOCK_REGISTRY.register_lazy("minecraft:deepslate_redstone_ore", lambda: Block().register_block_item())

# redstone torch, stone button, snow, ice, snow block

CACTUS = BLOCK_REGISTRY.register_lazy("minecraft:cactus", lambda: Block().register_block_item())
CLAY = BLOCK_REGISTRY.register_lazy("minecraft:clay", lambda: Block().register_block_item())

# sugar cane, jukebox

OAK_FENCE = BLOCK_REGISTRY.register_lazy("minecraft:oak_fence", lambda: FenceBlock().register_block_item())

# pumpkin

NETHERRACK = BLOCK_REGISTRY.register_lazy("minecraft:netherrack", lambda: Block().register_block_item())
SOUL_SAND = BLOCK_REGISTRY.register_lazy("minecraft:soul_sand", lambda: Block().register_block_item())
SOUL_SOIL = BLOCK_REGISTRY.register_lazy("minecraft:soul_soil", lambda: Block().register_block_item())
BASALT = BLOCK_REGISTRY.register_lazy("minecraft:basalt", lambda: LogBlock().register_block_item())
POLISHED_BASALT = BLOCK_REGISTRY.register_lazy("minecraft:polished_basalt", lambda: LogBlock().register_block_item())

# soul torch, glowstone, nether portal, carved pumpkin, jack o lantern, cake, repeater

WHITE_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:white_stained_glass", lambda: Block().register_block_item())
ORANGE_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:orange_stained_glass", lambda: Block().register_block_item())
MAGENTA_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:magenta_stained_glass", lambda: Block().register_block_item())
LIGHT_BLUE_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:light_blue_stained_glass", lambda: Block().register_block_item())
YELLOW_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:yellow_stained_glass", lambda: Block().register_block_item())
LIME_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:lime_stained_glass", lambda: Block().register_block_item())
PINK_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:pink_stained_glass", lambda: Block().register_block_item())
GRAY_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:gray_stained_glass", lambda: Block().register_block_item())
LIGHT_GRAY_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:light_gray_stained_glass", lambda: Block().register_block_item())
CYAN_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:cyan_stained_glass", lambda: Block().register_block_item())
PURPLE_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:purple_stained_glass", lambda: Block().register_block_item())
BLUE_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:blue_stained_glass", lambda: Block().register_block_item())
BROWN_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:brown_stained_glass", lambda: Block().register_block_item())
GREEN_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:green_stained_glass", lambda: Block().register_block_item())
RED_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:red_stained_glass", lambda: Block().register_block_item())
BLACK_STAINED_GLASS = BLOCK_REGISTRY.register_lazy("minecraft:black_stained_glass", lambda: Block().register_block_item())

# trapdoors

STONE_BRICKS = BLOCK_REGISTRY.register_lazy("minecraft:stone_bricks", lambda: Block().register_block_item())
MOSSY_STONE_BRICKS = BLOCK_REGISTRY.register_lazy("minecraft:mossy_stone_bricks", lambda: Block().register_block_item())
CRACKED_STONE_BRICKS = BLOCK_REGISTRY.register_lazy("minecraft:cracked_stone_bricks", lambda: Block().register_block_item())
CHISELED_STONE_BRICKS = BLOCK_REGISTRY.register_lazy("minecraft:chiseled_stone_bricks", lambda: Block().register_block_item())

PACKED_MUD = BLOCK_REGISTRY.register_lazy("minecraft:packed_mud", lambda: Block().register_block_item())
MUD_BRICKS = BLOCK_REGISTRY.register_lazy("minecraft:mud_bricks", lambda: Block().register_block_item())

# infested variants, mushroom blocks, mushroom stem

IRON_BARS = BLOCK_REGISTRY.register_lazy("minecraft:iron_bars", lambda: FenceBlock().register_block_item())

CHAIN = BLOCK_REGISTRY.register_lazy("minecraft:chain", lambda: LogBlock().register_block_item())

GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:glass_pane", lambda: FenceBlock().register_block_item())

MELON = BLOCK_REGISTRY.register_lazy("minecraft:melon", lambda: Block().register_block_item())

# stems for plants, vine, glow litchen

OAK_FENCE_GATEWAY = BLOCK_REGISTRY.register_lazy("minecraft:oak_fence_gate", lambda: FenceGate().register_block_item())

BRICK_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:brick_stairs", lambda: StairsBlock().register_block_item())
STONE_BRICK_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:stone_brick_stairs", lambda: StairsBlock().register_block_item())
MUD_BRICK_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:mud_brick_stairs", lambda: StairsBlock().register_block_item())

MYCELIUM = BLOCK_REGISTRY.register_lazy("minecraft:mycelium", lambda: SingleBlockStateBlock("snowy=false").register_block_item())

# lily pad

NETHER_BRICKS = BLOCK_REGISTRY.register_lazy("minecraft:nether_bricks", lambda: Block().register_block_item())
NETHER_BRICK_FENCE = BLOCK_REGISTRY.register_lazy("minecraft:nether_brick_fence", lambda: FenceBlock().register_block_item())
NETHER_BRICK_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:nether_brick_stairs", lambda: StairsBlock().register_block_item())

# nether wart, enchanting table, brewing stand, cauldrons, end portal, end portal frame

END_STONE_BRICK = BLOCK_REGISTRY.register_lazy("minecraft:end_stone", lambda: Block().register_block_item())

# dragon egg, redstone lamp, cocoa

SANDSTONE_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:sandstone_stairs", lambda: StairsBlock().register_block_item())

EMERALD_ORE = BLOCK_REGISTRY.register_lazy("minecraft:emerald_ore", lambda: Block().register_block_item())
DEEPSLATE_EMERALD_ORE = BLOCK_REGISTRY.register_lazy("minecraft:deepslate_emerald_ore", lambda: Block().register_block_item())

# ender chest, tripwire hook, tripwire

EMERALD_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:emerald_block", lambda: Block().register_block_item())

SPRUCE_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:spruce_stairs", lambda: StairsBlock().register_block_item())
BIRCH_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:birch_stairs", lambda: StairsBlock().register_block_item())
JUNGLE_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:jungle_stairs", lambda: StairsBlock().register_block_item())

# command block, beacon

COBBLESTONE_WALL = BLOCK_REGISTRY.register_lazy("minecraft:cobblestone_wall", lambda: WallBlock().register_block_item())
MOSSY_COBBLESTONE_WALL = BLOCK_REGISTRY.register_lazy("minecraft:mossy_cobblestone_wall", lambda: WallBlock().register_block_item())

# flower pot and potted plants, carrots, potatoes, wooden buttons, mob heads, anvils, trapped chest
# pressure plate, comparator, daylight detector

REDSTONE_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:redstone_block", lambda: Block().register_block_item())

NETHER_QUARTZ_ORE = BLOCK_REGISTRY.register_lazy("minecraft:nether_quartz_ore", lambda: Block().register_block_item())

# hopper

QUARTZ_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:quartz_block", lambda: Block().register_block_item())
CHISELED_QUARTZ_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:chiseled_quartz_block", lambda: Block().register_block_item())
QUARTZ_PILLAR = BLOCK_REGISTRY.register_lazy("minecraft:quartz_pillar", lambda: LogBlock().register_block_item())
QUARTZ_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:quartz_stairs", lambda: StairsBlock().register_block_item())

# activator rail, dropper

WHITE_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:white_terracotta", lambda: Block().register_block_item())
ORANGE_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:orange_terracotta", lambda: Block().register_block_item())
MAGENTA_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:magenta_terracotta", lambda: Block().register_block_item())
LIGHT_BLUE_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:light_blue_terracotta", lambda: Block().register_block_item())
YELLOW_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:yellow_terracotta", lambda: Block().register_block_item())
LIME_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:lime_terracotta", lambda: Block().register_block_item())
PINK_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:pink_terracotta", lambda: Block().register_block_item())
GRAY_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:gray_terracotta", lambda: Block().register_block_item())
LIGHT_GRAY_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:light_gray_terracotta", lambda: Block().register_block_item())
CYAN_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:cyan_terracotta", lambda: Block().register_block_item())
PURPLE_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:purple_terracotta", lambda: Block().register_block_item())
BLUE_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:blue_terracotta", lambda: Block().register_block_item())
BROWN_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:brown_terracotta", lambda: Block().register_block_item())
GREEN_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:green_terracotta", lambda: Block().register_block_item())
RED_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:red_terracotta", lambda: Block().register_block_item())
BLACK_TERRACOTTA = BLOCK_REGISTRY.register_lazy("minecraft:black_terracotta", lambda: Block().register_block_item())

WHITE_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:white_stained_glass_pane", lambda: FenceBlock().register_block_item())
ORANGE_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:orange_stained_glass_pane", lambda: FenceBlock().register_block_item())
MAGENTA_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:magenta_stained_glass_pane", lambda: FenceBlock().register_block_item())
LIGHT_BLUE_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:light_blue_stained_glass_pane", lambda: FenceBlock().register_block_item())
YELLOW_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:yellow_stained_glass_pane", lambda: FenceBlock().register_block_item())
LIME_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:lime_stained_glass_pane", lambda: FenceBlock().register_block_item())
PINK_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:pink_stained_glass_pane", lambda: FenceBlock().register_block_item())
GRAY_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:gray_stained_glass_pane", lambda: FenceBlock().register_block_item())
LIGHT_GRAY_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:light_gray_stained_glass_pane", lambda: FenceBlock().register_block_item())
CYAN_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:cyan_stained_glass_pane", lambda: FenceBlock().register_block_item())
PURPLE_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:purple_stained_glass_pane", lambda: FenceBlock().register_block_item())
BLUE_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:blue_stained_glass_pane", lambda: FenceBlock().register_block_item())
BROWN_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:brown_stained_glass_pane", lambda: FenceBlock().register_block_item())
GREEN_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:green_stained_glass_pane", lambda: FenceBlock().register_block_item())
RED_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:red_stained_glass_pane", lambda: FenceBlock().register_block_item())
BLACK_STAINED_GLASS_PANE = BLOCK_REGISTRY.register_lazy("minecraft:black_stained_glass_pane", lambda: FenceBlock().register_block_item())

ACACIA_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:acacia_stairs", lambda: StairsBlock().register_block_item())
DARK_OAK_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:dark_oak_stairs", lambda: StairsBlock().register_block_item())
MANGROVE_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:mangrove_stairs", lambda: StairsBlock().register_block_item())
BAMBOO_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:bamboo_stairs", lambda: StairsBlock().register_block_item())
BAMBOO_MOSAIC_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:bamboo_mosaic_stairs", lambda: StairsBlock().register_block_item())

# slime block, barrier, light, iron trapdoor

PRISMARINE = BLOCK_REGISTRY.register_lazy("minecraft:prismarine", lambda: Block().register_block_item())
PRISMARINE_BRICKS = BLOCK_REGISTRY.register_lazy("minecraft:prismarine_bricks", lambda: Block().register_block_item())
DARK_PRISMARINE = BLOCK_REGISTRY.register_lazy("minecraft:dark_prismarine", lambda: Block().register_block_item())
PRISMARINE_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:prismarine_stairs", lambda: StairsBlock().register_block_item())
PRISMARINE_BRICK_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:prismarine_brick_stairs", lambda: StairsBlock().register_block_item())
DARK_PRISMARINE_STAIRS = BLOCK_REGISTRY.register_lazy("minecraft:dark_prismarine_stairs", lambda: StairsBlock().register_block_item())
PRISMARINE_SLAB = BLOCK_REGISTRY.register_lazy("minecraft:prismarine_slab", lambda: SlabBlock().register_block_item())
PRISMARINE_BRICK_SLAB = BLOCK_REGISTRY.register_lazy("minecraft:prismarine_brick_slab", lambda: SlabBlock().register_block_item())
DARK_PRISMARINE_SLAB = BLOCK_REGISTRY.register_lazy("minecraft:dark_prismarine_slab", lambda: SlabBlock().register_block_item())

# fmt: on
