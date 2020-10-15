#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 21:10:54 2020

@author: wuboyi
"""

import requests
from bs4 import BeautifulSoup

import pandas as pd
import json

import sched
import time

s = sched.scheduler(time.time, time.sleep)

timeGap = 1
stockList = ['6443', '2330']

# Get token
token = ""

# This function will be a module into another file 
def readTokenInFile():
    f = open("Token.txt", "r")
    tokenStr = f.readline()
    f.close()
    return tokenStr;

def lineSendMsg(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    params = {"message": msg}
    
    # Show send msg in IDE
    print('Msg: ' + msg)
    
    # Send msg
    r = requests.post("https://notify-api.line.me/api/notify",
                      headers=headers, params=params)
    #print(r.status_code)

def getStockUrl(targets):
    urlPart1 = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch="
    urlPart2 = ""
    urlPart3 = "&json=1&delay=0&_=1552123547443"
    
    for codename in targets:
        urlPart2 = urlPart2 + "tse_{stock}.tw|".format(stock = codename)
    url = urlPart1 + urlPart2 + urlPart3
    
    return url

def crawlStock(targets):
    # Set url
    url = getStockUrl(targets);
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 解析成Json格式
    data = json.loads(soup.prettify())
        
    # 將Json格式解析成DataFrame
    columns = ['c', 'n', 'z']
    df = pd.DataFrame(data['msgArray'], columns=columns)
    
    # Set send msg
    msg = ""
    for rowIndex in range(len(stockList)):
        if rowIndex != 0:
            msg = msg + ", "
        price = round(float(df.at[rowIndex, 'z']), 2)
        msg = msg + str(df.at[rowIndex, 'n']) \
            + "  " + str(price)
        
    lineSendMsg(token, msg)
    
    # Call itself again
    #s.enter(timeGap, 0, crawlStock, argument = (stockList,))
     
if __name__ == '__main__':
    token = readTokenInFile()
    s.enter(timeGap, 0, crawlStock, argument = (stockList,))
    s.run()
    
    
    