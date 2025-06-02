# Aufruf der HTML-Seite für die Eingabe eines Limits: http://nnn.nnn.nnn.nnn/soda/inverterlimits
# Aufruf: SetzeHoymilesLimits( 400)
# Script für das Einstellen der Limits der Hoymiles-Wechselrichter per OpenDTU-Funkeinheit
# Script wird SVN-verwaltet im Projekt openDTU
# Script wird ausgeführt im Django-Projekt d1/soda über \\nnn.nnn.nnn.nnn\SambaWd2Tb\script\django\d1\soda\sethoylimit.py
# Vorlage war opendtu.py

# Weitere Voraussetzungen für die Ausführung unter django:
# per ssh mit Solarraspi verbinden
#  source  virtenv2/bin/activate
#  u.U. müssen einige Module nachinstalliert werden, z.B.suntime und pytz
#  cd /mnt/wd2tb/script/django/d1
# u.a. alle python.Scripte prüfen:
#  python manage.py migrate

#!/usr/bin/env python3

import logging
import requests, time, sys

from time import sleep

from requests.auth import HTTPBasicAuth

import datetime
import json

import base64

import socket
import subprocess

from soda.gmsimplebase import CSimpleBaseApp


# Einstellungen: 
sn_hoy20241gh = "nnnnnnnnnnnn" # Seriennummer des Hoymiles Wechselrichters 
sn_hoy20251sp = "nnnnnnnnnnnn" # Seriennummer des Hoymiles Wechselrichters

dtu_nutzer = 'aaaaaaaa' # OpenDTU Nutzername
dtu_passwort = '********' # OpenDTU Passwort


###### CInverterDaten ##############################################################################
###### Container für die Daten eines Wechselrichters ###############################################
class CInverterDaten:
   def __init__(self, sInvSn):
      self.sName = '?'
      self.sSn = sInvSn
      self.altes_limit = 0


