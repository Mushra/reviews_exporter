from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("Ouverture de Metacritic...")
    page.goto("https://www.metacritic.com")

    print("Titre de la page :")
    print(page.title())

    print("Pause de 10 secondes...")
    time.sleep(10)

    browser.close()

print("Terminé.")
