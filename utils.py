import os
from typing import Optional, Dict
import traceback
from enum import Enum
import json


class BotUtils:
    @staticmethod
    async def load_cog(bot, cog_name: str) -> tuple[bool, Optional[str]]:
        try:
            await bot.load_extension(f'cogs.{cog_name}')
            return True, None
        except Exception as e:
            return False, f"{str(e)}\n{traceback.format_exc()}"

    @staticmethod
    async def sync_commands(bot) -> tuple[bool, int, Optional[str]]:
        try:
            synced = await bot.tree.sync()
            return True, len(synced), None
        except Exception as e:
            return False, 0, f"{str(e)}\n{traceback.format_exc()}"

    @staticmethod
    def get_default_template() -> Dict:
        with open(os.path.abspath("default_template.json"), 'r', encoding='utf-8') as f:
            return json.load(f)

class Status(Enum):
    SUCCESS = "✅"
    ERROR = "❌"
    IN_PROGRESS = "🔄"
    WARNING = "⚠️"