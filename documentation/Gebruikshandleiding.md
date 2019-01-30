# Handleiding Pannenkoekenprinter 2.0
Niek Janssen: **2018-09-27**

Update: Frank Gerlings **2019-01-30**

## Benodigdheden
### Standaard bij de printer
  - Printer
  - Kookplaatstand
  - Kookplaat
  - Router
  - 2 LAN-kabels
  - Stekkerdoos/-dozen voor minimaal 6 stekkers
  - Stroomkabels voor de printer
  - Zeer fijne zeef
  - Garde
  - Spateltje
  - Weegschaal
  - Maatbeker
### Mogelijk bijkopen
  - Koopmans Pannenkoekenbeslag Compleet (hoeft alleen water bij), 1 pak per 2-3
    uur aaneensluitend demo
  - Servetten om pannenkoeken op te dienen
  - Poedersuiker/stroop
  - Keukenpapier 
  - Olie/boter
### Sowieso zelf meenemen
  - Laptop met SSH
  - 3 beslagkommen
  - Prullenbak
  - Schoonmaakspullen


## Printer klaarzetten
  - Zet de printer ergens met voldoende ruimte
  - Zet de kookplaatstand voor de printer met de kookplaat erin. Het goed
    positioneren van de kookplaat kan een beetje lastig zijn, maar het past
    precies en het is belangrijk dat hij goed staat
  - Verbind de printer en router met een LAN-kabel. De laptop kun je met een 
  LAN-kabel verbinden aan de router, maar je kan ook op het wifi netwerk gaan 
  (SSID: NETGEAR63, password: ancientpond182)
  - Zorg dat alle componenenten stroom hebben:
    - De pi
    - De pi motor hat (zit op de pi)
    - Het relais (via de powerbrick die eraan hangt)
    - De kookplaat
    - De router
    - De besturingslaptop
  - Maak een SSH-verbinding naar de Raspberry Pi
    - Hij staat standaard op poort `192.168.1.2:22`. Mocht dit niet het geval zijn, 
    verbind dan via je browser met de router op `http://192.168.1.1` en log in met 
    (user: user, password: password)
    - Log in op de pi met (user: pi, password: raspberry)
  - Zorg dat je de hygienehandleiding (zie hieronder) doorleest voordat je gaat
    printen, zeker op open dagen
  - Maak beslag, zoals hieronder aangegeven en hang/tape de slang in de
    beslagkom. 

## Hygienehandleiding
  - Zorg dat je de slang voordat je gaat printen van binnen en van buiten
    schoonmaakt. De slang van binnen schoonmaken doe je door er 5 minuten lang warm 
    water doorheen te pompen. Draai het klemmetje hiervoor volledig open. Dit kan 
    via de TUI, zoals later uitgelegd.
  - Spoel na afloop de slang eerst 10 minuten met warm water MET dreft,
    vervolgen 10 minuten ZONDER dreft. Zorg ook dat de buitenkant van de slang
    weer schoon is. 

## Het beslag
  - Gebruik Koopmans Pannenkoekenmix Compleet. Andere mixen zal misschien melk
    bij moeten, maar dat kan i.v.m. andere viscositeit problemen opleveren. 
  - Mix 400 gram beslag met 750 mililiter water. Zorg dat je de weegschaal en de
    maatbeker gebruikt om dit enigszins precies te doen.  Roer het beslag goed
    met een garde totdat bijna alle klontjes verdwenen zijn. Doe dit niet in de
    beslagkom waaruit je gaat printen, maar in de andere. 
  - Giet het beslag nu door de zeef in de beslagkom waar je uit gaat printen. 

## Printen
  - Ga naar de map `/home/pi/Desktop/Pannenkoekenprinter/`. `runme.py` runt de 
  printer. Het is belangrijk dat je in de map zit, omdat je anders geen 
  afbeeldingen kan vinden. Makkelijker: je kan vanaf iedere directory het
  commando `pancake` uitvoeren. Beiden manieren openen een TUI die je de keuze geeft 
  uit verschillende operaties. Iedere operatie kan vroegtijdig afgebroken worden 
  met `ctrl + c`. Na iedere operatie zal de printkop zich aan de kant zetten. 
  De operaties zijn:
    - Een maximale range tekenen. Dit kun je gebruiken om te kijken of je de 
    pan goed hebt staan.
    - De slang door te spoelen. Dit staat standaard op 10 minuten, maar valt te 
    onderbreken met `ctrl + c`.
    - Een lijst te geven met alle printbare afbeeldingen. Deze zijn allemaal 
    uitgetest en worden goed geparseerd door het algoritme
    - Een afbeelding te printen, gegeven zijn naam. Het is soms handig plaatjes 
    eerder af te breken omdat het printen anders te lang duurt. Het algoritme 
    neigt nog wel eens te veel aandacht aan details te besteden.
