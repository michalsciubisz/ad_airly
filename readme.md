## Airly

Projekt zbierający i prezentujący dane pobrane z platformy [Airly](https://airly.org/map/pl/#50.057224,19.933157,i103904).

Do połączenia do bazy danych konieczne jest wykorzystanie VPNa lub korzystania z sieci AGH.

### Wykorzystane technologie

Flask -> backend + SQLAlchemy </br>
urllib.request -> zapytania poprzez API </br>
BackgroundScheduler -> do realizacji zapytań co określony czas </br>
sqlalchemy.orm -> do tworzenia sesji wysyłania danych do bazy </br>
Dash -> frontend, utworzenie dashboardów

```
pip install -r requirements.txt
```

### Baza danych

Używamy bazy MySQL dostępnej z AGH: </br>

[Baza](https://mysql.agh.edu.pl/phpMyAdmin/index.php) </br>

Login:

```
michals1
```

Hasło:

```
ZDg8L4NMGhAVDkGV
```

### Uruchomienie aplikacji

W celu użytkowania aplikacji konieczne jest uruchomienie dwóch plików, początkowo nalezy uruchomić plik *database.py*

```
python database.py
```

Następnie należy uruchomić plik odpowiedzialny za dashboardy *switch.py*

```
python switch.py
```

### Linki

[Mapa](https://airly.org/map/pl/) </br>
[Dokumentacja](https://developer.airly.org/en/docs#introduction) </br>
[Requesty](https://developer.airly.org/en/api) </br>

