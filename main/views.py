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
from cfd_fakenews.settings import AZURE_KEY
import requests

sentiment_url = 'https://westcentralus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment'
key_phrases_url = 'https://westcentralus.api.cognitive.microsoft.com/text/analytics/v2.0/keyPhrases'

with open('model/bias_news.pickle','r') as f:
    bias_clf = pickle.load(f)

with open('model/bias_vectorizer.pickle', 'r') as f:
    bias_vectorizer = pickle.load(f)
    
with open('model/fake_news.pickle','r') as f:
    fake_clf = pickle.load(f)

with open('model/fake_vectorizer.pickle', 'r') as f:
    fake_vectorizer = pickle.load(f)
    
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
        fake_vector = fake_vectorizer.transform([content])
        fake_result = fake_clf.predict(fake_vector)[0]
        bias_vector = bias_vectorizer.transform([title])
        bias_result = bias_clf.predict(bias_vector)[0]
        response['bias_result'] = bias_result
        response['fake_result'] = fake_result
        headers   = {"Ocp-Apim-Subscription-Key": AZURE_KEY}
        post_dict = {'documents':[{'id':1,'text':content}]}
        r = requests.post(sentiment_url, headers = headers, json=post_dict)
        resp = r.json()
        sentiment = resp['documents'][0]['score']
        r = requests.post(key_phrases_url, headers = headers, json=post_dict)
        resp = r.json()
        key_phrases = resp['documents'][0]['keyPhrases']
        response['key_phrases'] = key_phrases
        response['sentiment'] = sentiment
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
    content_vector = fake_vectorizer.transform([content])
    ans = fake_clf.predict(content_vector)
    return HttpResponse(title + '\n\n' + content + '\n' + str(ans[0]))
