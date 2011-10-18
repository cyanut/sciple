#!/usr/bin/python

import tweepy
import nflkdata
import re
import sys
from xml.sax.saxutils import unescape as xmlunescape
try:
    import cPickle as pickle
except ImportError:
    import pickle

class DummyClass:
    def __init__(self):
        pass


class NeuTweet:
    '''Represent a single catagorized tweet object.'''
    
    #thresholds for non-neuroscience related catagory
    #catagory 8
    cat_threshold = 1.4
    #catagory 9
    neu_threshold = 1.01
    norms = None
    ncata = 7
    default_format = "<<id>>\t<<user.name>>\t<<user.profile_image_url>>\t\
                      <<user.url>>\t<<created_at>>\t<<source>>\t\
                      <<catagory>>\t<<retweet_count>>\t<<text>>"

    def __init__(self, status):
        self.status = status
        #contain the catagory of the tweet
        self.catagory = NeuTweet.get_catagory(self.text)

    def __getattr__(self, attr):
        return getattr(self.status, attr)
    
    def __str__(self):
        return self.tostr()

    def _repl(self, attrmatch):
        attrlist = attrmatch.group(1).split(".")
        res = self
        for attr in attrlist:
            res = getattr(res, attr)
        if not res:
            return ""
        #return str(res)
        return unicode(res)
    def tostr(self, fmt=default_format):
        '''Format the tweet to string according to a template.
        fmt: the template. Fields are enclosed by << and >>. For example, \
             <<user.screen_name>> will be replace by the screen name of \
             author. A full list of fields are described in \
             http://dev.twiiter.com/doc/get/statuses/user_timeline. \
             Default to NeuTweet.default_format.\
        Returns a String.
        '''
        return xmlunescape(\
                re.sub("<<([a-z0-9A-Z._\-]+)>>", self._repl, fmt))        
    
    @staticmethod
    def search2stat(searchobj):
        setattr(searchobj, "user", DummyClass())
        setattr(searchobj.user, "name", searchobj.from_user)
        setattr(searchobj.user, "profile_image_url", searchobj.profile_image_url)
        setattr(searchobj.user, "url", "http://twitter.com/"+searchobj.from_user)
        setattr(searchobj, "retweet_count", -1)

    @staticmethod
    def get_catagory(text, worddic=nflkdata.worddic):
        '''Catagorize the tweet and save the result in tweet.catagory.
        Return None.
        '''
        result = [1.0] * NeuTweet.ncata
        minweight = 0.001
        
        if not NeuTweet.norms:
            NeuTweet.norms = [sum([word[cata] for word in worddic.values()]) / len(worddic) for cata in range(NeuTweet.ncata)]
        words = nflkdata.word_splitter.split(\
                nflkdata.link_matcher.sub("", text).lower())
        for word in words:
            if word in nflkdata.worddic:
                for i in range(NeuTweet.ncata):
                    weight = nflkdata.worddic[word][i]
                    if weight >= minweight:
                        result[i] *= weight / NeuTweet.norms[i]
                    else:
                        result[i] *= minweight / NeuTweet.norms[i]
        
        #Scoring catagory 8/9: non-neuroscience related.
        maxscore = -999
        indmax = -1
        restavg = 1
        for i in range(len(result)):
            if result[i] >= maxscore:
                maxscore = result[i]
                indmax = i
            restavg *= result[i]
        neuscore = maxscore / pow(restavg / maxscore, 1 / NeuTweet.ncata)
        totalavg = 1
        for i in result:
            totalavg *= i
        totalavg = pow(totalavg, 1/len(result))
        
        if neuscore > NeuTweet.cat_threshold:
            #If some catagory standout, it's what we want
            return indmax
        elif totalavg > NeuTweet.neu_threshold:
            #If no catagory stands out but general mark is high, classify \
            #to neuroscience - unclassified.
            return 8
        else:
            #Non-neuroscience related, mostly tweets with no keyword found.
            return 9

