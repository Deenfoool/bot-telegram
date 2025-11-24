from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import asyncio
import json
import re
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance

API_TOKEN = '8595692863:AAH2QENhXN6Cjdkmt-D0sneu3h6eJ6bWD5o'  # Замени на токен от @BotFather

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Загружаем JSON файлы
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

# Reply Keyboard (появляется в поле ввода)
main_reply_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔧 Настройка")],
        [KeyboardButton(text="⚙️ Оптимизация")],
        [KeyboardButton(text="🧹 Очистка")],
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

    # Удаляем повторяющиеся символы (например, "активиииировать" -> "активировать")
    # Это помогает при опечатках
    text = re.sub(r'(.)\1{2,}', r'\1', text)

    # Приводим к нижнему регистру
    return text.lower()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=main_reply_menu)

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
    file_path = "scripts/Clean_disk_C.bat.txt"  # Путь к файлу в папке scripts
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

# Обработка текстовых сообщений (FAQ) с нормализацией и Damerau-Levenshtein
@dp.message()
async def handle_text_message(message: types.Message):
    user_text = message.text.lower()
    # Нормализуем ввод пользователя
    normalized_user_text = normalize_text(user_text)

    response = "Неизвестный запрос. Попробуйте использовать кнопки или задайте вопрос иначе."
    keyboard = None

    best_match = None
    best_similarity = 0  # Будем искать НАИБОЛЬШУЮ схожесть (1.0 - идентично, 0.0 - совсем разные)

    # Проходим по всем ключам из словаря FAQ
    for key in faq_dict:
        # Нормализуем ключ из словаря
        normalized_key = normalize_text(key)
        # Сравниваем нормализованный ввод с нормализованным ключом
        # normalized_damerau_levenshtein_distance возвращает 1.0 (идентичны) - 0.0 (совсем разные)
        similarity = normalized_damerau_levenshtein_distance(normalized_user_text, normalized_key)

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = key

    # Если лучшая схожесть достаточно высокая (например, > 0.7) - это порог настраивается
    # 0.7 означает, что 70% символов (с учётом транспозиций) совпадают
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
    await callback_query.answer() # Закрывает уведомление о нажатии

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
