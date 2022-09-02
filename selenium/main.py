import time
import pyautogui
import selenium.common
from selenium import webdriver
import random

from selenium.webdriver.chrome.options import Options


def __getRadomPauseScondes():
    return random.uniform(0.6, 0.9)


def simulateDragX(source, targetOffsetX):
    """
    模仿人的拖拽动作：快速沿着X轴拖动（存在误差），再暂停，然后修正误差
    防止被检测为机器人，出现“图片被怪物吃掉了”等验证失败的情况
    :param source:要拖拽的html元素
    :param targetOffsetX: 拖拽目标x轴距离
    :return: None
    """
    action_chains = webdriver.ActionChains(chrome)
    # 点击，准备拖拽
    action_chains.click_and_hold(source)
    # 拖动次数，二到三次
    dragCount = random.randint(2, 3)
    if dragCount == 2:
        # 总误差值
        sumOffsetx = random.randint(-15, 15)
        action_chains.move_by_offset(targetOffsetX + sumOffsetx, 0)
        # 暂停一会
        action_chains.pause(__getRadomPauseScondes())
        # 修正误差，防止被检测为机器人，出现图片被怪物吃掉了等验证失败的情况
        action_chains.move_by_offset(-sumOffsetx, 0)
    elif dragCount == 3:
        # 总误差值
        sumOffsetx = random.randint(-15, 15)
        action_chains.move_by_offset(targetOffsetX + sumOffsetx, 0)
        # 暂停一会
        action_chains.pause(__getRadomPauseScondes())

        # 已修正误差的和
        fixedOffsetX = 0
        # 第一次修正误差
        if sumOffsetx < 0:
            offsetx = random.randint(sumOffsetx, 0)
        else:
            offsetx = random.randint(0, sumOffsetx)

        fixedOffsetX = fixedOffsetX + offsetx
        action_chains.move_by_offset(-offsetx, 0)
        action_chains.pause(__getRadomPauseScondes())

        # 最后一次修正误差
        action_chains.move_by_offset(-sumOffsetx + fixedOffsetX, 0)
        action_chains.pause(__getRadomPauseScondes())

    else:
        raise Exception("莫不是系统出现了问题？!")

    action_chains.release().perform()


def get_tracks(distance):
    '''
    模仿先加速后减速的过程
    :param distance: 移动的距离
    :return: 列表
    '''
    # 当前速度
    v = 0

    # 定义时间间隔
    t = 0.3
    tracks = []

    # 当前距离
    current = 0

    # 加速和减速的分割线
    mid = distance * 3 / 5

    while current < distance:
        # 定义加速度
        if current < mid:
            a = 2
        else:
            a = -3
        # 移动了
        # 定义初速度
        v0 = v
        s = v0 * t + 0.5 * a * t * t
        current += s
        # 保持移动的时候有效果
        # 0.1个像素。像素不能是小数
        tracks.append(round(s))
        # 设置当前速度
        v = v0 + a * t
    return tracks


if __name__ == "__main__":
    url = "https://e.waimai.meituan.com/"
    url = "https://epassport.meituan.com/account/unitivelogin?bg_source=3&service=waimai&platform=2&continue=https://e.waimai.meituan.com%2Fnew_fe%2Flogin_gw%23%2Flogin%2Fcontinue&left_bottom_link=%2Faccount%2Funitivesignup%3Fbg_source%3D3%26service%3Dwaimai%26platform%3D2%26extChannel%3Dwaimaie%26ext_sign_up_channel%3Dwaimaie%26continue%3Dhttps%3A%2F%2Fe.waimai.meituan.com%2Fv2%2Fepassport%2FsignUp&right_bottom_link=%2Faccount%2Funitiverecover%3Fbg_source%3D3%26service%3Dwaimai%26platform%3D2%26continue%3Dhttps%3A%2F%2Fe.waimai.meituan.com%252Fnew_fe%252Flogin_gw%2523%252Flogin%252Frecover"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
    chrome_options.add_argument("disable-blink-features=AutomationControlled")  # 就是这一行告诉chrome去掉了webdriver痕迹
    chrome = webdriver.Chrome(chrome_options=chrome_options)

    # chrome = webdriver.Chrome()
    chrome.get(url)

    """
    login:
    login__login input input_m input_primary input_fluid input_desc
    passwd:
    login__password input input_m input_primary input_fluid input_desc
    """
    time.sleep(2)
    login_username = chrome.find_element_by_id("login")
    login_password = chrome.find_element_by_class_name("login__password")
    submit = chrome.find_element_by_class_name("login__submit")
    script1 = 'document.getElementById("login").value = "123"; document.getElementById("password").value = "456";'
    login_username.send_keys("wmfsml5567801")
    login_password.send_keys("S399204")
    submit.click()
    # print(script1)
    # chrome.execute_script(script1)
    print(login_username)
    print(login_password)
    time.sleep(100)
    while True:
        try:
            chrome.find_element_by_id("yodaBox")
            break
        except selenium.common.exceptions.NoSuchElementException:
            print("**-------------**")
            time.sleep(0.2)

    box = chrome.find_element_by_id("yodaBox")

    action_chains = webdriver.ActionChains(chrome)
    # 拖动滑块按钮，注意滑块距离左边有 5~10 像素左右误差
    offsetX = 200
    # simulateDragX(box, offsetX)
    off_sum = 0
    action_chains.click_and_hold(box).perform()
    action_chains.move_by_offset(xoffset=50, yoffset=0)
    action_chains.move_by_offset(xoffset=50, yoffset=0)
    action_chains.move_by_offset(xoffset=50, yoffset=0)
    action_chains.move_by_offset(xoffset=40, yoffset=0)
    off_sum += 190
    # action_chains.pause(0.5)
    tracks = get_tracks(200)
    print(tracks)
    for s in tracks:
        if s == 0:
            continue
        off_sum += s
        if off_sum > 197:
            break
        action_chains.move_by_offset(xoffset=s, yoffset=0)
        action_chains.pause(0)
    action_chains.release().perform()
    # action_chains.perform()
        # 4、放开鼠标即可
    # action_chains.release().perform()

    # action_chains.click_and_hold(box).perform()
    # action_chains.move_by_offset(50, 0)
    # action_chains.pause(0.3)
    # action_chains.move_by_offset(50, 0)
    # action_chains.pause(0.4)
    # action_chains.move_by_offset(50, 0)
    # action_chains.pause(0.3)
    # action_chains.move_by_offset(46, 0)
    # action_chains.pause(0.3)
    # action_chains.move_by_offset(4, 0)
    # action_chains.pause(0.5)
    # action_chains.release()
    # action_chains.perform()
    # for i in range(8):
    #     offset = offsetX // 8
    #     action_chains.move_by_offset(offset, 0)
    #     action_chains.pause(0.05)
    # action_chains.release()
    # action_chains.perform()

    # action_chains.click_and_hold(box)
    #
    # action_chains.pause(0.2)
    # action_chains.move_by_offset(offsetX - 10, 0)
    # action_chains.pause(1)
    # action_chains.move_by_offset(10, 0)
    # action_chains.pause(1)
    # action_chains.release()
    # action_chains.perform()

    # action_chains.drag_and_drop_by_offset(box, offsetX, 0).perform()

    # pyautogui.moveTo(box.location['x'] + 20, box.location['y']+140)
    # # duration是几秒内完成滑动  location['x']是水平轴滑动，
    # distance = "210"
    # pyautogui.dragTo(box.location['x'] + int(distance) + 20, box.location['y']+140, duration=2)

    print("box:", chrome.find_element_by_id("yodaBox"))
    time.sleep(1000)

    ## 197, 209
