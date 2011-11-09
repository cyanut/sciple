#!/usr/bin/python

import nflk
import time
from datetime import datetime

dumpprefix="./"

if __name__ == "__main__":
    
    #create a NeuFlock instance
    f = nflk.NeuFlock()
    count = 0 
    maxsince = 1
    while 1:
        

        #retrieve new tweets, every 30 seconds
        try:
            n = f.update_query("#sfn11", since=maxsince)
        except:
            time.sleep(30)
            continue
        for t in f.tweets[-n:]:
            print(t.tostr("<<id>>\t<<created_at>>\t<<user.name>>\t<<catagory>>\t<<text>>"))
        maxsince = f.maxsince + 1
        print ".",#str(n) + " :: " + datetime.now().strftime("%m-%d_%H.%M.%S") 
        time.sleep(30)
        count += 1
         
        #save tweets every 20*30s = 10min
        if count == 20: 
            count = 0
            fname = dumpprefix + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".twt"
            if len(f.tweets) > 0:
                f.dump(fname)
                f.tweets = []
    
    #Format the output
    #print(f.tostr("<<user.name>> at <<created_at>> said: <<text>>"))a

