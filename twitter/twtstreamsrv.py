#!/usr/bin/python

import sys
import urllib.request 
import base64
import socket, os, threading, json
import time
from urllib.parse import quote as urlquote

#keywords = "neuroscience, neuron, brain"
keywords = "#fail"
uname = b"scipleauto1"
upass = b"scipleftw"

FILTER_URL = "http://stream.twitter.com/1/statuses/filter.json?track="
conn_pool = []
srvskt = None
sktfile = "/tmp/twtstream.skt"

def init_socket():
    srvskt = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        os.remove(sktfile)
    except OSError:
        pass
    srvskt.bind(sktfile)
    os.chmod(sktfile, 666)
    srvskt.listen(1)

    #def incoming():
    print("Server listening...")
    while True:
        conn, addr = srvskt.accept()
        print(addr.decode("utf8") + " connected!")
        conn.setblocking(0)
        conn_pool.append(conn)

def init_twt_conn():
    kw = urlquote(keywords)
    requrl = FILTER_URL + kw
    authstr = uname + b":" + upass
    hauth = {"Authorization":"basic " + base64.b64encode(authstr).decode("utf-8")}
    req = urllib.request.Request(requrl, headers=hauth)
    f = urllib.request.urlopen(req)
    return f

def main_loop():
    buff = b""
    f = init_twt_conn()
    while True:
        try:
            buff += f.readline()
        except KeyboardInterrupt:
            quit()
        except:
            print("connection error, reconnect in 10s ...")
            time.sleep(10)
            f = init_twt_conn()
            continue
        if buff[-2:] == b"\r\n":
            json = buff
            process_json(json)
            buff = b""

def process_json(j):
    broadcast(j)
    #print(fmtjson(j))

def broadcast(s):
    p = 0
    while p < len(conn_pool):
        try:
            conn_pool[p].send(s)
            p += 1
        except KeyboardInterrupt:
            quit()
        except:
            print("broadcast to conn number %d failed, disconnect" %p)
            conn_pool.pop(p)


def dummy_client():
    cliskt = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    cliskt.connect(sktfile)
    buff = b""
    while True:
        try:
            buff += cliskt.recv(4096)
        except:
            print("connection error, exiting ...")
            quit()
        arrj = buff.split(b"\r\n")
        if arrj[-1][-2:] != b"\r\n":
            buff = arrj[-1]
            arrj.pop(-1)
        else:
            buff = b""
        for jstwt in arrj:
            print(fmtjson(jstwt), end="")

def fmtjson(j):
    if len(j) <= 2:
        return "."
    twt = json.loads(j.decode("utf8"))
    return (twt["user"]["screen_name"] + ": " + twt["text"]\
            + " @" +twt["created_at"] + "\n" + "-"*20 + "\n")

def run_srv():
    srvthread = threading.Thread(target=init_socket)
    srvthread.start()
    main_loop()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-s":
        run_srv()
    else:
        dummy_client()
    

