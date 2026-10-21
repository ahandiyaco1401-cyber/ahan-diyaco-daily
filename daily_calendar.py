import os
import html
import asyncio
import requests
import jdatetime

from playwright.async_api import async_playwright


W = 1080
H = 1350

ORANGE = "#EE9130"
BG = "#161B22"
WHITE = "#FAFAFA"
GRAY = "#BEC3CA"

QUOTES = [
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


def create_html():
    now = jdatetime.datetime.now()
    gregorian = now.togregorian()

    quote = QUOTES[now.timetuple().tm_yday % len(QUOTES)]

    jalali_date = html.escape(now.strftime("%Y/%m/%d"))
    gregorian_date = html.escape(gregorian.strftime("%Y/%m/%d"))
    quote = html.escape(quote)

    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">

<style>
* {{
    box-sizing: border-box;
}}

html, body {{
    margin: 0;
    padding: 0;
    width: {W}px;
    height: {H}px;
}}

body {{
    background: {BG};
    color: {WHITE};
    font-family: "Noto Naskh Arabic", "Noto Sans Arabic", sans-serif;
    direction: rtl;
}}

.poster {{
    position: relative;
    width: {W}px;
    height: {H}px;
    overflow: hidden;
    text-align: center;
    background: {BG};
}}

.frame {{
    position: absolute;
    inset: 30px;
    border: 5px solid {ORANGE};
    border-radius: 32px;
}}

.top-line {{
    position: absolute;
    top: 70px;
    right: 70px;
    left: 70px;
    height: 14px;
    background: {ORANGE};
    border-radius: 8px;
}}

.brand {{
    position: absolute;
    top: 125px;
    width: 100%;
    color: {ORANGE};
    font-size: 60px;
    font-weight: bold;
}}

.english {{
    position: absolute;
    top: 215px;
    width: 100%;
    font-family: Arial, sans-serif;
    font-size: 28px;
    direction: ltr;
    color: {WHITE};
}}

.divider {{
    position: absolute;
    top: 280px;
    right: 140px;
    left: 140px;
    border-top: 3px solid {ORANGE};
}}

.title {{
    position: absolute;
    top: 310px;
    width: 100%;
    font-size: 46px;
}}

.jalali {{
    position: absolute;
    top: 400px;
    width: 100%;
    font-size: 45px;
    color: {ORANGE};
    direction: ltr;
}}

.gregorian {{
    position: absolute;
    top: 465px;
    width: 100%;
    font-size: 30px;
    color: {GRAY};
    direction: ltr;
}}

.quote-box {{
    position: absolute;
    top: 580px;
    right: 85px;
    left: 85px;
    height: 390px;
    border: 3px solid {ORANGE};
    border-radius: 28px;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 45px;
}}

.quote {{
    width: 100%;
    font-size: 42px;
    line-height: 2;
    text-align: center;
    overflow-wrap: break-word;
}}

.values {{
    position: absolute;
    top: 1010px;
    width: 100%;
    color: {ORANGE};
    font-size: 35px;
}}

.telegram {{
    position: absolute;
    top: 1090px;
    width: 100%;
    font-family: Arial, sans-serif;
    font-size: 29px;
    color: {GRAY};
    direction: ltr;
}}

.footer {{
    position: absolute;
    top: 1170px;
    width: 100%;
    font-size: 28px;
}}
</style>
</head>

<body>
<div class="poster">

    <div class="frame"></div>
    <div class="top-line"></div>

    <div class="brand">آهن استحکام دیاکو</div>

    <div class="english">AHAN ESTEHKAM DIYACO</div>

    <div class="divider"></div>

    <div class="title">تقویم روزانه</div>

    <div class="jalali">{jalali_date}</div>

    <div class="gregorian">{gregorian_date}</div>

    <div class="quote-box">
        <div class="quote">{quote}</div>
    </div>

    <div class="values">اعتماد | کیفیت | تعهد</div>

    <div class="telegram">@ahandiyaco1401</div>

    <div class="footer">
        همراه شما در تأمین محصولات فولادی
    </div>

</div>
</body>
</html>"""


async def make_image():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        page = await browser.new_page(
            viewport={"width": W, "height": H},
            device_scale_factor=1
        )

        await page.set_content(
            create_html(),
            wait_until="load"
        )

        await page.screenshot(
            path="daily_calendar.png",
            full_page=False
        )

        await browser.close()


def send_to_telegram():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    channel = os.environ["TELEGRAM_CHANNEL"]

    now = jdatetime.datetime.now()

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

    print("تقویم با موفقیت در تلگرام منتشر شد.")


async def main():
    await make_image()
    send_to_telegram()


if __name__ == "__main__":
    asyncio.run(main())
