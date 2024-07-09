from aiogram import Bot, Dispatcher
from telegram_bot.handlers import router


class TelegramBot(Bot):
    def __init__(self, token):
        super().__init__(token = token)
        self.dp = Dispatcher()
    
    
    async def start(self):
        self.dp.include_router(router)
        print("Bot is on")
        await self.dp.start_polling(self)
