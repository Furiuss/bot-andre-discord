import discord
from discord.ext import commands
import asyncio
import os
from config import COMMAND_PREFIX, setup_logging, BOT_TOKEN
from utils import BotUtils, Status
import traceback

logger = setup_logging()


class DiscordBot(commands.Bot):
    def __init__(self):
        logger.info("Iniciando inicialização do bot...")
        intents = discord.Intents.all()
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)
        self.utils = BotUtils()
        logger.info("Bot inicializado com sucesso")

    async def setup_hook(self):
        logger.info("Iniciando setup do bot...")
        await self._load_cogs()
        await self._sync_commands()
        logger.info("Setup do bot concluído!")

    async def _load_cogs(self):
        logger.info("Iniciando carregamento dos cogs...")

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                cog_name = filename[:-3]
                success, error = await self.utils.load_cog(self, cog_name)

                if success:
                    logger.info(f"{Status.SUCCESS.value} Cog carregado com sucesso: {filename}")
                else:
                    logger.error(f"{Status.ERROR.value} Erro ao carregar cog {filename}: {error}")

    async def _sync_commands(self):
        logger.info("Iniciando sincronização de comandos...")

        success, count, error = await self.utils.sync_commands(self)

        if success:
            logger.info(f"{Status.SUCCESS.value} Comandos sincronizados: {count} comandos")
        else:
            logger.error(f"{Status.ERROR.value} Erro ao sincronizar comandos: {error}")

    async def on_ready(self):
        logger.info(f"Bot logado como: {self.user.name}")
        logger.info(f"Bot ID: {self.user.id}")
        logger.info("-" * 20)

async def main():
    try:
        bot = DiscordBot()
        await bot.start(BOT_TOKEN)
    except Exception as e:
        logger.critical(f"Erro crítico ao iniciar o bot: {str(e)}\n{traceback.format_exc()}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot encerrado pelo usuário")
    except Exception as e:
        logger.critical(f"Erro não tratado: {str(e)}\n{traceback.format_exc()}")