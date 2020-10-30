from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait


def scroll(total_scrolls, driver, scroll_time):
    global old_height
    current_scrolls = 0

    while True:
        try:
            if current_scrolls == total_scrolls:
                return

            old_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, scroll_time, 0.05).until(
                lambda driver: check_height(driver, old_height)
            )
            current_scrolls += 1
        except TimeoutException:
            break

    return


# check if height changed
def check_height(driver, old_height):
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height