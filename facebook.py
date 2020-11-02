import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import pandas as pd

import util


class Facebook:
    """
    爬取Facebook类
    """

    def __init__(self):
        self.driverPath = "./webdriver/win32/chromedriver.exe"
        self.driver = self.start()

        self.loginURL = "https://www.facebook.com"
        self.username = "csy5677@gmail.com"
        self.password = "c3995677"

        # 要爬取的facebookid列表
        self.facebookids = []

    @staticmethod
    def read_facebookids():
        facebookidDF = pd.read_excel("./data/facebook_id.xlsx")
        return facebookidDF['facebookid'].drop_duplicates().values.tolist()

    def start(self):
        """
        启动webdriver
        :return: webdriver
        """
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
        """
        手动登录
        :return:
        """
        timeStart = time.time()
        self.driver.get(self.loginURL)
        print("手动登录开始。")
        # 强制声明浏览器长宽为1024*768以适配所有屏幕
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1024, 768)
        input("请手动登录，确认登录后不要关闭浏览器，回编辑器点击回车：")
        # 最小化窗口
        self.driver.minimize_window()
        timeEnd = time.time()
        print('您的本次登录共用时{}秒。'.format(int(timeEnd - timeStart)))

    def login_auto(self):
        """
        自动登录
        :return:
        """
        timeStart = time.time()
        self.driver.get(self.loginURL)
        print("自动登录开始。")
        # 强制声明浏览器长宽为1024*768以适配所有屏幕
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1024, 768)

        self.driver.find_element_by_name("email").send_keys(self.username)
        self.driver.find_element_by_name("pass").send_keys(self.password)

        try:
            # clicking on login button
            self.driver.find_element_by_id("loginbutton").click()
        except NoSuchElementException:
            # Facebook new design
            self.driver.find_element_by_name("login").click()

        # 处理跳转到主界面的过程
        time.sleep(3)

        # 最小化窗口
        # self.driver.minimize_window()

        timeEnd = time.time()
        print('您的本次登录共用时{}秒。'.format(int(timeEnd - timeStart)))

    def crawl(self, facebookid):
        """
        开始爬取用户页信息
        :return:
        """
        timeStart = time.time()

        print("进入要爬取的个人页面：" + self.loginURL + "/" + facebookid)
        self.driver.get(self.loginURL + "/" + facebookid)

        # 用字典保存数据
        postsResult = {}
        # 目前可以提取的到的post的最后一个index
        indexValid = 0

        # 最多的滚动次数range来指定
        # 经过实验大概每一次滚动可以提取5个左右的post，由于无法删去之前的div，之后的处理会越来越慢
        for scrollTime in range(50):
            print('第{}次滚动...'.format(scrollTime))

            try:
                WebDriverWait(self.driver, 0.5, 0.05).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    ".//div[@class='rq0escxv l9j0dhe7 du4w35lb d2edcug0 hpfvmrgz gile2uim buofh1pr g5gj957u aov4n071 oi9244e8 bi6gxh9e h676nmdw aghb5jc5']/div"))
                )
                posts = self.driver.find_elements_by_xpath(
                    ".//div[@class='rq0escxv l9j0dhe7 du4w35lb d2edcug0 hpfvmrgz gile2uim buofh1pr g5gj957u aov4n071 oi9244e8 bi6gxh9e h676nmdw aghb5jc5']/div")
            except TimeoutException:
                print('错误！在网页中未找到{}的post列表'.format(facebookid))
                return postsResult

            indexValidUpdate = False
            for (indexPost, post) in enumerate(posts):
                # print('-------postStart:{}-------'.format(indexPost))
                # print(post)
                # print('-------postEnd:{}-------'.format(indexPost))

                itemsResult = []

                try:
                    WebDriverWait(self.driver, 0.5, 0.05).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        ".//*[self::blockquote or self::div[@class='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a']]"))
                    )
                    # blockquote 表示翻译后的
                    # div[@class='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a'] 表示直接的文字
                    items = post.find_elements_by_xpath(".//*[self::blockquote or self::div[@class='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a']]")
                except TimeoutException:
                    print('错误！在{}的post列表中未找到文字item'.format(facebookid))
                    return postsResult

                for (indexItem, item) in enumerate(items):
                    # print('------itemStart:{}--------'.format(indexItem))
                    # print(item.text)
                    # print('------itemEnd:{}--------'.format(indexItem))
                    if item.text != "":
                        itemText = item.text.replace('\n', '').replace(' · See original  · Rate this translation',
                                                                       '').strip()
                        itemsResult.append(itemText)
                # 如果有文本内容且存储结果中该post序号内还没有东西
                if itemsResult != [] and indexPost not in postsResult:
                    postsResult[indexPost] = itemsResult
                    indexValid = indexPost
                    indexValidUpdate = True
                    print('第{}个post，内容为：{}'.format(indexPost, postsResult[indexPost]))
            # 滚动
            # 如果没有更新
            if not indexValidUpdate:
                indexValid += 1
            util.scroll(self.driver, posts[indexValid], 1)

            print('第{}次滚动，滚动到第{}个post'.format(scrollTime, len(posts) - 1))
            time.sleep(3)

        timeEnd = time.time()
        print('爬取用户{}的数据共用时{}秒，爬取了{}条post。'
              .format(facebookid, int(timeEnd - timeStart), len(postsResult)))
        # print(postsResult)

        return postsResult

    def run(self):
        """
        运行爬虫入口
        :return:
        """

        # 从excel中读取id列表
        self.facebookids = self.read_facebookids()

        self.driver.implicitly_wait(2)

        # 自动登录Facebook
        self.login_auto()

        self.driver.implicitly_wait(0.5)

        # 开始爬取
        for i in range(0, 10):
            postsResult = self.crawl(self.facebookids[i])
            result = []
            for key, value in postsResult.items():
                item = {'facebookid': self.facebookids[i], 'index': key, 'main': value[0],
                        'reference': '||'.join(value[1:])}
                result.append(item)
            postsResultDF = pd.DataFrame(result)
            postsResultDF.to_csv("./data/{}.csv".format(self.facebookids[i]), index=False, header=True)

        input("回编辑器点击回车关闭浏览器：")
        self.driver.close()
        self.driver.quit()


if __name__ == '__main__':
    Facebook().run()
