import os
import requests
import jdatetime
from PIL import Image, ImageDraw, ImageFont, features

# بررسی پشتیبانی از نمایش صحیح فارسی
if not features.check("raqm"):
    raise RuntimeError(
        "محیط اجرا از پردازش صحیح متن فارسی پشتیبانی نمی‌کند."
    )

W, H = 1080, 1350

BG = (22, 27, 34)
ORANGE = (238, 145, 48)
WHITE = (250, 250, 250)
GRAY = (190, 195, 202)

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

FONT_PATH = (
    "/usr/share/fonts/truetype/noto/"
    "NotoNaskhArabic-Regular.ttf"
)

if not os.path.exists(FONT_PATH):
    raise FileNotFoundError("فونت فارسی مناسب پیدا نشد.")

def font(size):
    return ImageFont.truetype(FONT_PATH, size)

now = jdatetime.datetime.now()

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

def text_width(text, fnt):
    box = draw.textbbox(
        (0, 0),
        text,
        font=fnt,
        direction="rtl",
        language="fa"
    )
    return box[2] - box[0]

def centered(text, y, fnt, color):
    draw.text(
        (W // 2, y),
        text,
        font=fnt,
        fill=color,
        anchor="mm",
        direction="rtl",
        language="fa"
    )

# کادر اصلی
draw.rounded_rectangle(
    (30, 30, W - 30, H - 30),
    radius=32,
    outline=ORANGE,
    width=5
)

draw.rounded_rectangle(
    (70, 70, W - 70, 88),
    radius=8,
    fill=ORANGE
)

# سربرگ شرکت
centered("آهن استحکام دیاکو", 165, font(60), ORANGE)

draw.text(
    (W // 2, 225),
    "AHAN ESTEHKAM DIYACO",
    font=font(28),
    fill=WHITE,
    anchor="mm"
)

draw.line(
    (140, 280, W - 140, 280),
    fill=ORANGE,
    width=3
)

# عنوان و تاریخ شمسی
centered("تقویم روزانه", 350, font(46), WHITE)

centered(
    now.strftime("%Y/%m/%d"),
    440,
    font(45),
    ORANGE
)

# کادر جمله روز
draw.rounded_rectangle(
    (85, 580, W - 85, 970),
    radius=28,
    outline=ORANGE,
    width=3
)

quote = quotes[now.timetuple().tm_yday % len(quotes)]
quote_font = font(40)

# تقسیم جمله با حفظ پردازش صحیح فارسی
words = quote.split()
lines = []
current = ""

for word in words:
    candidate = (current + " " + word).strip()

    if text_width(candidate, quote_font) <= 820:
        current = candidate
    else:
        if current:
            lines.append(current)
        current = word

if current:
    lines.append(current)

line_height = 78
start_y = 775 - (len(lines) - 1) * line_height // 2

for i, line in enumerate(lines):
    centered(
        line,
        start_y + i * line_height,
        quote_font,
        WHITE
    )

# بخش پایانی
centered("اعتماد | کیفیت | تعهد", 1050, font(35), ORANGE)
centered("@ahandiyaco1401", 1130, font(29), GRAY)
centered(
    "همراه شما در تأمین محصولات فولادی",
    1210,
    font(28),
    WHITE
)

# ذخیره تصویر
img.save("daily_calendar.png")

# ارسال به کانال
token = os.environ["TELEGRAM_BOT_TOKEN"]
channel = os.environ["TELEGRAM_CHANNEL"]

with open("daily_calendar.png", "rb") as photo:
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        data={
            "chat_id": channel,
            "caption": (
                "آهن استحکام دیاکو | تقویم روزانه | "
                + now.strftime("%Y/%m/%d")
            )
        },
        files={"photo": photo},
        timeout=60
    )

response.raise_for_status()

if not response.json().get("ok"):
    raise RuntimeError("انتشار تصویر در تلگرام ناموفق بود.")

print("تقویم روزانه با موفقیت منتشر شد.")
