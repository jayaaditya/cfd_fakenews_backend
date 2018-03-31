# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from sklearn.naive_bayes import MultinomialNB 
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer
from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from bs4 import BeautifulSoup as bs
import requests
import json
import numpy as np 
import pickle

with open('main/model','r') as f:
    clf = pickle.load(f)

with open('main/vectorizer', 'r') as f:
    vectorizer = pickle.load(f)
    
# Create your views here.

class LinkView(APIView):

    def get(self, request, format=None):
        url = request.GET['url']
        r = requests.get(url)
        b = bs(r.content, 'lxml')
        title = ''
        for x in b.find_all('h1'):
            title += x.text
        response = {'title':title}
        content = ''
        for x in b.find_all('p'):
            content += x.text
        print url
        print title, '\n'
        print content
        response['content'] = content
        return Response(response)

def linkFView(request):
    print request.GET
    url = request.GET['url']
    r = requests.get(url)
    b = bs(r.content, 'lxml')
    title = ''
    for x in b.find_all('h1'):
        title += x.text
    response = {'title':title}
    content = ''
    for x in b.find_all('p'):
        content += x.text
    response['content'] = content
    content_vector = vectorizer.transform([content])
    ans = clf.predict(content_vector)
    return HttpResponse(title + '\n\n' + content + '\n' + str(ans[0]))
