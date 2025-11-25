import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from math import ceil
from aiogram.filters import Command
import asyncio
import json
import re
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance 

load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN')

if not API_TOKEN:
    print("Ошибка: BOT_TOKEN не найден в переменных окружения.")
    exit(1)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

try:
    with open('faq.json', 'r', encoding='utf-8') as f:
        faq_data = json.load(f)
        faq_dict = faq_data["faq_dict"]
        faq_details = faq_data["faq_details"]
    print(f"Загружено {len(faq_dict)} FAQ записей.")
except Exception as e:
    print(f"Ошибка загрузки faq.json: {e}")
    faq_dict = {}
    faq_details = {}

try:
    with open('setting.json', 'r', encoding='utf-8') as f:
        setting_guides = json.load(f)
    print(f"Загружено {len(setting_guides)} настроек.")
except Exception as e:
    print(f"Ошибка загрузки setting.json: {e}")
    setting_guides = {}

try:
    with open('optimiz.json', 'r', encoding='utf-8') as f:
        optimiz_guides = json.load(f)
    print(f"Загружено {len(optimiz_guides)} оптимизаций.")
except Exception as e:
    print(f"Ошибка загрузки optimiz.json: {e}")
    optimiz_guides = {}

try:
    with open('clear.json', 'r', encoding='utf-8') as f:
        clear_guides = json.load(f)
    print(f"Загружено {len(clear_guides)} очисток.")
except Exception as e:
    print(f"Ошибка загрузки clear.json: {e}")
    clear_guides = {}

# --- НОВОЕ: Загружаем error_solutions.json с отладкой ---
try:
    with open('error_solutions.json', 'r', encoding='utf-8') as f:
        error_solutions_dict = json.load(f)
    print(f"Загружено {len(error_solutions_dict)} решений ошибок BSOD.")
    # Проверим наличие конкретных ключей
    if "0x00000069" in error_solutions_dict:
        print("Ключ '0x00000069' найден в error_solutions.json")
    else:
        print("Ключ '0x00000069' НЕ НАЙДЕН в error_solutions.json")
    if "0x00000001" in error_solutions_dict:
        print("Ключ '0x00000001' найден в error_solutions.json")
    else:
        print("Ключ '0x00000001' НЕ НАЙДЕН в error_solutions.json")
except json.JSONDecodeError as je:
    print(f"Ошибка синтаксиса JSON в error_solutions.json: {je}")
    error_solutions_dict = {}
except FileNotFoundError:
    print("Файл error_solutions.json не найден в папке с main.py!")
    error_solutions_dict = {}
except Exception as e:
    print(f"Ошибка загрузки error_solutions.json: {e}")
    error_solutions_dict = {}

# --- НОВОЕ: Загружаем error_codes_names.json ---
try:
    with open('error_codes_names.json', 'r', encoding='utf-8') as f:
        error_codes_names_dict = json.load(f)
    print(f"Загружено {len(error_codes_names_dict)} названий ошибок BSOD.")
except json.JSONDecodeError as je:
    print(f"Ошибка синтаксиса JSON в error_codes_names.json: {je}")
    error_codes_names_dict = {}
except FileNotFoundError:
    print("Файл error_codes_names.json не найден в папке с main.py!")
    error_codes_names_dict = {}
except Exception as e:
    print(f"Ошибка загрузки error_codes_names.json: {e}")
    error_codes_names_dict = {}

