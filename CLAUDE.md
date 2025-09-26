# CLAUDE.md - Instrukcje Rozwoju Gry Principia

## 🎯 Główna Zasada: GLOBALNA SPÓJNOŚĆ

**NAJWAŻNIEJSZE:** Przy każdej zmianie w grze Principia musisz myśleć GLOBALNIE. Żadna mechanika nie może pojawić się znikąd - wszystko musi być spójne, przemyślane i mieć odpowiedni ciąg logiczny.

## 📋 Obowiązkowa Lista Kontrolna Przed Każdą Zmianą

### ✅ 1. Analiza Wpływu Globalnego
Przed wprowadzeniem jakiejkolwiek zmiany ZAWSZE sprawdź:

- [ ] **Instrukcja główna** (`instrukcja.md`) - czy zmiana jest opisana/przewidziana
- [ ] **Wszystkie pliki CSV** - czy dane są spójne z nową mechaniką
- [ ] **Implementacja w kodzie** - czy wszystkie pliki .py uwzględniają zmianę
- [ ] **Dokumentacja techniczna** (`README_GRA.md`, `testing.md`) - czy wymaga aktualizacji
- [ ] **Gra sieciowa** (`network_game.py`) - czy synchronizacja jest zachowana

### ✅ 2. Macierz Spójności
Sprawdź spójność we WSZYSTKICH obszarach:

| Obszar | Plik/Lokalizacja | Status |
|--------|------------------|---------|
| Mechanika w instrukcji | `instrukcja.md` sekcje 6.1-7.5 | ☐ |
| Implementacja w kodzie | `principia_card_ui.py` | ☐ |
| Dane kart/zasobów | `karty_*.csv` | ☐ |
| System heksagonalny | `hex_research_system.py` | ☐ |
| Synchronizacja sieciowa | `network_game.py` | ☐ |
| Testy i dokumentacja | `testing.md`, `README_GRA.md` | ☐ |

### ✅ 3. Walidacja Logiczna
- [ ] Czy nowa mechanika ma **jasne wymagania** i **oczywiste konsekwencje**?
- [ ] Czy **balans gry** pozostaje zachowany (analiza ekonomiczna)?
- [ ] Czy mechanika **pasuje tematycznie** do świata nauki i uniwersytetów?
- [ ] Czy **złożoność** jest uzasadniona korzyściami dla rozgrywki?

## 🔄 Proces Wprowadzania Zmian

### Krok 1: Planowanie (OBOWIĄZKOWE)
```markdown
## Analiza Zmiany
**Opis:** [Co chcesz zmienić]
**Uzasadnienie:** [Dlaczego ta zmiana jest potrzebna]
**Wpływ globalny:** [Jakie inne mechaniki/pliki będą dotknięte]

## Lista Plików do Modyfikacji
- [ ] instrukcja.md (sekcja: X.Y)
- [ ] principia_card_ui.py (funkcje: abc, def)
- [ ] karty_X.csv (dodanie/modyfikacja wierszy)
- [ ] hex_research_system.py (jeśli dotyczy badań)
- [ ] network_game.py (jeśli wpływa na synchronizację)
- [ ] testing.md (aktualizacja testów)

## Harmonogram Zmian
1. Aktualizacja instrukcji/dokumentacji
2. Modyfikacja danych CSV
3. Implementacja w kodzie
4. Testy funkcjonalności
5. Aktualizacja dokumentacji technicznej
```

### Krok 2: Implementacja Uporządkowana
1. **ZAWSZE** zacznij od aktualizacji `instrukcja.md`
2. Następnie zaktualizuj odpowiednie pliki CSV
3. Dopiero potem modyfikuj kod Python
4. Na końcu zaktualizuj dokumentację techniczną

### Krok 3: Weryfikacja Post-Implementacja
- [ ] Uruchom grę i przetestuj zmianę
- [ ] Sprawdź czy wszystkie referencje są aktualne
- [ ] Upewnij się że gra sieciowa nadal działa
- [ ] Zweryfikuj czy testy przechodzą

## 📚 Hierarchia Dokumentacji (Kolejność Ważności)

### 1. Źródło Prawdy: `instrukcja.md`
- **To jest biblia gry** - wszystko musi być tutaj opisane
- Każda mechanika musi mieć swój rozdział/podrozdział
- Przykłady i przypadki brzegowe muszą być wyjaśnione

### 2. Dane Gry: `karty_*.csv`
- Wszystkie karty, zasoby, bonusy muszą być spójne z instrukcją
- Nazwy, wartości, efekty muszą być identyczne

### 3. Implementacja: `principia_card_ui.py` + pozostałe `.py`
- Kod musi DOKŁADNIE odzwierciedlać instrukcję
- Żadnych "ukrytych" mechanik nie opisanych w instrukcji

### 4. Dokumentacja Techniczna: `README_GRA.md`, `testing.md`
- Instrukcje użytkownika i testery
- Muszą być aktualne z faktycznym stanem gry

## ⚠️ Czerwone Flagi - NIGDY Nie Rób Tego

