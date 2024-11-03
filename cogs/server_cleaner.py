from discord.ext import commands
from discord import app_commands
import discord

class ServerCleaner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="clean_server",
        description="Remove todos os canais e cargos do servidor (CUIDADO: Não pode ser desfeito!)"
    )
    @app_commands.default_permissions(administrator=True)
    async def clear_server(self, interaction: discord.Interaction):
        # Verifica se o usuário é o dono do servidor
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "❌ Apenas o dono do servidor pode usar este comando!",
                ephemeral=True
            )
            return

        # Confirmação inicial
        await interaction.response.send_message(
            "⚠️ **ATENÇÃO**: Isso irá remover TODOS os canais e cargos do servidor.\n"
            "Esta ação não pode ser desfeita!\n\n"
            "Digite `CONFIRMAR` para prosseguir.",
            ephemeral=True
        )

        def check(m):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
        except TimeoutError:
            await interaction.followup.send("Tempo esgotado. Operação cancelada.", ephemeral=True)
            return

        if msg.content.upper() != "CONFIRMAR":
            await interaction.followup.send("Operação cancelada.", ephemeral=True)
            return

        # Começa a limpeza
        status_msg = await interaction.followup.send("🔄 Iniciando limpeza do servidor...", ephemeral=True)

        # Remove canais
        for channel in interaction.guild.channels:
            try:
                await channel.delete()
            except discord.Forbidden:
                await status_msg.edit(content=f"❌ Não tenho permissão para deletar o canal {channel.name}")
                return
            except Exception as e:
                await status_msg.edit(content=f"❌ Erro ao deletar canal {channel.name}: {str(e)}")
                return

        # Remove cargos (exceto @everyone)
        for role in interaction.guild.roles:
            if role.name != "@everyone":
                try:
                    await role.delete()
                except discord.Forbidden:
                    await status_msg.edit(content=f"❌ Não tenho permissão para deletar o cargo {role.name}")
                    return
                except Exception as e:
                    await status_msg.edit(content=f"❌ Erro ao deletar cargo {role.name}: {str(e)}")
                    return

        # Cria um canal geral para não deixar o servidor vazio
        try:
            await interaction.guild.create_text_channel('geral')
            await status_msg.edit(content="✅ Servidor limpo com sucesso! Criei um canal 'geral' para você começar.")
        except Exception as e:
            await status_msg.edit(content=f"❌ Erro ao criar canal geral: {str(e)}")

async def setup(bot):
    await bot.add_cog(ServerCleaner(bot))