# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 13:19:43 2015

@author: zhangjian5
"""
import logging

try:
    import requests
except ImportError:
    logging.warn("can not find requests module")
try:
    from bs4 import BeautifulSoup
except ImportError:
    logging.warn("can not find BeautifulSoup4 module")
import sys
import os
import time
import ConfigParser

reload(sys)
sys.setdefaultencoding('utf-8')


class AutoGetGeneralSS():
    def __init__(self, main_url, data):
        self.main_url = main_url
        self.data = data
        self.session = requests.session()
        self.login_url = '/_login.php'
        self.node_url = '/node.php'
        self.targetUrls = []

        # 日志记录

    @staticmethod
    def loger(content):
        if not os.path.exists('logger'):
            os.mkdir('logger')
        f = open(r'logger//logger.txt', 'wb')
        f.write(content)
        f.write('\r\n')
        f.flush()
        f.close()

    # 模拟登录，从网页中获取含有配置文件的地址
    def getTargetUrls(self):
        r = self.session.post(url=str(self.main_url + self.login_url), data=self.data)
        print self.main_url + self.login_url
        if r.status_code == 200:
            AutoGetGeneralSS.loger((time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) + ":" + r.text))
            print '[+]loger:%s' % r.text
            ss_r = self.session.get(url=self.main_url + self.node_url)
            soup = BeautifulSoup(ss_r.text)
            nodeUrls = soup.find_all('a', {'role': 'menuitem', 'target': '_blank'})
            for i in xrange(0, len(nodeUrls), 2):
                self.targetUrls.append(self.main_url + nodeUrls[i].get('href'))
            print '[+]targetUrls has been finished.'

    # 保存SS数据到本地SS配制文件中
    def saveSS(self, localSSPath):
        f = open(localSSPath, 'r')
        config = str(f.read())
        f.close()
        s = ''
        tmp = ''
        for j in self.targetUrls:
            AutoGetGeneralSS.loger(('[+]targetUrls is :%s' % j))
            print '[+]targetUrls is :%s' % j
            r = self.session.get(url=j)
            tmp += r.text + ','
            s = config[:config.index('[') + 2] + tmp + config[config.index('[') + 2:]
        print s
        fw = open(localSSPath, 'wb')
        fw.write(s)
        fw.close()


def main(config_file_path):
    # 从配置文件中读取mainUrl，用户和本地ss配置文件路径
    cf = ConfigParser.ConfigParser()
    cf.read(config_file_path)

    main_url = cf.get('loginGeneralSS', 'mainUrl')
    userlists = cf.get('loginGeneralSS', 'userlists')
    localSSPath = cf.get('local', 'shadowscoksPath')

    users = userlists.split('|')
    for i in users:
        email = i.split('&')[0]
        passwd = i.split('&')[1]
        print email + ':' + passwd
        data = dict(email=email, passwd=passwd, remember_me='week')
        a = AutoGetGeneralSS(main_url, data)
        a.getTargetUrls()
        a.saveSS(localSSPath)


if __name__ == '__main__':
    main('config.ini')
