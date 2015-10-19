#!/usr/bin/python
# coding: utf-8
import requests
from bs4 import BeautifulSoup
import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')

import html2text

class ptt_data_fetcher(object):

    def __init__(self):
        self.now_page = ''
        self.start_page = ''
        self.processing_pages = 1
        self.board_names = [
            # 'WomenTalk',
            # 'Gossiping',
            # 'C_Chat',
            'Tech_Job',
            # 'Travel',
            # 'Japan_Travel',
            # 'Boy-Girl',
            # 'StupidClown',
            # 'ONE_PIECE',
            # 'WOW'
            # 'joke',
            # 'ingress'
        ]

    def is_int(self, value):
        try:
            value = int(value)
            return True
        except ValueError:
            return False

    def start(self):
        for board_name in self.board_names:
            print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> %s' % board_name
            self.start_page = '/bbs/%s/index.html' % board_name
            self.now_page = self.start_page

            for i in xrange(self.processing_pages):
                print '======== page %s ========' % i
                res = self.get_data()
                self.process_page_list(res)
                self.now_page = self.last_page

    def get_data(self, url=''):
        payload = {
            'from': self.start_page,
            'yes' : 'yes'
        }

        rs = requests.Session()
        res = rs.post(
            'https://www.ptt.cc/ask/over18',
            verify=False,
            data=payload
        )

        if url:
            link = 'https://www.ptt.cc%s' % url
        else:
            link = 'https://www.ptt.cc%s' % self.now_page

        print link

        res = rs.get(
            link,
            verify=False
        )
        return res

    def process_page_list(self, plain_text_res):
        soup = BeautifulSoup(plain_text_res.text, "html.parser")

        for entry in soup.select('a.wide'):
            print entry.text
            if entry.text == u'‹ 上頁':
                self.last_page = entry.get('href')

        for entry in soup.select('.r-ent'):
            title = entry.select('.title')[0].text.strip()
            if not title.startswith(u'[公告]') and u'刪除' not in title:

                date = entry.select('.date')[0].text.strip()
                author = entry.select('.author')[0].text.strip()

                link = ''
                href = entry.select('.title a')[0]['href'].strip()
                if href:
                    link = 'https://www.ptt.cc%s' % href
                content = self.get_article_content_v2(href)

                total_content = ''
                for line in content['content']:
                    total_content = total_content + line + '\n'

                print 'date: %s\nauthor: %s\ntitle: %s\nlink: %s\ncontent: %s' % (
                    date,
                    author,
                    title,
                    link,
                    total_content
                )

                if entry.select('span'):
                    recommandation = entry.select('span')[0].text
                    if recommandation == u'爆':
                        print '%s!!!!!!!!!!!!!!!!!' % recommandation
                    elif recommandation.startswith('X'):
                        print u'廢文勿看'
                    elif self.is_int(recommandation) and int(recommandation) > 10:
                        print '還算熱門'

                print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'

    def get_article_content(self, href):
        content = ''
        total_content = ''

        res = self.get_data(href)
        soup = BeautifulSoup(res.text, "html.parser")

        try:
            content = soup.select('div.article-metaline')[2].next_sibling

            descendants = soup.select('div.bbs-screen')[0].children
            for item in descendants:
                try:
                    if item.content:
                        total_content = total_content + item.content.strip()
                except Exception:
                    total_content = total_content + item.strip()
        except Exception:
            pass

        if total_content:
            return total_content
        else:
            return content

    def get_article_content_v2(self, href):
        time.sleep(1)
        res = self.get_data(href)
        h = html2text.HTML2Text()
        h.ignore_links = True
        pure_content = h.handle(res.text)
        pure_content_by_line = pure_content.split('\n')

        split_line = self.find_split_line(pure_content_by_line)

        content_last_line_index = pure_content_by_line.index(split_line)
        if split_line != '':
            res = {
                'content': pure_content_by_line[:content_last_line_index+2],
                'comment': pure_content_by_line[content_last_line_index+2:]
            }
        else:
            res = {
                'content': pure_content_by_line,
                'comment': ''
            }
        return res

    def find_split_line(self, content_by_line):
        split_line = ''
        for index, line in list(enumerate(content_by_line)):
            if u'文章網址' in line:
                split_line = line
                if u'編輯' in content_by_line[index + 1]:
                    split_line = content_by_line[index + 1]
                return split_line
            elif u'編輯' in line:
                split_line = line
                return split_line

    def find_keyword(self, total_content):
        keyword = '金'
        for line in total_content['content']:
            if keyword in line:
                print line

        for line in total_content['comment']:
            if keyword in line:
                print line

if __name__ == '__main__':
    df = ptt_data_fetcher()

    if len(sys.argv) == 1:
        df.start()
    else:
        if sys.argv[1] == 'get_keyword_from_article':
            total_content = df.get_article_content_v2('/bbs/Gossiping/M.1442559625.A.F6E.html')
            df.find_keyword(total_content)
        elif sys.argv[1] == 'get_article_v2':
            res = df.get_article_content_v2('/bbs/Gossiping/M.1445161731.A.0DE.html')
            for line in res['content']:
                print line.strip()
            print '======================='
            for line in res['comment']:
                print line
        else:
            print 'unsupport command'
