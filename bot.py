import asyncio
import logging
import sys
import os
from os import getenv
import httpx
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InputMediaPhoto


load_dotenv()
TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()
API_BASE_URL = "http://localhost:8000"

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Get Tiktok Wrapped results")],
        [KeyboardButton(text="Guide on getting Tiktok data file")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)


class SendZipFile(StatesGroup):
    waiting_for_zip = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if message.from_user is None:
        await message.answer("Couldn't identify the user")
        return
    
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{API_BASE_URL}/users/new/?user_id={message.from_user.id}&username={message.from_user.full_name}"
        )

    await message.answer(html.bold("Welcome to Tiktok Wrapped 2025!"),
                         reply_markup=main_kb
                        )
    

@dp.message(F.text=="Guide on getting Tiktok data file")
async def get_guide(message: Message, state: FSMContext):
    images = [
        os.path.join("guide", f"{i}.jpg")
        for i in range(1, 8)
    ]

    media_group = MediaGroupBuilder(caption="""1. Click on "Profile\n2. Click on 3 lines at the top-right corner\n3. Click on "Settings and privacy"\n4. Click on "Account"\n5. Click on "Download your data"\n6. Make sure to select JSON format\n7. Click on "Request Data"\n8. Wait until TikTok sends you a notification "Your data file is ready" and download the ZIP file\n9. Sens that ZIP file to this bot""")
    for photo in images:
        media_group.add_photo(type="photo", media=FSInputFile(photo))

    await message.answer_media_group(media=media_group.build())
    await state.clear()

@dp.message(F.text=="Get Tiktok Wrapped results")
async def get_tiktok_wrapped(message: Message, state: FSMContext):
    await message.answer(html.bold("Send the ZIP file from TikTok"))
    await state.set_state(SendZipFile.waiting_for_zip)


@dp.message(SendZipFile.waiting_for_zip)
async def get_zip_file(message: Message, state: FSMContext, bot: Bot):
        if not message.document:
            await message.answer("Please send a ZIP file")
            return
        
        if not message.document.file_name.lower().endswith(".zip"):
            await message.answer("Please send a ZIP file")
            return

        processing = await message.answer("Your data is being processed...")
        try:

            zip_file = await bot.get_file(message.document.file_id)
            zip_bytes = await bot.download_file(zip_file.file_path)
            
            zip_bytes = zip_bytes.getvalue() if hasattr(zip_bytes, 'getvalue') else zip_bytes.read()


            files = {
                'file': (message.document.file_name, zip_bytes, 'application/zip')
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{API_BASE_URL}/tiktok_wrapped/zip/",
                                files=files,
                                timeout=30.0
                )

            resp.raise_for_status()

            async with httpx.AsyncClient() as client:
                await client.post(f"{API_BASE_URL}/users/new_request/?user_id={message.from_user.id}")

            await processing.edit_text("Proccessing has been finished")
            data = resp.json()
            text = (
                f"📊 <b>Your TikTok Stats</b>\n\n"
                f"👁️ <b>Total watched:</b> {data['total_watched']}\n"
                f"❤️ <b>Total liked:</b> {data['total_liked']}\n"
                f"🔄 <b>Total shared:</b> {data['total_shared']}"
            )
            await message.answer(text, parse_mode="HTML")
            await state.clear()

        except httpx.ConnectError:
            await processing.edit_text("Can't connect to the server. Please, try again later")

        except httpx.TimeoutException:
            await processing.edit_text("Request timed out. Please, try again later")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 422:
                await processing.edit_text("Invalid file format. Please, send a ZIP file")

            else:
                await processing.edit_text("An error occured. Please, try again later")




async def main() -> None:
    if TOKEN is None:
        raise RuntimeError("BOT_TOKEN is not set in environment")

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream = sys.stdout)
    asyncio.run(main()) 