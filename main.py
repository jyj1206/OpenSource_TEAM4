#!/usr/bin/python
#-*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for

app = Flask(__name__)

url=[]

@app.route('/')
def url_analysis():
    return render_template('info.html',url=url)

@app.route('/url',methods=['POST'])
def url_input():
    url.append(request.form['name'])
    return redirect(url_for('url_analysis'))

@app.route('/urltext',methods=['POST'])
def url_input2():
    f=request.files['file']
    fp=open(f.filename,'r')
    urls=fp.readlines()
    for temp in urls:
        url.append(temp)
    return redirect(url_for('url_analysis'))

if __name__ == '__main__':
    app.run()
