#!/usr/bin/python

import nflk
import time
from datetime import datetime
import tweepy.streaming as twtstream

dumprefix = "streaming-twts/"

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
        if t - self.dump_timestamp > 600:
            self.dump_timestamp = t
            fname = dumprefix + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".twt"
            self.nflk.dump(fname)
            self.nflk.tweets = []




if __name__ == "__main__":
    
    #create a NeuFlock instance
    f = nflk.NeuFlock()
    fjson = open(dumprefix+"sfntwts.json", 'a')
    mysfnlistener = SfnListener(nflk=f, json=fjson)
    sfnstream = twtstream.Stream("scipleauto1", \
                                 "scipleftw", \
                                 mysfnlistener, \
                                 timeout = None) 
    print(sfnstream)
    sfnstream.filter(track=("sfn11",))
    print("done")
