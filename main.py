import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class BotCommands(commands.Cog):
    @commands.command(name="cenoura", help="Mostra a resposta de exemplo do bot.")
    async def cenoura(self, ctx: commands.Context) -> None:
        await ctx.send("CADÊ, EU QUERO!")

    @commands.command(name="ajuda", help="Mostra os comandos disponíveis.")
    async def ajuda(self, ctx: commands.Context) -> None:
        command_list = "\n".join(
            f"- {ctx.clean_prefix}{command.name}: {command.help or 'Sem descrição.'}"
            for command in sorted(ctx.bot.commands, key=lambda command: command.name)
        )
        await ctx.send(f"Comandos disponíveis:\n{command_list}")

    @commands.command(
        name="temperatura",
        help="Mostra uma resposta de exemplo sobre a temperatura.",
    )
    async def temperatura(self, ctx: commands.Context) -> None:
        await ctx.send(
            "Como um coelho, eu não tenho a menor ideia sobre a temperatura! "
            "Eu só sei que você está quente demais."
        )


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        prefix = os.getenv("COMMAND_PREFIX") or "!"
        super().__init__(
            command_prefix=prefix,
            intents=intents,
            help_command=None,
            description="Um template simples para bots do Discord.",
        )

    async def setup_hook(self) -> None:
        await self.add_cog(BotCommands())

    async def on_ready(self) -> None:
        logging.info("Bot conectado como %s", self.user)


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit(
            "DISCORD_TOKEN não foi definido. Configure-o no arquivo .env."
        )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    DiscordBot().run(token)


if __name__ == "__main__":
    main()
