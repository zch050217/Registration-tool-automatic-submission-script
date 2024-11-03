import random
import os
from rich.console import Console

console = Console()

# 随机生成User-Agent


def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    ]
    return random.choice(user_agents)

# 清除屏幕并打印标题


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(
        "\n[bold cyan]-------------------------------------------[/bold cyan]")
    console.print("        微信报名工具抢讲座小工具v2.2.1")
    console.print("                By C3ngH 2024.10.22")
    console.print(
        "[bold cyan]-------------------------------------------[/bold cyan]\n")
