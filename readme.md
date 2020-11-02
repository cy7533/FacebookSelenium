# 编写过程

## 创建venv虚拟环境

pycharm自动创建

## 在虚拟环境中安装selenium
```
pip list
pip install selenium
pip list
```

## 下载webdriver
chrome的webdriver： http://chromedriver.storage.googleapis.com/index.html

# 编写思路

## 登录：
自动登录，暂时采用id查找，可以通过文本查找
## 进入个人页面：
提取post，因为post都是用<div></div>包裹，没有标签，但是div上层有一个class名存在的div，通过它搜索到每个post
```python
posts = self.driver.find_elements_by_xpath(
                ".//div[@class='rq0escxv l9j0dhe7 du4w35lb d2edcug0 hpfvmrgz gile2uim buofh1pr g5gj957u aov4n071 oi9244e8 bi6gxh9e h676nmdw aghb5jc5']/div")
```
再通过遍历搜索posts中的blockquote标签得到每一个发言，第一个发言大概率是本人，后面的为引用他人的（也存在本人不发言的情况，那么第一个也不是本人的发言【**需要改进，要通过xpath判断上面的元素是不是当前的个人信息**】）
```python
items = post.find_elements_by_xpath(".//blockquote")
```
## 滚动：
滚动加载比较复杂。
尝试直接滚到底，再全部提取，发现页面加载不出来。
尝试滚到底部的百分之80，再全部提取，页面可以加载出来，但是之前的post提取不出
这里猜测是Facebook有设计机制，滚动条滚到后面前面的就提取不出来了
目前采用的是，先提取一页，再滚动到提取不到的post的那个位置（用indexValid记录），再提取
如果indexValid没有变化，则滚动一个post的长度

## 保存
按id作为文件名保存

## 时间提取
还未完成，初步发现Facebook是对style进行改变来加密，通过xpath判断没有style的应该就是当前显示的时间。

# 运行方法
1. 在当前创建虚拟环境venv
2. 安装pip install requirement.txt
3. python运行

```bash
python facebook.py
```