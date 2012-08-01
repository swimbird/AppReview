#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys
import textwrap

import AppStoreReview
import GooglePlayReview
import ReviewDB

class AppReview(object):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def fetch(self):
        if (len(sys.argv) == 2):
            app_id = sys.argv[1]
            ReviewDB.ReviewDB().create_database()
            count = ReviewDB.ReviewDB().count_reviews(app_id)
            pages = 3 if count > 0 else 11
            self.fetch_reviews(app_id, pages)
        else:
            print textwrap.dedent("""\
            app_idを正しく指定してください。
            [例. AppStore]
            %python Fetch.py 409807569

            [例. GooglePlay]
            %python Fetch.py com.rovio.angrybirds""")
            quit()
        #self.fetch_reviews('409807569', pages)
        #self.fetch_reviews('com.rovio.angrybirds', 1)

    def fetch_reviews(self, app_id, pages):
        if (self.is_app_store_app(app_id)):
            task = AppStoreReview.AppStoreReview()
        else:
            task = GooglePlayReview.GooglePlayReview()
        task.fetch_reviews(app_id, pages)

    def is_app_store_app(self, id):
        return re.compile('^\d+$').search(id)
