
import openai
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from litellm import completion

key = "YOUR OPENAI API KEY"
tg_token = "YOUR TELEGRAM TOKEN"

openai.api_key = key
bot = Bot(tg_token)
dp = Dispatcher(bot)

user_requests = {}
chat_active = False


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_start = types.KeyboardButton('/help')
    keyboard.add(button_start)
    user = message.from_user
    await message.answer(f"Привет, {user.first_name}! Нажмите /help, чтобы получить дополнительную информацию о командах бота.", reply_markup=keyboard)

async def send_menu(message: types.Message):
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.add(
        types.KeyboardButton('/activation'),
        types.KeyboardButton('/stop'),
        types.KeyboardButton('/help'),
        types.KeyboardButton('/info')
    )
    return keyboard_markup

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/activation - Активировать чат с GPT-3 для решения математических задач\n"
        "/stop - Завершить диалог с GPT-3\n"
        "/help - Получить список доступных команд\n"
        "/info - Получить список возможностей бота\n"
    )
    menu = await send_menu(message)
    await message.answer(help_text, reply_markup=menu)

@dp.message_handler(commands=['info'])
async def help_command(message: types.Message):
    info_text = (
        "Наш бот использует ChatGPT-3.5 и поможет решить вам любую математическую задачу!\n"
        "Для списка команд вы можете написать /help\n"
        "Во время использования нейросети советуем использовать ключевое слово 'реши'.\n"
        "Наши соц.сети:"
    )
    await message.answer(info_text)

@dp.message_handler(commands=['activation'])
async def start_chat(message: types.Message):
    global chat_active
    chat_active = True
    user_id = message.from_user.id

    await message.answer("Бот активирован. Теперь вы можете отправлять математические задачи для решения.")
@dp.message_handler(commands=['stop'])
async def stop_chat(message: types.Message):
    global chat_active
    if not chat_active:
        await message.answer("Вы еще не начинали диалог с GPT-3.")
        return

    chat_active = False
    await message.answer("Диалог с GPT-3 завершен. Если вы хотите начать чат заново, нажмите /activation.")

@dp.message_handler()
async def message(message: types.Message):
    global chat_active
    user_id = message.from_user.id

    if chat_active:
        math_keywords = ["реши", "посчитай", "вычисли", "задачу", "задача", "формула", "задачи", "теорема", "решение", "ответ", "+", "-", "*", "/"]
        is_math_task = any(keyword in message.text.lower() for keyword in math_keywords)

        if is_math_task:
            user_requests[user_id] = message.text

            response = completion(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Вы: " + message.text}],
                temperature=0.5,
                max_tokens=1024,
                stop=["\n"],
                api_key="YOUR OPENAI API KEY",

            )

            await message.answer(response['choices'][0]['message']['content'])
        else:
            await message.answer("Извините, я специализируюсь на математических задачах. Пожалуйста, отправьте математическую задачу.")
    else:
        await message.answer("Неккоректная команда, введите /help дабы получить список доступных команд.")

executor.start_polling(dp)

