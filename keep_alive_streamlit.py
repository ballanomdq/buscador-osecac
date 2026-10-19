import sys
from playwright.sync_api import sync_playwright

URL = "https://buscador-osecac-6jztx7xjhgkvcaubfinn5y.streamlit.app/"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(10000)

    boton = page.get_by_role("button", name="Yes, get this app back up!")
    if boton.count() > 0:
        print("App dormida, despertando...")
        boton.click()
        page.wait_for_timeout(60000)
    else:
        print("App ya estaba activa")
        page.wait_for_timeout(15000)

    browser.close()
