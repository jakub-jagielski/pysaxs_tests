# 🌐 Gra sieciowa PRINCIPIA - Instrukcja

## 📋 Przegląd funkcji

Gra PRINCIPIA została rozszerzona o możliwość gry sieciowej, która pozwala na:
- Konfigurację liczby graczy (2-4) i ich imion
- Hostowanie gry lokalnie na swoim komputerze
- Łączenie się z grą hostowaną przez innego gracza
- Synchronizację akcji między wszystkimi graczami

## 🎮 Jak rozpocząć grę

### 1. Uruchamianie gry
```bash
python principia_card_ui.py
```

### 2. Wybór trybu gry
Po uruchomieniu kliknij przycisk **"Nowa Gra"** - otworzy się dialog konfiguracji z trzema opcjami:

#### 🏠 Gra lokalna
- Wszystkie osoby grają na jednym komputerze
- Można ustawić liczbę graczy (2-4) i ich imiona
- Gracze na zmianę wykonują swoje tury

#### 🌐 Hostuj grę sieciową
- Twój komputer będzie serwerem gry
- Inni gracze będą się łączyć z Tobą przez internet/sieć lokalną
- Możesz ustawić liczbę graczy i ich imiona
- Port domyślny: 8888

#### 🔗 Dołącz do gry
- Łączysz się z grą hostowaną przez innego gracza
- Potrzebujesz adres IP i port hosta
- Podajesz swoją nazwę gracza

## 👑 Jak hostować grę

### Krok 1: Wybierz "Hostuj grę sieciową"
1. Ustaw liczbę graczy (2-4)
2. Wprowadź imiona graczy
3. Sprawdź port (domyślnie 8888)
4. Kliknij "Rozpocznij grę"

### Krok 2: Przekaż informacje innym graczom
Po uruchomieniu serwera zobaczysz dialog z informacjami:
```
IP:Port - np. 192.168.1.100:8888
```

**Skopiuj ten adres i przekaż go innym graczom!**

### Krok 3: Czekaj na graczy
- Gracze będą się łączyć jeden po drugim
- Zobaczysz ich w logach gry
- Gdy wszyscy będą gotowi, możesz rozpocząć rozgrywkę

## 🔗 Jak dołączyć do gry

### Krok 1: Pobierz adres od hosta
Host powinien przekazać Ci adres w formacie:
```
192.168.1.100:8888
```

### Krok 2: Dołącz do gry
1. Wybierz "Dołącz do gry"
2. W polu "Adres hosta" wpisz IP (np. 192.168.1.100)
3. W polu "Port" wpisz port (np. 8888)
4. Kliknij "Rozpocznij grę"

### Krok 3: Podaj swoją nazwę
- Wprowadź swoją nazwę gracza
- Kliknij "Połącz"

### Krok 4: Oczekuj na rozpoczęcie
- Zobaczysz ekran oczekiwania
- Host rozpocznie grę gdy wszyscy będą gotowi

## 🔧 Rozwiązywanie problemów

### Nie mogę się połączyć z serwerem
1. **Sprawdź adres IP i port** - upewnij się, że są poprawne
2. **Firewall** - host musi mieć otwarty port w firewallu
3. **Sieć lokalna** - sprawdź czy jesteście w tej samej sieci
4. **Internet** - jeśli przez internet, host może potrzebować przekierowania portów w routerze

### Gra się rozłącza
1. **Stabilne połączenie** - upewnij się, że połączenie internetowe jest stabilne
2. **Host aktywny** - host musi mieć uruchomioną grę
3. **Ponowne połączenie** - spróbuj rozłączyć się i połączyć ponownie

### Błędy synchronizacji
1. **Restart serwera** - host może zrestartować serwer gry
2. **Wszyscy ponownie** - wszyscy gracze powinni się ponownie połączyć

## 📡 Informacje techniczne

### Porty i protokoły
- **Protokół**: TCP
- **Port domyślny**: 8888
- **Kodowanie**: UTF-8
- **Format wiadomości**: JSON

### Bezpieczeństwo
- Gra używa nieszyfrowanej komunikacji TCP
- Nie przesyłaj wrażliwych danych przez grę
- Ufaj tylko znanym hostom

### Wymagania sieciowe
- **Host**: otwarty port w firewallu i routerze (jeśli przez internet)
- **Klienci**: dostęp do internetu/sieci lokalnej
- **Przepustowość**: minimalna (kilka KB/s na gracza)

## 🎯 Wskazówki dla lepszego doświadczenia

### Dla hostów
1. **Stabilne połączenie** - upewnij się, że masz stałe połączenie internetowe
2. **Informuj graczy** - regularnie komunikuj się z graczami o statusie gry
3. **Backup** - zapisuj stan gry regularnie (jeśli dostępne)

### Dla graczy
1. **Cierpliwość** - oczekuj na swoją kolej
2. **Komunikacja** - używaj czatu lub komunikatora do koordynacji
3. **Stabilność** - nie zamykaj gry niepotrzebnie

## 🔄 Stan gry i synchronizacja

### Co jest synchronizowane
- Akcje graczy (karty, heksy, badania)
- Stan gry (faza, runda, aktualny gracz)
- Zasoby graczy (kredyty, punkty, reputacja)
- Stan rynków (granty, czasopisma, naukowcy)

### Co NIE jest synchronizowane (jeszcze)
- Szczegółowy stan każdej karty w ręce
- Historia wszystkich akcji
- Chat między graczami

## 📁 Pliki i backup

### Ważne pliki
- `principia_card_ui.py` - główna gra
- `network_game.py` - moduł sieciowy
- `hex_research_system.py` - system badań
- `*.csv` - dane gry (karty, naukowcy, etc.)

### Backup (zalecane)
Przed każdą grą sieciową zrób kopię zapasową plików:
```bash
cp principia_card_ui.py principia_card_ui_backup.py
cp hex_research_system.py hex_research_system_backup.py
```

---

**Miłej gry! 🎲🔬🎯**