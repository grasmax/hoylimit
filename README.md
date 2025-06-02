# hoylimit - django python project to set limit for hoymiles inverters in a web browser
Das Setzen von Limits für die Inverter der HMS-Serie von Hoymiles über die Oberfläche der OpenDTU ist einigermaßen umständlich.
Das Einstellen des Limits wird durch die hier beschriebene Anwendung stark vereinfacht.
Die Anwendung setzt ein funktionierendes Django-Projekt (hier 'd1/soda') mit einem Apache-Server und eine OpenDTU-Funkeinheit mit Verbindung zu den Invertern voraus.

Erweiterung eines Django-Projekts:
urls.py
```
from . import limitview
from . import sethoylimit
...
urlpatterns = [
...
   path('inverterlimits', limitview.ZeigeLimitFormular, name='Inverter-Limits einstellen, Parameter 1 uebergibt den Limitwert'),
   path('setlimits/<str:limit>', sethoylimit.SetzeLimit, name='Limits setzen, Parameter 1 uebergibt den Limitwert'),
] 
```

limitview.py - zeigt eine HTML-Seite an

templates\limit.html - die HTML-Seite für die Einstellung eines Limit-Wertes

sethoylimit.py - SetzeLimit()-Funktion

gmsimplebase.py - CSimpleBaseApp()

opendtuhoylimit.py - COpenDtuLimitOnly (CSimpleBaseApp) definiert die Funktion SetzeHoymilesLimits( iLimit) zum Setzen der Limits

Aufruf: http://nnn.nnnn.nnn.nnn/<Name des Django-Projekts>/inverterlimits

![image](https://github.com/user-attachments/assets/c4eded52-7fec-43fb-9ab3-13426b9edbf5)

Fehler werden protokolliert ins Apache-Fehlerprotokoll: \\nnn.nnn.nnn.nnn\SambaVar\log\apache2\error.log
