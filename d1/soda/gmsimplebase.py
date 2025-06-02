import os
import sys
import base64

import time
import datetime
import suntime  #pip install suntime
import pytz     #pip install pytz

import json

import logging
#from self.logger.handlers import RotatingFileHandler


import socket
import subprocess



###### CSimpleBaseApp {   ##############################################################################

class CSimpleBaseApp:

   ###### __init__(self) ##############################################################################
   def __init__(self):
      self.tNow = datetime.datetime.now()
      self.sNow = self.tNow.strftime("%Y-%m-%d-%H-%M")
      self.tJetztStunde = datetime.datetime( self.tNow.year, self.tNow.month, self.tNow.day, self.tNow.hour, 0)

   ###### def vInit(self, sPrjName, sAppName) ##############################################################################
   def vInit(self, sPrjName, sAppName):

      self.sPrjApp = f'{sPrjName}/{sAppName}'

      # sLogDir = './log'
      # if not os.path.exists(sLogDir):
      #    os.mkdir(sLogDir)
      
      # self.logger.basicConfig(encoding='utf-8', level=self.logger.INFO, # absteigend: DEBUG, INFO, WARNING,ERROR, CRITICAL
      #                     # DEBUG führt dazu, dass der HTTP-Request samt Passwörtern und APIKeys geloggt wird!
      #                     style='{', datefmt='%Y-%m-%d %H:%M:%S', format='{asctime} {levelname} {filename}:{lineno}: {message}',
      #                     handlers=[RotatingFileHandler(f'{sLogDir}/{sPrjName}.txt', maxBytes=100000, backupCount=20)],)
      self.logger = logging.getLogger(__name__)


      sStart = f'Programmstart {self.sPrjApp} um {self.sNow}'
      self.logger.info(sStart)
      print( sStart)

      self.sHostName = "unknown"
      try:
         self.sHostName =  socket.gethostname()
      except Exception as e:
          self.logger.error(f'Fehler bei socket.gethostname(): {e}')
          self.sHostName = "unknown"
      
      if self.sHostName == 'unknown':
         self.logger.error(f'Fehler: Hostname konnte nicht ermittelt werden')
         quit()      
      else:
         self.logger.info(f'Hostname: {self.sHostName}')

      


###### __Record2Log(self, eTyp, eLadeart, sText) ##############################################################################
   def __Record2Log(self, eTyp, sText):
   # Logeintrag in die Datenbank schreiben, bei Fehler auch in die Log-Datei
      s250 = sText[:250].replace('"', '') # t_prognose_log.sText ist aktuell 250 Zeichen lang und könnte " enthalten, die beim insert stören
      print(s250)
      try:
         if eTyp == "info":
            self.logger.info(sText)
         else:
            self.logger.error(sText)
         print(f'Logeintrag: {eTyp}: {sText}')

      except Exception as e:
         sErr = f'Fehler in __Record2Log(): {e}'
         self.vScriptAbbruch(sErr)


   ###### Info2Log(self, sText) ##############################################################################
   def Info2Log(self, sText):
      self.__Record2Log( "info", sText)


   ###### Error2Log(self, sText) ##############################################################################
   def Error2Log(self, sText):
      self.__Record2Log( "error", sText)

  ###### vEndeNormal(self) ##############################################################################
   def vEndeNormal(self, sEnde):
   #Script beenden und aufräumen
      self.Info2Log( f'Programmende {self.sPrjApp}: {sEnde}')
      quit()


   ###### vScriptAbbruch(self) ##############################################################################
   def vScriptAbbruch(self, sGrund):
   #Script beenden und aufräumen
      self.Error2Log(f'Programmabbruch wegen: {sGrund}')
      quit()


###### CSimpleBaseApp }   ##############################################################################
