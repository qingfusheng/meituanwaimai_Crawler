import json

import requests
from bs4 import BeautifulSoup
import re

if __name__ == "__main__":
    num = 100
    url = "https://www.89ip.cn/tqdl.html?num=%d&address=&kill_address=&port=&kill_port=&isp="%num
    res = requests.get(url)
    soup = BeautifulSoup(res.text, features="lxml")
    elem = str(soup.find("div", attrs={"class":"fly-panel"}))
    print(elem)
    reg = re.compile(r'\d+\.\d+\.\d+\.\d+:\d+')
    elems = reg.findall(elem)
    with open("proxy.json","w", encoding="utf-8") as f:
        f.write(json.dumps(elems, ensure_ascii=False))
