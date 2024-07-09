import os
import asyncio
from dotenv import load_dotenv
from telegram_bot.telegram_bot import TelegramBot


load_dotenv()


async def main():
    bot = TelegramBot(token = os.getenv("BOT_TOKEN"))
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is off")
