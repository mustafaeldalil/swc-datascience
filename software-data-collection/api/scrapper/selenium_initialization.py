import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from django.conf import settings


def initialize_selenium():

    options = ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')

    options.add_argument('--window-size=1980,1080')
    options.add_argument("--headless") # Ensure GUI is off
    #pyoptions.add_argument("--no-sandbox")

    if settings.SELENIUM_IS_HEADLESS == 1:
        options.add_argument('--headless')

    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    user_agent_rotator = UserAgent(software_names=software_names,
                                operating_systems=operating_systems,
                                limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()

    options.add_argument(f"user-agent={user_agent})")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)

    if settings.SELENIUM_IS_HEADLESS == 1:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": "Object.defineProperty(navigator, 'plugins', {get: () => [5, 3, 9, 2, 1, 8, 4]});"
        })

    driver.set_page_load_timeout(settings.SELENIUM_MAX_TIMEOUT)
    return driver
