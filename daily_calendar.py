import os
import requests
import jdatetime
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350

BG = (20, 24, 30)
ORANGE = (235, 135, 45)
WHITE = (245, 245, 245)
GRAY = (180, 185, 190)

quotes = [
    "موفقیت از اعتماد، تعهد و تلاش مستمر ساخته می‌شود.",
    "کیفیت امروز، اعتبار فردای کسب‌وکار شماست.",
    "اعتماد مشتری، ارزشمندترین سرمایه ماست.",
    "هر همکاری پایدار، با صداقت آغاز می‌شود.",
    "برای موفقیت، کیفیت را به عادت تبدیل کنید.",
    "قدم‌های کوچک و مستمر، نتایج بزرگ می‌سازند.",
    "اعتبار بازرگانی با تعهد به مشتری ساخته می‌شود.",
    "بهترین معامله، معامله‌ای همراه با اعتماد است.",
    "پشت هر موفقیت بزرگ، تلاش پیوسته قرار دارد.",
    "کیفیت، امضای ماندگار یک کسب‌وکار است."
]

def fa(text):
    return arabic_reshaper.reshape(str(text))

def font(size):
    paths = [
        "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

now = jdatetime.datetime.now()
gregorian = now.togregorian()

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

draw.rounded_rectangle(
    (35, 35, W - 35, H - 35),
    radius=28,
    outline=ORANGE,
    width=5
)

draw.rectangle((70, 75, W - 70, 85), fill=ORANGE)

def centered(text, y, fnt, fill):
    draw.text(
        (W // 2, y),
        fa(text),
        font=fnt,
        fill=fill,
        anchor="mm"
    )
direction="rtl"
centered("آهن استحکام دیاکو", 175, font(62), ORANGE)
centered("AHAN ESTEHKAM DIYACO", 235, font(29), WHITE)

draw.line((150, 290, W - 150, 290), fill=ORANGE, width=3)

centered("تقویم روزانه", 365, font(46), WHITE)
centered(now.strftime("%A %d %B %Y"), 460, font(40), ORANGE)
centered(gregorian.strftime("%Y/%m/%d"), 520, font(34), GRAY)

draw.rounded_rectangle(
    (100, 620, W - 100, 970),
    radius=30,
    outline=ORANGE,
    width=3
)

quote = quotes[now.timetuple().tm_yday % len(quotes)]
words = quote.split()
lines = []
line = ""

for word in words:
    test = (line + " " + word).strip()
    shaped = fa(test)
    box = draw.textbbox((0, 0), shaped, font=font(43))

    if box[2] - box[0] < 790:
        line = test
    else:
        if line:
            lines.append(line)
        line = word

if line:
    lines.append(line)

start_y = 795 - (len(lines) - 1) * 45

for i, part in enumerate(lines):
    centered(part, start_y + i * 90, font(43), WHITE)

centered("اعتماد • کیفیت • تعهد", 1080, font(36), ORANGE)
centered("@ahandiyaco1401", 1160, font(30), GRAY)
centered("همراه شما در تأمین محصولات فولادی", 1230, font(28), WHITE)

img.save("daily_calendar.png")

token = os.environ["TELEGRAM_BOT_TOKEN"]
channel = os.environ["TELEGRAM_CHANNEL"]

with open("daily_calendar.png", "rb") as photo:
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        data={
            "chat_id": channel,
            "caption": "آهن استحکام دیاکو | " + now.strftime("%Y/%m/%d")
        },
        files={"photo": photo},
        timeout=60
    )

response.raise_for_status()

if not response.json().get("ok"):
    raise RuntimeError(response.text)

print("تصویر تقویم با موفقیت منتشر شد.")
