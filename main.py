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

app = Flask(__name__)
url_list=[]
url_totalword=[]
lines=[]
count=0
def cleanText(line):
    text = re.sub('[©®™¶\”\“{\}\-=+,#/\;?^$:.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', ' ', line)
    return text

def url_add(url):
    global count
    wordcount=0
    for temp in url_list:
        if temp==url :
            return 0
    try:
        res=requests.get(url)
        url_list.append(url)
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
            count+=1
        url_totalword.append(wordcount)
        return 1
    except:
        return -1

@app.route('/')
def url_analysis():
    return render_template('info.html',url=url_list)

@app.route('/url',methods=['POST'])
def url_input():
    url=request.form['name']
    url_add(url)
    return redirect(url_for('url_analysis'))

@app.route('/urltext',methods=['POST'])
def url_input2():
    f=request.files['file']
    fp=open(f.filename,'r')
    urls=fp.readlines()
    for url in urls:
        url=url.replace('\n','')
        url_add(url)
    return redirect(url_for('url_analysis'))

if __name__ == '__main__':
    app.run()
