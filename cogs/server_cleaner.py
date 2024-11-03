import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional
import asyncio

from utils import Status

logger = logging.getLogger('server_cleaner')


class ServerCleanerMessages:
    OWNER_ONLY = f"{Status.ERROR.value} Apenas o dono do servidor pode usar este comando!"
    CONFIRMATION_REQUEST = (
        F"{Status.WARNING.value} **ATENÇÃO**: Isso irá remover TODOS os canais e cargos do servidor.\n"
        "Esta ação não pode ser desfeita!\n\n"
        "Digite `CONFIRMAR` para prosseguir."
    )
    TIMEOUT = "Tempo esgotado. Operação cancelada."
    OPERATION_CANCELLED = "Operação cancelada."
    CLEANUP_START = f"{Status.IN_PROGRESS.value} Iniciando limpeza do servidor..."
    CLEANUP_SUCCESS = f"{Status.SUCCESS.value} Servidor limpo com sucesso! Criei um canal 'geral' para você começar."

    @staticmethod
    def error_message(action: str, item_name: str, error: Exception) -> str:
        return f"{Status.ERROR.value} Erro ao {action} {item_name}: {str(error)}"

    @staticmethod
    def permission_error(action: str, item_name: str) -> str:
        return f"{Status.ERROR.value} Não tenho permissão para {action} {item_name}"


class ServerCleanerUtils:

    @staticmethod
    async def delete_channel(channel: discord.abc.GuildChannel) -> tuple[bool, Optional[str]]:
        try:
            await channel.delete()
            logger.info(f"{Status.SUCCESS.value} Canal deletado com sucesso: {channel.name}")
            return True, None
        except discord.Forbidden:
            error_msg = f"Sem permissão para deletar canal: {channel.name}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Erro ao deletar canal {channel.name}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    @staticmethod
    async def delete_role(role: discord.Role) -> tuple[bool, Optional[str]]:
        try:
            await role.delete()
            logger.info(f"Cargo deletado com sucesso: {role.name}")
            return True, None
        except discord.Forbidden:
            error_msg = f"Sem permissão para deletar cargo: {role.name}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Erro ao deletar cargo {role.name}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    @staticmethod
    async def create_general_channel(guild: discord.Guild) -> tuple[bool, Optional[str]]:
        try:
            await guild.create_text_channel('geral')
            logger.info("Canal 'geral' criado com sucesso")
            return True, None
        except Exception as e:
            error_msg = f"Erro ao criar canal geral: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


class ServerCleaner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.utils = ServerCleanerUtils()
        self.messages = ServerCleanerMessages()
        logger.info("ServerCleaner inicializado")

    async def _verify_owner(self, interaction: discord.Interaction) -> bool:
        is_owner = interaction.user.id == interaction.guild.owner_id
        if not is_owner:
            logger.warning(f"Usuário não-proprietário tentou limpar o servidor: {interaction.user.id}")
            await interaction.response.send_message(
                self.messages.OWNER_ONLY,
                ephemeral=True
            )
        return is_owner

    async def _await_confirmation(self, interaction: discord.Interaction) -> bool:
        await interaction.response.send_message(
            self.messages.CONFIRMATION_REQUEST,
            ephemeral=True
        )

        def check(m):
            return (m.author.id == interaction.user.id and
                    m.channel.id == interaction.channel.id)

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            return msg.content.upper() == "CONFIRMAR"
        except asyncio.TimeoutError:
            await interaction.followup.send(self.messages.TIMEOUT, ephemeral=True)
            logger.info("Tempo de confirmação esgotado")
            return False

    async def _clean_channels(self,
                              guild: discord.Guild,
                              status_msg: discord.WebhookMessage) -> bool:
        for channel in guild.channels:
            success, error_msg = await self.utils.delete_channel(channel)
            if not success:
                await status_msg.edit(content=error_msg)
                return False
            await asyncio.sleep(0.5)  # Evita rate limiting
        return True

    async def _clean_roles(self,
                           guild: discord.Guild,
                           status_msg: discord.WebhookMessage) -> bool:
        for role in guild.roles:
            if role.name != "@everyone":
                success, error_msg = await self.utils.delete_role(role)
                if not success:
                    await status_msg.edit(content=error_msg)
                    return False
                await asyncio.sleep(0.5)  # Evita rate limiting
        return True

    @app_commands.command(
        name="clean_server",
        description="Remove todos os canais e cargos do servidor (CUIDADO: Não pode ser desfeito!)"
    )
    @app_commands.default_permissions(administrator=True)
    async def clear_server(self, interaction: discord.Interaction):
        logger.info(f"Comando clean_server iniciado por {interaction.user.id}")

        if not await self._verify_owner(interaction):
            return

        if not await self._await_confirmation(interaction):
            return

        status_msg = await interaction.followup.send(
            self.messages.CLEANUP_START,
            ephemeral=True
        )

        if not await self._clean_channels(interaction.guild, status_msg):
            return

        if not await self._clean_roles(interaction.guild, status_msg):
            return

        success, error_msg = await self.utils.create_general_channel(interaction.guild)
        if not success:
            await status_msg.edit(content=error_msg)
            return

        await status_msg.edit(content=self.messages.CLEANUP_SUCCESS)
        logger.info(f"Servidor {interaction.guild.id} limpo com sucesso")


async def setup(bot):
    await bot.add_cog(ServerCleaner(bot))