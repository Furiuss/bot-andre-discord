import os
import logging
from logging.handlers import RotatingFileHandler

BOT_TOKEN = os.getenv('BOT-ANDRE-TOKEN')
COMMAND_PREFIX = '!'


def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('discord_bot')
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        'logs/bot.log',
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger