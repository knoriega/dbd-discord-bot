import discord
import logging
from pathlib import Path

formatter = logging.Formatter(
    '%(asctime)s-%(levelname)s-%(name)s: %(message)s')

repo_root = Path(__file__).parent
repo_root.joinpath('logs').mkdir(exist_ok=True)


def new_logger(name, level, filename):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    f_handler = logging.FileHandler(repo_root.joinpath('logs', filename), mode='w')
    f_handler.setFormatter(formatter)
    logger.addHandler(f_handler)
    return logger


discord_logger = new_logger('discord', logging.INFO, 'discord.log')
