from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio
import json
import re

API_TOKEN = 'YOUR_BOT_TOKEN'  # Замени на токен от @BotFather

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- ЗАГРУЗКА JSON ФАЙЛОВ ---
with open('faq.json', 'r', encoding='utf-8') as f:
    faq_data = json.load(f)
    faq_dict = faq_data["faq_dict"]
    faq_details = faq_data["faq_details"]

with open('setting.json', 'r', encoding='utf-8') as f:
    setting_guides = json.load(f)

with open('optimiz.json', 'r', encoding='utf-8') as f:
    optimiz_guides = json.load(f)

with open('clear.json', 'r', encoding='utf-8') as f:
    clear_guides = json.load(f)

# --- НОВОЕ: Загрузка beep_codes.json ---
try:
    with open('beep_codes.json', 'r', encoding='utf-8') as f:
        beep_codes_data = json.load(f)
    print(f"Загружено {len(beep_codes_data)} типов BIOS звуковых кодов.")
except FileNotFoundError:
    print("Файл beep_codes.json не найден. Функция 'Звуковые сигналы BIOS' будет отключена.")
    beep_codes_data = {}
except json.JSONDecodeError:
    print("Файл beep_codes.json содержит ошибки в формате. Функция 'Звуковые сигналы BIOS' будет отключена.")
    beep_codes_data = {}

# --- FSM для звуковых сигналов BIOS ---
class BeepCodeState(StatesGroup):
    waiting_for_bios_type = State()
    waiting_for_sequence = State()

# --- Reply Keyboard (появляется в поле ввода) ---
main_reply_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔧 Настройка")],
        [KeyboardButton(text="⚙️ Оптимизация")],
        [KeyboardButton(text="🧹 Очистка")],
        [KeyboardButton(text="🔊 Звуковые сигналы BIOS")], # <--- НОВАЯ КНОПКА
        [KeyboardButton(text="🛠️ Готовые скрипты")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Подменю "Настройка"
setup_reply_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отключить автозапуск")],
        [KeyboardButton(text="Отключить телеметрию")],
        [KeyboardButton(text="Отключить Bing и Cortana")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Подменю "Оптимизация"
optimize_reply_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отключить службы")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Подменю "Очистка"
clean_reply_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Очистить временные файлы")],
        [KeyboardButton(text="Очистить Windows Update")],
        [KeyboardButton(text="Очистить DNS кэш")],
        [KeyboardButton(text="Удалить кэш приложений")],
        [KeyboardButton(text="Очистить Recycle Bin")],
        [KeyboardButton(text="Проверка диска и очистка (SFC)")],
        [KeyboardButton(text="Отключить гибернацию")],
        [KeyboardButton(text="Изменить файл подкачки")],
        [KeyboardButton(text="Очистить кэш rescache")],
        [KeyboardButton(text="Очистить кэш обновлений")],
        [KeyboardButton(text="Очистить кэш системы")],
        [KeyboardButton(text="Скачать скрипт очистки диска")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Подменю "Скрипты"
scripts_reply_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Активация Windows")],
        [KeyboardButton(text="Удаление пароля")],
        [KeyboardButton(text="Обход блока для YT и DS")],
        [KeyboardButton(text="Скрипт очистки диска")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Inline Keyboard (только для кнопки "Подробнее" в ответах на текст)
def create_faq_keyboard(callback_data):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔧 Подробнее", callback_data=callback_data)]
    ])

# --- НОВОЕ: Inline Keyboard для выбора BIOS или "Как узнать?" ---
def create_bios_choice_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="IBM BIOS", callback_data="bios_ibm"),
            InlineKeyboardButton(text="Award BIOS", callback_data="bios_award")
        ],
        [
            InlineKeyboardButton(text="AMI BIOS", callback_data="bios_ami"),
            InlineKeyboardButton(text="AST BIOS", callback_data="bios_ast")
        ],
        [
            InlineKeyboardButton(text="Phoenix BIOS", callback_data="bios_phoenix"),
            InlineKeyboardButton(text="Compaq BIOS", callback_data="bios_compaq")
        ],
        [
            InlineKeyboardButton(text="DELL BIOS", callback_data="bios_dell"),
            InlineKeyboardButton(text="Quadtel BIOS", callback_data="bios_quadtel")
        ],
        [
            InlineKeyboardButton(text="Как узнать какой у меня BIOS?", callback_data="how_to_check_bios")
        ]
    ])

