#!/usr/bin/python

import nflk
from datetime import datetime

if __name__ == "__main__":
    fname = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".twt"
    
    #create a NeuFlock instance
    f = nflk.NeuFlock()
    
    #retrieve new tweets
    f.update_query("#sfn11")

    #You can also include previous tweets in the analysis
    #f.load("previously-dumped.twt")
    
    #save all the tweets
    f.dump(fname)
    
    #Format the output
    #print(f.tostr("<<user.name>> at <<created_at>> said: <<text>>"))
    print(f.tostr("<<id>>\t<<created_at>>\t<<user.name>>\t<<catagory>>\t<<text>>"))

    print("\n"+"-"*25+" TOP 10 "+"-"*25+"\n")

    #Top 10 retweets
    for twt in f.top_rts(ntop=10):
        print(twt.tostr("<<user.name>> said <<text>> is retweeted <<retweet_count>> times.\n"))
