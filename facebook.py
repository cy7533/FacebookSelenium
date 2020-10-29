import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class Facebook:
    def __init__(self):
        self.driverPath = "./webdriver/win32/chromedriver.exe"
        self.driver = self.start()

        self.loginURL = "https://www.facebook.com"
        self.username = "csy5677@gmail.com"
        self.password = "c3995677"

        self.needToCrawl = ["helge.thomas"]

    def start(self):
        options = webdriver.ChromeOptions()
        prefs = {
            'profile.default_content_setting_values': {
                'notifications': 2
            }
        }
        options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(executable_path=self.driverPath, options=options)
        return driver

    def login_manual(self):
        timeStart = time.time()
        self.driver.get(self.loginURL)
        print("手动登录开始。")
        # 强制声明浏览器长宽为1024*768以适配所有屏幕
        self.driver.implicitly_wait(2)
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1024, 768)
        self.driver.implicitly_wait(2)
        input("请手动登录，确认登录后不要关闭浏览器，回编辑器点击回车：")
        # 最小化窗口
        self.driver.implicitly_wait(2)
        self.driver.minimize_window()
        self.driver.implicitly_wait(2)
        timeEnd = time.time()
        print('您的本次登录共用时{}秒。'.format(int(timeEnd - timeStart)))

    def login_auto(self):
        timeStart = time.time()
        self.driver.get(self.loginURL)
        print("自动登录开始。")
        # 强制声明浏览器长宽为1024*768以适配所有屏幕
        self.driver.implicitly_wait(2)
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1024, 768)
        self.driver.implicitly_wait(2)

        self.driver.find_element_by_name("email").send_keys(self.username)
        self.driver.find_element_by_name("pass").send_keys(self.password)

        try:
            # clicking on login button
            self.driver.find_element_by_id("loginbutton").click()
        except NoSuchElementException:
            # Facebook new design
            self.driver.find_element_by_name("login").click()

        # 最小化窗口
        # self.driver.implicitly_wait(2)
        # self.driver.minimize_window()
        self.driver.implicitly_wait(10)
        timeEnd = time.time()
        print('您的本次登录共用时{}秒。'.format(int(timeEnd - timeStart)))

    def crawl(self):
        timeStart = time.time()
        time.sleep(5)
        print("进入要爬取的个人页面。")
        print(self.loginURL + "/" + self.needToCrawl[0])
        self.driver.get(self.loginURL + "/" + self.needToCrawl[0])
        self.driver.implicitly_wait(5)

        posts = self.driver.find_elements_by_xpath(
            ".//div[@class='rq0escxv l9j0dhe7 du4w35lb d2edcug0 hpfvmrgz gile2uim buofh1pr g5gj957u aov4n071 oi9244e8 bi6gxh9e h676nmdw aghb5jc5']/div")

        print('--------------')
        print(len(posts))
        print('--------------')

        for (index, post) in posts:
            items = post.find_elements_by_xpath(".//blockquote")
            for item in items:
                print('------item--------')
                print(item.text)
                print('------itemEnd--------')


    def run(self):
        self.login_auto()

        self.crawl()

        input("回编辑器点击回车关闭浏览器：")
        self.driver.close()
        self.driver.quit()


if __name__ == '__main__':
    Facebook().run()
