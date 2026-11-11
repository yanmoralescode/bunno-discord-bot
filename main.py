import logging
import os
import re

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bunny_ai import BunnyAI

load_dotenv()


class BotCommands(commands.Cog):
    @commands.command(name="cenoura", help="Mostra a resposta de exemplo do bot.")
    async def cenoura(self, ctx: commands.Context) -> None:
        await ctx.send("CADÊ, EU QUERO! 🥕🥕🥕 (*^ω^*)")

    @commands.command(name="ajuda", help="Mostra os comandos disponíveis.")
    async def ajuda(self, ctx: commands.Context) -> None:
        command_list = "\n".join(
            f"- {ctx.clean_prefix}{command.name}: {command.help or 'Sem descrição.'}"
            for command in sorted(ctx.bot.commands, key=lambda command: command.name)
        )
        ai_help = (
            f"\n\n💬 **Conversar com a IA do Coelho:**\n"
            f"Basta me marcar em qualquer canal com uma pergunta, por exemplo:\n"
            f"`@{ctx.bot.user.display_name} por que comemos cenoura?`\n"
            f"Ou responder diretamente a uma mensagem minha!"
        )
        await ctx.send(f"🐰 **Comandos disponíveis:**\n{command_list}{ai_help}")

    @commands.command(
        name="temperatura",
        help="Mostra uma resposta de exemplo sobre a temperatura.",
    )
    async def temperatura(self, ctx: commands.Context) -> None:
        await ctx.send(
            "Como um coelho, eu não tenho a menor ideia sobre a temperatura! "
            "Eu só sei que você está quente demais. (•ㅅ•)"
        )

    @commands.command(
        name="esquecer",
        aliases=["limpar", "reset"],
        help="Limpa a memória recente da conversa com o coelho neste canal.",
    )
    async def esquecer(self, ctx: commands.Context) -> None:
        cleared = ctx.bot.ai.reset_history(ctx.channel.id)
        if cleared:
            await ctx.send("*pisca os olhos várias vezes e sacode a cabeça* Ué, onde estou? Esqueci de tudo o que conversamos aqui! (•ㅅ•)")
        else:
            await ctx.send("*mexe o focinho* Minha cabecinha já estava vazia aqui mesmo! Não tinha nada pra esquecer. (*^ω^*)")


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        prefix = os.getenv("COMMAND_PREFIX") or "!"
        super().__init__(
            command_prefix=prefix,
            intents=intents,
            help_command=None,
            description="BunnoBot - Um bot de coelho com inteligência artificial.",
        )

        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self.ai = BunnyAI(base_url=ollama_url, model=ollama_model)

    async def setup_hook(self) -> None:
        await self.add_cog(BotCommands())

    async def on_ready(self) -> None:
        logging.info("Bot conectado como %s (ID: %s)", self.user, self.user.id)
        logging.info("Modelo de IA configurado: %s via %s", self.ai.model, self.ai.base_url)

    async def on_message(self, message: discord.Message) -> None:
        # Ignora mensagens de outros bots para evitar loops
        if message.author.bot:
            return

        # Verifica se o bot foi mencionado ou se responderam diretamente a uma mensagem do bot
        bot_mentioned = self.user in message.mentions
        is_reply_to_bot = False

        if message.reference and message.reference.resolved:
            resolved = message.reference.resolved
            if isinstance(resolved, discord.Message) and resolved.author == self.user:
                is_reply_to_bot = True

        # Se foi mencionado ou responderam ao bot
        if bot_mentioned or is_reply_to_bot:
            # Remove menções do tipo <@ID> ou <@!ID> para pegar somente o texto da pergunta
            clean_content = re.sub(rf"<@!?{self.user.id}>", "", message.content).strip()

            # Mostra o status "digitando..." enquanto a IA gera a resposta
            async with message.channel.typing():
                reply_text = await self.ai.ask(
                    channel_id=message.channel.id,
                    user_name=message.author.display_name,
                    user_prompt=clean_content,
                )

            await message.reply(reply_text, mention_author=False)

        # Permite que comandos normais como !cenoura ou !ajuda continuem funcionando
        await self.process_commands(message)


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
