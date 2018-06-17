# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from sklearn.naive_bayes import MultinomialNB 
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer
from django.http.response import HttpResponse
import rest_framework.status as status
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.decorators import api_view
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
        try:
            r = requests.get(url)
        except:
            return Response({'error':'Unable to parse'})
        b = bs(r.content, 'lxml')
        title = ''
        for x in b.find_all('h1'):
            title += x.text
        response = {'title':title}
        content = ''
        for x in b.find_all('p'):
            content += x.text
        if content == '':
            return Response({'error':'Unable to parse'})
        print url
        print title, '\n'
        print content
        response['content'] = content
        fake_vector = fake_vectorizer.transform([content])
        fake_result = fake_clf.predict(fake_vector)[0]
        bias_vector = bias_vectorizer.transform([content])
        bias_result = bias_clf.predict(bias_vector)[0]
        response['bias_result'] = bias_result
        response['fake_result'] = fake_result
        headers   = {"Ocp-Apim-Subscription-Key": AZURE_KEY}
        if len(content) >= 5120:
            crop = 5120
        else:
            crop = -1
        post_dict = {'documents':[{'id':1,'text':title}]}
        try:
            r = requests.post(sentiment_url, headers = headers, json=post_dict)
            resp = r.json()
            sentiment = resp['documents'][0]['score']
        except:
            sentiment = "unavailable"
        post_dict = {'documents':[{'id':1,'text':content[0:crop]}]}
        try:
            r = requests.post(key_phrases_url, headers = headers, json=post_dict)
            resp = r.json()
            key_phrases = resp['documents'][0]['keyPhrases']
        except:
            key_phrases = 'unavailable'
        response['key_phrases'] = key_phrases
        response['sentiment'] = sentiment
        return Response(response)

@api_view(['POST'])
@csrf_exempt
def updateView(request):
    if request.method == 'POST':
        print request.POST
        try:
            url = request.POST['link']
            fake_result = request.POST['fake_result']
            bias_result = request.POST['bias_result']
        except:
            print "1"
            return Response({'error':'BAD REQUEST'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            r = requests.get(url)
        except:
            print "2"
            return Response({'error':'Unable to parse'}, status = status.HTTP_400_BAD_REQUEST)
        b = bs(r.content, 'lxml')
        title = ''
        for x in b.find_all('h1'):
            title += x.text
        response = {'title':title}
        content = ''
        for x in b.find_all('p'):
            content += x.text
        if content == '':
            print "3"
            return Response({'error':'Unable to parse'}, status = status.HTTP_400_BAD_REQUEST)
        print url
        print title, '\n'
        print content
        response['content'] = content
        fake_vector = fake_vectorizer.transform([content])
        fake_clf.partial_fit(fake_vector, [json.loads(fake_result)])
        bias_vector = bias_vectorizer.transform([content])
        bias_clf.partial_fit(bias_vector, [json.loads(fake_result)])
        return Response(request.POST, status = status.HTTP_202_ACCEPTED)
    else:
        return Response({'error':'Forbidden request'}, status = status.HTTP_403_FORBIDDEN)
