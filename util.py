from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait


def scroll(driver, ele, totalScrolls):
    """
    自动滚动，每次滚动到底部上面一点，最多滚动totalScrolls次
    :param driver:
    :param ele: 要滚动到的元素位置
    :param totalScrolls: 最大尝试滚动总次数
    :return:
    """

    # 记录当前的滚动次数
    currentScrolls = 0

    while currentScrolls != totalScrolls:
        try:
            # 网页总高度
            oldHeight = driver.execute_script("return document.body.scrollHeight;")
            # # 每次滚动到网页的8/10处（测试不能直接滚到底）
            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight/10*8);")
            driver.execute_script("arguments[0].scrollIntoView();", ele)
            # 等待直到网页总高度发生变化，如果没有发生变化则再等待10s
            WebDriverWait(driver, 0.5, 0.05).until(
                lambda driver: check_height(driver, oldHeight)
            )
            currentScrolls += 1
        except TimeoutException:
            # 如果高度没有发生变化，最后则滚到最底
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            break

    return


def check_height(driver, oldHeight):
    """
    check if height changed
    :param driver:
    :param oldHeight:
    :return: true代表高度发生变化
    """
    newHeight = driver.execute_script("return document.body.scrollHeight")
    return newHeight != oldHeight
