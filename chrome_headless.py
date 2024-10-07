from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
options.add_argument('--no-sandbox')  # Bypass OS security model
options.add_argument('--disable-gpu')  # Applicable for Windows, but helps in headless mode
driver = webdriver.Chrome(options=options)
WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script("return document.readyState") == "complete"
)

driver.get("https://www.winnings.com.au/inspirations/kitchen")

print(driver.page_source)
driver.quit()