class NeuFlock:
    '''Class representing a NeuroFlock.'''

    def __init__(self):
        self.twapi = None

        #Stores a list of NeuTweetS. Public.
        self.tweets = []
        
        self._twtids = set()
        self.isauth = False

        #Stores the max id of self.tweets. Public read only. Useful to \
        #retrive tweets only newer than self.tweets.
        self.maxsince = 0

    def auth(self, followlist = None ,\
         consumer_key=nflkdata.consumer_key, \
         consumer_secret = nflkdata.consumer_secret, \
         access_key = nflkdata.access_key, \
         access_secret = nflkdata.access_secret \
    ):
        if self.isauth:
            return
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        self.twapi = tweepy.API(auth)
        self.isauth = True

    def update_home(self, since=1):
        '''retrieve the tweets from all the friends and store in self.tweets
        since: if supplied, only tweets newer than `since' will be retrieved
        '''

        self.auth()
        count = 0
        for tweet in self.twapi.home_timeline(count=200, since_id=since):
            count += self.add(NeuTweet(tweet))
        return count
     
    def update_query(self, query, since=1):
        self.auth()
        count = 0
        for tweet in self.twapi.search(q=query, rpp=100, since_id=since):
            NeuTweet.search2stat(tweet)
            count += self.add(NeuTweet(tweet))
        return count
    

    def update_users(self, userlist=nflkdata.userlist, since=1):
        '''retrieve the tweets from each user in the userlist.
        If userlist is long, result may be truncated due to rate limit.
        '''
        self.auth()
        count = 0
        for user in userlist:
            f = self.twapi.user_timeline(id=user, since_id=since)
            for twt in f:
                try:
                    count += self.add(NeuTweet(twt))
                except TweepError:
                    pass
        return count 

    def add(self, tweet):
        '''Add a tweet to self.tweets.
        tweet: a tweepy.model.Status object.
        '''
        if tweet.id not in self._twtids:
            self.tweets.append(tweet)
            self._twtids.add(tweet.id)
            if tweet.id > self.maxsince:
                self.maxsince = tweet.id
            return 1
        return 0

    def dump(self, fname):
        '''Dump all the tweets in self.tweets, catagory info excluded.
        fname: the file name of the dump.
        '''
        f = open(fname, "wb")
        pickle.dump([nt.status for nt in self.tweets], f)
        f.close()

    def load(self, fname):
        '''Load a file into self.tweets. Tweets will be catagorized, and\
                duplicates are removed.
        fname: filename to load.
        '''
        f = open(fname, "rb")
        temptweets = pickle.load(f)
        count = 0
        for twt in temptweets:
            count += self.add(NeuTweet(twt))
        f.close()
        return count
         
    def top_rts(self, ntop=None, catalist=list(range(1, NeuTweet.ncata+1))):
        '''Return most retweeted tweets in self.tweets. 
        ntop: number of tweets to return. If not supplied, return all, \
                sorted by number of retweets in descending order.
        catalist: list of catagory included for top rt, defaults to neuro\
                related (catagory 1 - 7).
        Return a list of NeuTweetS.
        '''
        temptwt = []
        if not catalist:
            temptwt = self.tweets
        else:
            for twt in self.tweets:
                if twt.catagory in catalist:
                    temptwt.append(twt)
        if not ntop:
            ntop = len(temptwt)
        temptwt.sort(key=NeuFlock._fmt_rt, reverse=True)
        return temptwt[:ntop]   
    
    @staticmethod
    def _fmt_rt(twt):
        rt = str(twt.retweet_count)
        if rt[-1] == "+":
            return int(rt[:-1]) + 1
        else:
            return int(rt)

        

    def tostr(self, strformat=NeuTweet.default_format, splitter="\n"):
        '''Format NeuFlock to string.
        strformat: See NeuTweet.tostr()
        splitter: String delimiting two tweets.
        Return a String.
        '''
        return splitter.join([twt.tostr(strformat) for twt in self.tweets])

if __name__ == "__main__":
    '''
    nflk = NeuFlock()
    nflk.update_home()
    for twt in nflk.tweets[:5]:
        print(twt)
    print("-"*50)
    nflk = NeuFlock()
    nflk.update_users(userlist=nflkdata.userlist[:5])
    for twt in nflk.tweets[:5]:
        print(twt)
    print("-"*50)
    '''
    quit()
