import dotenv
from selenium import webdriver
import getpass


def login() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    print("starting up...".ljust(40), end="\r")
    driver = webdriver.Chrome(options=options)
    print("started".ljust(40))
    driver.get("https://apda.online/forum/")
    print("logging in...".ljust(40), end="\r")

    values = dotenv.dotenv_values(".env")
    user_login = driver.find_element("id", "user_login")
    username = values.get("USERNAME") or input("username: ")
    user_login.send_keys(username)

    user_pass = driver.find_element("id", "user_pass")
    password = values.get("PASSWORD") or getpass.getpass("password: ")
    user_pass.send_keys(password)

    wp_submit = driver.find_element("id", "wp-submit")
    wp_submit.click()
    print("logged in".ljust(40))
    return driver
