#!/usr/bin/python
#-*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from flask import request
import sys
import re
import requests
from bs4 import BeautifulSoup
from flask import redirect, url_for
from elasticsearch import Elasticsearch
import numpy
from numpy import dot
from numpy.linalg import norm
from nltk import word_tokenize
import math

app = Flask(__name__)

es_host="127.0.0.1"
es_port="9200"
es=Elasticsearch([{'host':es_host,'port':es_port}],timeout=30)
e={
    "url":[]
}

count=0
lines=[]
# status
url_num=0
status=0
success=0
fail=0
same=0

def cleanText(line):
    text = re.sub('[©®™¶\”\“{\}\-=+,#/\;?^$:.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', ' ', line)
    return text

def url_add(url):
    global count
    wordcount=0
    for temp in e["url"]:
        if temp==url :
            return 0
    try:
        res=requests.get(url)
        e["url"].append(url)
        html=BeautifulSoup(res.content,"html.parser")
        html_body=html.find_all('body')
        for line in html_body:
            line = line.text
            line = cleanText(line)
            line = line.replace('\n',' ')
            s = line.split(' ')
            for word in s:
                if(word==''):
                     continue
                if(word.isdigit()==True):
                     continue
                if(wordcount==0):
                     lines.append(word.lower())
                else:
                     lines[count]=lines[count] + ' ' + word.lower()
                wordcount+=1
        e[count]={'url':url,'Total_word':wordcount,'Lines':lines[count],'Process_Time' : 0}
        count+=1
        return 1
    except:
        return -1

@app.route('/')
def url_analysis():
    global es;
    res=es.index(index='web',doc_type='word',id=1,body=e)
    return render_template('info.html',url_num=url_num,status=status,success=success,fail=fail,same=same,count=count,url_info=e)

@app.route('/url',methods=['POST'])
def url_input():
    global url_num, status
    url_num=1
    url=request.form['name']
    status=url_add(url)
    return redirect(url_for('url_analysis'))

@app.route('/urltext',methods=['POST'])
def url_input2():
    global url_num, success, fail, same
    url_num=0
    success=0
    fail=0
    same=0
    f=request.files['file']
    fp=open(f.filename,'r')
    urls=fp.readlines()
    for url in urls:
        url=url.replace('\n','')
        temp=url_add(url)
        if(temp==1):
            success+=1
        elif(temp==-1):
            fail+=1
        else:
            same+=1
        url_num+=1
    return redirect(url_for('url_analysis'))

if __name__ == '__main__':
    app.run()