# --- НОВОЕ: Нормализация текста ---
def normalize_text(text: str) -> str:
    # Замена кириллических букв на латинские (например, 'с' -> 'c', 'а' -> 'a')
    cyrillic_to_latin = {
        'а': 'a', 'е': 'e', 'ё': 'e', 'и': 'i', 'о': 'o', 'у': 'u', 'ы': 'y', 'э': 'e',
        'А': 'A', 'Е': 'E', 'Ё': 'E', 'И': 'I', 'О': 'O', 'У': 'U', 'Ы': 'Y', 'Э': 'E',
        'с': 'c', 'к': 'k', 'р': 'p', 'х': 'x', 'у': 'y', 'в': 'v', 'т': 't', 'н': 'n',
        'А': 'A', 'С': 'C', 'К': 'K', 'Р': 'P', 'Х': 'X', 'У': 'Y', 'В': 'V', 'Т': 'T', 'Н': 'N'
    }
    for cyr, lat in cyrillic_to_latin.items():
        text = text.replace(cyr, lat)

    # Удаляем повторяющиеся символы (например, "активиииировать" -> "активировать")
    # Это помогает при опечатках
    text = re.sub(r'(.)\1{2,}', r'\1', text)

    # Приводим к нижнему регистру
    return text.lower()

# --- НОВОЕ: Обработчик нажатия на кнопку "🔊 Звуковые сигналы BIOS" ---
@dp.message(lambda m: m.text == "🔊 Звуковые сигналы BIOS")
async def ask_bios_type(message: types.Message, state: FSMContext):
    if not beep_codes_data:
        await message.answer("❌ Функция 'Звуковые сигналы BIOS' временно недоступна (файл данных отсутствует).")
        return

    keyboard = create_bios_choice_keyboard()
    await message.answer(
        "🔍 **Шаг 1 из 2:** Пожалуйста, укажите тип BIOS или узнайте, как его определить.",
        reply_markup=keyboard,
        parse_mode="MarkdownV2"
    )
    await state.set_state(BeepCodeState.waiting_for_bios_type)

# --- НОВОЕ: Обработчик нажатия кнопок выбора BIOS или "Как узнать?" ---
@dp.callback_query(lambda c: c.data.startswith("bios_") or c.data == "how_to_check_bios")
async def process_bios_choice(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer() # Закрываем уведомление о нажатии

    if callback_query.data == "how_to_check_bios":
        info_text = (
            "ℹ️ **Как узнать, какой у вас BIOS?**\n\n"
            "**Вариант 1:** Посмотреть документацию к вашему ПК (материнской плате).\n\n"
            "**Вариант 2:** Если Windows на компьютере загружается — нажмите сочетание клавиш **Win+R** (чтобы появилось окно \"Выполнить\"), и введите `msinfo32` (см. \"1\" на скрине ниже).\n\n"
            "**Вариант 3:** Зайти в настройки BIOS — в верхней части окна (обычно) всегда указывается версия."
        )
        # await callback_query.message.edit_text( # Не редактируем, а отправляем новое сообщение
        #     text=info_text,
        #     parse_mode="MarkdownV2"
        # )
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=info_text,
            parse_mode="MarkdownV2"
        )
        # После показа информации, снова спрашиваем BIOS
        keyboard = create_bios_choice_keyboard()
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="🔍 **Шаг 1 из 2 (повтор):** Пожалуйста, **выберите тип BIOS**.",
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        # Не меняем состояние, остаёмся на waiting_for_bios_type
        return

    # Если выбран тип BIOS
    bios_key = callback_query.data.replace("bios_", "") # Например, "ami"
    bios_info = beep_codes_data.get(bios_key)

    if not bios_info:
         await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="❌ Произошла ошибка: тип BIOS не найден. Попробуйте снова.",
            parse_mode="MarkdownV2"
        )
        await state.clear()
        return

    bios_name = bios_info.get("name", "Неизвестный BIOS")

    await callback_query.message.edit_text(
        text=f"✅ Выбран: **{bios_name}**\n\n"
             f"📋 **Шаг 2 из 2:** Теперь **введите последовательность сигналов** (например, `1 короткий 2 длинных` или `1-2-1`).",
        parse_mode="MarkdownV2"
    )
    await state.update_data(selected_bios=bios_key)
    await state.set_state(BeepCodeState.waiting_for_sequence)

