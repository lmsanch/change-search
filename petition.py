# !/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import requests
import numpy as np


class Petition():
    """Features in the web page."""

    def __init__(self):
        """Features in summary of search."""
        self.link = ""
        self.to = ""
        self.body = ""
        self.origin = ""
        self.supporters = ""
        self.created = ""
        self.status = ""
        self.title = ""
        self.image = ""
        self.creator = ""


petition_list = []
url_seed = 'https://www.change.org'
url_action = '/search?q=Venezuela'
url = url_seed + url_action
page_data = requests.get(url)
menu = BeautifulSoup(page_data.text, 'lxml')
pages_list = []

# pages containing the term Venezuela
for i, page in enumerate(menu.find_all('a', class_='phxxxs js-pagination-link')):
    pages_list.append(int(page['data-page-number']))

# list of pages to collect
pages_to_parse = np.array(list(range(0, max(pages_list))))
offsets = pages_to_parse*10
pt = Petition()
data_dict = {}
j = 0
for page in offsets:
    options = webdriver.ChromeOptions()
    options.add_argument(f'headless')
    # change to the location of your chrome driver
    driver_chrome = webdriver.Chrome('/Users/luissanchez/Dropbox (Personal)/chromedriver_osx/chromedriver', options=options)
    url = url_seed + url_action + '&offset=' + str(page)
    driver_chrome.get(url)
    arepas = BeautifulSoup(driver_chrome.page_source, 'lxml')
    for i, arepa in enumerate(arepas.find_all(class_='search-result')):
        try:
            new_link = url_seed + arepa.find('a', class_='link-block js-click-search-result')['href']
            pt.link = new_link
            new_to = arepa.find('div', class_="type-s").text
            new_to = new_to.split('Petition to ')[1]
            pt.to = new_to
            pt.title = arepa.find('h3', class_="mtn mbn prxs xs-mbs").text
            pt.image = arepa.find('div', class_="flex-embed-content flex-embed-cover-image ")
            pt.image = 'http:' + pt.image['style'].split("url('")[1][:-3]
            pt.origin = arepa.find('li', class_="type-ellipsis mrs").span.text.strip()
            search = arepa.findAll('ul', class_="hidden-xs list-inline type-s type-weak")
            for x, _ in enumerate(search[0].findAll('li')):
                if x == 0:
                    pt.creator = _.text.split(pt.origin)[0].title()
                if x == 1:
                    pt.supporters = _.text.split('supporters')[0]
                    pt.supporters = int(pt.supporters.replace(',', ''))
                if x == 2:
                    pt.created = _.text.split('Created')[1].strip()

        # bare except, I know
        except:
            continue
        data_dict[j] = {'link': pt.link,
                        'to': pt.to,
                        'title': pt.title,
                        'image': pt.image,
                        'origin': pt.origin,
                        'creator': pt.creator,
                        'supporters': pt.supporters,
                        'created': pt.created}
    driver_chrome.close()
data_dict
df = pd.DataFrame(data_dict).transpose()
df = df.sort_values(by='supporters', ascending=False).reset_index(drop=True)
df.to_excel('petition1.xls')