###### COpenDtuLimitOnly ##############################################################################
class COpenDtuLimitOnly (CSimpleBaseApp):

   ###### __init__(self) ##############################################################################
   def __init__(self):
       super().__init__()
       self.vInit('opendtu', 'opendtuhoylimit.py')

      
   ###### vInit(self, sPrjName, sAppName) ##############################################################################
   def vInit(self, sPrjName, sAppName):
      
      super().vInit(sPrjName, sAppName)

      try:
         self.sDtuIp =  ""

         self.nSendeIntervall_Abfrage =  0
         self.nSendeIntervall_Normal =  0

         self.nSendeDbm = 0  #Schleife läuft von 5 bis 20

         # if self.sHostName == 'solarraspi':
         #    self.sDateipfad = self.Settings['Datei']['Pfad_raspi'] 
         # elif self.sHostName == 'leno2018':
         #    self.sDateipfad = self.Settings['Datei']['Pfad_leno'] 

         self.nLimit = 0
         self.aInv = [CInverterDaten(sn_hoy20241gh), CInverterDaten(sn_hoy20251sp)]

      except Exception as e:
         sErr = f'Ausnahme in COpenDtuLimitOnly.vInit: {e}'
         self.vScriptAbbruch(sErr)


   ###### def bIstOpenDtuErreichbar(self) ##############################################################################
   def bIstOpenDtuErreichbar(self):
      if self.sHostName == 'solarraspi':
         command = ['ping', '-c', '1', self.sDtuIp]  # Für Raspbian
     
      elif self.sHostName == 'leno2018':
         command = ['ping', '-n', '1', self.sDtuIp]  # Für Windows

      try:
         output = subprocess.check_output(command, stderr=subprocess.STDOUT) #fktnicht: universal_newlines=True)
         sOutput = output.decode('utf-8', errors='replace') # ohne errors='replace' gibt es eine Ausnahme

         sLower = sOutput.lower()
         if "zielhost nicht erreichbar" in sLower or "destination host unreachable" in sLower:
            return False  # Gerät ist nicht erreichbar
         else:
            return True  # Gerät ist erreichbar

      except subprocess.CalledProcessError as e:
         self.Error2Log(f'subprocess.CalledProcessError-Ausnahme in bIstOpenDtuErreichbar: ret: {e.returncode}: output: {e.output}'  )
         return False  # Gerät ist nicht erreichbar

   ###### HoleHoymilesNamen(self) ##############################################################################
   def HoleHoymilesNamen(self):
      try:
         # Nimmt Daten von der openDTU Rest-API und übersetzt sie in ein json-Format
         # liefert seit März 2024 leider nur noch rudimentäre Daten:
         # r = requests.get(url = f'http://{self.sDtuIp}/api/livedata/status/inverters' ).json()
         
         sRet = ''
         sRetErr = 'notreachable'
         
         for inv in self.aInv:
      
            r1 = requests.get(url = f'http://{self.sDtuIp}/api/livedata/status?inv={inv.sSn}' ).json()
            # sPretty1 = json.dumps( r1, sort_keys=True, indent=2)
            # self.logger.info(sPretty1)

            if len(r1['inverters']) == 0:
               return sRetErr  #gar keinen Wechselrichter gefunden
                      
            inv.reachable   = r1['inverters'][0]['reachable'] # Ist erreichbar?
            if inv.reachable == False:
               self.Error2Log( f'Wechselrichter {inv.sSn} ist nicht erreichbar')
               sRet = sRetErr
            else:
               inv.sName = r1['inverters'][0]['name'] 

         return sRet

      except Exception as e:
         self.Error2Log( f'Ausnahme in HoleHoymilesNamen(): {e}')
         return sRetErr

   ###### SetzeSendeleistung(self, nDbm, nInterval) ##############################################################################
   def SetzeSendeleistung(self, nDbm, nInterval):
      try:
         print(f'Versuch mit {nDbm} dBm')

         # In den Parametern ist viel Dynamik drin. Deshalb immer erst alle Paramter holen
         # und ggf unten ergänzen. post(api/dtu/config) ist nicht sehr tolerant, was fehlende Parameter angeht!
         ret = requests.get(
                  url = f'http://{self.sDtuIp}/api/dtu/config',
                  auth = HTTPBasicAuth(dtu_nutzer, dtu_passwort),
                  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
         )
         jData = ret.json()
         #sPretty = json.dumps( jData, sort_keys=True, indent=2)
         #self.logger.info(sPretty)


         sendeleistung = int(jData["cmt_palevel"])
         interval = int(jData["pollinterval"])
         if sendeleistung == int(nDbm and nInterval == interval):
            return True
         
         sendeleistung = f'{jData["cmt_palevel"]} dBm'
         sendefrequenz = f'{round(jData["cmt_frequency"] /1000)} Mhz'
         d_sendefrequenz = round(jData["cmt_frequency"] /1000)
         
         serialOpenDtu = jData["serial"] # Achtung! Das ist die Seriennummer der OpenDTU-Unit, diese muss bei post(api/dtu/config) angegeben werden!

         # Abfrageintervall und Sendeleistung setzen
         ret = requests.post(
                  url = f'http://{self.sDtuIp}/api/dtu/config',
                  data = f'data={{"serial":"{serialOpenDtu}", "pollinterval":{nInterval},\
                  "nrf_enabled": "true", "nrf_palevel":0,\
                  "cmt_country": 0, "cmt_chan_width": 250000,\
                  "cmt_enabled": "true", "cmt_palevel":{nDbm},"cmt_frequency": 865000000}}',
                  auth = HTTPBasicAuth(dtu_nutzer, dtu_passwort),
                  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            ).json()
         

         if ret["type"] == 'success':
            self.Info2Log( f'Sendeleistung {nDbm} und Intervall {nInterval} gesetzt')         
            return True
         else:
            self.Error2Log( f'Fehler bei Setzen Sendeleistung {nDbm} und Intervall {nInterval} ')         
            return False
         
      except Exception as e:
         print(f'Ausn{e}')
         self.Error2Log(f'Fehler beim Setzen der Sendeleistung ({nDbm} dBm): {e}')
         return False

            


   ###### SetzeLimit(self) ##############################################################################
   def SetzeLimit(self):
      try:

         # Abfrage des aktuellen Limits:
         #  http://nnn.nnn.nnn.nnn/api/limit/status
         #  Antwort: {"nnnnnnnnnnn":{"limit_relative":40,"max_power":2000,"limit_set_status":"Ok"}}
         #                |____das ist die Seriennummer der OpenDTU-Unit, nicht des Wechselrichters

         # Limit für den Wechselrichter setzen
         #  https://github.com/tbnobody/OpenDTU/discussions/742
         # limit_type = 0 AbsoluteNonPersistent
         # limit_type = 1 RelativeNonPersistent
         # limit_type = 256 AbsolutePersistent
         # limit_type = 257 RelativePersistent

         bFehler = False
         for inv in self.aInv:
            if inv.sName == '?':
               self.Error2Log( f'Limit {self.nLimit} setzen für {inv.sSn}/{inv.sName} nicht möglich')         
               bFehler = True
               continue;
            if inv.altes_limit == self.nLimit:
               continue;

            ret = requests.post(
                  url = f'http://{self.sDtuIp}/api/limit/config',
                  data = f'data={{"serial":"{inv.sSn}", "limit_type":256, "limit_value":{self.nLimit}}}',
                  auth = HTTPBasicAuth(dtu_nutzer, dtu_passwort),
                  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            ).json()
         
            if ret["type"] != 'success':
               self.Error2Log(f'Fehler beim Setzen des Limits für {inv.sName}: code: {ret["code"]}, message: {ret["message"]}')
               bFehler = True
               continue;
               
            self.Info2Log( f'Limit {self.nLimit} für {inv.sName} gesetzt')         

         return not bFehler


      except Exception as e:
        self.vScriptAbbruch(f'Ausnahme beim Setzen des Limits({self.nLimit}): {e}')
        return False



