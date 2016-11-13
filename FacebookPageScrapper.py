
# coding: utf-8

# In[96]:

"""
Facebook Page Scrapper.
author          : Ridho Akbar (github username: rabkar)
last modified   : 2016-11-13 12:17:00 UTC+7

Example ussage:
------------------
app_id = <your app_id here>
app_secret = <your app_secret here>
page_id = "kompasTV"
num_status = 75 # facebook API has limit. Mine was 75 status at once, others may vary

import FacebookPageScrapper as scr
# initialize scrapper object
myScrapper = scr.FacebookPageScrapper(app_id, app_secret)
    # myScrapper._id to get the scrapper app_id
    # myScrapper.app_secret to get the scrapper app_secreet
    # myScrapper.access_token to get the scrapper access_token

# get the data
page_feeds = scr.PageFeedData(myScrapper, page_id, num_status)
    # page_feeds._scrapper to see the FacebookScrapper object
    # page_feed.data to see the data retreived by scrapper

# convert data to Pandas Dataframe
page_feed_dataframe = page_feed.facebook_page_feed_to_dataframe()
"""

# import python dependencies
import urllib2
import json
from datetime import datetime, timedelta
import csv
import time
import pandas as pd

# Setting up credential

class FacebookPageScrapper(object):
    
    def __init__(self, app_id, app_secret):
        self._id = str(app_id)
        self._app_secret = app_secret
        self._access_token = app_id + "|" + app_secret
        
    def get_facebook_page_feed(self, page_id, num_status):
        """
        :parameters
            page_id (string) : name of page to be scraped
            access_token (string) : personal access token got from \
                                    facebook for developer
            num_status (string) : number of status to be scraped

        :return
            list of dict
        """
        
        def request_until_succeed(url):
            """
            : parameter
                url
            : return
                dict / string
            """
            response = "Error"
            req = urllib2.Request(url)
            success = False
            for trial in range(1):
                try: 
                    response = urllib2.urlopen(req)
                    if response.getcode() == 200:
                        success = True
                except Exception, e:
                    print e
                    time.sleep(5)
                    print "Error for URL {0}: {1} \n".format(url, datetime.now())
            if not isinstance(response,str):
                return response.read()
            else:
                return response

        access_token = self._access_token
        # construct the URL string
        base = "https://graph.facebook.com"
        node = "/" + page_id + "/feed" 
        parameters = "/?fields=message,link,created_time,type,name,id," \
                     "likes.summary(true),"\
                     "comments.summary(true),"\
                     "shares&limit={0}&access_token={1}" \
                     .format(num_status, access_token) # changed
        url = base + node + parameters

        # retrieve data
        request_response = request_until_succeed(url)
        try:
            data = json.loads(request_until_succeed(url))
            return data.get('data')
        except Exception, e:
            print e
            return "Error reading url"
    
class PageFeedData(object):
    
    def __init__(self, myscrapper, page_id, num_status):
        self._scrapper =  myscrapper
        self.data = self._scrapper.get_facebook_page_feed(
                            page_id,
                            num_status
                        )

    def facebook_page_feed_to_dataframe(self):
        """
        :parameters
            feed (list of dict)
        :return
            Dataframe Object
        """
        
        def process_facebook_page_feed(datum):
            """
            :parameters
                datum (dict) : single facebook feed

            :return
                dict
            """

            def cleanse_timestamp_format(ts):
                """
                :paramters: 
                    timestamp (string)
                :return
                    string
                """
                date = ts[0:10]
                time = ts[11:19]
                return date + ' ' + time

            message = datum.get('message')
            feed_type = datum.get('type')
            ts = str(datum.get('created_time'))
            creation_time = cleanse_timestamp_format(
                                str(datum.get('created_time'))
                            )
            if datum.get('likes') is not None:
                n_likes = datum.get('likes')\
                               .get('summary')\
                               .get('total_count')
            else:
                n_likes = 0
            if datum.get('comments') is not None:
                n_comments = datum.get('comments')\
                                  .get('summary')\
                                  .get('total_count')
            else:
                n_comments = 0
            if datum.get('shares') is not None:
                n_shared = datum.get('shares')\
                                .get('count')
            else:
                n_shared = 0
            link = datum.get('link')
            modified_at = datetime.now()\
                                  .strftime("%Y-%m-%d %H:%M:%S")

            datum = {
                "message" : message,
                "feed_type" : feed_type,
                "creation_time" : creation_time,
                "n_likes" : n_likes,
                "n_comments" : n_comments,
                "n_shared" : n_shared,
                "link" : link,
                "modified_at" : modified_at
            }
            return datum
        
        feeds = self.data
        n = len(feeds)
        df = []
        for i in range(n):
            datum = process_facebook_page_feed(feeds[i])
            df.append(datum)

        return pd.DataFrame(df)

