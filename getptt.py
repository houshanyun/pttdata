import re
import time
import sys

import requests
import pandas as pd
from bs4 import BeautifulSoup

class GetPttdata:
    header ={
    'User-Agent':
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
}
    href_list = list()
    author_list = list()
    date_list = list()
    title_list = list()
    url_list =list()

    def __init__(self, input_url):
        self.url = input_url
        html = requests.get(self.url)
        self.soup = BeautifulSoup(html.text, 'lxml')
    

    def get_index(self):
        atags = self.soup.find_all('a',{'class':'btn wide'})
        for atag in atags:
            pat = re.findall(r'\d{2,}', atag.get('href'))
            if pat:
                ptt_name = atag.get('href').split('/')[2]
                print(pat, ptt_name) 
                return pat, ptt_name


    def get_soup(self):
        soups =list()
        (b, a) = self.get_index()
        try:
            for page in range(int(b[0])+1 ,int(b[0])-9, -1):
                html = requests.get(
                    str(page).join([f'https://www.ptt.cc/bbs/{a}/index', '.html']),
                    headers=self.header
                )
                if html.status_code == 200:
                    sp = BeautifulSoup(html.text, 'lxml')
                    soups.append(sp)
                    time.sleep(3)
                else:
                    print('網站無法讀取！')
                    html.raise_for_status()
            return soups
        except Exception as e:
            print(e)
            sys.exit()
            

    def get_data(self):
        for sp in self.get_soup():
            title_data = sp.select('.title')
            author_data = sp.select('.author')
            date_data = sp.find_all('div',{'class':'date'})

            self.author_list += [_.text for _ in author_data]

            self.date_list += [_.text for _ in date_data]

            for _ in title_data:
                pat = re.sub(r'\s', '', _.text)
                self.title_list.append(pat)

            self.href_list = [_.find('a') for _ in title_data]

            for url in self.href_list:
                if url is None:
                    self.url_list.append(0)
                elif url:
                    href = url.get('href')
                    self.url_list.append('https://www.ptt.cc'+ href)


    def to_exc(self):
        datas = [
                self.title_list, 
                self.author_list, 
                self.date_list, 
                self.url_list
        ]
        dexs = ['title', 'author', 'date', 'href']
        df = pd.DataFrame(datas, index=dexs)
        df_chr = df.stack()
        df_chr.to_excel('pttdata.xlsx')


print('請輸入想抓取的ptt看板網址！')
print('網址格式：https://www.ptt.cc/bbs/看板名稱/index.html.')
url = input('網址： ')
pat = re.compile(r'https://www\.ptt\.cc/bbs/.+/index\.html')
pat_str = pat.findall(url)

if pat_str:
    print('解析網址中......')
    pttobj = GetPttdata(url)

    print('網站資料抓取中......')
    pttobj.get_index()
    pttobj.get_soup()

    print('資料整理中......')
    pttobj.get_data()

    print('資料輸出中......')
    pttobj.to_exc()
    
    print("資料以輸出試算表'pttdata.xlsx'")
else:
    print('網址格式錯誤')