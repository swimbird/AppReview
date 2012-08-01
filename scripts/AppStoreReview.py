#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import requests
import pprint
import re
from lxml import etree

import model.Review
import ReviewDB

class AppStoreReview(ReviewDB.ReviewDB):
    __base = os.path.dirname(os.path.abspath(__file__))
    __reviewXML = os.path.normpath(os.path.join(__base, './tmp/app_review.xml'))
    __basehost = "http://ax.itunes.apple.com"
    __basePath = "/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id="
    __baseUrl = __basehost + __basePath
    __userAgent = ("iTunes/9.2 (Windows; Microsoft Windows 7 "
            "Home Premium Edition (Build 7600)) AppleWebKit/533.16")

    def __init__(self):
        pass

    def __del__(self):
        pass

    def get_reviews(self, doc, app_id):
        #item = model.Review.Review()
        ns = { "itms" : "http://www.apple.com/itms/"}
        root = etree.fromstring(doc)

        users = []
        versions = []
        dates = []
        infotags = root.xpath('.//itms:TextView[@topInset="0"][@styleSet="basic13"][@squishiness="1"][@leftInset="0"][@truncation="right"][@textJust="left"][@maxLines="1"]', namespaces = ns)
        for tag in infotags:
            if(etree.tostring(tag).find('by') != -1):
              tmplist = re.sub(' ', '', etree.tostring(tag, encoding='utf-8')).split('\n')
              #print tmplist
              for i, tmp in enumerate(tmplist):
                  if i == 0: #user byAnonymous
                      if(tmp.find('byAnonymous') > 0):
                          users.append('byAnonymous')
                          versions.append('')
                          dates.append('')
                  elif i == 4: #user
                      users.append(tmp)
                      #print tmp
                  elif i == 9: #version
                      m = re.compile('^Version([\d\.]+)').search(tmp)
                      if m:
                          versions.append(m.group(1))
                          #print m.group(1)
                      else:
                          versions.append('')
                          #print "Version None"
                  elif i == 12: #date
                      if re.compile('^\d\d-[A-Za-z]{3}-\d\d\d\d').search(tmp):
                          dates.append(tmp)
                          #print tmp
                      else:
                          dates.append('')
                          #print "Date None"

        titles = []
        titletags = root.xpath('.//itms:TextView[@styleSet="basic13"][@textJust="left"][@maxLines="1"]', namespaces = ns)
        for tag in titletags:
            tmplist = tag.xpath('.//itms:b', namespaces = ns)
            for tmp in tmplist:
                titles.append(tmp.text.encode('utf_8'))
                #print tmp.text.encode('utf_8')

        stars = []
        startags = root.xpath('.//itms:HBoxView[@topInset="1"]', namespaces = ns)
        for tag in startags:
            m = re.compile('^(\d).+').search(tag.get('alt'))
            if m:
                stars.append(m.group(1))
            else:
                stars.append('')

        bodies = []
        bodytags = root.xpath('.//itms:TextView[@styleSet="normal11"]/itms:SetFontStyle', namespaces = ns)
        for tag in bodytags:
            bodies.append(tag.text.encode('utf_8'))
            #print tag.text.encode('utf_8')

        items = []
        count = len(stars)
        for i in range(0, count):
            item = {
                'app_id'  : app_id,
                'user'    : users[i],
                'version' : versions[i],
                'date'    : dates[i],
                'title'   : titles[i],
                'star'    : stars[i],
                'body'    : bodies[i]
            }
            items.append(item)
        #print items
        #print users, versions, dates, titles, stars
        #print len(users), len(versions), len(dates), len(titles), len(stars)

        return items

    def fetch_reviews(self, app_id, pages):

        for i in range(0, pages):
            print "processing ID:%s %s/%s...." % (app_id, i+1, pages)

            url = self.__baseUrl\
                    + app_id\
                    + "&pageNumber="\
                    + str(i)\
                    + "&sortOrdering=4&type=Purple+Software"\

            response = requests.get(url, headers={'User-Agent':self.__userAgent, 'X-Apple-Store-Front':'143462-1'})
            if response.status_code == 200:
                reviews = self.get_reviews(response.text.encode('utf_8'), app_id)
                self.insert_reviews(reviews)

                """
                #[DEBUG]とりあえずはローカルに保存
                f = open(self.__reviewXML, "w")
                f.write(response.text.encode("utf_8"))
                f.close()
                """

            """
            #[DEBUG]とりあえずはローカルのテキストから読み取る
            xml = self.readReviewXML()
            reviews = self.get_reviews(xml, app_id)
            self.insert_reviews(reviews)
            """


    def readReviewXML(self):
        f = open(self.__reviewXML)
        xml = f.read()
        f.close()

        return xml

