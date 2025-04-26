import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from flask import Flask, request
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

PRODUCTS = {
    "Wakatake": "https://www.marukyu-koyamaen.co.jp/english/shop/products/11b1100c1",
    "Isuzu": "https://www.marukyu-koyamaen.co.jp/english/shop/products/1191040c1",
    "Aoarashi": "https://www.marukyu-koyamaen.co.jp/english/shop/products/11a1040c1",
    "Tenju": "https://www.marukyu-koyamaen.co.jp/english/shop/products/1111020c1",
    "Chigi no Shiro": "https://www.marukyu-koyamaen.co.jp/english/shop/products/1181040c1"
}

EMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
TO_EMAIL = os.getenv("ALERT_RECIPIENT")

def send_email(product_name, link):
    msg = EmailMessage()
    msg.set_content(f"🟢 {product_name} is in stock!\n{link}")
    msg["Subject"] = f"Matcha Alert: {product_name} In Stock!"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        print(f"📤 Sent alert for {product_name}")

def check_stock():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)

    for name, link in PRODUCTS.items():
        driver.get(link)
        time.sleep(3)

        rows = driver.find_elements(By.CSS_SELECTOR, "div.product-form-row")
        out = driver.find_elements(By.CSS_SELECTOR, "p.stock.out-of-stock")

        if len(out) < len(rows):
            send_email(name, link)
        else:
            print(f"🔴 {name} is SOLD OUT ({len(out)}/{len(rows)} variants)")

    driver.quit()

@app.route("/", methods=["GET"])
def ping():
    return "✅ Matcha Alert Bot is live!"

@app.route("/check", methods=["POST"])
def trigger_check():
    check_stock()
    return "✅ Check complete."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
