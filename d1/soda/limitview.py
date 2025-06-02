from ast import Try
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import random

import os
import psutil

import time 
import datetime

#def ZeigeLimitFormular(request, limit):
def ZeigeLimitFormular(request):
   try:   
      ctx = {
            'Fehler': "",
            'limit': 200,
      }
      template1 = loader.get_template('limit.html')
      return HttpResponse(template1.render(ctx, request))

   except Exception as e:
      ctxErr = {
         'Fehler': e,
      }
      template2 = loader.get_template('limit.html')
      return HttpResponse(template2.render(ctxErr, request))
