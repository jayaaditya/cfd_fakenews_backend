# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from bs4 import BeautifulSoup as bs
import requests
import json

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
    return HttpResponse(title + '\n\n' + content)