# --- НОВОЕ: Обработчик ввода последовательности сигнала ---
@dp.message(BeepCodeState.waiting_for_sequence)
async def process_signal_sequence(message: types.Message, state: FSMContext):
    user_input_raw = message.text
    user_input_normalized = normalize_text(user_input_raw) # Нормализуем ввод

    data = await state.get_data()
    selected_bios_key = data.get("selected_bios")

    if not selected_bios_key or selected_bios_key not in beep_codes_data:
        await message.answer("❌ Произошла ошибка: тип BIOS не выбран или не найден. Попробуйте снова.")
        await state.clear()
        return

    bios_info = beep_codes_data[selected_bios_key]
    bios_codes = bios_info.get("codes", {})
    bios_name = bios_info.get("name", "Неизвестный BIOS")

    found_solution = None
    matched_key = None
    # Проходим по всем ключам (последовательностям) в кодах для выбранного BIOS
    for key in bios_codes:
        # Нормализуем ключ из JSON
        normalized_key = normalize_text(key)
        # Сравниваем нормализованный ввод с нормализованным ключом
        if user_input_normalized == normalized_key:
            found_solution = bios_codes[key]
            matched_key = key
            break

    if found_solution:
        # Извлекаем описание и решение из найденной записи
        description = found_solution.get("description", "Описание отсутствует.")
        solution = found_solution.get("solution", "Решение не найдено.")
        response = (
            f"**Решение для {bios_name}:**\n\n"
            f"**Код ошибки:** `{matched_key}`\n"  # Показываем оригинальный ключ
            f"**Описание:** {description}\n\n"
            f"**Решение:**\n```\n{solution}\n```"
        )
    else:
        response = f"❌ Решение для последовательности `{user_input_raw}` в BIOS **{bios_name}** не найдено в базе данных\\."

    await message.answer(response, parse_mode="MarkdownV2")
    await state.clear() # Сбрасываем состояние FSM

# --- Команда /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=main_reply_menu)

# --- Обработчики нажатий на кнопки Reply Keyboard (старые) ---
@dp.message(lambda m: m.text == "🔧 Настройка")
async def show_setup_menu(message: types.Message):
    await message.answer("🔧 Меню настройки:", reply_markup=setup_reply_menu)

@dp.message(lambda m: m.text == "⚙️ Оптимизация")
async def show_optimize_menu(message: types.Message):
    await message.answer("⚙️ Меню оптимизации:", reply_markup=optimize_reply_menu)

@dp.message(lambda m: m.text == "🧹 Очистка")
async def show_clean_menu(message: types.Message):
    await message.answer("🧹 Меню очистки:", reply_markup=clean_reply_menu)

@dp.message(lambda m: m.text == "🛠️ Готовые скрипты")
async def show_scripts_menu(message: types.Message):
    await message.answer("🛠️ Меню готовых скриптов:", reply_markup=scripts_reply_menu)

@dp.message(lambda m: m.text == "Назад")
async def back_to_main(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=main_reply_menu)

# --- Обработчики подменю "Настройка" (старые) ---
@dp.message(lambda m: m.text == "Отключить автозапуск")
async def send_setting_guide_autostart(message: types.Message):
    guide = setting_guides.get("disable_autostart")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Отключить телеметрию")
async def send_setting_guide_telemetry(message: types.Message):
    guide = setting_guides.get("disable_telemetry")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Отключить Bing и Cortana")
async def send_setting_guide_bing_cortana(message: types.Message):
    guide = setting_guides.get("disable_bing_cortana")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

# --- Обработчики подменю "Оптимизация" (старые) ---
@dp.message(lambda m: m.text == "Отключить службы")
async def send_optimiz_guide_services(message: types.Message):
    guide = optimiz_guides.get("disable_services")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

# --- Обработчики подменю "Очистка" (старые) ---
@dp.message(lambda m: m.text == "Очистить временные файлы")
async def send_clear_guide_temp_files(message: types.Message):
    guide = clear_guides.get("temp_files")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Очистить Windows Update")
async def send_clear_guide_windows_update(message: types.Message):
    guide = clear_guides.get("windows_update")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Очистить DNS кэш")
async def send_clear_guide_dns_cache(message: types.Message):
    guide = clear_guides.get("dns_cache")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Удалить кэш приложений")
async def send_clear_guide_app_cache(message: types.Message):
    guide = clear_guides.get("app_cache")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Очистить Recycle Bin")
async def send_clear_guide_recycle_bin(message: types.Message):
    guide = clear_guides.get("recycle_bin")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Проверка диска и очистка (SFC)")
async def send_clear_guide_sfc_check(message: types.Message):
    guide = clear_guides.get("sfc_check")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Отключить гибернацию")
async def send_clear_guide_disable_hibernation(message: types.Message):
    guide = clear_guides.get("disable_hibernation")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Изменить файл подкачки")
async def send_clear_guide_swap_file(message: types.Message):
    guide = clear_guides.get("swap_file")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Очистить кэш rescache")
async def send_clear_guide_rescache_clean(message: types.Message):
    guide = clear_guides.get("rescache_clean")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Очистить кэш обновлений")