###### COpenDtuLimitOnly } ##############################################################################

def SetzeHoymilesLimits( iLimit):
   try:
      
      odl = COpenDtuLimitOnly() 
   

      odl.sDtuIp =  "nnn.nnn.nnn.nnn"
      odl.nSendeIntervall_Abfrage =  3
      odl.nSendeIntervall_Normal =  30
      odl.nSendeDbm = 0  #Schleife läuft von 5 bis 20
      odl.nLimit = iLimit

      bErreichbar = False
      for v in range (0,10,1):
         if odl.bIstOpenDtuErreichbar():
            bErreichbar = True
            break
         time.sleep(3.0)
      
      if not bErreichbar:     
         sErr = f"Das Gerät mit der IP-Adresse {odl.sDtuIp} ist im Netzwerk nicht verfügbar."   
         odl.vScriptAbbruch(sErr)


      bErfolg = False
      for odl.nSendeDbm in range(2,20,1): # Sendeleistung steigern...im Sommer mit viel Blattwerk kann der Wechselrichter nur mit 16dBm erreicht werden!

         if not odl.SetzeSendeleistung( odl.nSendeDbm, odl.nSendeIntervall_Abfrage): # auch kurzes Abfrageintervall einstellen
            break

         if odl.HoleHoymilesNamen() == 'notreachable':      # Namen auslesen 
            time.sleep(5.0)
            if odl.HoleHoymilesNamen() == 'notreachable':      # Zweiter Versuch
               time.sleep(5.0)
            continue

         if not odl.SetzeLimit():         # Vorgeschriebenes Limit kontrollieren und ggf einstellen
            time.sleep(5.0)
            if not odl.SetzeLimit():         # Zweiter Versuch
               time.sleep(5.0)
               continue

         bErfolg = True
         break

      odl.SetzeSendeleistung( odl.nSendeDbm, odl.nSendeIntervall_Normal) # normales Abfrageintervall einstellen

      if bErfolg: 
         rv = "okok"
         sOut = f'Programmende {odl.sPrjApp}: Limit {iLimit} setzen und Abfragen erfolgreich mit {odl.nSendeDbm} dbm.'
         odl.Info2Log( sOut)
      else:
         rv = "err"
         sOut = f'Programmende {odl.sPrjApp}: Limit {iLimit} setzen und Abfragen nicht oder nur teilweise möglich.'
         odl.Error2Log(sOut)

      jrv = {
         "rv": rv,
         "text": sOut,
      }      
      return jrv
   
   except Exception as e:
       jrv = {
          "rv": "exc",
          "text": f'Ausnahme in SetzeHoymilesLimits(Limit={iLimit}): {e}',
       }      
       return jrv


#SetzeHoymilesLimits( 777)
