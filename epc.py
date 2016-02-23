#!/usr/bin/env python
# encoding: utf-8

import sys
import requests

from collections import namedtuple

from time import sleep, mktime, strptime
from datetime import datetime
from random import randrange

from bs4 import BeautifulSoup as BS
#from gi.repository import Notify
import notify2
from argparse import ArgumentParser
from http.cookies import SimpleCookie

from PyQt4 import QtCore, QtGui

oralclass = namedtuple('oralclass', 'action, name, week, day, teacher, date, time, number')

def extract(soup, line):
    classes = []
    elem = soup.find_all('form')
    for e in elem:
        action = e.get("action")
        cols = e.find_all('td')

        name = cols[0].find_all(text=True)[0]
        week = cols[1].find_all(text=True)[0][1]
        day = cols[2].find_all(text=True)[0]
        teacher = cols[3].find_all(text=True)[0]
        date, time = cols[5].find_all(text=True)
        number = cols[10].find_all(text=True)[0]
        o = oralclass(action, name, week, day, teacher, date, time, number)
        classes.append(o)

    if classes:
        #filtedclasses = [c for c in classes if int(c.week) <= line]
        filtedclasses = [c for c in classes if (datetime.fromtimestamp(mktime(strptime(c.date, "%Y-%m-%d")))-datetime.today()).days < 7]
        return filtedclasses

    else:
        text = soup.find_all(text=True)
        for e in text:
            if e == u'登录后可以查看详细信息':
                #print(soup.prettify())
                return None

class EPC_Quary(QtGui.QMainWindow):

    start = QtCore.pyqtSignal()

    def __init__(self, cookie=dict(), week_line=None):
        super(EPC_Quary, self).__init__()
        notify2.init("epc")

        self.url_top = "http://epc.ustc.edu.cn/m_practice.asp?second_id=2002"
        self.url_sit = "http://epc.ustc.edu.cn/m_practice.asp?second_id=2001"

        self.ignore_list = []
        self.cookie = cookie
        self.week_line = week_line

        self.class_menu = QtGui.QMenu(self)

        icon = QtGui.QIcon(style.standardPixmap(QtGui.QStyle.SP_FileIcon))
        self.trayIcon = QtGui.QSystemTrayIcon(icon, self)
        self.trayIcon.setContextMenu(self.class_menu)
        self.trayIcon.show()
        self.trayIcon.setVisible(True)

        self.exitAction = QtGui.QAction("Exit", self)
        self.exitAction.triggered.connect(QtGui.QApplication.quit)

        self.class_menu.addAction(self.exitAction)

        #self.input_cookie.connect(self.get_cookie)
        #self.input_cookie.emit()

        QtCore.QTimer.singleShot(0, self.quary)
        #self.start.connect(self.quary)
        #self.start.emit()


    def setVisible(self, visible):
        super(EPC_Quary, self).setVisible(visible)


    def ignore(self, action):
        print("ignore {0}".format(action.text()))
        s = action.text()
        self.ignore_list.append(action.text())
        print(self.ignore_list)
        print(s in self.ignore_list)


    def quary(self):
        week_line = 7
        if not self.cookie:
            s, flag = QtGui.QInputDialog.getText(self, "EPC_Quary", "Cookie")
            if flag:
                cookies = SimpleCookie(s.strip('"'))
                if cookies:
                    for k,v in cookies.items():
                        self.cookie[k] = v.value
                print(self.cookie)
            else:
                return False

        print(datetime.today())
        track = False
        self.class_menu.clear()
        self.class_group = QtGui.QActionGroup(self)
        self.class_group.triggered.connect(self.ignore)

        re = requests.get(url=self.url_top, cookies=self.cookie)
        soup = BS(re.content)
        r = extract(soup, week_line)
        if r:
            n = []
            for c in r:
                print("topical >>> ", c.week, c.day, c.date, c.time, c.number)
                t = "{0} {1}".format(c.date, c.time)
                if t in self.ignore_list:
                    continue
                n.append(t)
                a = self.class_menu.addAction(t)
                #a.triggered.connect(self.ignore)
                self.class_group.addAction(a)

            find_note = notify2.Notification("EPC found", "EPC found topical\n{0}".format('\n'.join(n)), "dialog-information")
            find_note.show()
            track = True
        elif r is None:
            outdate_note = notify2.Notification("PEC outdate", "EPC cookies outdate", "dialog-warning")
            outdate_note.show()

        re = requests.get(url=self.url_sit, cookies=self.cookie)
        soup = BS(re.content)
        r = extract(soup, week_line)
        if r:
            n = []
            for c in r:
                print("situation >>> ", c.week, c.day, c.date, c.time, c.number)
                t = "{0} {1}".format(c.date, c.time)
                if n in self.ignore_list:
                    print(n, self.ignore_list)
                    continue
                n.append(t)
                a = self.class_menu.addAction(t)
                #a.triggered.connect(self.ignore)
                self.class_group.addAction(a)

            find_note = notify2.Notification("EPC found", "EPC found situation\n{0}".format('\n'.join(n)), "dialog-information")
            find_note.show()
            track = True
        elif r is None:
            outdate_note = notify2.Notification("PEC outdate", "EPC cookies outdate", "dialog-warning")
            outdate_note.show()

        self.class_menu.addAction(self.exitAction)
        delay = (track and 3 or randrange(2, 15, 1))
        print("delay {0}".format(delay))
        QtCore.QTimer.singleShot(delay * 60000, self.quary)

        return track


if __name__ == '__main__':

    parser = ArgumentParser(description='monitor the epc site')

    parser.add_argument('-c', '--cookie', type=SimpleCookie,
                       help='offer the cookies')
    parser.add_argument('-w', '--week_line', type=int,
                       help='the week to order')

    args = parser.parse_args()
    #import ipdb; ipdb.set_trace()
    cookies = args.cookie
    week_line = args.week_line

    c = dict()
    if cookies:
        for k,v in cookies.items():
            c[k] = v.value

    #main(c, week_line)

    app = QtGui.QApplication(sys.argv)
    QtGui.QApplication.setQuitOnLastWindowClosed(False)
    style = app.style()
    e = EPC_Quary(c, week_line)

    sys.exit(app.exec_())