async def send_clear_guide_windows_update_cache(message: types.Message):
    guide = clear_guides.get("windows_update_cache")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

@dp.message(lambda m: m.text == "Очистить кэш системы")
async def send_clear_guide_general_cache(message: types.Message):
    guide = clear_guides.get("general_cache")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

# --- Обработчик кнопки "Скачать скрипт очистки диска" из меню "Очистка" ---
@dp.message(lambda m: m.text == "Скачать скрипт очистки диска")
async def send_clean_script_from_clean_menu(message: types.Message):
    file_path = "scripts/Clean_disk_C.bat.txt"  # Путь к файлу в папке scripts
    try:
        await bot.send_document(
            chat_id=message.chat.id,
            document=types.FSInputFile(file_path),
            caption="Скрипт для очистки диска (Clean_disk_C.bat.txt)"
        )
    except Exception as e:
        await message.answer("❌ Файл не найден. Пожалуйста, свяжитесь с администратором.")

# --- Обработчики подменю "Готовые скрипты" (старые) ---
@dp.message(lambda m: m.text == "Активация Windows")
async def send_mas_info(message: types.Message):
    info_text = "```\nДля запуска скрипта активации Windows:\n\n1. Нажмите сочетание клавиш Win + X на клавиатуре.\n2. В появившемся меню выберите 'Windows PowerShell (Администратор)' или 'Терминал (Администратор)'.\n3. В открывшемся окне вставьте следующую команду и нажмите Enter:\n\nirm https://get.activated.win | iex\n\n⚠️ Важно: выполнение этой команды запустит скрипт активации.\nУбедитесь, что вы понимаете, что делаете, и доверяете источнику.\n```"
    await message.answer(info_text, parse_mode="MarkdownV2")

@dp.message(lambda m: m.text == "Удаление пароля")
async def send_delete_pass_info(message: types.Message):
    info_text = "```\nВ строке поиска Windows (рядом с кнопкой «Пуск») написать cmd или «командная строка».\nКликнуть правой кнопкой мыши по приложению, затем левой — «Запуск от имени администратора».\nВвести команду net user, чтобы посмотреть все учётные записи системы.\nОпределить имя учётной записи, для которой нужно сбросить пароль.\nВвести команду net user USERNAME *, где USERNAME — имя учётной записи, для которой сбрасывается пароль. После имени обязательно нужно поставить пробел и звёздочку.\nДважды нажать Enter, чтобы сбросить пароль.\n```"
    await message.answer(info_text, parse_mode="MarkdownV2")

@dp.message(lambda m: m.text == "Обход блока для YT и DS")
async def send_zapret_file(message: types.Message):
    file_path = "scripts/zapret-discord-youtube-1.7.2b.zip"  # Путь к файлу в папке scripts
    try:
        await bot.send_document(
            chat_id=message.chat.id,
            document=types.FSInputFile(file_path),
            caption="Архив с инструментами для обхода блокировки YouTube и Discord (zapret-discord-youtube-1.7.2b.zip)"
        )
    except Exception as e:
        await message.answer("❌ Файл не найден. Пожалуйста, свяжитесь с администратором.")

@dp.message(lambda m: m.text == "Скрипт очистки диска")
async def send_clean_script_from_scripts_menu(message: types.Message):
    file_path = "scripts/Clean_disk_C.bat.txt"  # Путь к файлу в папке scripts
    try:
        await bot.send_document(
            chat_id=message.chat.id,
            document=types.FSInputFile(file_path),
            caption="Скрипт для очистки диска (Clean_disk_C.bat.txt)"
        )
    except Exception as e:
        await message.answer("❌ Файл не найден. Пожалуйста, свяжитесь с администратором.")

# --- Обработка текстовых сообщений (FAQ) ---
@dp.message()
async def handle_text_message(message: types.Message):
    user_text = message.text.lower()
    response = "Неизвестный запрос. Попробуйте использовать кнопки или задайте вопрос иначе."
    keyboard = None

    for key, value in faq_dict.items():
        if key in user_text:
            response = value["message"]
            callback_data = value["callback_data"]
            keyboard = create_faq_keyboard(callback_data)
            break

    await message.answer(response, reply_markup=keyboard)

# --- Обработчик кнопки "Подробнее" (Inline Keyboard для FAQ) ---
@dp.callback_query(lambda c: c.data in faq_details)
async def show_faq_detail(callback_query: types.CallbackQuery):
    text = faq_details[callback_query.data]
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=text,
        parse_mode="MarkdownV2"
    )
    await callback_query.answer() # Закрывает уведомление о нажатии

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