# Reply Keyboard (появляется в поле ввода)
main_reply_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔧 Настройка")],
        [KeyboardButton(text="⚙️ Оптимизация")],
        [KeyboardButton(text="🧹 Очистка")],
        [KeyboardButton(text="🛡️ Коды ошибок Windows")], # Новая кнопка
        [KeyboardButton(text="🛠️ Готовые скрипты")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Reply Keyboard для подменю
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

optimize_reply_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отключить службы")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

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

# Новое подменю для скриптов (обновлено)
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

# Нормализация текста
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


    text = re.sub(r'(.)\1{2,}', r'\1', text)

    # Приводим к нижнему регистру
    return text.lower()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 Привет! Я — <b>WinHelper</b>, твой помощник по настройке, оптимизации, очистке и диагностике Windows 11.\n\n"
        "<b>Что я умею:</b>\n"
        "🔧 <b>Настройка:</b> Отключение ненужных функций (Cortana, телеметрия, Bing в поиске и т.д.) для упрощения и повышения приватности.\n"
        "⚙️ <b>Оптимизация:</b> Рекомендации по отключению служб, настройке визуальных эффектов, файлов подкачки и т.п. для улучшения производительности.\n"
        "🧹 <b>Очистка:</b> Инструкции по удалению временных файлов, кэша обновлений, гибернации и другого мусора для освобождения места и ускорения системы.\n"
        "🛠️ <b>Готовые скрипты:</b> Предоставление полезных скриптов (например, для очистки, активации).\n"
        "🛡️ <b>Решение ошибок BSOD:</b> Поиск и отправка инструкций по устранению неполадок по коду ошибки (например, 0x00000001).\n\n"
        "<b>Важно:</b>\n"
        "⚠️ Я предлагаю <i>рекомендации и инструкции</i>. Применение их может <b>улучшить</b> работу ПК, но также <b>требует осторожности</b>.\n"
        "⚠️ <b>Всегда создавайте точку восстановления системы перед внесением изменений.</b>\n"
        "⚠️ Вы <b>используете</b> этого бота <b>на свой страх и риск</b>. Автор бота <b>не несёт ответственности</b> за возможные проблемы, повреждение данных или неисправность оборудования, возникшие в результате выполнения инструкций.\n"
        "💡 <i>Бот — это помощник, а не панацея от всех бед. Всегда думайте критически и уточняйте информацию.</i>\n\n"
        "Выберите действие с помощью кнопок ниже или задайте вопрос текстом."
    )
    await message.answer(welcome_text, reply_markup=main_reply_menu, parse_mode="HTML")


ERROR_CODES_PER_PAGE = 40

def escape_md_v2(text: str) -> str:
    """
    Экранирует специальные символы MarkdownV2.
    """
    # Эти символы нужно экранировать, если они не используются в синтаксисе
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, '\\' + char)
    return text

def get_page_content(page_number: int, codes_dict: dict):
    """
    Возвращает список строк для заданной страницы.
    """
    sorted_items = sorted(codes_dict.items())
    start_index = page_number * ERROR_CODES_PER_PAGE
    end_index = start_index + ERROR_CODES_PER_PAGE
    page_items = sorted_items[start_index:end_index]

    # --- ИСПРАВЛЕНО: экранируем имя ошибки ---
    lines = [f"{escape_md_v2(name)} - {code}" for code, name in page_items]
    return lines
    
