import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
from typing import List, Dict, Optional

# Template padrão
DEFAULT_TEMPLATE = {
    "roles": [
        "Administrador",
        "Gerente de Projeto",
        "Desenvolvedor",
        "QA",
        "Documentação"
    ],
    "categories": {
        "📢 GERAL": [
            "boas-vindas",
            "anúncios",
            "regras",
            "recursos"
        ],
        "📆 REUNIÕES E DAILY": [
            "agendamento-reunioes",
            "daily-reports",
            "atas-reunioes-quarta",
            "atas-reunioes-domingo"
        ],
        "🎯 GESTÃO DO PROJETO": [
            "cronograma",
            "status-geral",
            "dúvidas-gerais",
            "sugestões-melhorias"
        ],
        "💻 DESENVOLVIMENTO": {
            "Módulo de Extração": [
                "extração-dados-discussão",
                "apis-fontes-dados",
                "implementação-extração"
            ],
            "Módulo de IA": [
                "ia-modelo-discussão",
                "treinamento-modelo",
                "validação-respostas"
            ],
            "Módulo WhatsApp": [
                "whatsapp-api-setup",
                "implementação-mensagens",
                "logs-monitoramento"
            ]
        },
        "🧪 TESTES E QUALIDADE": [
            "testes-unitarios",
            "testes-integração",
            "bugs-reports",
            "validação-qualidade"
        ],
        "📚 DOCUMENTAÇÃO": [
            "documentação-técnica",
            "guias-processos",
            "manuais-configuração"
        ],
        "🤝 EQUIPE": [
            "chat-geral-equipe",
            "off-topic"
        ]
    },
    "voice_channels": [
        "Reunião Semanal",
        "Daily Sync",
        "Discussões Técnicas",
        "Sala de Pair Programming"
    ]
}

class TemplateManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_roles(self, guild: discord.Guild, roles: List[str]) -> List[str]:
        log_messages = []
        for role_name in roles:
            existing_role = discord.utils.get(guild.roles, name=role_name)
            if not existing_role:
                await guild.create_role(name=role_name)
                log_messages.append(f"✅ Cargo criado: {role_name}")
            else:
                log_messages.append(f"ℹ️ Cargo já existe: {role_name}")
        return log_messages

    async def create_category_with_channels(self, guild: discord.Guild, category_name: str,
                                          channels_data: List[str] | dict) -> List[str]:
        log_messages = []

        existing_category = discord.utils.get(guild.categories, name=category_name)
        if existing_category:
            log_messages.append(f"ℹ️ Categoria já existe: {category_name}")
            category = existing_category
        else:
            category = await guild.create_category(category_name)
            log_messages.append(f"✅ Categoria criada: {category_name}")

        if isinstance(channels_data, list):
            for channel_name in channels_data:
                existing_channel = discord.utils.get(category.channels, name=channel_name)
                if not existing_channel:
                    await guild.create_text_channel(channel_name, category=category)
                    log_messages.append(f"✅ Canal criado: {channel_name}")
                else:
                    log_messages.append(f"ℹ️ Canal já existe: {channel_name}")

        elif isinstance(channels_data, dict):
            for subcategory_name, subchannel_data in channels_data.items():
                sub_cat_name = f"{category_name} | {subcategory_name}"
                sub_logs = await self.create_category_with_channels(guild, sub_cat_name, subchannel_data)
                log_messages.extend(sub_logs)

        return log_messages

    async def create_voice_channels(self, guild: discord.Guild, voice_channels: List[str]) -> List[str]:
        log_messages = []
        voice_category_name = "🎤 REUNIÕES"

        existing_category = discord.utils.get(guild.categories, name=voice_category_name)
        if existing_category:
            voice_category = existing_category
            log_messages.append(f"ℹ️ Categoria de voz já existe: {voice_category_name}")
        else:
            voice_category = await guild.create_category(voice_category_name)
            log_messages.append(f"✅ Categoria de voz criada: {voice_category_name}")

        for vc_name in voice_channels:
            existing_vc = discord.utils.get(voice_category.channels, name=vc_name)
            if not existing_vc:
                await guild.create_voice_channel(vc_name, category=voice_category)
                log_messages.append(f"✅ Canal de voz criado: {vc_name}")
            else:
                log_messages.append(f"ℹ️ Canal de voz já existe: {vc_name}")

        return log_messages

    @app_commands.command(name="create-template", description="Cria uma estrutura de canais e cargos baseada em um template")
    async def create_template(self, interaction: discord.Interaction, template_file: discord.Attachment = None):
        await interaction.response.defer()

        try:
            if template_file:
                template_content = await template_file.read()
                template_data = json.loads(template_content.decode('utf-8'))
            else:
                template_data = DEFAULT_TEMPLATE

            log_messages = []
            guild = interaction.guild

            # Criar roles
            role_logs = await self.create_roles(guild, template_data.get("roles", []))
            log_messages.extend(role_logs)

            # Criar categorias e canais
            for category_name, channels_data in template_data.get("categories", {}).items():
                category_logs = await self.create_category_with_channels(guild, category_name, channels_data)
                log_messages.extend(category_logs)
                await asyncio.sleep(1)

            # Criar canais de voz
            voice_logs = await self.create_voice_channels(guild, template_data.get("voice_channels", []))
            log_messages.extend(voice_logs)

            # Dividir os logs em chunks
            chunks = []
            current_chunk = "```diff\n"

            for message in log_messages:
                if len(current_chunk) + len(message) + 1 > 1990:
                    current_chunk += "```"
                    chunks.append(current_chunk)
                    current_chunk = "```diff\n"
                current_chunk += message + "\n"

            if current_chunk != "```diff\n":
                current_chunk += "```"
                chunks.append(current_chunk)

            await interaction.followup.send("🚀 Iniciando configuração do servidor...")
            for chunk in chunks:
                await interaction.followup.send(chunk)
            await interaction.followup.send("✅ Configuração concluída!")

        except Exception as e:
            await interaction.followup.send(f"❌ Erro durante a configuração: {str(e)}")

    @app_commands.command(name="template-format", description="Mostra o formato do arquivo JSON para criar template")
    async def template_format(self, interaction: discord.Interaction):
        example_template = {
            "roles": ["Cargo1", "Cargo2"],
            "categories": {
                "Categoria1": ["canal1", "canal2"],
                "Categoria2": {
                    "Subcategoria1": ["canal3", "canal4"],
                    "Subcategoria2": ["canal5", "canal6"]
                }
            },
            "voice_channels": ["Voz1", "Voz2"]
        }

        json_str = json.dumps(example_template, indent=2)
        await interaction.response.send_message(
            f"Para criar um template personalizado, envie um arquivo JSON com este formato:\n```json\n{json_str}\n```"
        )

async def setup(bot):
    await bot.add_cog(TemplateManager(bot))