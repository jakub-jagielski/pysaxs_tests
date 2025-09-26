# PRINCIPIA - Gra Planszowa w Pythonie

## Opis
Kompletna implementacja gry planszowej "Principia" w języku Python z interfejsem graficznym tkinter. Gra symuluje rywalizację instytutów naukowych w walce o prestiż i przełomowe odkrycia.

## Wymagania
- Python 3.7+
- Standardowe biblioteki Python (tkinter, csv, random, math)
- Pliki CSV z danymi gry (opcjonalne - gra stworzy przykładowe dane)

## Jak uruchomić

### Sposób 1: Z pełnymi danymi
```bash
python principia_full_game.py
```

### Sposób 2: Podstawowa wersja
```bash
python principia_game.py
```

### Sposób 3: Test systemu heksagonalnego
```bash
python hex_research_system.py
```

## Instrukcja gry

### 1. Setup gry
1. Uruchom grę
2. Kliknij "Nowa Gra"
3. Gra automatycznie utworzy 3 graczy z różnymi instytutami
4. Każdy gracz otrzymuje startowe zasoby zgodnie ze swoim instytutem

### 2. Struktura rundy
Każda runda składa się z 3 faz:

#### Faza Grantów
- Gracze mogą wybrać dostępne granty
- Każdy gracz może wziąć maksymalnie 1 grant na rundę
- Granty mają różne wymagania i cele

#### Faza Akcji
- Gracze na zmianę wykonują akcje
- 5 typów kart akcji: PROWADŹ BADANIA, ZATRUDNIJ, PUBLIKUJ, FINANSUJ, ZARZĄDZAJ
- Każda karta ma akcję podstawową (darmową) i opcjonalne akcje dodatkowe

#### Faza Porządkowa
- Wypłata pensji naukowcom
- Sprawdzenie celów grantów
- Odświeżenie rynków
- Przygotowanie następnej rundy

### 3. Główne mechaniki

#### System Badań Heksagonalnych
- Każde badanie ma unikalną mapę heksagonalną
- Gracze układają swoje heksy tworząc ścieżkę od START do END
- Heksy bonusowe dają dodatkowe nagrody
- Ukończenie badania daje punkty prestiżu i badań

#### Zarządzanie Zespołem
- Doktoranci: 1 heks, bez pensji
- Doktorzy: 2 heksy, 2K pensji
- Profesorowie: 3 heksy, 3K pensji
- Więcej niż 3 naukowców = kara przeciążenia (+1K pensji każdy)

#### System Publikacji
- Publikuj artykuły w czasopismach
- Koszt: Punkty Badań (PB)
- Nagroda: Punkty Prestiżu (PZ)
- Wyższy Impact Factor = więcej PZ

#### System Grantów
- Każdy grant ma wymagania, cele i nagrody
- Punkty aktywności: Zatrudnienie (2p), Publikacja (3p), Ukończenie badania (4p)
- Spełnienie celu grantu daje pieniądze

### 4. Interfejs użytkownika

#### Panel Graczy (lewa strona)
- Stan zasobów każdego gracza
- Zespół naukowców
- Aktywne i ukończone badania
- Aktualny grant

#### Główny panel (środek)
**Zakładka "Główna gra":**
- Informacje o bieżącej fazie
- Dostępne akcje

**Zakładka "Badania":**
- Lista dostępnych badań
- Mapa heksagonalna wybranego badania
- Przyciski do rozpoczęcia i prowadzenia badań

**Zakładka "Rynki":**
- Dostępni naukowcy do zatrudnienia
- Czasopisma do publikacji
- Dostępne granty

#### Panel Kontroli (prawa strona)
- Przyciski sterowania grą
- Szybkie akcje (testowe)
- Log wydarzeń

### 5. Jak grać

1. **Rozpocznij grę** - Kliknij "Nowa Gra"

2. **Faza Grantów** - Idź do zakładki "Rynki", wybierz grant i kliknij "Weź grant"

3. **Faza Akcji** - Używaj różnych akcji:
   - **Zatrudnianie:** Zakładka "Rynki" → wybierz naukowca → "Zatrudnij"
   - **Badania:** Zakładka "Badania" → wybierz badanie → "Rozpocznij badanie" → klikaj na mapie heksagonalnej
   - **Publikacje:** Zakładka "Rynki" → wybierz czasopismo → "Publikuj"

4. **Prowadzenie badań:**
   - Rozpocznij badanie (1 PA)
   - Klikaj na heksy aby układać ścieżkę od START do END
   - Pierwszy heks MUSI być na START
   - Kolejne heksy muszą przylegać do już położonych
   - Osiągnij END aby ukończyć badanie

5. **Następna faza** - Kliknij "Następna faza" gdy skończysz akcje

### 6. Zasoby i punkty

- **Kredyty (K):** Waluta gry, pensje, koszty
- **Punkty Prestiżu (PZ):** Główny sposób wygranej
- **Punkty Badań (PB):** Koszt publikacji
- **Reputacja:** Wpływa na dostęp do czasopism
- **Punkty Aktywności:** Cel wielu grantów

### 7. Cel gry
Zdobądź jak najwięcej Punktów Prestiżu (PZ) poprzez:
- Ukończanie badań
- Publikowanie artykułów
- Realizację grantów
- Tworzenie konsorcjów (w pełnej wersji)

## Struktura plików

- `principia_full_game.py` - Główna gra z pełnym interfejsem
- `hex_research_system.py` - System heksagonalnych badań
- `principia_game.py` - Podstawowa wersja gry
- `karty_*.csv` - Dane gry (opcjonalne)

## Funkcje testowe

W panelu kontroli znajdują się przyciski testowe:
- "Dodaj 5K kredytów" - Szybko dodaj pieniądze
- "Dodaj 3 PZ" - Dodaj punkty prestiżu
- "Zatrudnij naukowca" - Losowy naukowiec

## Znane ograniczenia

1. Gra nie sprawdza wszystkich wymagań grantów
2. Niektóre bonusy instytutów nie są w pełni zaimplementowane
3. Brak systemu konsorcjów (Wielkich Projektów)
4. Brak kart kryzysów i scenariuszy
5. Uproszczony system końca gry

## Rozwój

Gra jest w pełni funkcjonalna do testowania podstawowych mechanik. Można łatwo rozszerzyć o:
- Pełny system konsorcjów
- Karty kryzysów
- Więcej rodzajów akcji
- Warunki końca gry
- Zapisywanie/wczytywanie gier

## Troubleshooting

**Problem: Gra nie wczytuje danych z CSV**
- Rozwiązanie: Gra automatycznie stworzy przykładowe dane

**Problem: Nie można kliknąć na mapę heksagonalną**
- Rozwiązanie: Najpierw rozpocznij badanie przyciskiem "Rozpocznij badanie"

**Problem: Nie można zatrudnić naukowca**
- Rozwiązanie: Sprawdź czy masz wystarczająco kredytów (koszt = 2× pensja)

**Problem: Nie można opublikować**
- Rozwiązanie: Sprawdź czy masz wystarczająco Punktów Badań (PB)