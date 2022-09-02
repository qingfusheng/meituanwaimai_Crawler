import json
import re
import sys
import argparse
import time
from urllib import parse
from bs4 import BeautifulSoup
import numpy as np
import random
import asyncio
from pyppeteer import launch, launcher
from fake_useragent import UserAgent

launcher.DEFAULT_ARGS.remove("--enable-automation")


def ease_out_quad(x):
    return 1 - (1 - x) * (1 - x)


def get_tracks2(distance, seconds, ease_func=None):
    """轨迹离散分布的数学生成"""
    distance += 20
    tracks = [0]
    offsets = [0]
    for t in np.arange(0.0, seconds, 0.1):
        offset = round(ease_func(t / seconds) * distance)
        tracks.append(offset - offsets[-1])
        offsets.append(offset)
    tracks.extend([-3, -2, -3, -2, -2, -2, -2, -1, -0, -1, -1, -1])
    return tracks


async def page_init(page):
    """初始化页面特征值"""
    await page.evaluateOnNewDocument('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.evaluateOnNewDocument('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluateOnNewDocument('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ["zh-CN", "zh"] }); }''')
    await page.evaluateOnNewDocument('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')


async def try_validation(page, distance=200, count=0):
    """滑块验证
    :param page:
    :param distance: 滑动距离
    :param count: 滑动次数
    :return:
    """
    if count == 10:
        # 最大滑动次数
        return False
    await page.waitForXPath('//*[@id="yodaBox"]')
    btn_position = await page.evaluate('''
       () =>{
        return {
         x: document.querySelector('#yodaBox').getBoundingClientRect().x,
         y: document.querySelector('#yodaBox').getBoundingClientRect().y,
         width: document.querySelector('#yodaBox').getBoundingClientRect().width,
         height: document.querySelector('#yodaBox').getBoundingClientRect().height
         }}
        ''')
    x = btn_position['x'] + btn_position['width'] / 2
    y = btn_position['y'] + btn_position['height'] / 2
    await page.mouse.move(x, y)
    await page.mouse.down()
    x_track = get_tracks2(distance, random.randint(2, 4), ease_out_quad)
    y_track = []
    _x, _y = x, y
    for _ in x_track:
        y_track.append(random.randint(15, 50))
    while x_track:
        _x += x_track.pop(0)
        _y += y_track.pop(0)
        await page.mouse.move(_x, _y)

    await page.waitFor(2000)
    content = await page.content()
    if '拒绝操作' in content:
        print('请求异常')
        await page.evaluate('location.reload();')
        return await try_validation(page, distance, count + 1)
    if '验证失败' in content:
        print('验证失败')
        await page.mouse.up()
        return await try_validation(page, distance, count + 1)
    if '404' in content:
        return True

def get_order_url(region_id, region_version, startDate, endDate, nextLabel, lastLabel):
    # 获取外卖商家的Order信息的url
    return "https://e.waimai.meituan.com/gw/v2/order/common/history/all/r/list/common?region_id=%s&region_version=%s&tag=all&startDate=%s&endDate=%s&nextLabel=%s&lastLabel=%s&userId=-1" % (
    region_id, region_version, startDate, endDate, nextLabel, lastLabel)


async def main(**kwargs):
    ua = UserAgent()
    args = ['--no-sandbox', '--disable-infobars']
    # if proxyPort:
    #     args.append('--proxy-server=%s' % proxyPort)
    _kwargs = {'headless': False, 'args': args}
    _kwargs.update(kwargs)
    browser = await launch(_kwargs)
    page = await browser.pages()
    page = page[0]
    await page.setViewport(viewport={'width': 1920, 'height': 800})
    await page.setUserAgent(ua.chrome)
    await page.goto(url)
    # 类似于selenium的send_key
    username = "username"
    password = "password"
    await page.type("#login", username)
    await page.type("#password", password)
    await page.click(".login__submit")
    try:
        await page.waitForSelector("#yodaBox", timeout=3)
        print("____________________")
        await page_init(page)
        r = await try_validation(page)
        if r:
            print('轨迹验证成功')
    except Exception as error:
        print(error)
        print("登录成功")

    print("____________")
    # await page.waitForSelector("#历史订单")
    # await page.click("#历史订单")
    # await asyncio.sleep(3)
    # 异步等待看起来要比延时要高级得多
    await page.waitForSelector(".left-menu")

    await page.goto("https://e.waimai.meituan.com/?time=1662092494671&region_id=1000510100&region_version=1647935208#/v2/index")
    print("1------------")
    await page.goto("https://e.waimai.meituan.com/?time=1662088385753&region_id=1000510100&region_version=1647935208#/new_fe/business#/order/history")
    print("2------------")
    ## roo-input roo-input-
    # script1 = "document.getElementsByClassName('roo-input-')[0]."
    # page.evaluate("document.getEl")
    params = parse.parse_qs(parse.urlparse(page.url).query)
    region_id = params["region_id"][0]
    region_version = params["region_version"][0]
    startDate = "2022-09-02"
    endDate = "2022-09-02"
    nextLabel = ""
    lastLabel = ""
    circle_ture = True
    data_list = []
    page2 = await browser.newPage()
    while circle_ture:
        order_url = get_order_url(region_id, region_version, startDate, endDate, nextLabel, lastLabel)
        await page2.setViewport(viewport={'width': 1920, 'height': 1000})
        await page2.setUserAgent(ua.chrome)
        await page2.goto(order_url)
        # 这里出了一点小问题，就是在Pycharm中print一个长文件会有显示不全的问题，排了半天的错才发现是Pycharm的问题
        # await page2.evaluate("var data_content=JSON.parse(document.querySelector(\"body\").innerText);")
        # nextLabel = await page2.evaluate("()=>{return data_content[\"data\"][\"nextLabel\"]}")
        # data = await page2.evaluate("()=>{return data_content['data']['wmOrderList']}")
        # print(nextLabel)
        # print(data)
        # "nextLabel"
        # innerText = await page2.evaluate("()=>{return JSON.parse(document.querySelector(\"body\").innerText); }")
        # print(innerText)

        html_content = await page2.content()
        # 这里是对文本完整性的测试
        # with open("1.json", "w", encoding="utf-8") as f:
        #     f.write(html_content)

        # # reg = re.compile(r"\{.*\}")
        # # elem = reg.findall(html_content)[0]
        # # print(elem)
        soup = BeautifulSoup(html_content, features="lxml")
        json_content = json.loads(soup.find("body").text)
        nextLabel_json = json_content["data"]["nextLabel"]
        for each in json_content["data"]["wmOrderList"]:
            data_list.append({
                "businessType": each["businessType"],
                "commonInfo": json.loads(each["commonInfo"]),
                "orderInfo": json.loads(each["orderInfo"])
            })
        if not nextLabel_json:
            circle_ture = False
        # 将nextLabel_Json转为URL编码
        nextLabel = parse.quote(json.dumps(nextLabel_json))
        time.sleep(0)
        # {"day":%2020220902,%20"day_seq":%20122,%20"page":%200}
    await page2.close()
    with open("data.json","w", encoding="utf-8") as f:
        f.write(json.dumps(data_list, ensure_ascii=False))
    await asyncio.sleep(1000)


if __name__ == '__main__':
    # url = 'https://apimobile.meituan.com/group/v4/poi/pcsearch/'
    url = "https://epassport.meituan.com/account/unitivelogin?bg_source=3&service=waimai&platform=2&continue=https://e.waimai.meituan.com%2Fnew_fe%2Flogin_gw%23%2Flogin%2Fcontinue&left_bottom_link=%2Faccount%2Funitivesignup%3Fbg_source%3D3%26service%3Dwaimai%26platform%3D2%26extChannel%3Dwaimaie%26ext_sign_up_channel%3Dwaimaie%26continue%3Dhttps%3A%2F%2Fe.waimai.meituan.com%2Fv2%2Fepassport%2FsignUp&right_bottom_link=%2Faccount%2Funitiverecover%3Fbg_source%3D3%26service%3Dwaimai%26platform%3D2%26continue%3Dhttps%3A%2F%2Fe.waimai.meituan.com%252Fnew_fe%252Flogin_gw%2523%252Flogin%252Frecover"
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-P', '--port', type=int, help='代理层端口')
    # args = parser.parse_args()
    # with open("proxy.json", "r", encoding="utf-8") as f:
    #     proxyList = json.loads(f.read())
    # proxyPort = proxyList[0]
    # print(proxyPort)
    if sys.version_info >= (3, 7):
        asyncio.run(main())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())