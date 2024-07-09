import asyncio
from concurrent.futures import ThreadPoolExecutor
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from seleniumbase.common.exceptions import NoSuchElementException, NotConnectedException
from scraper.scraper import Scraper
from .states import Check_state


router = Router()
executor_pool = ThreadPoolExecutor(max_workers = 5)


# -------- Router functions --------
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Welcome to Dexscreener scraper Bot\nUse Commands to interact with data")


@router.message(Command("check"))
async def cmd_check(message: Message, state: FSMContext):
    await state.set_state(Check_state.address)
    await message.answer("Send token address that you want to check for valid wallets")


@router.message(Check_state.address)
async def check_address(message: Message, state: FSMContext):
    await state.update_data(address = message.text)
    data = await state.get_data()

    if len(data["address"].strip().split()) > 1:
        await message.answer("Invalid value\nAddress must contain no spaces")
        await state.clear()
        return
    
    await message.answer("Fetching wallets\nThis may take some time")
    await state.clear()

    try:
        scraper = Scraper()
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(executor_pool, scraper.check_address, data["address"])
        reply = f"_Token:_ [{result['token_symbol']}](https://dexscreener.com/solana/{data['address']})\n\n"
        
        if len(result["wallets_list"]) > 0:
            reply += "_Valid wallets:_\n"
            for wallet in result["wallets_list"]:
                reply += f"[{wallet['address']}](https://gmgn.ai/sol/address/{wallet['address']})\n"
        else:
            reply += "_No valid wallets_\n"
        await message.reply(reply, parse_mode = "MarkdownV2", disable_web_page_preview = True)

    except NotConnectedException as exception:
        print(str(exception))
        await message.reply(str(exception))
        await state.clear()

    except IndexError as exception:
        print(str(exception))
        await message.reply(str(exception))
        await state.clear()
        
    except NoSuchElementException as exception:
        print(str(exception))
        await message.reply(str(exception))
        await state.clear()
    
    except Exception as exception:
        print(str(exception))
        await message.reply(str(exception))
        await message.answer("Contact the admin to resolve this")
        await state.clear()
