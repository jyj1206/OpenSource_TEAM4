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

word_d = {}
sent_list = []

def cosine_similarity(x,c):
    global count
    sent_list=[]
    word_d={}
    for i in range(0,count):
        process_new_sentence(x[i]['lines'])
        x[i]['vector']=make_vector(i)
    v1=x[c]['vector']
    for i in range(0,count):
        if(c==i):
            continue
        v2=x[i]['vector']
        dotpro= numpy.dot(v1,v2)
        cossimil = dotpro/(norm(v1)*norm(v2))
        x[i]['cossimil'][i]=cossimill

def tf_idf(x,c):
    sent_list=[]
    word_d={}
    for i in range(0,count):
        process_new_sentence(x[i]['lines'])
    idf_d = compute_idf()
    tf_d = compute_tf(sent_list[c])
    for word,tfval in tf_d.items():
        x[c]['tf_idf'][word]=tfval*idf_d[word]

def process_new_sentence(s):
    sent_list.append(s)
    tokenized = word_tokenize(s)
    for word in tokenized:
        if word not in word_d.keys():
            word_d[word]=0
        word_d[word] += 1

#cosine similarity
def make_vector(i):
    v = []
    s = sent_list[i]
    tokenized = word_tokenize(s)
    for w in word_d.keys():
        val = 0
        for t in tokenized:
            if t==w:
                val +=1
        v.append(val)
    return v

#tf-idf
def compute_tf(s):
    bow = set()
    wordcount_d = {}
    tokenized = word_tokenize(s)
    for tok in tokenized:
        if tok not in wordcount_d.keys():
            wordcount_d[tok]=0
        wordcount_d[tok] += 1
        bow.add(tok)

    tf_d = {}
    for word,count in wordcount_d.items():
        tf_d[word]=count/float(len(bow))
    return tf_d

def compute_idf():
    Dval = len(sent_list)
    bow = set()
    for i in range(0,len(sent_list)):
        tokenized = word_tokenize(sent_list[i])
        for tok in tokenized:
            bow.add(tok)
    idf_d = {}
    for t in bow:
        cnt = 0
        for s in sent_list:
            if t in word_tokenize(s):
                cnt += 1;
        idf_d[t]=math.log(Dval/cnt)

    return idf_d

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
        e[count]={'url':url,'Total_word':wordcount,'Lines':lines[count],'Process_Time' : 0,'cosimil':{}}
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
