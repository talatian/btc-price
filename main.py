import json
from time import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+


def get_btc_prices(logs):
    """
    Return only logs which have a method that start with "Network.response", "Network.request", or "Network.webSocket"
    since we're interested in the network events specifically.
    """
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if (
                "Network.webSocketFrameReceived" in log["method"]
        ):
            data = json.loads(log["params"]["response"]["payloadData"])
            if data.get("stream") == 'btcusdt@aggTrade':
                btc_price = data.get("data")["p"]
                yield btc_price


def wait_for_price():
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "showPrice"))
    )
    print("Page loaded!")


def btc_average(minutes):
    with open("log.txt", "wt") as out:
        t_end = time() + 60 * minutes
        btc_sum = 0
        counter = 0
        while time() < t_end:
            logs = driver.get_log("performance")
            btc_prices = get_btc_prices(logs)
            for price in btc_prices:
                counter += 1
                print(price, file=out)
                print(f"#{counter} btc-usd price: {price}")
                btc_sum += float(price)
        btc_avg = btc_sum / counter
        print(f"btc-usd avg. price within {minutes} minutes: {btc_avg}")


if __name__ == '__main__':
    driver = webdriver.Chrome(r"chromedriver.exe", desired_capabilities=capabilities)
    driver.get("https://www.binance.com/en/trade/btc_usdt")
    wait_for_price()
    btc_average(1)
    driver.close()
