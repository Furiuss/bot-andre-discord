import discord
from discord.ext import commands
import asyncio
import os


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        print("Iniciando setup do bot...")
        # Carrega todos os cogs automaticamente
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Cog carregado com sucesso: {filename}')
                except Exception as e:
                    print(f'❌ Erro ao carregar cog {filename}: {str(e)}')
        # Tenta sincronizar os comandos
        try:
            print("Sincronizando comandos com o Discord...")
            synced = await self.tree.sync()
            print(f'✅ Comandos sincronizados: {len(synced)} comandos')
        except Exception as e:
            print(f'❌ Erro ao sincronizar comandos: {str(e)}')
        print('Bot está pronto!')

    async def on_ready(self):
            print(f'Bot logado como: {self.user.name}')
            print(f'Bot ID: {self.user.id}')
            print('-------------------')

async def main():
    bot = Bot()
    async with bot:
        await bot.start(os.getenv('BOT-ANDRE-TOKEN'))


if __name__ == "__main__":
        asyncio.run(main())