### ❌ Zakazy Bezwzględne:
- **NIE** dodawaj mechanik tylko w kodzie bez opisu w instrukcji
- **NIE** modyfikuj wartości w CSV bez sprawdzenia wpływu na balans
- **NIE** zmieniaj logiki gry bez aktualizacji dokumentacji
- **NIE** wprowadzaj "szybkich poprawek" omijających proces weryfikacji
- **NIE** kopiuj mechanik z innych gier bez dostosowania do tematu Principia

### ❌ Typowe Błędy do Unikania:
- Dodanie karty do CSV ale nie do instrukcji
- Zmiana kosztu akcji w kodzie ale nie w dokumentacji
- Modyfikacja systemu badań bez uwzględnienia wszystkich plików
- Wprowadzenie nowej waluty/zasobu bez globalnej analizy

## 🎮 Specyficzne Zasady dla Mechanik Principia

### System Badań Heksagonalnych
- Każda zmiana w `hex_research_system.py` musi być odzwierciedlona w kartach badań CSV
- Mapy heksagonalne w CSV muszą być prawidłowo parsowane przez kod
- Bonusy z heksów muszą być opisane w instrukcji

### System Akcji (5 Kart)
- Każda zmiana kosztów/efektów musi być w instrukcji (sekcja 6.2)
- Punkty Akcji (PA) muszą być spójne wszędzie
- Akcje podstawowe vs dodatkowe - jasny podział

### Zasoby i Ekonomia
- Każda zmiana cen/kosztów wymaga analizy balansu (sekcja "NOTATKI BALANSOWE")
- Średni dochód vs wydatki musi pozostać zrównoważony
- ROI (Return on Investment) dla różnych strategii

### Konsorcja i Wielkie Projekty
- Wymagania projektów w CSV muszą być możliwe do osiągnięcia
- Nagrody muszą być proporcjonalne do trudności
- System współpracy musi działać w trybie sieciowym

## 🔧 Narzędzia Weryfikacji

### Przed Każdym Commitem:
```bash
# Sprawdź czy wszystkie pliki CSV są czytelne
python -c "import csv; [print(f) for f in ['karty_badan.csv', 'karty_naukowcy.csv'] if not list(csv.DictReader(open(f, encoding='utf-8')))]"

# Uruchom podstawowy test gry
python principia_card_ui.py

# Sprawdź składnię wszystkich plików Python
python -m py_compile principia_card_ui.py hex_research_system.py network_game.py
```

### Pytania Kontrolne:
1. "Czy gracz czytający tylko instrukcję zrozumie tę zmianę?"
2. "Czy wszystkie odniesienia do tej mechaniki są aktualne?"
3. "Czy gra pozostaje zbalansowana po tej zmianie?"
4. "Czy zmiana pasuje do tematu naukowego gry?"

## 📝 Szablon Dokumentacji Zmian

### Dla Każdej Znaczącej Zmiany:
```markdown
## Zmiana: [Nazwa]
**Data:** [YYYY-MM-DD]
**Typ:** [Nowa mechanika/Poprawka/Balans/UI]

### Opis Problemu:
[Co było nie tak / czego brakowało]

### Rozwiązanie:
[Co zostało zaimplementowane]

### Pliki Zmienione:
- instrukcja.md (sekcja X.Y.Z)
- karty_X.csv (wiersze A-B)
- principia_card_ui.py (funkcje: X, Y)
- [inne pliki...]

### Wpływ na Balans:
[Analiza ekonomiczna / gameplay'owa]

### Testy Wykonane:
- [ ] Podstawowa funkcjonalność
- [ ] Spójność z instrukcją
- [ ] Balans ekonomiczny
- [ ] Gra sieciowa (jeśli dotyczy)
```

## 🎯 Wytyczne Specjalne

### Dodawanie Nowych Kart:
1. Najpierw dodaj opis do instrukcji
2. Dodaj kartę do odpowiedniego CSV
3. Upewnij się że parser w kodzie obsługuje nowe pola
4. Przetestuj interakcje z istniejącymi mechanikami

### Modyfikacja Balansu:
1. Udokumentuj obecny stan w "NOTATKI BALANSOWE"
2. Przeprowadź analizę matematyczną (Taps & Sinks)
3. Zaktualizuj instrukcję z nowymi wartościami
4. Przetestuj kilka rozgrywek

### Zmiany w UI:
1. Zachowaj spójność z `ModernTheme` w kodzie
2. Upewnij się że nowe elementy działają w trybie sieciowym
3. Zaktualizuj screenshots w dokumentacji (jeśli istnieją)

---

## 🚀 Podsumowanie

**Pamiętaj:** Principia to złożona gra z wieloma wzajemnie powiązanymi mechanikami. Każda zmiana to efekt domina - myśl globalnie, działaj lokalnie, ale zawsze weryfikuj wpływ na całość.

**Zasada Złota:** Jeśli wątpisz czy zmiana jest spójna - zatrzymaj się i przeanalizuj wszystkie powiązania. Lepiej poświęcić więcej czasu na planowanie niż naprawiać błędy spójności później.

**Cel:** Principia ma być przykładem doskonale zaprojektowanej gry, gdzie każdy element ma swoje miejsce i uzasadnienie. Twoja rola to utrzymanie tej spójności na najwyższym poziomie.