#!/usr/bin/python

import nflk
import time
import urllib
from datetime import datetime
import tweepy.streaming as twtstream

dumprefix = "streaming-twts/"
keyword_list = ("sfn11",)
upload_interval = 600 #seconds
default_posturl = "http://127.0.0.1:8010/tweet-buff.php"
postargs = ("passwd", "tweetjson")
postpass = "SciPleFTW" #1/0 #just to get your attention here

class SfnListener(twtstream.StreamListener):


    def __init__(self, nflk=None, json=None):
        super(SfnListener, self).__init__()
        if json:
            self.jsonlog = json
        if nflk:
            self.nflk = nflk
        self.dump_timestamp = 0

    def on_data(self, data):
        super(SfnListener, self).on_data(data)
        if self.jsonlog:
            self.jsonlog.write(data)
            self.jsonlog.flush()

    def on_status(self, status):
        self.nflk.add(nflk.NeuTweet(status))
        if self.nflk.tweets:
            print(self.nflk.tweets[-1].tostr("<<id>>\t<<created_at>>\t<<user.name>>\t<<catagory>>\t<<text>>"))
        t = time.time()
        if t - self.dump_timestamp > upload_interval:
            self.dump_timestamp = t
            fname = dumprefix + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".twt"
            self.nflk.dump(fname)
            
            postdata = self.nflk.tojson()
            params = urllib.urlencode(dict(zip(postargs, \
                                              (postpass, postdata))))
            f = urllib.urlopen(default_posturl, params)
            lastid = f.read()
            if lastid:
                print("tweets uploaded. Last =", lastid)
                self.nflk.tweets = []




if __name__ == "__main__":
    import glob

    f = nflk.NeuFlock()
    for fn in glob.glob("*.twt"):
        f.load(fn)
    fjson = open(dumprefix+"sfntwts.json", 'a')
    mysfnlistener = SfnListener(nflk=f, json=fjson)
    sfnstream = twtstream.Stream("scipleauto1", \
                                 "scipleftw", \
                                 mysfnlistener, \
                                 timeout = None) 
    sfnstream.filter(track=keyword_list)
    print("done")
