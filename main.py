import re
import asyncio
from telethon import TelegramClient, events
from aiogram import Bot, Dispatcher

# ==== 1. НАСТРОЙКИ ====
# Эти данные ты получишь на сайте my.telegram.org
API_ID = int("29333521")
API_HASH = "a628993ea695e1580829863dac9d99b9"

# Твой bot token от BotFather:
BOT_TOKEN = "8485398329:AAFN7xq37IAuh-mvdzC_XrYkdw_ICxGyYBc"

# ID чата, куда бот будет отправлять подборки (твой Telegram ID):
USER_ID = int("456496188")

# Список каналов, которые бот должен отслеживать (их @имена или numeric ID):
CHANNELS_TO_WATCH = [
    "https://t.me/PremierAgency24",
    "https://t.me/castingnncway",
    "https://t.me/spotcasting",
    "https://t.me/c/2090693689",
    "https://t.me/c/2569890697",
    "https://t.me/castings5000",
    "https://t.me/KastingEA",
    "https://t.me/joinchat/-8BL9dl926I5ZWYy",
    "https://t.me/vsemassovki",
    "https://t.me/c/3046014819",
    "https://t.me/castingsertainss",
    "https://t.me/modeli_kastingi_msk",
    "https://t.me/mskeventjob",
    "https://t.me/castingsactors",
    "https://t.me/facetoface_ma",
    "https://t.me/c/1797191303",
    "https://t.me/cast_day",
    "https://t.me/castingsmsc",
    "https://t.me/tfp_commerce",
    "https://t.me/newcast2023",
    "https://t.me/casting_moscoww",
    "https://t.me/artiyork_casting_director",
    "https://t.me/KatyaLetoKastDir",
    "https://t.me/moscowfilms",
    "https://t.me/kinoandreclama",
    "https://t.me/SPBmskcasting",
    "https://t.me/acmodasi_ru",
    "https://t.me/kastingi2",
    "https://t.me/artpablopirat",
    "https://t.me/kastingi3",
    "https://t.me/Agent_golomidov",
    "https://t.me/AgencyMalykh",
    "https://t.me/topmediarina",
    "https://t.me/elimodmodels",
    "https://t.me/gogotovacasting",
    "https://t.me/c/1406211267",
    "https://t.me/c/2578843731",
    "https://t.me/castingpolinagroup",
    "https://t.me/kastingiD",
    "https://t.me/SilaModelingaVIDTV",
    "https://t.me/TALOCHKiNAvera_official",
    "https://t.me/vbmodel",
    "https://t.me/fancypeolechannel",
    "https://t.me/newfacescasting",
    "https://t.me/nebytov_entr",
    "https://t.me/c/2996032086"
]

# ==== 2. Личная информация и критерии ====

MY_HEIGHT = 166
MAX_ACCEPTABLE_HEIGHT = 168

ALLOWED_HAIR = ["рус", "блондин", "рыж"]  # включают русые, блонд, рыжие
FORBIDDEN_HAIR = ["брюнет"]

MY_SIZE = 46
ALLOWED_SIZES = [46, 48]
FORBIDDEN_SIZES = [44, 42, 40, 50, 52, 54]

# Параметры фигуры
BUST = 95
WAIST = 75
HIPS = 100

BUST_RANGE = (BUST - 3, BUST + 3)
WAIST_RANGE = (WAIST - 3, WAIST + 3)
HIPS_RANGE = (HIPS - 3, HIPS + 3)

AGE_MIN = 27
AGE_MAX = 37

CITY = "моск"  # ищем по ключу “моск” → Москва

BLOCK_WORDS = [
    "обучени", "курс", "тренинг", "платн", "купит", "взнос",
    "оплат", "донат", "покупк", "заняти", "вебинар"
]

# ==== 3. Инициализация ====
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = TelegramClient("session", API_ID, API_HASH)


# ==== 4. Функции для фильтрации ====

def contains(block_list, text):
    return any(word in text for word in block_list)


def extract_number(pattern, text):
    m = re.search(pattern, text)
    return int(m.group(1)) if m else None


def check_height(text):
    h = extract_number(r"рост[^0-9]{0,10}(\d{2,3})", text)
    if h is None:
        return True
    return h <= MAX_ACCEPTABLE_HEIGHT


def check_hair(text):
    if contains(FORBIDDEN_HAIR, text):
        return False
    if contains(ALLOWED_HAIR, text):
        return True
    return True


def check_size(text):
    s = extract_number(r"размер[^0-9]{0,10}(\d{2})", text)
    if s is None:
        return True
    if s in ALLOWED_SIZES:
        return True
    if s in FORBIDDEN_SIZES:
        return False
    return False


def check_parameters(text):
    bust = extract_number(r"груд[^\d]{0,10}(\d{2,3})", text)
    waist = extract_number(r"тали[^\d]{0,10}(\d{2,3})", text)
    hips = extract_number(r"бед[^\d]{0,10}(\d{2,3})", text)

    if bust and not (BUST_RANGE[0] <= bust <= BUST_RANGE[1]):
        return False
    if waist and not (WAIST_RANGE[0] <= waist <= WAIST_RANGE[1]):
        return False
    if hips and not (HIPS_RANGE[0] <= hips <= HIPS_RANGE[1]):
        return False

    return True


def check_age(text):
    a = extract_number(r"возраст[^0-9]{0,10}(\d{2})", text)
    if a is None:
        return True
    return AGE_MIN <= a <= AGE_MAX


def check_city(text):
    # Москва / Подмосковье / заграница
    if CITY in text:
        return True
    if "выезд" in text:
        return True
    return False


def is_paid_offer(text):
    return contains(BLOCK_WORDS, text)


# ==== 5. ОБРАБОТКА СООБЩЕНИЙ ИЗ КАНАЛОВ ====

@client.on(events.NewMessage(chats=CHANNELS_TO_WATCH))
async def new_post(event):
    text = event.raw_text.lower()

    if is_paid_offer(text):
        return

    if not check_height(text):
        return
    if not check_hair(text):
        return
    if not check_size(text):
        return
    if not check_parameters(text):
        return
    if not check_age(text):
        return
    if not check_city(text):
        return

    await bot.send_message(USER_ID, f"Найдено подходящее объявление:\n\n{text}")


# ==== 6. ЗАПУСК ====
async def main():
    await client.start()
    print("Бот запущен и слушает каналы...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
