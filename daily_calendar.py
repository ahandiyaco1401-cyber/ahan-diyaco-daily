import os
import glob
import requests
import jdatetime
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

# ابعاد تصویر
W, H = 1080, 1350

# رنگ‌بندی صنعتی
BG = (22, 27, 34)
ORANGE = (238, 145, 48)
WHITE = (250, 250, 250)
GRAY = (190, 195, 202)

# جملات انگیزشی
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

# اصلاح نوشتار فارسی و جهت متن
def fa(text):
    shaped = arabic_reshaper.reshape(str(text))
    return get_display(shaped)

# پیدا کردن فونت مناسب فارسی
def font(size):
    paths = [
        "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]

    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    found = glob.glob(
        "/usr/share/fonts/**/*Arabic*Regular*.ttf",
        recursive=True
    )

    if found:
        return ImageFont.truetype(found[0], size)

    raise RuntimeError("فونت مناسب پیدا نشد.")

# تاریخ
now = jdatetime.datetime.now()
gregorian = now.togregorian()

# ایجاد تصویر
img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# کادر اصلی
draw.rounded_rectangle(
    (30, 30, W - 30, H - 30),
    radius=32,
    outline=ORANGE,
    width=5
)

draw.rounded_rectangle(
    (65, 70, W - 65, 88),
    radius=8,
    fill=ORANGE
)

# نوشتن متن در مرکز تصویر
def centered(text, y, fnt, color):
    draw.text(
        (W // 2, y),
        fa(text),
        font=fnt,
        fill=color,
        anchor="mm"
    )

# سربرگ
centered("آهن استحکام دیاکو", 165, font(60), ORANGE)
centered("AHAN ESTEHKAM DIYACO", 225, font(28), WHITE)

draw.line(
    (140, 280, W - 140, 280),
    fill=ORANGE,
    width=3
)

# عنوان تقویم
centered("تقویم روزانه", 350, font(46), WHITE)

# تاریخ شمسی و میلادی
centered(
    now.strftime("%Y/%m/%d"),
    435,
    font(43),
    ORANGE
)

centered(
    gregorian.strftime("%Y/%m/%d"),
    495,
    font(32),
    GRAY
)

# کادر جمله انگیزشی
draw.rounded_rectangle(
    (85, 590, W - 85, 970),
    radius=28,
    outline=ORANGE,
    width=3
)

# انتخاب جمله روز
quote = quotes[now.timetuple().tm_yday % len(quotes)]

# شکستن جمله به خطوط متناسب با عرض کادر
quote_font = font(40)
words = quote.split()
lines = []
current_line = ""

for word in words:
    candidate = (current_line + " " + word).strip()
    displayed = fa(candidate)

    box = draw.textbbox(
        (0, 0),
        displayed,
        font=quote_font
    )

    width = box[2] - box[0]

    if width <= 820:
        current_line = candidate
    else:
        if current_line:
            lines.append(current_line)
        current_line = word

if current_line:
    lines.append(current_line)

# قرار دادن خطوط در مرکز کادر
line_height = 78
total_height = (len(lines) - 1) * line_height
start_y = 780 - total_height // 2

for index, line in enumerate(lines):
    centered(
        line,
        start_y + index * line_height,
        quote_font,
        WHITE
    )

# اطلاعات پایانی
centered(
    "اعتماد | کیفیت | تعهد",
    1050,
    font(35),
    ORANGE
)

centered(
    "@ahandiyaco1401",
    1130,
    font(29),
    GRAY
)

centered(
    "همراه شما در تأمین محصولات فولادی",
    1210,
    font(28),
    WHITE
)

# ذخیره تصویر
img.save("daily_calendar.png")

# ارسال به تلگرام
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

result = response.json()

if not result.get("ok"):
    raise RuntimeError(
        "ارسال تصویر ناموفق بود: " + str(result)
    )

print("تقویم روزانه با موفقیت منتشر شد.")
