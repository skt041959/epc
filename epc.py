#!/usr/bin/env python
# encoding: utf-8

import requests
from bs4 import BeautifulSoup as BS
from collections import namedtuple
from time import sleep
from datetime import datetime
from random import randrange
from gi.repository import Notify


oralclass = namedtuple('oralclass', 'action, name, week, teacher, date, time, number')

def extract(soup):
    classes = []
    elem = soup.find_all('form')
    for e in elem:
        action = e.get("action")
        cols = e.find_all('td')

        name = cols[0].find_all(text=True)[0]
        week = cols[1].find_all(text=True)[0][1]
        teacher = cols[3].find_all(text=True)[0]
        date, time = cols[5].find_all(text=True)
        number = cols[10].find_all(text=True)[0]
        o = oralclass(action, name, week, teacher, date, time, number)
        classes.append(o)

    if classes:
        filtedclasses = [c for c in classes if int(c.week) < 6]
        return filtedclasses

    else:
        text = soup.find_all(text=True)
        for e in text:
            if e == u'登录后可以查看详细信息':
                print(soup.prettify())
                return None


def main():
    Notify.init("epc")
    cookies = dict(
            #ASPSESSIONIDASDDSDCT="KNPJPJABLABCPHDEFLFOMPMO",
            ASPSESSIONIDASBCRCCT="KNPJPJABLABCPHDEFLFOMPMO",
            counter="1",
            term="2",
            year="2014",
            querytype="")

    while 1:
        re = requests.get(url="http://epc.ustc.edu.cn/m_practice.asp?second_id=2002", cookies=cookies)
        soup = BS(re.content)
        r = extract(soup)
        print(datetime.today())
        if r:
            for c in r:
                print(">>> ", c.week, c.date, c.time, c.number)
            find_note = Notify.Notification.new("EPC found", "EPC found", "dialog-information")
            find_note.show()
            #res = requests.post(url="http://epc.ustc.edu.cn/"+r.action, cookies=cookies)
        elif r is None:
            outdate_note = Notify.Notification.new("PEC outdate", "EPC cookies outdate", "dialog-warning")
            outdate_note.show()
            break

        sleep(randrange(5, 15, 2)*60)


if __name__ == '__main__':
    main()
    #extract(BS(open('1.html')))



