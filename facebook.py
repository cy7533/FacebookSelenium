import argparse
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import pandas as pd

import util


class Facebook:
    """
    爬取Facebook类
    """

    def __init__(self, username, password, startID=0, endID=10, scrollTimes=50):
        self.driverPath = "./webdriver/win32/chromedriver.exe"
        self.driver = self.start()

        self.loginURL = "https://www.facebook.com"
        self.username = username
        self.password = password

        # 要爬取的facebookid列表
        self.facebookids = []
        # 开始和结束爬取的id号
        self.startID = int(startID)
        self.endID = int(endID)
        # 爬取的滚动次数
        self.scrollTimes = scrollTimes

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
        # self.driver.minimize_window()
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

        try:
            WebDriverWait(self.driver, 2, 0.05).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
        except TimeoutException:
            print('错误！在登录页面中未找到登录元素')

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
        for scrollTime in range(self.scrollTimes):
            # 每次滚动确定一次post中是否有内容即可
            checkContent = True
            print('第{}次滚动...'.format(scrollTime))

            # 等待post列表加载完毕
            # posts列表的XPath路径
            postsXPath = "(.//div[@class='rq0escxv l9j0dhe7 du4w35lb d2edcug0 hpfvmrgz gile2uim buofh1pr g5gj957u aov4n071 oi9244e8 bi6gxh9e h676nmdw aghb5jc5']/div " \
                         "| .//div[@role='feed'][2]/div[@class='du4w35lb k4urcfbm l9j0dhe7 sjgh65i0'])"
            try:
                WebDriverWait(self.driver, 2, 0.05).until(
                    EC.presence_of_element_located((By.XPATH, postsXPath))
                )
            except TimeoutException:
                print('错误！在网页中未找到{}的post列表'.format(facebookid))
                return postsResult

            # 获取当前post列表长度
            postEles = self.driver.find_elements_by_xpath(postsXPath)
            postElesLen = len(postEles)

            print("页面中的post列表共{}个post".format(len(postEles)))

            indexValidUpdate = False
            for indexPost in range(indexValid, postElesLen):
                postData = {}
                """等待加载完成"""
                # 等待第i个post的整体加载完毕
                postIndexXPath = postsXPath + "[position()={}]".format(indexPost + 1)
                try:
                    WebDriverWait(self.driver, 2, 0.05).until(
                        EC.presence_of_element_located((By.XPATH, postIndexXPath))
                    )
                except TimeoutException:
                    print('错误！在网页中未找到{}的第{}个post'.format(facebookid, indexPost))
                    return postsResult
                if checkContent:
                    # 等待第i个post的内容加载完毕
                    # 根据用户昵称是否显示
                    itemsPostIndexXPath = postIndexXPath + "//div[@class='nc684nl6']"
                    try:
                        WebDriverWait(self.driver, 100, 0.05).until(
                            EC.presence_of_element_located((By.XPATH, itemsPostIndexXPath))
                        )
                        checkContent = False
                    except TimeoutException:
                        print('错误！在网页中未找到{}的第{}个post中内容加载延迟'.format(facebookid, indexPost, facebookid))
                        return postsResult

                postEle = self.driver.find_element_by_xpath(postIndexXPath)

                """post发布时间提取"""
                try:
                    postTime = postEle.find_element_by_xpath(
                        ".//*[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw']") \
                        .get_attribute("aria-label")
                    print("post{}[time]:{}-------".format(indexPost, postTime))
                    postData['time'] = postTime
                except NoSuchElementException:
                    pass

                """post内容提取"""
                # blockquote 表示翻译后的
                # div[@class='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a'] 表示直接的文字
                itemEles = postEle.find_elements_by_xpath(
                    ".//blockquote | .//div[@class='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a']")

                itemsResult = []
                for (indexItem, item) in enumerate(itemEles):
                    if item.text != "":
                        itemText = item.text.replace('\n', '').replace(' · See original  · Rate this translation',
                                                                       '').strip()
                        itemsResult.append(itemText)
                print("post{}[items]:{}-------".format(indexPost, itemsResult))
                postData['items'] = itemsResult

                # 如果有文本内容且存储结果中该post序号内还没有东西
                if 'time' in postData and postData['items'] != [] and indexPost not in postsResult:
                    postsResult[indexPost] = postData
                    indexValid = indexPost
                    indexValidUpdate = True
                    print('保存第{}个post，内容为：{}'.format(indexPost, postsResult[indexPost]))

            # 滚动
            # 如果没有更新
            if not indexValidUpdate:
                indexValid += 1
            try:
                self.driver.execute_script("arguments[0].scrollIntoView();", postEles[indexValid])
            except IndexError or StaleElementReferenceException:
                if not util.scrollToPosition(self.driver, 1):
                    break

            print('第{}次滚动，滚动到第{}个post'.format(scrollTime, indexValid))
            time.sleep(5)

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

        # 自动登录Facebook
        self.driver.implicitly_wait(5)
        self.login_auto()
        self.driver.implicitly_wait(1)

        # 开始爬取
        for i in range(self.startID, self.endID):
            postsResult = self.crawl(self.facebookids[i])
            result = []
            for key, value in postsResult.items():
                item = {'facebookid': self.facebookids[i], 'index': key, 'time':value['time'],
                        'main': value['items'][0], 'reference': '||'.join(value['items'][1:])}
                result.append(item)
            postsResultDF = pd.DataFrame(result)
            postsResultDF.to_csv("./data/{}.csv".format(self.facebookids[i]), index=False, header=True)

        # input("回编辑器点击回车关闭浏览器：")
        print('爬取用户id序号从{}到{}，完成'.format(self.startID, self.endID))
        self.driver.close()
        self.driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="facebook selenium cookbook")
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('--startID', type=int, default=0)
    parser.add_argument('--endID', type=int, default=10)
    parser.add_argument('--scrollTimes', type=int, default=50)
    args = parser.parse_args()

    Facebook(args.username, args.password, args.startID, args.endID, args.scrollTimes).run()
