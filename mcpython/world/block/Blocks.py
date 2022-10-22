from mcpython.world.block.Block import Block
from mcpython.world.block.BlockManagement import BLOCK_REGISTRY
from mcpython.world.block.FenceBlock import FenceBlock
from mcpython.world.block.LogBlock import LogBlock
from mcpython.world.block.SingleBlockStateBlock import SingleBlockStateBlock
from mcpython.world.block.SlabBlock import SlabBlock
from mcpython.world.block.StairsBlocks import StairsBlock
from mcpython.world.block.FallingBlock import FallingBlock

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

# note block, beds

# fmt: on
