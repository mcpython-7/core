from mcpython.commands.Command import Command, FixedString

gamemode = Command("gamemode")
gamemode.construct().then(
    FixedString("0").executes(lambda player, _: player.set_gamemode(0))
).then(FixedString("1").executes(lambda player, _: player.set_gamemode(1))).then(
    FixedString("2").executes(lambda player, _: player.set_gamemode(2))
).then(
    FixedString("3").executes(lambda player, _: player.set_gamemode(3))
).then(
    FixedString("survival").executes(lambda player, _: player.set_gamemode(0))
).then(
    FixedString("creative").executes(lambda player, _: player.set_gamemode(1))
).then(
    FixedString("hardcore").executes(lambda player, _: player.set_gamemode(2))
).then(
    FixedString("spectator").executes(lambda player, _: player.set_gamemode(3))
)
