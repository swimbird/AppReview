#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import requests
import pprint
import re
import json
import lxml.html

import model.Review
import ReviewDB

class GooglePlayReview(ReviewDB.ReviewDB):
    __base = os.path.dirname(os.path.abspath(__file__))
    __reviewJSON = os.path.normpath(os.path.join(__base, './tmp/google_review.json'))
    __basehost = "https://play.google.com"
    __basePath = "/store/getreviews"
    __baseUrl = __basehost + __basePath

    def __init__(self):
        pass

    def __del__(self):
        pass

    def get_reviews(self, doc, app_id):
        root =  lxml.html.fromstring(doc)

        titles = []
        titletags = root.xpath("//h4[@class='review-title']")
        for tag in titletags:
            titles.append(tag.text.encode('utf_8') )
            #print tag.text.encode('utf_8')

        bodies = []
        bodytags = root.xpath("//div[@class='doc-review']")
        for tag in bodytags:
            html = lxml.html.tostring(tag, encoding='utf_8')
            bodies.append(self.get_body(html))


        dates = []
        datetags = root.xpath("//span[@class='doc-review-date']")
        for tag in datetags:
            dates.append(self.get_date(tag.text))
            #print self.get_date(tag.text)

        stars = []
        startags = root.xpath("//div[@class='ratings goog-inline-block']")
        for tag in startags:
            text = tag.attrib['title'].encode('utf_8')
            stars.append(self.get_star(text))
            #print lxml.html.tostring(tag)
            #print tag.attrib['title'].encode('utf_8')

        users = []
        usertags = root.xpath("//div[@class='doc-review']")
        for tag in usertags:
            html = lxml.html.tostring(tag, encoding='utf_8')
            users.append(self.get_user(html))
            #print tag.text.encode('utf_8')

        versions = []
        devices = []
        versiontags = root.xpath("//div[@class='doc-review']")
        for tag in versiontags:
            html = lxml.html.tostring(tag, encoding='utf_8')
            versions.append(self.get_version(html))
            devices.append(self.get_device(html))

        #print items
        #print users, versions, dates, titles, stars
        #print len(users), len(versions), len(dates), len(titles), len(stars)

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

        return items


    def get_body(self, text):
        body = ''
        m = re.compile('<p class="review-text">(.+)</p>').search(text)
        if m:
            body = m.group(1)
        return body

    def get_date(self, text):
        date = ''
        m = re.compile(' - (\d\d\d\d/\d\d/\d\d)').search(text)
        if m:
            date = m.group(1)
        return date

    def get_star(self, text):
        star = ''
        m = re.compile('(\d)\.0').search(text)
        if m:
            star = m.group(1)
        return star

    def get_user(self, text):
        user = ''
        m = re.compile('<strong>(.+)</strong>').search(text)
        if m:
            user = m.group(1)
        return user

    def get_version(self, text):
        version = ''
        m = re.compile('バージョン ([\d\.]+)\<').search(text)
        if m:
            version = m.group(1)
        return version

    def get_device(self, text):
        device = ''
        m = re.compile('</span> - (.+?)、バージョン').search(text)
        if m:
            device = m.group(1)
        return device

    def fetch_reviews(self, app_id, pages):

        for i in range(0, pages):
            print "processing ID:%s %s/%s...." % (app_id, i+1, pages)

            query = {
                'id'              : app_id,
                'pageNum'         : str(i),
                'reviewSortOrder' : '2',
                'reviewType'      : '1'
            }

            response = requests.post(self.__baseUrl, query);

            if response.status_code == 200:
                json_data = json.loads(response.text.encode("utf_8").split('\n')[1])
                html_string = json_data["htmlContent"]
                reviews = self.get_reviews(html_string, app_id)
                self.insert_reviews(reviews)

                """
                #[DEBUG]とりあえずはローカルに保存
                f = open(self.__reviewJSON, "w")
                f.write(response.text.encode("utf_8").split('\n')[1])
                f.close()
                """

        """
        #[DEBUG]とりあえずはローカルのテキストから読み取る
        json_data = json.loads(self.readReviewJSON())
        html_string = json_data["htmlContent"]
        reviews = self.get_reviews(html_string, app_id)
        self.insert_reviews(reviews)
        """

    def readReviewJSON(self):
        f = open(self.__reviewJSON)
        json = f.read()
        f.close()

        return json
