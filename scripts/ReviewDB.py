#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import hashlib
from datetime import datetime
from sqlite3 import dbapi2 as sqlite

class ReviewDB(object):
    __base = os.path.dirname(os.path.abspath(__file__))
    __database = os.path.normpath(os.path.join(__base, './db/app.db'))
    __table = 'reviews'

    def __init__(self):
        pass

    def __del__(self):
        pass

    def fetch_reviews(self, app_id, pages):
        raise NotImplementedError

    def insert_reviews(self, items):
        con = sqlite.connect(self.__database)
        con.text_factory = str
        query = '''
        INSERT INTO reviews
        (hash, user, date, title, body, version, app_id, star, created_at)
        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        for item in items:
            sha1hash = hashlib.sha1(item['user'] + item['body']).hexdigest()
            try:
                con.execute(query, (sha1hash, item['user'], item['date'], item['title'], item['body'], item['version'], item['app_id'], item['star'], datetime.now()))
            except sqlite.IntegrityError as e:
                print e.message
                pass

        con.commit()
        con.close()

        pass

    def create_database(self):
        con = sqlite.connect(self.__database)
        cur = con.execute("SELECT * FROM sqlite_master WHERE type='table' and name='%s'" % self.__table)
        if cur.fetchone() == None: #存在してないので作る
            con.execute("CREATE TABLE %s(id integer PRIMARY KEY AUTOINCREMENT, hash string UNIQUE, user string, date string, title string, body string, version string, device string, app_id string, nodes string, star int, created_at timestamp)" % self.__table)
            #print "create reviewsDB"
        else:
            #print "already reviewsDB"
            pass
        con.commit()
        con.close()

    def count_reviews(self, app_id):
        con = sqlite.connect(self.__database)
        cur = con.execute("select count(app_id) from reviews where app_id='%s'" % app_id)
        count = cur.fetchone()
        con.close()

        return count[0]