def get_navigation_keyboard(current_page: int, total_pages: int):
    """
    Возвращает InlineKeyboardMarkup с кнопками навигации.
    """
    keyboard = []
    row = []
    if current_page > 0:
        row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"error_codes_page_{current_page - 1}"))
    if current_page < total_pages - 1:
        row.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"error_codes_page_{current_page + 1}"))
    if row:
        keyboard.append(row)

    # Кнопка "Назад к меню"
    keyboard.append([InlineKeyboardButton(text="🔙 Назад к меню", callback_data="back_to_main_menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(lambda m: m.text == "🛡️ Коды ошибок Windows")
async def send_error_codes_list(message: types.Message):
    if not error_codes_names_dict:
        await message.answer("❌ Файл с названиями ошибок не найден или пуст.")
        return

    total_pages = ceil(len(error_codes_names_dict) / ERROR_CODES_PER_PAGE)
    current_page = 0

    lines = get_page_content(current_page, error_codes_names_dict)
    content = "\n".join(lines)

    keyboard = get_navigation_keyboard(current_page, total_pages)

    # --- ИСПРАВЛЕНО: экранируем заголовок ---
    escaped_title = escape_md_v2(f"Коды ошибок Windows (Страница {current_page + 1}/{total_pages}):")
    await message.answer(f"**{escaped_title}**\n\n```\n{content}\n```", parse_mode="MarkdownV2", reply_markup=keyboard)

# Обработчик навигации по страницам
@dp.callback_query(lambda c: c.data.startswith("error_codes_page_"))
async def navigate_error_codes_pages(callback_query: types.CallbackQuery):
    page_number = int(callback_query.data.split('_')[-1])

    total_pages = ceil(len(error_codes_names_dict) / ERROR_CODES_PER_PAGE)

    # Проверим, что номер страницы в пределах
    if page_number < 0 or page_number >= total_pages:
        await callback_query.answer("Недопустимый номер страницы.", show_alert=True)
        return

    lines = get_page_content(page_number, error_codes_names_dict)
    content = "\n".join(lines)

    keyboard = get_navigation_keyboard(page_number, total_pages)

    # --- ИСПРАВЛЕНО: экранируем заголовок ---
    escaped_title = escape_md_v2(f"Коды ошибок Windows (Страница {page_number + 1}/{total_pages}):")
    await callback_query.message.edit_text(
        text=f"**{escaped_title}**\n\n```\n{content}\n```",
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )
    await callback_query.answer()

# Обработчик кнопки "Назад к меню" из списка ошибок
@dp.callback_query(lambda c: c.data == "back_to_main_menu")
async def back_to_main_menu(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    short_welcome = (
        "✅  Главное меню <b>WinHelper</b>.\n\n"
        "Выберите интересующий вас раздел для настройки, оптимизации, очистки или получения помощи по ошибкам Windows:"
    )
    await callback_query.message.answer(short_welcome, reply_markup=main_reply_menu, parse_mode="HTML")
    await callback_query.answer()


# Обработчики нажатий на кнопки Reply Keyboard
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

# Обработчики подменю "Настройка"
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

# Обработчики подменю "Оптимизация"
@dp.message(lambda m: m.text == "Отключить службы")
async def send_optimiz_guide_services(message: types.Message):
    guide = optimiz_guides.get("disable_services")
    if guide:
        await message.answer(guide["text"], parse_mode="MarkdownV2")
    else:
        await message.answer("❌ Подсказка не найдена.")

# Обработчики подменю "Очистка"
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

# Обработчик кнопки "Скачать скрипт очистки диска" из меню "Очистка"
@dp.message(lambda m: m.text == "Скачать скрипт очистки диска")
async def send_clean_script_from_clean_menu(message: types.Message):
    file_path = "scripts/Clean_disk_C.bat.txt" 
    try:
        await bot.send_document(
            chat_id=message.chat.id,
            document=types.FSInputFile(file_path),
            caption="Скрипт для очистки диска (Clean_disk_C.bat.txt)"
        )
    except Exception as e:
        await message.answer("❌ Файл не найден. Пожалуйста, свяжитесь с администратором.")

# Обработчики подменю "Готовые скрипты"
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
    file_path = "scripts/zapret-discord-youtube-1.7.2b.zip" 
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
    file_path = "scripts/Clean_disk_C.bat.txt" 
    try:
        await bot.send_document(
            chat_id=message.chat.id,
            document=types.FSInputFile(file_path),
            caption="Скрипт для очистки диска (Clean_disk_C.bat.txt)"
        )
    except Exception as e:
        await message.answer("❌ Файл не найден. Пожалуйста, свяжитесь с администратором.")

# --- НОВОЕ: Обработчик сообщений с кодом ошибки ---
@dp.message()
async def handle_error_code_message(message: types.Message):
    user_text = message.text.lower()

    match = re.search(r'0x[0-9A-Fa-f]{8}', user_text)

    if match:
       
        error_code = match.group(0).lower()
        solution = error_solutions_dict.get(error_code)

        if solution:
              
            await message.answer(f"❌ Решение для ошибки `{error_code}` не найдено в базе данных\\.", parse_mode="MarkdownV2")
      
        return

  
    normalized_user_text = normalize_text(user_text)

    response = "Неизвестный запрос. Попробуйте использовать кнопки или задайте вопрос иначе."
    keyboard = None

    best_match = None
    best_similarity = 0  

    
    for key in faq_dict:
        
        normalized_key = normalize_text(key)
        
        similarity = normalized_damerau_levenshtein_distance(normalized_user_text, normalized_key)

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = key

    if best_similarity > 0.7:
        matched_entry = faq_dict[best_match]
        response = matched_entry["message"]
        callback_data = matched_entry["callback_data"]
        keyboard = create_faq_keyboard(callback_data)
    # else: # Необязательно, можно оставить стандартный ответ

    await message.answer(response, reply_markup=keyboard)


# Обработчик кнопки "Подробнее" (Inline Keyboard для FAQ)
@dp.callback_query(lambda c: c.data in faq_details)
async def show_faq_detail(callback_query: types.CallbackQuery):
    text = faq_details[callback_query.data]
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=text,
        parse_mode="MarkdownV2"
    )
    await callback_query.answer()

# Запуск бота
async def main():
    print("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
