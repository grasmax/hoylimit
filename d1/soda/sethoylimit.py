from django.db import models
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


import requests
import fileinput
import json
import datetime
import base64
import sys


import array

import os


#bringt nichts: 
#from os.path import dirname, abspath, join
#sys.path.insert(0,'soda')
# nur soda. vorangestellt hilft bei Ausführung unter django
import soda.opendtuhoylimit


def SetzeLimit(request, limit):
   try:
      jrv = soda.opendtuhoylimit.SetzeHoymilesLimits(limit)
            
      jsSoda = json.dumps(jrv)
      return HttpResponse(jsSoda, content_type='application/json')
        
   except Exception as e:
      sErr = f'Fehler in SetzeLimit: {e}'
      print( sErr)
      err = {
         "Fehler": sErr
      }      
      jsErr = json.dumps(err)
      return HttpResponse(jsErr, content_type='application/json')


