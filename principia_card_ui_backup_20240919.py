#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRINCIPIA - Ulepszona wersja z wyraźnymi kartami akcji
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Union
from enum import Enum
from hex_research_system import HexResearchMap, HexMapWidget, HexPosition

# Enums i stałe
class ActionType(Enum):
    PROWADZ_BADANIA = "PROWADŹ BADANIA"
    ZATRUDNIJ = "ZATRUDNIJ PERSONEL"
    PUBLIKUJ = "PUBLIKUJ"
    FINANSUJ = "FINANSUJ PROJEKT"
    ZARZADZAJ = "ZARZĄDZAJ"

class GamePhase(Enum):
    GRANTY = "Faza Grantów"
    AKCJE = "Faza Akcji"
    PORZADKOWA = "Faza Porządkowa"

class ScientistType(Enum):
    DOKTORANT = "Doktorant"
    DOKTOR = "Doktor"
    PROFESOR = "Profesor"

@dataclass
class ActionCard:
    """Klasa reprezentująca kartę akcji"""
    action_type: ActionType
    action_points: int
    basic_action: str
    additional_actions: List[Tuple[str, int]]  # (opis, koszt PA)
    is_used: bool = False

# Klasy danych (jak wcześniej)
@dataclass
class Scientist:
    name: str
    type: ScientistType
    field: str
    salary: int
    hex_bonus: int
    special_bonus: str
    description: str
    is_paid: bool = True

@dataclass
class ResearchCard:
    name: str
    field: str
    hex_map: str
    basic_reward: str
    bonus_reward: str
    description: str
    hexes_placed: int = 0
    max_hexes: int = 5
    is_completed: bool = False
    is_active: bool = False
    hex_research_map: Optional['HexResearchMap'] = None
    player_path: List = field(default_factory=list)  # Track player's hex path
    player_color: str = ""  # Color of the player conducting this research

    def __post_init__(self):
        """Inicjalizuje mapę heksagonalną po utworzeniu obiektu"""
        if self.hex_map and not self.hex_research_map:
            try:
                self.hex_research_map = HexResearchMap(self.hex_map)
            except Exception as e:
                print(f"Błąd parsowania mapy heksagonalnej dla {self.name}: {e}")
                # Stwórz prostą mapę fallback
                self.hex_research_map = HexResearchMap("START(0,0)->(1,0)->(2,0)->END(3,0)")

@dataclass
class JournalCard:
    name: str
    impact_factor: int
    pb_cost: int
    requirements: str
    pz_reward: int
    special_bonus: str
    description: str

@dataclass
class GrantCard:
    name: str
    requirements: str
    goal: str
    reward: str
    round_bonus: str
    description: str
    is_completed: bool = False

@dataclass
class InstituteCard:
    name: str
    starting_resources: str
    starting_reputation: int
    specialization_bonus: str
    special_ability: str
    description: str

@dataclass
class ConsortiumCard:
    """Karta konsorcjum - pozwala rozpocząć wielki projekt"""
    name: str = "Karta Konsorcjum"
    description: str = "Umożliwia rozpoczęcie Wielkiego Projektu"
    card_type: str = "KONSORCJUM"

@dataclass
class IntrigueEffect:
    """Efekt karty intryg - metadane dla automatycznego wykonania"""
    target_type: str     # "opponent", "all_opponents", "all_players", "self"
    parameter: str       # "credits", "reputation", "prestige_points", "research_points", "hex_tokens", etc.
    operation: str       # "subtract", "add", "set", "steal", "block", "copy", "reveal"
    value: int = 0       # wartość liczbowa (jeśli dotyczy)
    special_type: str = ""  # typ specjalny: "scientist", "research_hex", "publication", "grant", "consortium", "card"
    duration: int = 1    # czas trwania efektu w rundach (1 = natychmiastowy)
    condition: str = ""  # dodatkowy warunek

@dataclass
class OpportunityEffect:
    """Efekt karty okazji - metadane dla automatycznego wykonania"""
    parameter: str       # "credits", "reputation", "prestige_points", "research_points", "hex_tokens", "action_points"
    operation: str       # "add", "multiply", "set"
    value: int = 0       # wartość liczbowa
    special_type: str = ""  # typ specjalny: "scientist", "research_hex", "publication", "grant", "consortium", "card"
    duration: int = 1    # czas trwania efektu w rundach (1 = natychmiastowy)
    condition: str = ""  # dodatkowy warunek np. "Min. 1 publikacja"

@dataclass
class IntrigueCard:
    """Karta intryg - pozwala oddziaływać na przeciwników"""
    name: str
    effect: str
    target: str  # "opponent", "all", "self" (backward compatibility)
    description: str
    effects: List[IntrigueEffect] = field(default_factory=list)  # nowa struktura efektów
    card_type: str = "INTRYGA"

@dataclass
class OpportunityCard:
    """Karta okazji - daje różne bonusy"""
    name: str
    bonus_type: str  # "credits", "research_points", "reputation", "hex", "action_points"
    bonus_value: str
    requirements: str
    description: str
    card_type: str = "OKAZJA"
    effects: List[OpportunityEffect] = field(default_factory=list)  # nowa struktura efektów

@dataclass
class CrisisCard:
    """Karta kryzysu - globalny efekt natychmiastowy"""
    name: str
    effect: str
    description: str
    global_modifier: str  # Globalny modyfikator dla wszystkich graczy
    card_type: str = "KRYZYS"

@dataclass
class ScenarioCard:
    """Karta scenariusza - definiuje warunki gry"""
    name: str
    story_element: str  # Element fabularny
    global_modifiers: str  # Globalne modyfikatory rozgrywki
    max_rounds: int  # Maksymalna ilość rund
    victory_conditions: str  # Warunki zwycięstwa
    crisis_count: int  # Ile kart kryzysów dobierać
    crisis_rounds: List[int] = field(default_factory=list)  # W których rundach odkrywać kryzysy
    description: str = ""

@dataclass
class LargeProject:
    name: str
    requirements: str
    director_reward: str
    member_reward: str
    description: str
    cost_pb: int = 20  # Koszt w punktach badawczych
    cost_credits: int = 50  # Koszt w kredytach (w tysiącach)
    contributed_pb: int = 0
    contributed_credits: int = 0
    director: Optional['Player'] = None
    members: List['Player'] = field(default_factory=list)
    pending_members: List['Player'] = field(default_factory=list)  # Gracze oczekujący na akceptację
    is_completed: bool = False

@dataclass
class Player:
    name: str
    color: str
    institute: Optional[InstituteCard] = None
    credits: int = 0
    prestige_points: int = 0
    research_points: int = 0
    reputation: int = 3
    scientists: List[Scientist] = field(default_factory=list)
    active_research: List[ResearchCard] = field(default_factory=list)
    completed_research: List[ResearchCard] = field(default_factory=list)
    hand_cards: List[Union[ResearchCard, ConsortiumCard, IntrigueCard, OpportunityCard]] = field(default_factory=list)
    current_grant: Optional[GrantCard] = None
    hex_tokens: int = 20
    action_cards: List[ActionCard] = field(default_factory=list)
    publications: int = 0
    activity_points: int = 0
    has_passed: bool = False
    publication_history: List[JournalCard] = field(default_factory=list)  # Historia publikacji

class ActionCardWidget(tk.Frame):
    """Widget reprezentujący kartę akcji"""

    def __init__(self, parent, action_card: ActionCard, on_play_callback=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.action_card = action_card
        self.on_play_callback = on_play_callback

        self.setup_ui()

    def setup_ui(self):
        """Tworzy interfejs karty akcji"""
        # Ustaw styl karty
        self.configure(relief='raised', borderwidth=2, padx=10, pady=10)

        # Kolor tła zależny od statusu
        if self.action_card.is_used:
            self.configure(bg='lightgray')
        else:
            self.configure(bg='lightblue')

        # Nagłówek karty
        header_frame = tk.Frame(self, bg=self['bg'])
        header_frame.pack(fill='x', pady=(0, 5))

        title_label = tk.Label(header_frame, text=self.action_card.action_type.value,
                              font=('Arial', 12, 'bold'), bg=self['bg'])
        title_label.pack(side='top')

        points_label = tk.Label(header_frame, text=f"⚡ {self.action_card.action_points} PA",
                               font=('Arial', 10, 'bold'), fg='red', bg=self['bg'])
        points_label.pack(side='top')

        # Akcja podstawowa
        basic_frame = tk.LabelFrame(self, text="🔹 AKCJA PODSTAWOWA (DARMOWA)",
                                   font=('Arial', 9, 'bold'), bg=self['bg'])
        basic_frame.pack(fill='x', pady=(0, 5))

        basic_label = tk.Label(basic_frame, text=self.action_card.basic_action,
                              wraplength=250, justify='left', bg=self['bg'])
        basic_label.pack(padx=5, pady=2)

        # Akcje dodatkowe
        if self.action_card.additional_actions:
            additional_frame = tk.LabelFrame(self, text="⚡ AKCJE DODATKOWE",
                                           font=('Arial', 9, 'bold'), bg=self['bg'])
            additional_frame.pack(fill='x', pady=(0, 5))

            for action_desc, cost in self.action_card.additional_actions:
                action_text = f"• {action_desc} ({cost} PA)"
                action_label = tk.Label(additional_frame, text=action_text,
                                       wraplength=250, justify='left', bg=self['bg'])
                action_label.pack(anchor='w', padx=5, pady=1)

        # Przycisk zagrania karty
        if not self.action_card.is_used and self.on_play_callback:
            play_button = tk.Button(self, text="ZAGRAJ KARTĘ",
                                   command=self.play_card,
                                   font=('Arial', 10, 'bold'),
                                   bg='green', fg='white',
                                   relief='raised', borderwidth=2)
            play_button.pack(pady=(5, 0))
        elif self.action_card.is_used:
            used_label = tk.Label(self, text="KARTA UŻYTA",
                                 font=('Arial', 10, 'bold'),
                                 fg='gray', bg=self['bg'])
            used_label.pack(pady=(5, 0))

    def play_card(self):
        """Obsługuje zagranie karty"""
        if self.on_play_callback:
            self.on_play_callback(self.action_card)

    def update_display(self):
        """Aktualizuje wyświetlanie karty"""
        # Wyczyść i odbuduj UI
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()

class GameData:
    """Klasa do zarządzania danymi gry"""
    def __init__(self):
        self.scientists = []
        self.research_cards = []
        self.journals = []
        self.grants = []
        self.institutes = []
        self.large_projects = []
        self.consortium_cards = []
        self.intrigue_cards = []
        self.opportunity_cards = []
        self.main_deck = []  # Zmieszana talia wszystkich kart ręki
        self.scenarios = []
        self.crisis_cards = []
        self.active_scenario = None
        self.crisis_deck = []  # Talia kryzysów dla aktualnego scenariusza
        self.current_round = 1
        self.revealed_crises = []  # Aktywne kryzysy na planszy

    def safe_int_parse(self, value: str, default: int = 0) -> int:
        """Bezpiecznie parsuje int"""
        try:
            if isinstance(value, str):
                clean_value = ''.join(c for c in value if c.isdigit())
                return int(clean_value) if clean_value else default
            return int(value)
        except (ValueError, TypeError):
            return default

    def load_data(self):
        """Główna metoda ładowania danych gry"""
        try:
            # Próbuj załadować dane z CSV
            # (w przyszłości można tutaj dodać ładowanie z plików CSV)

            # Na razie używamy danych fallback
            self.load_fallback_data()

        except Exception as e:
            print(f"Błąd ładowania danych: {e}")
            self.load_fallback_data()

    def create_action_cards(self) -> List[ActionCard]:
        """Tworzy standardowy zestaw 5 kart akcji"""
        return [
            ActionCard(
                action_type=ActionType.PROWADZ_BADANIA,
                action_points=3,
                basic_action="Aktywuj 1 doktoranta → +1 heks na badanie",
                additional_actions=[
                    ("Aktywuj doktora → +2 heksy na badanie", 2),
                    ("Aktywuj profesora → +3 heksy na badanie", 2),
                    ("Rozpocznij nowe badanie → wyłóż kartę z ręki", 1)
                ]
            ),
            ActionCard(
                action_type=ActionType.ZATRUDNIJ,
                action_points=3,
                basic_action="Weź 1K z banku",
                additional_actions=[
                    ("Zatrudnij doktora z rynku → pensja 2K/rundę", 2),
                    ("Zatrudnij profesora z rynku → pensja 3K/rundę", 3),
                    ("Zatrudnij doktoranta → brak pensji", 1),
                    ("Kup kartę 'Projekty Badawcze' → 2 PB", 1),
                    ("Kup kartę 'Możliwości' → 1 PB", 1)
                ]
            ),
            ActionCard(
                action_type=ActionType.PUBLIKUJ,
                action_points=2,
                basic_action="Opublikuj 1 artykuł",
                additional_actions=[
                    ("Weź 3K z banku", 1),
                    ("Kup kartę 'Możliwości' → 1 PB", 1),
                    ("Konsultacje komercyjne → aktywuj profesora za 4K", 1)
                ]
            ),
            ActionCard(
                action_type=ActionType.FINANSUJ,
                action_points=3,
                basic_action="Weź 2K z banku",
                additional_actions=[
                    ("Wpłać do konsorcjum → 1 PB lub 3K na wybrany projekt", 1),
                    ("Załóż konsorcjum → zagraj kartę konsorcjum z ręki", 1),
                    ("Kredyt awaryjny → +5K, ale -1 Reputacja", 2)
                ]
            ),
            ActionCard(
                action_type=ActionType.ZARZADZAJ,
                action_points=2,
                basic_action="Weź 2K z banku",
                additional_actions=[
                    ("Odśwież rynek → czasopisma lub badania", 2),
                    ("Kampania PR → wydaj 4K za +1 Reputacja", 1),
                    ("Poprawa wizerunku → wydaj 2 PB za +1 Reputacja", 1)
                ]
            )
        ]

    def load_research_from_csv(self):
        """Wczytuje karty badań z pliku CSV"""
        self.research_cards = []
        with open('karty_badan.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                card = ResearchCard(
                    name=row['Nazwa'],
                    field=row['Dziedzina'],
                    hex_map=row['Mapa_Heksagonalna'],
                    basic_reward=row['Nagroda_Podstawowa'],
                    bonus_reward=row['Nagroda_Dodatkowa'],
                    description=row['Opis']
                )
                self.research_cards.append(card)

    def load_scientists_from_csv(self):
        """Wczytuje naukowców z pliku CSV"""
        self.scientists = []
        with open('karty_naukowcy.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                scientist_type = ScientistType.DOKTORANT if 'doktorant' in row['Typ'].lower() else \
                               ScientistType.DOKTOR if 'doktor' in row['Typ'].lower() else \
                               ScientistType.PROFESOR

                scientist = Scientist(
                    name=row['Imię i Nazwisko'],
                    type=scientist_type,
                    field=row['Dziedzina'],
                    salary=self.safe_int_parse(row['Pensja']),
                    hex_bonus=self.safe_int_parse(row['Bonus Heksów']),
                    special_bonus=row['Specjalny Bonus'],
                    description=row['Opis']
                )
                self.scientists.append(scientist)

    def load_journals_from_csv(self):
        """Wczytuje czasopisma z pliku CSV"""
        self.journals = []
        with open('karty_czasopisma.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                journal = JournalCard(
                    name=row['Nazwa'],
                    impact_factor=self.safe_int_parse(row['Impact_Factor']),
                    pb_cost=self.safe_int_parse(row['Koszt_PB']),
                    requirements=row['Wymagania'],
                    pz_reward=self.safe_int_parse(row['Nagroda_PZ']),
                    special_bonus=row['Specjalny_Bonus'],
                    description=row['Opis']
                )
                self.journals.append(journal)

    def load_grants_from_csv(self):
        """Wczytuje granty z pliku CSV"""
        self.grants = []
        with open('karty_granty.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                grant = GrantCard(
                    name=row['Nazwa'],
                    requirements=row['Wymagania'],
                    goal=row['Cel'],
                    reward=row['Nagroda'],
                    round_bonus=row['Runda_Bonus'],
                    description=row['Opis']
                )
                self.grants.append(grant)

    def load_large_projects_from_csv(self):
        """Wczytuje wielkie projekty z pliku CSV"""
        self.large_projects = []
        with open('karty_wielkie_projekty.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                project = LargeProject(
                    name=row['Nazwa'],
                    requirements=row['Wymagania'],
                    director_reward=row['Nagroda_Kierownika'],
                    member_reward=row['Nagroda_Członków'],
                    description=row['Opis']
                )
                self.large_projects.append(project)

    def load_data(self):
        """Wczytuje dane gry"""
        try:
            # Wczytaj wszystkie dane z CSV
            self.load_research_from_csv()
            print("Wczytano karty badań z CSV")

            self.load_scientists_from_csv()
            print("Wczytano naukowców z CSV")

            self.load_journals_from_csv()
            print("Wczytano czasopisma z CSV")

            self.load_grants_from_csv()
            print("Wczytano granty z CSV")

            self.load_large_projects_from_csv()
            print("Wczytano wielkie projekty z CSV")

            # Dla pozostałych danych użyj przykładowych (na razie)
            self.load_fallback_data()

        except Exception as e:
            print(f"Błąd wczytywania CSV: {e}, używam danych przykładowych")
            self.load_fallback_data()

    def load_fallback_data(self):
        # Stwórz przykładowych naukowców tylko jeśli nie zostali wczytani z CSV
        if not hasattr(self, 'scientists') or not self.scientists:
            self.scientists = [
                Scientist("Dr Jan Kowalski", ScientistType.DOKTOR, "Fizyka", 2000, 2, "+1PB przy publikacji", "Fizyk teoretyczny"),
                Scientist("Prof. Anna Nowak", ScientistType.PROFESOR, "Fizyka", 3000, 3, "+2K za badanie", "Ekspert w fizyce kwantowej"),
                Scientist("Dr Maria Wiśniewska", ScientistType.DOKTOR, "Biologia", 2000, 2, "+1PB przy publikacji", "Biolog molekularny"),
                Scientist("Prof. Piotr Zieliński", ScientistType.PROFESOR, "Chemia", 3000, 3, "+1 heks przy badaniach", "Chemik organiczny"),
                Scientist("Dr Tomasz Nowicki", ScientistType.DOKTOR, "Fizyka", 2000, 2, "Konsorcja -1 PA", "Specjalista detektorów"),
                Scientist("Prof. Ewa Kowalska", ScientistType.PROFESOR, "Biologia", 3000, 3, "+3K za badanie", "Genetyk")
            ]

        # NIE nadpisuj research_cards - zostaw te z CSV
        # Jeśli research_cards nie zostały wczytane, stwórz przykładowe
        try:
            if not hasattr(self, 'research_cards') or not self.research_cards:
                self.research_cards = [
                    ResearchCard("Bozon Higgsa", "Fizyka", "simple", "4 PB, 2 PZ", "Publikacja w Nature", "Poszukiwanie cząstki Boga", max_hexes=6),
                    ResearchCard("Algorytm Deep Learning", "Fizyka", "simple", "3 PB, 2 PZ", "+1K za publikację", "Sztuczna inteligencja", max_hexes=4),
                    ResearchCard("Synteza Organiczna", "Chemia", "simple", "2 PB, 3 PZ", "Dostęp do grantów", "Nowe związki chemiczne", max_hexes=5),
                    ResearchCard("Terapia Genowa", "Biologia", "simple", "5 PB, 4 PZ", "10K natychmiast", "Leczenie genów", max_hexes=7),
                    ResearchCard("Teoria Strun", "Fizyka", "simple", "6 PB, 3 PZ", "Dostęp do Uniwersum", "Unifikacja sił", max_hexes=8),
                    ResearchCard("Superprzewodnik", "Fizyka", "simple", "2 PB, 2 PZ", "+3K za badanie", "Zerowa rezystancja", max_hexes=4),
                    ResearchCard("Fuzja Jądrowa", "Fizyka", "simple", "5 PB, 4 PZ", "10K + energia", "Reaktor fuzji", max_hexes=6),
                    ResearchCard("Nanomateriały", "Chemia", "simple", "4 PB, 3 PZ", "Specjalne właściwości", "Rewolucyjne materiały", max_hexes=5)
                ]

                # Stwórz czasopisma tylko jeśli nie zostały wczytane z CSV
                if not hasattr(self, 'journals') or not self.journals:
                    self.journals = [
                        JournalCard("Nature", 10, 15, "Reputacja 4+", 5, "Prestiż międzynarodowy", "Najlepsze czasopismo świata"),
                        JournalCard("Science", 9, 14, "Reputacja 4+", 5, "Dostęp do konferencji", "Amerykański odpowiednik Nature"),
                        JournalCard("Physical Review", 8, 12, "1 badanie fizyczne", 4, "Współpraca fizyczna", "Czasopismo fizyczne"),
                        JournalCard("Cell", 8, 12, "1 badanie biologiczne", 4, "Przełom medyczny", "Czasopismo biologiczne"),
                        JournalCard("Journal of Chemistry", 7, 10, "1 badanie chemiczne", 4, "Innowacje chemiczne", "Czasopismo chemiczne"),
                        JournalCard("Local Journal", 3, 5, "Brak", 2, "Brak", "Lokalne czasopismo"),
                        JournalCard("Research Today", 4, 6, "Brak", 2, "Dostęp do sieci", "Ogólne czasopismo"),
                        JournalCard("Innovation Weekly", 5, 8, "1 publikacja", 3, "Networking", "Czasopismo innowacji")
                    ]

                # Stwórz granty tylko jeśli nie zostały wczytane z CSV
                if not hasattr(self, 'grants') or not self.grants:
                    self.grants = [
                        GrantCard("Grant Startup", "Brak wymagań", "10 punktów aktywności", "8K", "+2K/rundę", "Grant dla początkujących"),
                        GrantCard("Grant Badawczy", "Min. 1 doktor", "2 publikacje", "12K", "+2K/rundę", "Standardowy grant badawczy"),
                        GrantCard("Grant Fizyczny", "Spec. Fizyka", "1 badanie fizyczne", "14K", "+2K/rundę", "Grant dla fizyków"),
                        GrantCard("Grant Biologiczny", "Spec. Biologia", "1 badanie biologiczne", "14K", "+2K/rundę", "Grant dla biologów"),
                        GrantCard("Grant Chemiczny", "Spec. Chemia", "1 badanie chemiczne", "14K", "+2K/rundę", "Grant dla chemików"),
                        GrantCard("Grant Prestiżowy", "Reputacja 4+", "Publikacja w Nature", "18K", "+2K/rundę", "Elitarny grant"),
                        GrantCard("Grant Współpracy", "Brak", "Załóż konsorcjum", "15K", "+2K/rundę", "Grant na współpracę"),
                        GrantCard("Grant Kryzysowy", "Brak", "Utrzymaj pensje", "10K", "+2K/rundę", "Grant awaryjny"),
                        GrantCard("Grant Technologiczny", "Min. 1 profesor", "2 ukończone badania", "16K", "+2K/rundę", "Grant technologiczny"),
                        GrantCard("Grant Interdyscyplinarny", "2 różne dziedziny", "1 badanie z każdej dziedziny", "24K", "+2K/rundę", "Grant interdyscyplinarny")
                    ]

            # Stwórz instytuty (zawsze)
            self.institutes = [
                InstituteCard("MIT", "8K, 2 PZ", 3, "+1 heks przy fizyce", "4. naukowiec bez kary", "Czołowa uczelnia techniczna"),
                InstituteCard("CERN", "6K, 4 PZ", 3, "Konsorcja -1 PA", "Granty konsorcjów zawsze dostępne", "Największe lab fizyki"),
                InstituteCard("Max Planck", "7K, 3 PZ", 3, "+1 PB za badanie", "Limit ręki +2", "Niemiecki instytut badawczy"),
                InstituteCard("Harvard University", "10K, 1 PZ", 3, "+1 Rep za publikację IF 6+", "5. naukowiec bez kary", "Prestiżowa uczelnia"),
                InstituteCard("Cambridge", "7K, 3 PZ", 4, "+2K za badanie", "Wszystkie publikacje +1 PZ", "Brytyjska tradycja"),
                InstituteCard("Stanford", "9K, 2 PZ", 3, "+1 heks fizyka", "Karty Okazji podwójne bonusy", "Dolina Krzemowa")
            ]

            # Stwórz Wielkie Projekty tylko jeśli nie zostały wczytane z CSV
            if not hasattr(self, 'large_projects') or not self.large_projects:
                self.large_projects = [
                LargeProject(
                        name="FUZJA JĄDROWA",
                        requirements="22 PB + 20K + 2 ukończone badania fizyczne",
                        director_reward="+10 PZ + wszystkie akcje kosztują -1 PA",
                        member_reward="+4 PZ każdy",
                        description="Reaktor fuzji jądrowej - przełom energetyczny"
                    ),
                    LargeProject(
                        name="SUPERPRZEWODNIK",
                        requirements="18 PB + 25K + 2 ukończone badania fizyczne",
                        director_reward="+8 PZ + karta Superprzewodnik",
                        member_reward="+3 PZ każdy",
                        description="Materiał o zerowej rezystancji"
                    ),
                    LargeProject(
                        name="TERAPIA GENOWA",
                        requirements="15 PB + 30K + 1 profesor + 1 badanie biologiczne",
                        director_reward="+6 PZ + karta Terapia genowa",
                        member_reward="+2 PZ + 5K każdy",
                        description="Uniwersalna terapia genowa"
                    ),
                    LargeProject(
                        name="EKSPLORACJA MARSA",
                        requirements="20 PB + 35K + 3 ukończone badania",
                        director_reward="+7 PZ + dostęp do Mars Journal",
                        member_reward="+3 PZ + 1 dodatkowa karta",
                        description="Pierwsza stała baza na Marsie"
                    ),
                    LargeProject(
                        name="NANOMATERIAŁY",
                        requirements="16 PB + 15K + 2 badania chemiczne + 1 fizyczne",
                        director_reward="+5 PZ + granty chemiczne +3K",
                        member_reward="+2 PZ + ochrona przed kryzysem",
                        description="Rewolucyjne nanomateriały"
                )
            ]

            print("Dane gry załadowane pomyślnie!")

        except Exception as e:
            print(f"Błąd podczas wczytywania danych: {e}")

        # Stwórz karty konsorcjów (15 sztuk) - zawsze
        if not hasattr(self, 'consortium_cards') or not self.consortium_cards:
            self.consortium_cards = [ConsortiumCard() for _ in range(15)]

        # Stwórz karty intryg (20 sztuk) - zawsze
        if not hasattr(self, 'intrigue_cards') or not self.intrigue_cards:
            self.intrigue_cards = [
                IntrigueCard("Sabotaż", "Przeciwnik traci 1 heks z badania", "opponent", "Zakłócenie prac badawczych przeciwnika",
                    [IntrigueEffect("opponent", "research_hex", "subtract", 1, "research_hex")]),

                IntrigueCard("Szpiegostwo", "Skopiuj kartę badania przeciwnika", "opponent", "Kradzież pomysłów naukowych",
                    [IntrigueEffect("opponent", "research_card", "copy", 1, "research_card")]),

                IntrigueCard("Skandal", "Przeciwnik traci 1 punkt reputacji", "opponent", "Ujawnienie kompromitujących faktów",
                    [IntrigueEffect("opponent", "reputation", "subtract", 1)]),

                IntrigueCard("Poaching", "Przejmij naukowca od przeciwnika", "opponent", "Przeteapranie cennego pracownika",
                    [IntrigueEffect("opponent", "scientist", "steal", 1, "scientist")]),

                IntrigueCard("Blokada grantu", "Zablokuj grant przeciwnika na 1 rundę", "opponent", "Lobbowanie przeciw konkurencji",
                    [IntrigueEffect("opponent", "grant", "block", 1, "grant", 1)]),

                IntrigueCard("Przejęcie publikacji", "Przejmij pierwszeństwo publikacji", "opponent", "Szybsza publikacja tego samego tematu",
                    [IntrigueEffect("opponent", "publication", "steal", 1, "publication")]),

                IntrigueCard("Audit finansowy", "Przeciwnik traci 3K", "opponent", "Nieprzewidziane koszty kontroli",
                    [IntrigueEffect("opponent", "credits", "subtract", 3000)]),

                IntrigueCard("Atak hakera", "Przeciwnik traci 2 PB", "opponent", "Cyberatak na systemy badawcze",
                    [IntrigueEffect("opponent", "research_points", "subtract", 2)]),

                IntrigueCard("Kryzys wizerunkowy", "Wszystkich przeciwników -1 reputacja", "all", "Skandal dotyczący całej branży",
                    [IntrigueEffect("all_opponents", "reputation", "subtract", 1)]),

                IntrigueCard("Międzynarodowy bojkot", "Wszyscy tracą dostęp do konsorcjów na rundę", "all", "Polityczny kryzys naukowy",
                    [IntrigueEffect("all_players", "consortium_access", "block", 1, "consortium", 1)]),

                IntrigueCard("Kradzież IP", "Skopiuj kartę okazji przeciwnika", "opponent", "Przemysłowe szpiegostwo",
                    [IntrigueEffect("opponent", "opportunity_card", "copy", 1, "opportunity_card")]),

                IntrigueCard("Podkupstwo", "Przejmij członkostwo w konsorcjum", "opponent", "Nieczyste zagrania finansowe",
                    [IntrigueEffect("opponent", "consortium_membership", "steal", 1, "consortium")]),

                IntrigueCard("Dezinformacja", "Przeciwnik nie może publikować przez rundę", "opponent", "Fałszywe doniesienia o wynikach",
                    [IntrigueEffect("opponent", "publication_ability", "block", 1, "publication", 1)]),

                IntrigueCard("Przeciek", "Ujawnij rękę przeciwnika", "opponent", "Wyciek poufnych informacji",
                    [IntrigueEffect("opponent", "hand_cards", "reveal", 0, "cards")]),

                IntrigueCard("Awaria sprzętu", "Przeciwnik traci 2 heksy z aktywnego badania", "opponent", "Sabotaż laboratorium",
                    [IntrigueEffect("opponent", "research_hex", "subtract", 2, "research_hex")]),

                IntrigueCard("Strajk pracowników", "Przeciwnik traci akcję na rundę", "opponent", "Niepokoje społeczne w instytucie",
                    [IntrigueEffect("opponent", "action_ability", "block", 1, "action", 1)]),

                IntrigueCard("Epidemia", "Wszyscy tracą po 1 naukowcu", "all", "Choroba dziesiątkuje kadry naukowe",
                    [IntrigueEffect("all_players", "scientist", "subtract", 1, "scientist")]),

                IntrigueCard("Kryzys energetyczny", "Wszyscy tracą 2K", "all", "Rosnące koszty energii",
                    [IntrigueEffect("all_players", "credits", "subtract", 2000)]),

                IntrigueCard("Oszustwo naukowe", "Przeciwnik traci jedną publikację", "opponent", "Ujawnienie fałszowanych danych",
                    [IntrigueEffect("opponent", "publications", "subtract", 1)]),

                IntrigueCard("Afera korupcyjna", "Przeciwnik traci aktualny grant", "opponent", "Skandal finansowy w instytucie",
                    [IntrigueEffect("opponent", "current_grant", "remove", 1, "grant")])
            ]

        # Stwórz karty okazji (10 sztuk) - zawsze
        if not hasattr(self, 'opportunity_cards') or not self.opportunity_cards:
            self.opportunity_cards = [
                OpportunityCard("Niespodziana dotacja", "credits", "5K", "Brak", "Rządowe wsparcie dla nauki", "OKAZJA", [
                    OpportunityEffect("credits", "add", 5000, condition="Brak")
                ]),
                OpportunityCard("Odkrycie w laboratorium", "research_points", "3PB", "Brak", "Przypadkowe odkrycie podczas rutynowych badań", "OKAZJA", [
                    OpportunityEffect("research_points", "add", 3, condition="Brak")
                ]),
                OpportunityCard("Nagroda naukowa", "reputation", "2", "Min. 1 publikacja", "Prestiżowe wyróżnienie za osiągnięcia", "OKAZJA", [
                    OpportunityEffect("reputation", "add", 2, condition="Min. 1 publikacja")
                ]),
                OpportunityCard("Dodatkowe finansowanie", "credits", "7K", "Aktywne badanie", "Dofinansowanie trwającego projektu", "OKAZJA", [
                    OpportunityEffect("credits", "add", 7000, condition="Aktywne badanie")
                ]),
                OpportunityCard("Przełom metodologiczny", "hex_tokens", "2", "Aktywne badanie", "Nowa metoda przyspiesza badania", "OKAZJA", [
                    OpportunityEffect("hex_tokens", "add", 2, condition="Aktywne badanie")
                ]),
                OpportunityCard("Współpraca międzynarodowa", "action_points", "2", "Reputacja 3+", "Dodatkowe możliwości działania", "OKAZJA", [
                    OpportunityEffect("action_points", "add", 2, condition="Reputacja 3+")
                ]),
                OpportunityCard("Patent komercyjny", "credits", "10K", "Ukończone badanie", "Sprzedaż praw do wynalazku", "OKAZJA", [
                    OpportunityEffect("credits", "add", 10000, condition="Ukończone badanie")
                ]),
                OpportunityCard("Visiting professor", "research_points", "5PB", "Min. 1 profesor", "Wizyta wybitnego naukowca", "OKAZJA", [
                    OpportunityEffect("research_points", "add", 5, condition="Min. 1 profesor")
                ]),
                OpportunityCard("Technologiczny venture", "credits", "8K", "Badanie chemiczne lub fizyczne", "Inwestycja w start-up", "OKAZJA", [
                    OpportunityEffect("credits", "add", 8000, condition="Badanie chemiczne lub fizyczne")
                ]),
                OpportunityCard("Szczęśliwy przypadek", "research_points", "4PB", "Brak", "Nieoczekiwane odkrycie", "OKAZJA", [
                    OpportunityEffect("research_points", "add", 4, condition="Brak")
                ])
            ]

        # Stwórz scenariusze - zawsze
        if not hasattr(self, 'scenarios') or not self.scenarios:
            self.scenarios = [
                ScenarioCard(
                    name="Wyścig do Marsa",
                    story_element="Ludzkość przygotowuje się do pierwszej misji na Marsa. Konkurencja między instytutami badawczymi jest zacięta.",
                    global_modifiers="Badania fizyczne: +1 heks | Konsorcja: -1K koszt założenia",
                    max_rounds=8,
                    victory_conditions="35 PZ lub 6 ukończonych badań lub 3 Wielkie Projekty",
                    crisis_count=3,
                    crisis_rounds=[3, 5, 7],
                    description="Scenariusz skupiony na eksploracji kosmosu i technologiach fizycznych."
                ),
                ScenarioCard(
                    name="Pandemia Wirusowa",
                    story_element="Światowa pandemia zagraża ludzkości. Instytuty medyczne i biologiczne walczą o znalezienie rozwiązania.",
                    global_modifiers="Badania biologiczne: +2 heks | Publikacje medyczne: +1 PZ",
                    max_rounds=6,
                    victory_conditions="30 PZ lub 5 ukończonych badań biologicznych lub szczepionka (Wielki Projekt)",
                    crisis_count=4,
                    crisis_rounds=[2, 3, 4, 5],
                    description="Intensywny scenariusz z częstymi kryzysami i naciskiem na badania medyczne."
                ),
                ScenarioCard(
                    name="Kryzys Klimatyczny",
                    story_element="Zmiany klimatyczne przyspieszają. Świat potrzebuje przełomowych rozwiązań w chemii i inżynierii.",
                    global_modifiers="Badania chemiczne: +1 heks | Teknologie zielone: +2K za ukończenie",
                    max_rounds=10,
                    victory_conditions="40 PZ lub 8 ukończonych badań lub rozwiązanie klimatyczne (Wielki Projekt)",
                    crisis_count=2,
                    crisis_rounds=[4, 8],
                    description="Długi scenariusz z naciskiem na badania chemiczne i rozwiązania ekologiczne."
                ),
                ScenarioCard(
                    name="Rewolucja AI",
                    story_element="Sztuczna inteligencja rozwija się w zawrotnym tempie. Instytucje walczą o kontrolę nad przyszłością technologii.",
                    global_modifiers="Badania fizyczne (AI): +1 PB za ukończenie | Współpraca międzynarodowa: +1 PA",
                    max_rounds=7,
                    victory_conditions="35 PZ lub dominacja AI (4 badania fizyczne) lub superinteligencja (Wielki Projekt)",
                    crisis_count=3,
                    crisis_rounds=[2, 4, 6],
                    description="Scenariusz technologiczny z naciskiem na badania fizyczne i AI."
                )
            ]

        # Stwórz karty kryzysów - zawsze
        if not hasattr(self, 'crisis_cards') or not self.crisis_cards:
            self.crisis_cards = [
                CrisisCard("Krach Finansowy", "Wszyscy gracze tracą 50% kredytów",
                          "Globalny kryzys ekonomiczny wpływa na finansowanie nauki", "Kredyty: -50%"),
                CrisisCard("Cyberatak", "Wszyscy gracze tracą 2 PB",
                          "Hakerzy zaatakowali systemy badawcze na całym świecie", "Badania: -2 PB"),
                CrisisCard("Pandemia", "Wszyscy gracze tracą 1 naukowca (losowo)",
                          "Choroba dziesiątkuje kadry naukowe", "Personel: -1 naukowiec"),
                CrisisCard("Protest Społeczny", "Wszyscy gracze: -1 Reputacja",
                          "Społeczeństwo protestuje przeciwko niektórym badaniom", "Reputacja: -1"),
                CrisisCard("Kryzys Energetyczny", "Wszystkie akcje kosztują +1 PA",
                          "Niedobory energii spowalniają wszystkie działania", "Akcje: +1 PA"),
                CrisisCard("Regulacje Prawne", "Nowe badania kosztują +2K",
                          "Nowe przepisy zwiększają koszty rozpoczynania badań", "Badania: +2K koszt"),
                CrisisCard("Strajk Pracowników", "Pensje naukowców podwojone na 2 rundy",
                          "Naukowcy domagają się wyższych pensji", "Pensje: x2 przez 2 rundy"),
                CrisisCard("Katastrofa Naturalna", "Wszyscy gracze tracą 1 aktywne badanie",
                          "Klęska żywiołowa niszczy laboratoria", "Badania: -1 aktywne"),
                CrisisCard("Skandal Korupcyjny", "Gracz z najwyższą reputacją traci 2 punkty",
                          "Ujawniono aferę w największej instytucji", "Lider: -2 Reputacja"),
                CrisisCard("Wojna Handlowa", "Konsorcja międzynarodowe: +3K koszt dołączenia",
                          "Konflikty geopolityczne utrudniają współpracę", "Konsorcja: +3K"),
                CrisisCard("Kryzys Zaufania", "Publikacje: -1 PZ przez 2 rundy",
                          "Społeczeństwo traci zaufanie do nauki", "Publikacje: -1 PZ"),
                CrisisCard("Niedobór Materiałów", "Wszystkie zakupy kosztują +1K",
                          "Problemy z łańcuchem dostaw zwiększają koszty", "Zakupy: +1K"),
                CrisisCard("Exodus Talentów", "Każdy gracz może stracić 1 profesora (50% szans)",
                          "Najlepsi naukowcy emigrują za granicę", "Profesorowie: 50% utraty"),
                CrisisCard("Kryzys Polityczny", "Granty rządowe niedostępne przez 2 rundy",
                          "Niestabilność polityczna wstrzymuje finansowanie", "Granty: STOP na 2 rundy"),
                CrisisCard("Awaria Internetu", "Współpraca międzynarodowa niemożliwa przez rundę",
                          "Globalna awaria sieci paraliżuje komunikację", "Konsorcja: STOP na rundę")
            ]

        # Zmieszaj główną talię (badania + konsorcja + intrygi + okazje) - zawsze
        self.main_deck = (
            self.research_cards.copy() +
            self.consortium_cards.copy() +
            self.intrigue_cards.copy() +
            self.opportunity_cards.copy()
        )
        random.shuffle(self.main_deck)

class SimpleHexWidget(tk.Frame):
    """Uproszczony widget do wizualizacji postępu badań"""

    def __init__(self, parent, research: ResearchCard, **kwargs):
        super().__init__(parent, **kwargs)
        self.research = research
        self.setup_ui()

    def setup_ui(self):
        """Tworzy prosty interfejs badania"""
        # Nazwa badania
        title_label = tk.Label(self, text=self.research.name, font=('Arial', 10, 'bold'))
        title_label.pack(pady=2)

        # Pasek postępu
        progress_frame = tk.Frame(self)
        progress_frame.pack(fill='x', padx=5, pady=2)

        for i in range(self.research.max_hexes):
            color = 'lightgreen' if i < self.research.hexes_placed else 'lightgray'
            if i == 0:
                color = 'green'  # Start
            elif i == self.research.max_hexes - 1:
                color = 'red' if i < self.research.hexes_placed else 'pink'  # End

            hex_label = tk.Label(progress_frame, text='⬢', font=('Arial', 16), fg=color)
            hex_label.pack(side='left', padx=1)

        # Postęp
        progress_text = f"{self.research.hexes_placed}/{self.research.max_hexes}"
        progress_label = tk.Label(self, text=progress_text, font=('Arial', 8))
        progress_label.pack()

        # Przycisk dodania heksa
        if self.research.hexes_placed < self.research.max_hexes:
            add_btn = tk.Button(self, text="Dodaj heks",
                              command=self.add_hex, font=('Arial', 8))
            add_btn.pack(pady=2)

    def add_hex(self):
        """Dodaje heks do badania"""
        if self.research.hexes_placed < self.research.max_hexes:
            self.research.hexes_placed += 1

            if self.research.hexes_placed >= self.research.max_hexes:
                self.research.is_completed = True

            # Odśwież widok
            for widget in self.winfo_children():
                widget.destroy()
            self.setup_ui()

            # Powiadom o ukończeniu
            if self.research.is_completed:
                messagebox.showinfo("Sukces!", f"Badanie '{self.research.name}' zostało ukończone!")

class PrincipiaGame:
    """Główna klasa gry Principia"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PRINCIPIA - Gra Planszowa")
        self.root.geometry("1800x1000")

        self.game_data = GameData()
        self.players = []
        self.current_player_idx = 0
        self.current_round = 1
        self.current_phase = GamePhase.GRANTY
        self.available_grants = []
        self.available_journals = []
        self.available_scientists = []
        self.game_ended = False

        # System scenariuszy
        self.current_scenario = None
        self.active_crises = []  # Aktywne kryzysy wpływające na grę
        self.crisis_deck = []  # Talia kryzysów dla obecnego scenariusza

        # Aktualna aktywność
        self.current_action_card = None
        self.remaining_action_points = 0
        self.research_selection_mode = False
        self.selected_research_for_start = None

        # Hex placement state
        self.pending_hex_placements = 0  # Number of hexes waiting to be placed
        self.hex_placement_mode = False
        self.current_research_for_hex = None

        # Developer mode
        self.developer_mode = False

        self.setup_ui()

    def setup_ui(self):
        """Tworzy interfejs użytkownika"""
        # Główny kontener
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Panel informacji o grze
        self.info_frame = ttk.LabelFrame(main_frame, text="Informacje o grze")
        self.info_frame.pack(fill='x', pady=(0, 10))

        info_row = ttk.Frame(self.info_frame)
        info_row.pack(fill='x', padx=10, pady=5)

        self.round_label = ttk.Label(info_row, text="Runda: 1", font=('Arial', 12, 'bold'))
        self.round_label.pack(side='left')

        self.phase_label = ttk.Label(info_row, text="Faza: Grantów", font=('Arial', 12, 'bold'))
        self.phase_label.pack(side='left', padx=(20, 0))

        self.current_player_label = ttk.Label(info_row, text="Gracz: -", font=('Arial', 12, 'bold'))
        self.current_player_label.pack(side='left', padx=(20, 0))

        self.action_points_label = ttk.Label(info_row, text="PA: 0/0", font=('Arial', 12, 'bold'))
        self.action_points_label.pack(side='left', padx=(20, 0))

        # Developer mode indicator (initially hidden)
        self.dev_mode_label = ttk.Label(info_row, text="🔧 DEVELOPER MODE",
                                       font=('Arial', 12, 'bold'), foreground='red')
        self.dev_mode_label.pack(side='right', padx=(20, 0))
        self.dev_mode_label.pack_forget()  # Hide initially

        # Panel powiadomień konsorcjów (początkovo ukryty)
        self.notifications_frame = ttk.LabelFrame(main_frame, text="🔔 Powiadomienia")
        # Nie packujemy go od razu - będzie pokazywany tylko gdy są powiadomienia

        # Inicjalizacja systemu powiadomień
        if not hasattr(self, 'consortium_notifications'):
            self.consortium_notifications = []

        # Panel scenariusza i kryzysów
        scenario_row = ttk.Frame(self.info_frame)
        scenario_row.pack(fill='x', padx=10, pady=5)

        self.scenario_label = ttk.Label(scenario_row, text="Scenariusz: Brak", font=('Arial', 10))
        self.scenario_label.pack(side='left')

        # Panel aktywnych kryzysów
        self.crisis_frame = ttk.Frame(scenario_row)
        self.crisis_frame.pack(side='right', padx=(20, 0))

        self.crisis_label = ttk.Label(self.crisis_frame, text="Aktywne kryzysy: ", font=('Arial', 10, 'bold'))
        self.crisis_label.pack(side='left')

        self.active_crisis_text = ttk.Label(self.crisis_frame, text="Brak", font=('Arial', 10), foreground='red')
        self.active_crisis_text.pack(side='left')

        # Kontener główny
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)

        # Panel graczy (lewa strona)
        self.players_frame = ttk.LabelFrame(content_frame, text="Gracze")
        self.players_frame.pack(side='left', fill='y', padx=(0, 5))

        # Notebook dla głównej gry (środek)
        self.main_notebook = ttk.Notebook(content_frame)
        self.main_notebook.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Zakładka głównej gry
        self.game_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.game_tab, text="Główna gra")

        # Zakładka rynków
        self.markets_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.markets_tab, text="Rynki")

        # Zakładka Wielkich Projektów
        self.projects_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.projects_tab, text="Wielkie Projekty")

        # Zakładka Osiągnięć (ukończone badania i publikacje)
        self.achievements_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.achievements_tab, text="Osiągnięcia")

        # Zakładka Developer (initially hidden)
        self.developer_tab = ttk.Frame(self.main_notebook)
        # Tab will be added dynamically when developer mode is enabled

        # Panel badań (prawa strona)
        self.research_frame = ttk.LabelFrame(content_frame, text="Badania")
        self.research_frame.pack(side='right', fill='y')

        # Panel kontroli na dole
        self.control_frame = ttk.LabelFrame(main_frame, text="Kontrola")
        self.control_frame.pack(fill='x', pady=(10, 0))

        control_buttons = ttk.Frame(self.control_frame)
        control_buttons.pack(side='left', padx=10, pady=5)

        setup_btn = ttk.Button(control_buttons, text="Setup Gry", command=self.setup_game)
        setup_btn.pack(side='left', padx=(0, 5))

        self.next_phase_btn = ttk.Button(control_buttons, text="Następna faza",
                                        command=self.next_phase, state='disabled')
        self.next_phase_btn.pack(side='left', padx=(0, 5))

        self.pass_btn = ttk.Button(control_buttons, text="Pas", command=self.player_pass, state='disabled')
        self.pass_btn.pack(side='left', padx=(0, 5))

        self.end_action_btn = ttk.Button(control_buttons, text="Zakończ akcję",
                                        command=self.end_current_action, state='disabled')
        self.end_action_btn.pack(side='left', padx=(0, 5))

        self.next_round_btn = ttk.Button(control_buttons, text="Następna runda",
                                        command=self.advance_round, state='disabled')
        self.next_round_btn.pack(side='left', padx=(0, 5))

        # Log gry
        log_frame = ttk.LabelFrame(self.control_frame, text="Log gry")
        log_frame.pack(side='right', fill='both', expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=50, height=6)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Skonfiguruj zakładki
        self.setup_game_tab()
        self.setup_markets_tab()
        self.setup_projects_tab()
        self.setup_achievements_tab()

        # Bind keyboard shortcut for developer mode (Ctrl+Shift+D)
        self.root.bind('<Control-Shift-D>', self.toggle_developer_mode)
        self.root.focus_set()  # Ensure window can receive key events

    def setup_game_tab(self):
        """Konfiguruje zakładkę głównej gry"""
        # Zakładka głównej gry będzie zawierać karty akcji i fazy gry
        pass  # Zawartość będzie dodawana dynamicznie przez update_ui


    def setup_markets_tab(self):
        """Konfiguruje zakładkę rynków"""
        # Kontener główny
        markets_main = ttk.Frame(self.markets_tab)
        markets_main.pack(fill='both', expand=True, padx=5, pady=5)

        # Podział na kolumny
        left_markets = ttk.Frame(markets_main)
        left_markets.pack(side='left', fill='both', expand=True, padx=(0, 5))

        right_markets = ttk.Frame(markets_main)
        right_markets.pack(side='right', fill='both', expand=True)

        # Rynek naukowców
        scientists_frame = ttk.LabelFrame(left_markets, text="Rynek naukowców")
        scientists_frame.pack(fill='both', expand=True, pady=(0, 5))

        # Scrollable frame dla naukowców
        scientists_canvas = tk.Canvas(scientists_frame, height=300)
        scientists_scrollbar = ttk.Scrollbar(scientists_frame, orient="vertical", command=scientists_canvas.yview)
        self.scientists_scrollable_frame = ttk.Frame(scientists_canvas)

        self.scientists_scrollable_frame.bind(
            "<Configure>",
            lambda e: scientists_canvas.configure(scrollregion=scientists_canvas.bbox("all"))
        )

        scientists_canvas.create_window((0, 0), window=self.scientists_scrollable_frame, anchor="nw")
        scientists_canvas.configure(yscrollcommand=scientists_scrollbar.set)

        scientists_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scientists_scrollbar.pack(side="right", fill="y")

        # Rynek czasopism
        journals_frame = ttk.LabelFrame(right_markets, text="Dostępne czasopisma")
        journals_frame.pack(fill='both', expand=True, pady=(0, 5))

        # Scrollable frame dla czasopism
        journals_canvas = tk.Canvas(journals_frame, height=300)
        journals_scrollbar = ttk.Scrollbar(journals_frame, orient="vertical", command=journals_canvas.yview)
        self.journals_scrollable_frame = ttk.Frame(journals_canvas)

        self.journals_scrollable_frame.bind(
            "<Configure>",
            lambda e: journals_canvas.configure(scrollregion=journals_canvas.bbox("all"))
        )

        journals_canvas.create_window((0, 0), window=self.journals_scrollable_frame, anchor="nw")
        journals_canvas.configure(yscrollcommand=journals_scrollbar.set)

        journals_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        journals_scrollbar.pack(side="right", fill="y")

    def setup_projects_tab(self):
        """Konfiguruje zakładkę Wielkich Projektów"""
        # Wyczyść poprzednią zawartość
        for widget in self.projects_tab.winfo_children():
            widget.destroy()

        # Kontener główny z przewijaniem
        projects_canvas = tk.Canvas(self.projects_tab)
        projects_scrollbar = ttk.Scrollbar(self.projects_tab, orient="vertical", command=projects_canvas.yview)
        scrollable_projects_frame = ttk.Frame(projects_canvas)

        scrollable_projects_frame.bind(
            "<Configure>",
            lambda e: projects_canvas.configure(scrollregion=projects_canvas.bbox("all"))
        )

        projects_canvas.create_window((0, 0), window=scrollable_projects_frame, anchor="nw")
        projects_canvas.configure(yscrollcommand=projects_scrollbar.set)

        # Nagłówek
        header_frame = tk.Frame(scrollable_projects_frame, bg='darkblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text="🏛️ WIELKIE PROJEKTY NAUKOWE",
                font=('Arial', 16, 'bold'), bg='darkblue', fg='white').pack(pady=10)

        tk.Label(header_frame, text="Dostępne projekty do realizacji w konsorcjach",
                font=('Arial', 10), bg='darkblue', fg='lightgray').pack(pady=(0, 10))

        # Przyciski zarządzania konsorcjami
        management_frame = tk.Frame(header_frame, bg='darkblue')
        management_frame.pack(pady=5)

        # Przycisk zarządzania dla kierowników
        manage_btn = tk.Button(management_frame, text="👑 Zarządzaj swoimi konsorcjami",
                             command=self.show_consortium_management_panel,
                             bg='gold', font=('Arial', 10, 'bold'),
                             relief='raised', borderwidth=2)
        manage_btn.pack(pady=2)

        # Przycisk dołączania do konsorcjów (niezależny od kart akcji)
        join_btn = tk.Button(management_frame, text="🤝 Dołącz do konsorcjum",
                           command=self.show_independent_consortium_join,
                           bg='lightgreen', font=('Arial', 10, 'bold'),
                           relief='raised', borderwidth=2)
        join_btn.pack(pady=2)

        # Wyświetl wszystkie Wielkie Projekty
        for project in self.game_data.large_projects:
            project_frame = tk.Frame(scrollable_projects_frame, relief='raised', borderwidth=2, bg='lightcyan')
            project_frame.pack(fill='x', padx=10, pady=5)

            # Nagłówek projektu
            project_header = tk.Frame(project_frame, bg='steelblue')
            project_header.pack(fill='x', padx=5, pady=5)

            tk.Label(project_header, text=project.name, font=('Arial', 14, 'bold'),
                    bg='steelblue', fg='white').pack(pady=5)

            # Wymagania
            req_frame = tk.Frame(project_frame, bg='lightcyan')
            req_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(req_frame, text="📋 WYMAGANIA:", font=('Arial', 11, 'bold'),
                    bg='lightcyan').pack(anchor='w')
            tk.Label(req_frame, text=project.requirements, font=('Arial', 10),
                    bg='lightcyan', wraplength=600, justify='left').pack(anchor='w', padx=20)

            # Nagrody
            rewards_frame = tk.Frame(project_frame, bg='lightcyan')
            rewards_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(rewards_frame, text="🏆 NAGRODY:", font=('Arial', 11, 'bold'),
                    bg='lightcyan').pack(anchor='w')

            # Nagroda dyrektora
            tk.Label(rewards_frame, text=f"👑 Dyrektor: {project.director_reward}",
                    font=('Arial', 10, 'bold'), bg='lightcyan', fg='darkblue').pack(anchor='w', padx=20)

            # Nagroda członków
            tk.Label(rewards_frame, text=f"👥 Członkowie: {project.member_reward}",
                    font=('Arial', 10), bg='lightcyan', fg='darkgreen').pack(anchor='w', padx=20)

            # Opis
            if project.description:
                desc_frame = tk.Frame(project_frame, bg='lightcyan')
                desc_frame.pack(fill='x', padx=10, pady=5)

                tk.Label(desc_frame, text="📖 OPIS:", font=('Arial', 11, 'bold'),
                        bg='lightcyan').pack(anchor='w')
                tk.Label(desc_frame, text=project.description, font=('Arial', 10),
                        bg='lightcyan', wraplength=600, justify='left', fg='gray').pack(anchor='w', padx=20)

            # Status projektu
            status_frame = tk.Frame(project_frame, bg='lightcyan')
            status_frame.pack(fill='x', padx=10, pady=5)

            if project.director:
                if project.is_completed:
                    status_text = f"✅ UKOŃCZONY - 👑 Kierownik: {project.director.name}"
                    status_color = 'green'
                    bg_color = 'lightgreen'
                else:
                    status_text = f"🔨 W REALIZACJI - 👑 Kierownik: {project.director.name}"
                    status_color = 'darkblue'
                    bg_color = 'lightyellow'
            else:
                status_text = "⏳ OCZEKUJE NA KIEROWNIKA KONSORCJUM"
                status_color = 'gray'
                bg_color = 'lightgray'

            # Utwórz ramkę statusu z kolorowym tłem
            status_label_frame = tk.Frame(status_frame, bg=bg_color, relief='raised', borderwidth=2)
            status_label_frame.pack(fill='x', pady=2)

            tk.Label(status_label_frame, text=status_text, font=('Arial', 11, 'bold'),
                    bg=bg_color, fg=status_color).pack(pady=5)

            # Postęp (jeśli projekt ma dyrektora)
            if project.director and hasattr(project, 'contributed_pb'):
                progress_frame = tk.Frame(project_frame, bg='lightcyan')
                progress_frame.pack(fill='x', padx=10, pady=(0, 5))

                progress_text = f"📊 Postęp: {project.contributed_pb} PB, {project.contributed_credits//1000} K"
                tk.Label(progress_frame, text=progress_text, font=('Arial', 9),
                        bg='lightcyan', fg='darkblue').pack(anchor='w', padx=20)

                # Lista członków
                if project.members:
                    members_text = "👥 Członkowie: " + ", ".join([m.name for m in project.members])
                    tk.Label(progress_frame, text=members_text, font=('Arial', 9),
                            bg='lightcyan', fg='darkgreen').pack(anchor='w', padx=20)

                # Lista oczekujących na akceptację
                if hasattr(project, 'pending_members') and project.pending_members:
                    pending_text = "⏳ Oczekują na akceptację: " + ", ".join([m.name for m in project.pending_members])
                    tk.Label(progress_frame, text=pending_text, font=('Arial', 9),
                            bg='lightcyan', fg='orange').pack(anchor='w', padx=20)

        projects_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        projects_scrollbar.pack(side="right", fill="y")

    def setup_achievements_tab(self):
        """Konfiguruje zakładkę Osiągnięć (ukończone badania i publikacje)"""
        # Wyczyść poprzednią zawartość
        for widget in self.achievements_tab.winfo_children():
            widget.destroy()

        # Główny kontener z przewijaniem
        main_canvas = tk.Canvas(self.achievements_tab)
        main_scrollbar = ttk.Scrollbar(self.achievements_tab, orient="vertical", command=main_canvas.yview)
        scrollable_main_frame = ttk.Frame(main_canvas)

        scrollable_main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_main_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)

        # Nagłówek główny
        header_frame = tk.Frame(scrollable_main_frame, bg='darkgreen', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text="🏆 OSIĄGNIĘCIA GRACZY",
                font=('Arial', 16, 'bold'), bg='darkgreen', fg='white').pack(pady=10)

        # Panel dla każdego gracza
        if self.players:
            for i, player in enumerate(self.players):
                self.create_player_achievements_section(scrollable_main_frame, player)

        main_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        main_scrollbar.pack(side="right", fill="y")

    def create_player_achievements_section(self, parent, player):
        """Tworzy sekcję osiągnięć dla konkretnego gracza"""
        # Frame gracza
        player_frame = tk.Frame(parent, relief='raised', borderwidth=2, bg='lightyellow')
        player_frame.pack(fill='x', padx=10, pady=5)

        # Nagłówek gracza
        player_header = tk.Frame(player_frame, bg=player.color)
        player_header.pack(fill='x', padx=5, pady=5)

        tk.Label(player_header, text=f"🎓 {player.name} ({player.institute.name if player.institute else 'Brak instytutu'})",
                font=('Arial', 14, 'bold'), bg=player.color, fg='white').pack(pady=5)

        # Statystyki gracza
        stats_frame = tk.Frame(player_frame, bg='lightyellow')
        stats_frame.pack(fill='x', padx=10, pady=5)

        stats_text = f"📊 PZ: {player.prestige_points} | Badania: {len(player.completed_research)} | Publikacje: {player.publications} | Reputacja: {player.reputation}"
        tk.Label(stats_frame, text=stats_text, font=('Arial', 11, 'bold'),
                bg='lightyellow', fg='darkblue').pack(anchor='w')

        # Sekcja ukończonych badań
        if player.completed_research:
            research_frame = tk.LabelFrame(player_frame, text="🧪 Ukończone Badania", bg='lightyellow')
            research_frame.pack(fill='x', padx=10, pady=5)

            for research in player.completed_research:
                research_item = tk.Frame(research_frame, bg='lightcyan', relief='ridge', borderwidth=1)
                research_item.pack(fill='x', padx=5, pady=2)

                tk.Label(research_item, text=f"🔬 {research.name} ({research.field})",
                        font=('Arial', 10, 'bold'), bg='lightcyan').pack(anchor='w', padx=5, pady=2)

                tk.Label(research_item, text=f"Nagroda: {research.basic_reward}",
                        font=('Arial', 9), bg='lightcyan', fg='darkgreen').pack(anchor='w', padx=15)

        # Sekcja publikacji
        if player.publication_history:
            publications_frame = tk.LabelFrame(player_frame, text="📖 Historia Publikacji", bg='lightyellow')
            publications_frame.pack(fill='x', padx=10, pady=5)

            for journal in player.publication_history:
                pub_item = tk.Frame(publications_frame, bg='lightsteelblue', relief='ridge', borderwidth=1)
                pub_item.pack(fill='x', padx=5, pady=2)

                tk.Label(pub_item, text=f"📄 {journal.name} (IF: {journal.impact_factor})",
                        font=('Arial', 10, 'bold'), bg='lightsteelblue').pack(anchor='w', padx=5, pady=2)

                tk.Label(pub_item, text=f"Koszt: {journal.pb_cost} PB → Nagroda: {journal.pz_reward} PZ",
                        font=('Arial', 9), bg='lightsteelblue', fg='darkred').pack(anchor='w', padx=15)

        # Jeśli gracz nie ma żadnych osiągnięć
        if not player.completed_research and not player.publication_history:
            tk.Label(player_frame, text="Brak osiągnięć do wyświetlenia",
                    font=('Arial', 12), bg='lightyellow', fg='gray').pack(pady=20)

    def hire_selected_scientist(self):
        """Zatrudnia wybranego naukowca z listy"""
        if not hasattr(self, 'scientists_listbox'):
            return

        selection = self.scientists_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Wybierz naukowca do zatrudnienia")
            return

        scientist_idx = selection[0]
        if scientist_idx < len(self.available_scientists):
            scientist = self.available_scientists[scientist_idx]
            current_player = self.players[self.current_player_idx]

            # Sprawdź koszty
            hire_cost = scientist.salary * 2
            if current_player.credits < hire_cost:
                messagebox.showwarning("Błąd", f"Brak środków! Koszt: {hire_cost}K")
                return

            # Zatrudnij
            current_player.credits -= hire_cost
            current_player.scientists.append(scientist)

            # Usuń z rynku
            self.available_scientists.remove(scientist)

            self.log_message(f"Zatrudniono: {scientist.name} za {hire_cost}K")
            self.update_markets()
            self.update_ui()

    def publish_article(self):
        """Publikuje artykuł w wybranym czasopiśmie"""
        if not hasattr(self, 'journals_listbox'):
            return

        selection = self.journals_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Wybierz czasopismo do publikacji")
            return

        journal_idx = selection[0]
        if journal_idx < len(self.available_journals):
            journal = self.available_journals[journal_idx]
            current_player = self.players[self.current_player_idx]

            # Sprawdź koszty
            if current_player.research_points < journal.pb_cost:
                messagebox.showwarning("Błąd", f"Brak punktów badań! Koszt: {journal.pb_cost} PB")
                return

            # Sprawdź wymagania reputacji (parsuj z requirements)
            rep_required = 0
            if 'Rep' in journal.requirements:
                try:
                    rep_required = int(journal.requirements.replace('Rep', '').strip())
                except:
                    rep_required = 0
            if current_player.reputation < rep_required:
                messagebox.showwarning("Błąd", f"Za niska reputacja! Wymagane: {rep_required}")
                return

            # Publikuj
            current_player.research_points -= journal.pb_cost
            current_player.prestige_points += journal.pz_reward
            current_player.activity_points += 3  # Punkt aktywności za publikację
            self.log_message(f"Opublikowano w {journal.name} za {journal.pb_cost} PB, +{journal.pz_reward} PZ")
            self.update_ui()

    def take_selected_grant(self):
        """Bierze wybrany grant z listy"""
        if not hasattr(self, 'grants_listbox'):
            return

        selection = self.grants_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Wybierz grant do wzięcia")
            return

        grant_idx = selection[0]
        available_grants = [g for g in self.game_data.grants if not any(p.current_grant and p.current_grant.name == g.name for p in self.players)]

        if grant_idx < len(available_grants):
            grant = available_grants[grant_idx]
            current_player = self.players[self.current_player_idx]

            if current_player.current_grant:
                messagebox.showwarning("Błąd", "Masz już aktywny grant!")
                return

            # Weź grant
            current_player.current_grant = grant
            self.log_message(f"Wzięto grant: {grant.name}")
            self.update_markets()
            self.update_ui()


    def update_markets(self):
        """Aktualizuje zawartość rynków"""
        # Aktualizuj naukowców na rynku
        if hasattr(self, 'scientists_scrollable_frame'):
            # Usuń wszystkie istniejące przyciski
            for widget in self.scientists_scrollable_frame.winfo_children():
                widget.destroy()

            # Dodaj przyciski dla każdego dostępnego naukowca
            for scientist in self.available_scientists:
                scientist_frame = tk.Frame(self.scientists_scrollable_frame, relief='raised', borderwidth=1)
                scientist_frame.pack(fill='x', padx=2, pady=2)

                # Przycisk podglądu
                preview_btn = ttk.Button(scientist_frame,
                                       text=f"👁️ {scientist.name}",
                                       command=lambda s=scientist: self.preview_scientist(s))
                preview_btn.pack(side='left', padx=2)

                # Informacje podstawowe
                info_label = tk.Label(scientist_frame,
                                    text=f"{scientist.field} | {scientist.salary}K/rundę | {scientist.hex_bonus}⬢",
                                    font=('Arial', 9))
                info_label.pack(side='left', padx=5)

                # Przycisk zatrudnienia - tylko jeśli gracz ma aktywną akcję ZATRUDNIJ
                if (hasattr(self, 'current_action_card') and self.current_action_card and
                    self.current_action_card.action_type == ActionType.ZATRUDNIJ and
                    self.remaining_action_points >= (2 if scientist.type == ScientistType.DOKTOR else 3 if scientist.type == ScientistType.PROFESOR else 1)):
                    hire_btn = ttk.Button(scientist_frame,
                                        text="Zatrudnij",
                                        command=lambda s=scientist: self.hire_scientist_from_market(s))
                    hire_btn.pack(side='right', padx=2)
                else:
                    # Informacja o wymaganiu karty akcji
                    req_text = "Zagraj kartę ZATRUDNIJ PERSONEL" if not (hasattr(self, 'current_action_card') and self.current_action_card) else "Brak PA"
                    tk.Label(scientist_frame, text=req_text, font=('Arial', 8), fg='gray').pack(side='right', padx=2)

        # Aktualizuj czasopisma na rynku
        if hasattr(self, 'journals_scrollable_frame'):
            # Usuń wszystkie istniejące przyciski
            for widget in self.journals_scrollable_frame.winfo_children():
                widget.destroy()

            # Dodaj przyciski dla każdego dostępnego czasopisma
            for journal in self.available_journals:
                journal_frame = tk.Frame(self.journals_scrollable_frame, relief='raised', borderwidth=1)
                journal_frame.pack(fill='x', padx=2, pady=2)

                # Przycisk podglądu
                preview_btn = ttk.Button(journal_frame,
                                       text=f"👁️ {journal.name}",
                                       command=lambda j=journal: self.preview_journal(j))
                preview_btn.pack(side='left', padx=2)

                # Informacje podstawowe
                info_label = tk.Label(journal_frame,
                                    text=f"IF:{journal.impact_factor} | {journal.pb_cost}PB → {journal.pz_reward}PZ",
                                    font=('Arial', 9))
                info_label.pack(side='left', padx=5)

                # Przycisk publikacji - tylko jeśli gracz ma aktywną akcję PUBLIKUJ
                if (hasattr(self, 'current_action_card') and self.current_action_card and
                    self.current_action_card.action_type == ActionType.PUBLIKUJ):
                    publish_btn = ttk.Button(journal_frame,
                                           text="Publikuj",
                                           command=lambda j=journal: self.publish_in_journal_from_market(j))
                    publish_btn.pack(side='right', padx=2)
                else:
                    # Informacja o wymaganiu karty akcji
                    req_text = "Zagraj kartę PUBLIKUJ"
                    tk.Label(journal_frame, text=req_text, font=('Arial', 8), fg='gray').pack(side='right', padx=2)

    def log_message(self, message: str):
        """Dodaje wiadomość do logu gry"""
        self.log_text.insert(tk.END, f"[R{self.current_round}] {message}\n")
        self.log_text.see(tk.END)

    def setup_game(self):
        """Konfiguruje nową grę"""
        try:
            self.game_data.load_data()
            self.log_message("Wczytano dane gry")

            # Wybór scenariusza
            self.select_scenario()

            # Stwórz trzech graczy
            colors = ['red', 'blue', 'green']
            player_names = ['Gracz 1', 'Gracz 2', 'Gracz 3']

            self.players = []
            for i in range(3):
                player = Player(
                    name=player_names[i],
                    color=colors[i]
                )

                # Przypisz losowy instytut
                if self.game_data.institutes:
                    player.institute = random.choice(self.game_data.institutes)

                    # Parsuj zasoby startowe
                    resources = player.institute.starting_resources.split(', ')
                    for resource in resources:
                        if 'K' in resource:
                            credit_val = self.game_data.safe_int_parse(resource.replace('K', '').strip())
                            player.credits = credit_val * 1000
                        elif 'PZ' in resource:
                            pz_val = self.game_data.safe_int_parse(resource.replace('PZ', '').strip())
                            player.prestige_points = pz_val

                    player.reputation = player.institute.starting_reputation

                # Daj karty akcji
                player.action_cards = self.game_data.create_action_cards()

                # Daj startowe karty badań (maksymalnie 5)
                if self.game_data.main_deck:
                    start_cards = min(5, len(self.game_data.main_deck))
                    player.hand_cards = self.game_data.main_deck[:start_cards]
                    # Usuń rozdane karty z talii
                    self.game_data.main_deck = self.game_data.main_deck[start_cards:]

                # Daj każdemu graczowi jedną kartę konsorcjum na start
                if self.game_data.consortium_cards:
                    player.hand_cards.append(ConsortiumCard())

                # Daj startowego doktoranta
                player.scientists.append(Scientist("Doktorant", ScientistType.DOKTORANT, "Uniwersalny", 0, 1, "Brak", "Młody naukowiec"))

                self.players.append(player)

            self.setup_players_ui()
            self.prepare_round()

            # Odśwież zakładkę projektów po załadowaniu danych
            self.setup_projects_tab()

            self.next_phase_btn['state'] = 'normal'
            self.next_round_btn['state'] = 'normal'
            self.log_message("Gra skonfigurowana - 3 graczy")

        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas konfiguracji gry: {e}")
            print(f"Szczegóły błędu: {e}")

    def setup_players_ui(self):
        """Tworzy interfejs graczy"""
        # Wyczyść poprzedni UI
        for widget in self.players_frame.winfo_children():
            widget.destroy()

        for i, player in enumerate(self.players):
            # Podświetl aktywnego gracza
            relief = 'solid' if i == self.current_player_idx else 'flat'

            player_frame = ttk.LabelFrame(self.players_frame, text=f"{player.name} ({player.color})", relief=relief)
            player_frame.pack(fill='x', padx=5, pady=5)

            # Instytut
            if player.institute:
                inst_label = ttk.Label(player_frame, text=f"🏛️ {player.institute.name[:15]}...",
                                     font=('Arial', 8, 'bold'))
                inst_label.pack(anchor='w', padx=5)

            # Zasoby
            resources_frame = ttk.Frame(player_frame)
            resources_frame.pack(fill='x', padx=5, pady=2)

            ttk.Label(resources_frame, text=f"💰{player.credits//1000}K").pack(side='left')
            ttk.Label(resources_frame, text=f"⭐{player.prestige_points}PZ").pack(side='left', padx=(5, 0))
            ttk.Label(resources_frame, text=f"🔬{player.research_points}PB").pack(side='left', padx=(5, 0))
            ttk.Label(resources_frame, text=f"📊{player.reputation}Rep").pack(side='left', padx=(5, 0))

            # Personel i badania
            status_frame = ttk.Frame(player_frame)
            status_frame.pack(fill='x', padx=5, pady=2)

            scientists_count = len(player.scientists)
            scientists_btn = ttk.Button(status_frame, text=f"👨‍🔬{scientists_count}",
                                       command=lambda p=player: self.show_employed_scientists(p))
            scientists_btn.pack(side='left')

            active_research = len(player.active_research)
            completed_research = len(player.completed_research)
            ttk.Label(status_frame, text=f"🧪{active_research}/{completed_research}").pack(side='left', padx=(5, 0))

            hand_size = len(player.hand_cards)
            ttk.Label(status_frame, text=f"🃏{hand_size}").pack(side='left', padx=(5, 0))

            # Grant i akcje
            if player.current_grant:
                grant_label = ttk.Label(player_frame, text=f"📋 {player.current_grant.name[:12]}...",
                                      font=('Arial', 8))
                grant_label.pack(anchor='w', padx=5)

            used_actions = len([card for card in player.action_cards if card.is_used])
            available_actions = len(player.action_cards) - used_actions
            actions_label = ttk.Label(player_frame, text=f"⚡ {available_actions}/{len(player.action_cards)}",
                                    font=('Arial', 8))
            actions_label.pack(anchor='w', padx=5)

    def prepare_round(self):
        """Przygotowuje nową rundę"""
        # Resetuj karty akcji graczy
        for player in self.players:
            for card in player.action_cards:
                card.is_used = False
            player.has_passed = False

        # Przygotuj granty na rundę
        available_grant_count = min(6, len(self.game_data.grants))
        self.available_grants = random.sample(self.game_data.grants, available_grant_count)

        # Przygotuj czasopisma
        available_journal_count = min(4, len(self.game_data.journals))
        self.available_journals = random.sample(self.game_data.journals, available_journal_count)

        # Przygotuj naukowców na rynek
        available_scientist_count = min(4, len(self.game_data.scientists))
        self.available_scientists = random.sample(self.game_data.scientists, available_scientist_count)

        self.current_phase = GamePhase.GRANTY
        self.current_player_idx = 0
        self.current_action_card = None
        self.remaining_action_points = 0
        self.update_ui()
        self.log_message(f"Rozpoczęto rundę {self.current_round}")

    def next_phase(self):
        """Przechodzi do następnej fazy gry"""
        if self.current_phase == GamePhase.GRANTY:
            self.current_phase = GamePhase.AKCJE
            self.pass_btn['state'] = 'normal'
            self.log_message("Przejście do fazy akcji")

        elif self.current_phase == GamePhase.AKCJE:
            self.current_phase = GamePhase.PORZADKOWA
            self.pass_btn['state'] = 'disabled'
            self.end_action_btn['state'] = 'disabled'
            self.log_message("Przejście do fazy porządkowej")

        elif self.current_phase == GamePhase.PORZADKOWA:
            self.end_round()

        self.update_ui()

    def player_pass(self):
        """Gracz pasuje w fazie akcji"""
        if self.current_phase == GamePhase.AKCJE:
            current_player = self.players[self.current_player_idx]
            current_player.has_passed = True

            # Bonus za pasowanie zależny od liczby kart na ręku
            hand_size = len(current_player.hand_cards)
            pass_bonus = {5: 0, 4: 1000, 3: 3000, 2: 5000, 1: 8000}.get(hand_size, 0)
            current_player.credits += pass_bonus

            self.log_message(f"{current_player.name} pasuje (bonus: {pass_bonus//1000}K)")

            # Zakończ aktualną akcję
            self.current_action_card = None
            self.remaining_action_points = 0

            # Sprawdź czy wszyscy spasowali
            if all(p.has_passed for p in self.players):
                self.current_phase = GamePhase.PORZADKOWA
                self.pass_btn['state'] = 'disabled'
                self.end_action_btn['state'] = 'disabled'
                self.log_message("Wszyscy gracze spasowali - przejście do fazy porządkowej")
            else:
                self.next_player()

            self.update_ui()

    def end_current_action(self):
        """Kończy aktualną akcję"""
        if self.current_action_card:
            self.log_message(f"Zakończono akcję {self.current_action_card.action_type.value}")
            self.current_action_card = None
            self.remaining_action_points = 0
            self.next_player()
            self.update_ui()

    def next_player(self):
        """Przechodzi do następnego gracza"""
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        # Jeśli wszyscy spasowali, pomiń
        attempts = 0
        while self.players[self.current_player_idx].has_passed and attempts < len(self.players):
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            attempts += 1

    def end_round(self):
        """Kończy rundę i przechodzi do następnej"""
        # Zapłać pensje
        for player in self.players:
            self.pay_salaries(player)

        # Sprawdź cele grantów
        for player in self.players:
            self.check_grant_completion(player)

        # Sprawdź warunki końca gry
        if self.check_end_game():
            return

        self.current_round += 1
        self.prepare_round()

    def pay_salaries(self, player: Player):
        """Płaci pensje dla gracza"""
        total_salary = 0

        for scientist in player.scientists:
            if scientist.is_paid and scientist.type != ScientistType.DOKTORANT:
                total_salary += scientist.salary

        # Dodaj karę za przeciążenie (więcej niż 3 naukowców, nie licząc doktorantów)
        non_doctoral_count = len([s for s in player.scientists
                                if s.type != ScientistType.DOKTORANT])
        if non_doctoral_count > 3:
            overload_penalty = (non_doctoral_count - 3) * 1000
            total_salary += overload_penalty
            self.log_message(f"{player.name}: kara przeciążenia {overload_penalty//1000}K")

        # Sprawdź czy może zapłacić
        if player.credits >= total_salary:
            player.credits -= total_salary
            self.log_message(f"{player.name} zapłacił {total_salary//1000}K pensji")
        else:
            # Nie może zapłacić - kara reputacji tylko za pierwszą niewypłatę
            unpaid_count = len([s for s in player.scientists if not s.is_paid])
            if unpaid_count == 0:  # Pierwsza niewypłata
                player.reputation = max(0, player.reputation - 1)
                self.log_message(f"{player.name}: niewypłata pensji, -1 Reputacja")

            # Oznacz naukowców jako niewypłaconych
            for scientist in player.scientists:
                if scientist.type != ScientistType.DOKTORANT:
                    scientist.is_paid = False

    def check_grant_completion(self, player: Player):
        """Sprawdza czy gracz ukończył cel grantu"""
        if not player.current_grant or player.current_grant.is_completed:
            return

        goal = player.current_grant.goal.lower()
        completed = False

        if "publikacj" in goal:
            required_pubs = 2
            if player.publications >= required_pubs:
                completed = True

        elif "badanie" in goal:
            if len(player.completed_research) >= 1:
                completed = True

        elif "konsorcjum" in goal:
            # Sprawdź czy założył konsorcjum
            for project in self.game_data.large_projects:
                if project.director == player:
                    completed = True
                    break

        elif "aktywności" in goal:
            # Punkty aktywności: zatrudnienie (2p), publikacja (3p), ukończenie badania (4p), konsorcjum (5p)
            activity_points = 0
            activity_points += len(player.scientists) * 2  # Zatrudnienie
            activity_points += player.publications * 3  # Publikacje
            activity_points += len(player.completed_research) * 4  # Badania

            for project in self.game_data.large_projects:
                if project.director == player:
                    activity_points += 5

            required_activity = self.game_data.safe_int_parse(goal.split()[0], 10)
            if activity_points >= required_activity:
                completed = True

        if completed:
            player.current_grant.is_completed = True
            # Daj nagrodę
            reward = player.current_grant.reward
            credits = self.game_data.safe_int_parse(reward.replace('K', ''), 0) * 1000
            if credits > 0:
                player.credits += credits
                self.log_message(f"{player.name} ukończył grant: +{credits//1000}K")

    def check_end_game(self) -> bool:
        """Sprawdza warunki końca gry"""
        # Sprawdź różne warunki końca gry
        for player in self.players:
            # Warunek 1: 35 PZ
            if player.prestige_points >= 35:
                self.end_game(f"{player.name} osiągnął 35 PZ!")
                return True

            # Warunek 2: 6 ukończonych badań
            if len(player.completed_research) >= 6:
                self.end_game(f"{player.name} ukończył 6 badań!")
                return True

        # Warunek 3: 3 Wielkie Projekty ukończone
        completed_projects = len([p for p in self.game_data.large_projects if p.is_completed])
        if completed_projects >= 3:
            self.end_game("Ukończono 3 Wielkie Projekty!")
            return True

        return False

    def end_game(self, reason: str):
        """Kończy grę"""
        self.game_ended = True
        self.log_message(f"KONIEC GRY: {reason}")

        # Pokaż wyniki końcowe
        results = []
        for player in self.players:
            total_score = player.prestige_points
            results.append((player.name, total_score, player.prestige_points, len(player.completed_research), player.publications))

        results.sort(key=lambda x: x[1], reverse=True)

        result_text = "WYNIKI KOŃCOWE:\n\n"
        for i, (name, score, pz, research, pubs) in enumerate(results, 1):
            result_text += f"{i}. {name}: {score} PZ ({research} badań, {pubs} publikacji)\n"

        messagebox.showinfo("Koniec gry", result_text)

    def update_ui(self):
        """Aktualizuje interfejs użytkownika"""
        self.round_label.config(text=f"Runda: {self.current_round}")
        self.phase_label.config(text=f"Faza: {self.current_phase.value}")

        if self.current_action_card:
            self.action_points_label.config(text=f"PA: {self.remaining_action_points}/{self.current_action_card.action_points}")
        else:
            self.action_points_label.config(text="PA: 0/0")

        if self.players:
            current_player = self.players[self.current_player_idx]
            self.current_player_label.config(text=f"Gracz: {current_player.name}")

        # Ustaw stan przycisków
        if self.current_action_card and self.remaining_action_points > 0:
            self.end_action_btn['state'] = 'normal'
        else:
            self.end_action_btn['state'] = 'disabled'

        self.setup_players_ui()
        self.setup_game_area()
        self.setup_research_area()
        self.update_markets()
        self.setup_achievements_tab()  # Odśwież zakładkę osiągnięć
        self.update_notifications()  # Odśwież powiadomienia

        # Update developer tools if active
        if self.developer_mode and hasattr(self, 'dev_player_combo'):
            self.update_dev_player_list()
            self.update_dev_resource_displays()
            if hasattr(self, 'dev_card_player_combo'):
                self.update_dev_card_players()
            if hasattr(self, 'dev_current_player_combo'):
                self.update_dev_gamestate_displays()
            if hasattr(self, 'dev_scientist_player_combo'):
                self.update_dev_scientist_players()

    def setup_game_area(self):
        """Konfiguruje główny obszar gry w zależności od fazy"""
        # Wyczyść poprzedni UI
        for widget in self.game_tab.winfo_children():
            widget.destroy()

        if self.current_phase == GamePhase.GRANTY:
            self.setup_grants_phase()
        elif self.current_phase == GamePhase.AKCJE:
            self.setup_actions_phase()
        elif self.current_phase == GamePhase.PORZADKOWA:
            self.setup_cleanup_phase()

    def setup_grants_phase(self):
        """Konfiguruje interfejs fazy grantów"""
        ttk.Label(self.game_tab, text="🎯 Dostępne Granty", font=('Arial', 14, 'bold')).pack(pady=10)

        # Scroll frame dla grantów
        canvas = tk.Canvas(self.game_tab, height=400)
        scrollbar = ttk.Scrollbar(self.game_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, grant in enumerate(self.available_grants):
            grant_frame = ttk.LabelFrame(scrollable_frame, text=grant.name)
            grant_frame.pack(fill='x', padx=10, pady=5)

            ttk.Label(grant_frame, text=f"📋 Wymagania: {grant.requirements}").pack(anchor='w', padx=5)
            ttk.Label(grant_frame, text=f"🎯 Cel: {grant.goal}").pack(anchor='w', padx=5)
            ttk.Label(grant_frame, text=f"💰 Nagroda: {grant.reward}").pack(anchor='w', padx=5)

            # Sprawdź czy gracze są zainicjalizowani
            can_take = True
            if self.players and self.current_player_idx < len(self.players):
                current_player = self.players[self.current_player_idx]
                can_take = current_player.current_grant is None

            take_btn = ttk.Button(grant_frame, text="Weź grant",
                                 command=lambda g=grant: self.take_grant(g),
                                 state='normal' if can_take else 'disabled')
            take_btn.pack(anchor='e', padx=5, pady=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_actions_phase(self):
        """Konfiguruje interfejs fazy akcji"""
        current_player = self.players[self.current_player_idx]

        if current_player.has_passed:
            ttk.Label(self.game_tab, text=f"{current_player.name} spasował",
                     font=('Arial', 14, 'bold')).pack(pady=20)
            return

        ttk.Label(self.game_tab, text="⚡ KARTY AKCJI", font=('Arial', 14, 'bold')).pack(pady=10)

        # Jeśli gracz ma aktywną kartę akcji, pokaż menu akcji
        if self.current_action_card:
            self.show_action_menu()
        else:
            # Pokaż dostępne karty akcji
            cards_frame = tk.Frame(self.game_tab)
            cards_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Utwórz siatkę 2x3 dla kart
            row = 0
            col = 0
            for card in current_player.action_cards:
                card_widget = ActionCardWidget(cards_frame, card,
                                             on_play_callback=self.play_action_card)
                card_widget.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

                col += 1
                if col >= 3:  # 3 karty na rząd
                    col = 0
                    row += 1

            # Skonfiguruj elastyczność siatki
            for i in range(3):
                cards_frame.columnconfigure(i, weight=1)
            for i in range(2):
                cards_frame.rowconfigure(i, weight=1)

    def show_action_menu(self):
        """Pokazuje menu akcji dla aktywnej karty"""
        current_player = self.players[self.current_player_idx]

        # Nagłówek aktywnej karty
        header_frame = tk.Frame(self.game_tab, bg='lightgreen', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(header_frame, text=f"AKTYWNA KARTA: {self.current_action_card.action_type.value}",
                font=('Arial', 12, 'bold'), bg='lightgreen').pack(pady=5)
        tk.Label(header_frame, text=f"Pozostałe PA: {self.remaining_action_points}",
                font=('Arial', 10, 'bold'), bg='lightgreen').pack()

        # Menu akcji
        menu_frame = tk.Frame(self.game_tab)
        menu_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Akcje dodatkowe
        ttk.Label(menu_frame, text="Dostępne akcje:", font=('Arial', 11, 'bold')).pack(anchor='w')

        for action_desc, cost in self.current_action_card.additional_actions:
            if self.remaining_action_points >= cost:
                action_frame = tk.Frame(menu_frame, relief='groove', borderwidth=1)
                action_frame.pack(fill='x', pady=2)

                action_text = f"{action_desc} (Koszt: {cost} PA)"
                tk.Label(action_frame, text=action_text, font=('Arial', 10)).pack(side='left', padx=5, pady=2)

                action_btn = tk.Button(action_frame, text="Wykonaj",
                                     command=lambda desc=action_desc, c=cost: self.execute_additional_action(desc, c),
                                     bg='lightblue')
                action_btn.pack(side='right', padx=5, pady=2)

    def update_action_menu(self):
        """Aktualizuje menu akcji po wykonaniu akcji"""
        if not (hasattr(self, 'current_action_card') and self.current_action_card):
            return

        # Usuń stare elementy menu akcji
        for widget in self.game_tab.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_children():
                # Sprawdź czy to nagłówek lub menu akcji
                first_child = widget.winfo_children()[0]
                if isinstance(first_child, tk.Label):
                    text = first_child.cget('text')
                    if 'AKTYWNA KARTA' in str(text) or 'Dostępne akcje' in str(text):
                        widget.destroy()

        # Pokaż zaktualizowane menu
        self.show_action_menu()

    def play_action_card(self, action_card: ActionCard):
        """Gracz zagrywa kartę akcji"""
        if action_card.is_used:
            messagebox.showwarning("Uwaga", "Ta karta została już użyta w tej rundzie!")
            return

        current_player = self.players[self.current_player_idx]

        # Oznacz kartę jako użytą
        action_card.is_used = True
        self.current_action_card = action_card
        self.remaining_action_points = action_card.action_points

        # Wykonaj akcję podstawową
        self.execute_basic_action(action_card)

        self.log_message(f"{current_player.name} zagrał kartę: {action_card.action_type.value}")
        self.update_ui()

    def execute_basic_action(self, action_card: ActionCard):
        """Wykonuje akcję podstawową karty"""
        current_player = self.players[self.current_player_idx]

        if action_card.action_type == ActionType.PROWADZ_BADANIA:
            doktoranci = [s for s in current_player.scientists if s.type == ScientistType.DOKTORANT]
            if doktoranci and doktoranci[0].is_paid and current_player.active_research:
                self.add_hex_to_research(current_player, 1)
                self.log_message(f"Aktywowano doktoranta (+1 heks)")
            elif doktoranci and doktoranci[0].is_paid:
                self.log_message(f"Doktorant gotowy - rozpocznij badanie aby go aktywować")
            else:
                self.log_message(f"Brak aktywnego doktoranta")

        elif action_card.action_type == ActionType.ZATRUDNIJ:
            current_player.credits += 1000
            self.log_message(f"Otrzymano 1K")

        elif action_card.action_type == ActionType.PUBLIKUJ:
            # Akcja podstawowa: możliwość publikacji w czasopiśmie z rynku
            # Pokaż okno wyboru czasopisma
            self.show_journal_selection_for_publish()
            self.log_message(f"Możesz opublikować w dostępnych czasopismach (akcja podstawowa)")

        elif action_card.action_type == ActionType.FINANSUJ:
            current_player.credits += 2000
            self.log_message(f"Otrzymano 2K")

        elif action_card.action_type == ActionType.ZARZADZAJ:
            current_player.credits += 2000
            self.log_message(f"Otrzymano 2K")

    def execute_additional_action(self, action_desc: str, cost: int):
        """Wykonuje akcję dodatkową"""
        if self.remaining_action_points < cost:
            messagebox.showwarning("Uwaga", "Brak wystarczających punktów akcji!")
            return

        current_player = self.players[self.current_player_idx]
        self.remaining_action_points -= cost

        # Parsuj akcję i wykonaj
        if "doktora" in action_desc.lower() and "aktywuj" in action_desc.lower():
            self.use_scientist(ScientistType.DOKTOR, 2)
        elif "profesora" in action_desc.lower() and "aktywuj" in action_desc.lower():
            self.use_scientist(ScientistType.PROFESOR, 3)
        elif "rozpocznij" in action_desc.lower() and "badanie" in action_desc.lower():
            self.enter_research_selection_mode()
        elif "zatrudnij doktora" in action_desc.lower():
            self.show_scientist_selection(ScientistType.DOKTOR, cost)
        elif "zatrudnij profesora" in action_desc.lower():
            self.show_scientist_selection(ScientistType.PROFESOR, cost)
        elif "zatrudnij doktoranta" in action_desc.lower():
            self.hire_scientist(ScientistType.DOKTORANT)
        elif "weź 3k" in action_desc.lower():
            current_player.credits += 3000
            self.log_message(f"Otrzymano 3K")
        elif "konsultacje" in action_desc.lower():
            self.commercial_consulting()
        elif "wpłać do konsorcjum" in action_desc.lower():
            self.contribute_to_consortium()
        elif "załóż konsorcjum" in action_desc.lower():
            self.start_consortium()
        elif "kredyt awaryjny" in action_desc.lower():
            current_player.credits += 5000
            current_player.reputation = max(0, current_player.reputation - 1)
            self.log_message(f"Kredyt awaryjny (+5K, -1 Rep)")
        elif "odśwież rynek" in action_desc.lower():
            self.refresh_market()
        elif "kampania pr" in action_desc.lower():
            if current_player.credits >= 4000:
                current_player.credits -= 4000
                current_player.reputation = min(5, current_player.reputation + 1)
                self.log_message(f"Kampania PR (+1 Rep)")
        elif "poprawa wizerunku" in action_desc.lower():
            if current_player.research_points >= 2:
                current_player.research_points -= 2
                current_player.reputation = min(5, current_player.reputation + 1)
                self.log_message(f"Poprawa wizerunku (+1 Rep)")

        self.log_message(f"Wykonano: {action_desc}")
        self.update_ui()
        self.update_action_menu()

    def add_hex_to_research(self, player: Player, hex_count: int):
        """Inicjuje tryb układania heksów dla gracza"""
        if not player.active_research:
            messagebox.showinfo("Info", "Brak aktywnych badań. Najpierw rozpocznij badanie.")
            return

        if player.hex_tokens < hex_count:
            messagebox.showwarning("Uwaga", "Brak wystarczającej liczby heksów!")
            return

        # Znajdź pierwsze aktywne badanie
        research = player.active_research[0]

        # Wprowadź tryb układania heksów
        self.pending_hex_placements = hex_count
        self.hex_placement_mode = True
        self.current_research_for_hex = research

        self.log_message(f"Układaj {hex_count} heks(ów) na mapie badania '{research.name}'. Kliknij na dozwolone pola.")
        self.update_ui()

        # Auto-expand odpowiedni widget badania
        self.auto_expand_research_widget(research)

    def on_hex_clicked(self, position, research: ResearchCard):
        """Obsługuje kliknięcie na heks podczas układania"""
        if not self.hex_placement_mode or research != self.current_research_for_hex:
            return

        current_player = self.players[self.current_player_idx]

        # Sprawdź czy można położyć heks na tej pozycji
        if research.hex_research_map.can_place_hex(position, research.player_path):
            # Umieść heks
            result = research.hex_research_map.place_hex(position, current_player.color, research.player_path)

            if result['success']:
                # Usuń heks z puli gracza
                current_player.hex_tokens -= 1
                self.pending_hex_placements -= 1

                # Aktualizuj postęp badania
                research.hexes_placed = len(research.player_path)

                self.log_message(f"Położono heks na pozycji ({position.q},{position.r})")

                # Sprawdź bonusy
                if result['bonus']:
                    self.apply_hex_bonus(current_player, result['bonus'])
                    self.log_message(f"Bonus z heksa: {result['bonus']}")

                # Sprawdź ukończenie badania
                if result['completed']:
                    self.log_message(f"Badanie '{research.name}' zostało ukończone!")
                    self.complete_research(current_player, research)
                    self.hex_placement_mode = False
                    self.pending_hex_placements = 0
                    self.current_research_for_hex = None
                    self.auto_collapse_all_research_widgets()
                    self.update_ui()
                    return

                # Sprawdź czy pozostały jeszcze heksy do położenia
                if self.pending_hex_placements <= 0:
                    self.hex_placement_mode = False
                    self.current_research_for_hex = None
                    self.auto_collapse_all_research_widgets()
                    self.log_message("Wszystkie heksy zostały położone.")

                self.update_ui()
            else:
                self.log_message("Nie można położyć heksa w tym miejscu!")
        else:
            self.log_message("Nie można położyć heksa w tym miejscu! Heks musi przylegać do już położonych.")

    def apply_hex_bonus(self, player: Player, bonus: str):
        """Aplikuje bonus z heksa bonusowego"""
        if "+1PB" in bonus:
            player.research_points += 1
        elif "+2PB" in bonus:
            player.research_points += 2
        elif "+3PB" in bonus:
            player.research_points += 3
        elif "+1PZ" in bonus:
            player.prestige_points += 1
        elif "+2PZ" in bonus:
            player.prestige_points += 2
        elif "+1K" in bonus:
            player.credits += 1000
        elif "+2K" in bonus:
            player.credits += 2000
        elif "+3K" in bonus:
            player.credits += 3000
        elif "+1Rep" in bonus:
            player.reputation = min(5, player.reputation + 1)

    def complete_research(self, player: Player, research: ResearchCard):
        """Kończy badanie"""
        research.is_completed = True
        player.active_research.remove(research)
        player.completed_research.append(research)

        # Reset hex map for this player
        if research.hex_research_map:
            research.hex_research_map.reset_player_progress(player.color)

        # Clear player path
        research.player_path = []

        # Odzyskaj heksy - gracz zawsze wraca do 20 heksów
        player.hex_tokens = 20

        # Daj nagrodę podstawową
        self.apply_research_reward(player, research.basic_reward)

        # Zwiększ punkty aktywności
        player.activity_points += 4

        self.log_message(f"Ukończono badanie: {research.name}")

    def apply_research_reward(self, player: Player, reward: str):
        """Aplikuje nagrodę za ukończone badanie"""
        parts = reward.split(', ')
        for part in parts:
            part = part.strip()
            if 'PB' in part:
                pb = self.game_data.safe_int_parse(part.split(' ')[0], 0)
                player.research_points += pb
            elif 'PZ' in part:
                pz = self.game_data.safe_int_parse(part.split(' ')[0], 0)
                player.prestige_points += pz

    def use_scientist(self, scientist_type: ScientistType, hexes: int):
        """Używa naukowca do badań"""
        current_player = self.players[self.current_player_idx]
        scientists = [s for s in current_player.scientists
                     if s.type == scientist_type and s.is_paid]

        if scientists:
            self.add_hex_to_research(current_player, hexes)
            self.log_message(f"Aktywowano {scientist_type.value} (+{hexes} heks)")
        else:
            messagebox.showwarning("Uwaga", f"Brak dostępnego {scientist_type.value}!")

    def hire_scientist(self, scientist_type: ScientistType):
        """Zatrudnia naukowca"""
        current_player = self.players[self.current_player_idx]

        # Sprawdź czy może sobie pozwolić
        cost = {
            ScientistType.DOKTORANT: 0,
            ScientistType.DOKTOR: 2000,
            ScientistType.PROFESOR: 3000
        }.get(scientist_type, 0)

        if current_player.credits >= cost:
            # Stwórz nowego naukowca
            if scientist_type == ScientistType.DOKTORANT:
                new_scientist = Scientist(f"Doktorant {len(current_player.scientists)+1}",
                                        ScientistType.DOKTORANT, "Uniwersalny", 0, 1, "Brak", "Młody naukowiec")
            elif scientist_type == ScientistType.DOKTOR:
                new_scientist = Scientist(f"Dr {len(current_player.scientists)+1}",
                                        ScientistType.DOKTOR, "Uniwersalny", 2000, 2, "Brak", "Doktor nauk")
            else:  # PROFESOR
                new_scientist = Scientist(f"Prof. {len(current_player.scientists)+1}",
                                        ScientistType.PROFESOR, "Uniwersalny", 3000, 3, "Brak", "Profesor nauk")

            current_player.scientists.append(new_scientist)
            if cost > 0:
                current_player.credits -= cost
            self.log_message(f"Zatrudniono: {new_scientist.name}")
        else:
            messagebox.showwarning("Uwaga", "Brak wystarczających środków!")

    def start_new_research(self):
        """Rozpoczyna nowe badanie"""
        current_player = self.players[self.current_player_idx]
        if current_player.hand_cards:
            # Weź pierwszą kartę z ręki
            card = current_player.hand_cards[0]
            current_player.hand_cards.remove(card)
            current_player.active_research.append(card)
            card.is_active = True
            self.log_message(f"Rozpoczęto badanie: {card.name}")

    def commercial_consulting(self):
        """Konsultacje komercyjne"""
        current_player = self.players[self.current_player_idx]
        professors = [s for s in current_player.scientists if s.type == ScientistType.PROFESOR and s.is_paid]

        if professors:
            current_player.credits += 4000
            self.log_message(f"Konsultacje komercyjne (+4K)")
        else:
            messagebox.showwarning("Uwaga", "Brak dostępnego profesora!")

    def contribute_to_consortium(self):
        """Wpłaca do konsorcjum lub składa wniosek o dołączenie"""
        current_player = self.players[self.current_player_idx]
        available_consortiums = [p for p in self.game_data.large_projects if p.director and not p.is_completed]

        if not available_consortiums:
            messagebox.showinfo("Info", "Brak dostępnych konsorcjów")
            return

        # Sprawdź czy gracz jest kierownikiem któregoś konsorcjum
        player_consortiums = [p for p in available_consortiums if p.director == current_player]
        other_consortiums = [p for p in available_consortiums if p.director != current_player]

        if player_consortiums and other_consortiums:
            # Gracz ma własne konsorcja i są też inne - daj wybór
            self.show_consortium_contribution_choice(player_consortiums, other_consortiums)
        elif player_consortiums:
            # Gracz ma tylko własne konsorcja
            self.show_consortium_selection_for_contribution(player_consortiums, is_director=True)
        else:
            # Gracz nie ma własnych konsorcjów - może tylko składać wnioski
            self.show_consortium_selection_for_join(other_consortiums)

    def show_consortium_contribution_choice(self, player_consortiums, other_consortiums):
        """Pokazuje wybór między wpłacaniem do własnych konsorcjów a składaniem wniosków do innych"""
        popup = tk.Toplevel(self.root)
        popup.title("Wybór akcji")
        popup.geometry("400x300")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='lightblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text="WYBIERZ AKCJĘ", font=('Arial', 16, 'bold'), bg='lightblue').pack(pady=5)

        # Opcje
        options_frame = tk.Frame(popup)
        options_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Wpłać do własnego konsorcjum
        own_btn = tk.Button(options_frame, text="💰 Wpłać do mojego konsorcjum",
                           command=lambda: [popup.destroy(), self.show_consortium_selection_for_contribution(player_consortiums, is_director=True)],
                           bg='lightgreen', font=('Arial', 12, 'bold'), height=2)
        own_btn.pack(fill='x', pady=10)

        # Złóż wniosek do innego konsorcjum
        other_btn = tk.Button(options_frame, text="📝 Złóż wniosek o dołączenie do innego konsorcjum",
                             command=lambda: [popup.destroy(), self.show_consortium_selection_for_join(other_consortiums)],
                             bg='lightyellow', font=('Arial', 12, 'bold'), height=2)
        other_btn.pack(fill='x', pady=10)

        # Anuluj
        cancel_btn = tk.Button(options_frame, text="Anuluj", command=popup.destroy,
                              bg='lightgray', font=('Arial', 10))
        cancel_btn.pack(pady=10)

    def show_consortium_selection_for_contribution(self, consortiums, is_director=False):
        """Pokazuje interfejs wyboru konsorcjum do wpłacania zasobów"""
        popup = tk.Toplevel(self.root)
        popup.title("Wpłać do konsorcjum")
        popup.geometry("600x500")

        # Nagłówek
        header_color = 'gold' if is_director else 'lightgreen'
        header_text = "💰 WPŁAĆ DO KONSORCJUM" if is_director else "📝 DOŁĄCZ DO KONSORCJUM"
        header_frame = tk.Frame(popup, bg=header_color, relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text=header_text, font=('Arial', 16, 'bold'), bg=header_color).pack(pady=5)

        if is_director:
            tk.Label(header_frame, text="Jako kierownik możesz wpłacać bezpośrednio", font=('Arial', 10), bg=header_color).pack()
        else:
            tk.Label(header_frame, text="Złóż wniosek o dołączenie", font=('Arial', 10), bg=header_color).pack()

        # Obszar przewijania
        canvas = tk.Canvas(popup)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Lista konsorcjów
        for project in consortiums:
            project_frame = tk.Frame(scrollable_frame, bg='lightcyan', relief='raised', borderwidth=2)
            project_frame.pack(fill='x', padx=5, pady=5)

            # Nazwa i kierownik
            header_frame = tk.Frame(project_frame, bg='lightcyan')
            header_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(header_frame, text=project.name, font=('Arial', 12, 'bold'), bg='lightcyan').pack(side='left')
            if is_director:
                tk.Label(header_frame, text="👑 TWOJE KONSORCJUM", font=('Arial', 10), bg='lightcyan', fg='darkblue').pack(side='right')
            else:
                tk.Label(header_frame, text=f"👑 Kierownik: {project.director.name}", font=('Arial', 10), bg='lightcyan').pack(side='right')

            # Postęp
            progress_frame = tk.Frame(project_frame, bg='lightcyan')
            progress_frame.pack(fill='x', padx=5, pady=2)
            progress_text = f"Postęp: {project.contributed_pb} PB / {project.contributed_credits//1000}K zebrane"
            tk.Label(progress_frame, text=progress_text, font=('Arial', 9), bg='lightcyan').pack(anchor='w')

            # Przyciski wpłacania
            buttons_frame = tk.Frame(project_frame, bg='lightcyan')
            buttons_frame.pack(fill='x', padx=5, pady=5)

            if is_director:
                # Kierownik może wpłacać bezpośrednio
                pb_btn = tk.Button(buttons_frame, text="Wpłać 1 PB",
                                  command=lambda p=project: self.contribute_resources_to_project(p, "pb", 1, popup),
                                  bg='lightblue', font=('Arial', 9))
                pb_btn.pack(side='left', padx=2)

                credits_btn = tk.Button(buttons_frame, text="Wpłać 3K",
                                       command=lambda p=project: self.contribute_resources_to_project(p, "credits", 3000, popup),
                                       bg='lightblue', font=('Arial', 9))
                credits_btn.pack(side='left', padx=2)
            else:
                # Nie-kierownik składa wniosek
                join_btn = tk.Button(buttons_frame, text="Złóż wniosek o dołączenie",
                                    command=lambda p=project: self.request_consortium_membership(p, popup),
                                    bg='lightgreen', font=('Arial', 9))
                join_btn.pack(side='left', padx=2)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk anulowania
        tk.Button(popup, text="Anuluj", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def contribute_resources_to_project(self, project, resource_type, amount, popup):
        """Kierownik wpłaca zasoby bezpośrednio do swojego konsorcjum"""
        current_player = self.players[self.current_player_idx]

        if resource_type == "pb":
            if current_player.research_points >= amount:
                current_player.research_points -= amount
                project.contributed_pb += amount
                self.log_message(f"{current_player.name} wpłacił {amount} PB do konsorcjum: {project.name}")
            else:
                messagebox.showwarning("Uwaga", f"Brak wystarczających punktów badawczych! Potrzebujesz {amount} PB")
                return
        elif resource_type == "credits":
            if current_player.credits >= amount:
                current_player.credits -= amount
                project.contributed_credits += amount
                self.log_message(f"{current_player.name} wpłacił {amount//1000}K do konsorcjum: {project.name}")
            else:
                messagebox.showwarning("Uwaga", f"Brak wystarczających środków! Potrzebujesz {amount//1000}K")
                return

        popup.destroy()
        self.update_ui()

    def show_consortium_selection_for_join(self, available_consortiums):
        """Pokazuje interfejs wyboru konsorcjum do złożenia wniosku o członkostwo"""
        popup = tk.Toplevel(self.root)
        popup.title("Dołącz do Konsorcjum")
        popup.geometry("600x500")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='lightgreen', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text="🤝 DOŁĄCZ DO KONSORCJUM", font=('Arial', 16, 'bold'), bg='lightgreen').pack(pady=5)
        tk.Label(header_frame, text="Wybierz konsorcjum i złóż wniosek o dołączenie", font=('Arial', 10), bg='lightgreen').pack()

        # Obszar przewijania
        canvas = tk.Canvas(popup)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Lista konsorcjów
        for project in available_consortiums:
            project_frame = tk.Frame(scrollable_frame, bg='lightcyan', relief='raised', borderwidth=2)
            project_frame.pack(fill='x', padx=5, pady=5)

            # Nazwa i kierownik
            header_frame = tk.Frame(project_frame, bg='lightcyan')
            header_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(header_frame, text=project.name, font=('Arial', 12, 'bold'), bg='lightcyan').pack(side='left')
            tk.Label(header_frame, text=f"👑 Kierownik: {project.director.name}",
                    font=('Arial', 10), bg='lightcyan').pack(side='right')

            # Opis
            tk.Label(project_frame, text=project.description, font=('Arial', 9),
                    bg='lightcyan', wraplength=500).pack(anchor='w', padx=5, pady=2)

            # Postęp
            progress_frame = tk.Frame(project_frame, bg='lightcyan')
            progress_frame.pack(fill='x', padx=5, pady=2)
            progress_text = f"Postęp: {project.contributed_pb} PB / {project.contributed_credits//1000}K zebrane"
            tk.Label(progress_frame, text=progress_text, font=('Arial', 9), bg='lightcyan').pack(anchor='w')

            # Członkowie
            if project.members:
                members_text = "Członkowie: " + ", ".join([member.name for member in project.members])
                tk.Label(project_frame, text=members_text, font=('Arial', 8),
                        bg='lightcyan', wraplength=500).pack(anchor='w', padx=5, pady=2)

            # Nagroda członka
            reward_frame = tk.Frame(project_frame, bg='lightcyan')
            reward_frame.pack(fill='x', padx=5, pady=2)
            tk.Label(reward_frame, text=f"🎁 Nagroda członka: {project.member_reward}",
                    font=('Arial', 9, 'bold'), bg='lightcyan').pack(anchor='w')

            # Przycisk składania wniosku
            join_btn = ttk.Button(project_frame, text="Złóż wniosek o dołączenie",
                                 command=lambda p=project: self.request_consortium_membership(p, popup))
            join_btn.pack(pady=5)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk anulowania
        tk.Button(popup, text="Anuluj", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def request_consortium_membership(self, project, popup):
        """Składa wniosek o członkostwo w konsorcjum"""
        current_player = self.players[self.current_player_idx]

        # Sprawdź czy gracz już jest członkiem lub już złożył wniosek
        if current_player in project.members:
            messagebox.showinfo("Info", "Jesteś już członkiem tego konsorcjum!")
            return

        if current_player in project.pending_members:
            messagebox.showinfo("Info", "Już złożyłeś wniosek o dołączenie do tego konsorcjum!")
            return

        # Dodaj gracza do listy oczekujących
        project.pending_members.append(current_player)

        self.log_message(f"{current_player.name} złożył wniosek o dołączenie do konsorcjum: {project.name}")

        # Powiadomienie kierownika
        if hasattr(self, 'consortium_notifications'):
            self.consortium_notifications.append({
                'type': 'membership_request',
                'project': project,
                'applicant': current_player,
                'director': project.director
            })
        else:
            self.consortium_notifications = [{
                'type': 'membership_request',
                'project': project,
                'applicant': current_player,
                'director': project.director
            }]

        messagebox.showinfo("Sukces", f"Złożono wniosek o dołączenie do konsorcjum '{project.name}'. Kierownik zostanie powiadomiony.")

        popup.destroy()
        self.update_ui()

    def approve_consortium_membership(self, project, applicant):
        """Kierownik akceptuje wniosek o członkostwo"""
        if applicant in project.pending_members:
            project.pending_members.remove(applicant)
            project.members.append(applicant)

            # Usuń powiadomienie
            if hasattr(self, 'consortium_notifications'):
                self.consortium_notifications = [
                    notif for notif in self.consortium_notifications
                    if not (notif.get('type') == 'membership_request' and
                           notif.get('project') == project and
                           notif.get('applicant') == applicant)
                ]

            self.log_message(f"{project.director.name} zaakceptował {applicant.name} do konsorcjum: {project.name}")
            self.update_ui()
            return True
        return False

    def reject_consortium_membership(self, project, applicant):
        """Kierownik odrzuca wniosek o członkostwo"""
        if applicant in project.pending_members:
            project.pending_members.remove(applicant)

            # Usuń powiadomienie
            if hasattr(self, 'consortium_notifications'):
                self.consortium_notifications = [
                    notif for notif in self.consortium_notifications
                    if not (notif.get('type') == 'membership_request' and
                           notif.get('project') == project and
                           notif.get('applicant') == applicant)
                ]

            self.log_message(f"{project.director.name} odrzucił wniosek {applicant.name} o członkostwo w konsorcjum: {project.name}")
            self.update_ui()
            return True
        return False

    def show_consortium_management_panel(self):
        """Pokazuje panel zarządzania konsorcjami dla kierowników"""
        current_player = self.players[self.current_player_idx]

        # Znajdź konsorcja kierowane przez obecnego gracza
        managed_projects = [p for p in self.game_data.large_projects if p.director == current_player]

        if not managed_projects:
            messagebox.showinfo("Info", "Nie kierujesz żadnym konsorcjum")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Zarządzanie Konsorcjami")
        popup.geometry("700x600")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='gold', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text="👑 ZARZĄDZANIE KONSORCJAMI", font=('Arial', 16, 'bold'), bg='gold').pack(pady=5)
        tk.Label(header_frame, text="Zarządzaj swoimi konsorcjami i wnioskami o członkostwo", font=('Arial', 10), bg='gold').pack()

        # Obszar przewijania
        canvas = tk.Canvas(popup)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Lista zarządzanych konsorcjów
        for project in managed_projects:
            project_frame = tk.Frame(scrollable_frame, bg='lightyellow', relief='raised', borderwidth=3)
            project_frame.pack(fill='x', padx=5, pady=5)

            # Nazwa i status
            header_frame = tk.Frame(project_frame, bg='lightyellow')
            header_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(header_frame, text=f"👑 {project.name}", font=('Arial', 14, 'bold'), bg='lightyellow').pack(side='left')
            status_text = "✅ UKOŃCZONY" if project.is_completed else "🔨 W REALIZACJI"
            tk.Label(header_frame, text=status_text, font=('Arial', 10), bg='lightyellow').pack(side='right')

            # Postęp
            progress_frame = tk.Frame(project_frame, bg='lightyellow')
            progress_frame.pack(fill='x', padx=5, pady=2)
            progress_text = f"Zebrane zasoby: {project.contributed_pb} PB / {project.contributed_credits//1000}K"
            tk.Label(progress_frame, text=progress_text, font=('Arial', 10), bg='lightyellow').pack(anchor='w')

            # Członkowie
            if project.members:
                members_frame = tk.Frame(project_frame, bg='lightyellow')
                members_frame.pack(fill='x', padx=5, pady=2)
                members_text = "Członkowie: " + ", ".join([member.name for member in project.members])
                tk.Label(members_frame, text=members_text, font=('Arial', 9), bg='lightyellow').pack(anchor='w')

            # Oczekujące wnioski
            if project.pending_members:
                pending_frame = tk.LabelFrame(project_frame, text="⏳ Oczekujące wnioski o członkostwo", bg='lightyellow')
                pending_frame.pack(fill='x', padx=5, pady=5)

                for applicant in project.pending_members:
                    applicant_frame = tk.Frame(pending_frame, bg='lightcyan', relief='groove', borderwidth=1)
                    applicant_frame.pack(fill='x', padx=2, pady=2)

                    # Nazwa gracza
                    tk.Label(applicant_frame, text=f"👤 {applicant.name}", font=('Arial', 10, 'bold'), bg='lightcyan').pack(side='left', padx=5)

                    # Przyciski akceptacji/odrzucenia
                    button_frame = tk.Frame(applicant_frame, bg='lightcyan')
                    button_frame.pack(side='right', padx=5)

                    accept_btn = tk.Button(button_frame, text="✅ Akceptuj",
                                         command=lambda p=project, a=applicant: [self.approve_consortium_membership(p, a), popup.destroy(), self.show_consortium_management_panel()],
                                         bg='lightgreen', font=('Arial', 8))
                    accept_btn.pack(side='left', padx=2)

                    reject_btn = tk.Button(button_frame, text="❌ Odrzuć",
                                         command=lambda p=project, a=applicant: [self.reject_consortium_membership(p, a), popup.destroy(), self.show_consortium_management_panel()],
                                         bg='lightcoral', font=('Arial', 8))
                    reject_btn.pack(side='left', padx=2)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk zamknięcia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def show_independent_consortium_join(self):
        """Pokazuje interfejs dołączania do konsorcjów niezależnie od kart akcji"""
        current_player = self.players[self.current_player_idx]
        available_consortiums = [p for p in self.game_data.large_projects
                               if p.director and not p.is_completed and p.director != current_player]

        if not available_consortiums:
            messagebox.showinfo("Info", "Brak dostępnych konsorcjów do dołączenia")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Dołącz do Konsorcjum")
        popup.geometry("700x600")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='lightgreen', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text="🤝 DOŁĄCZ DO KONSORCJUM", font=('Arial', 16, 'bold'), bg='lightgreen').pack(pady=5)
        tk.Label(header_frame, text="Złóż wniosek o dołączenie do wybranego konsorcjum", font=('Arial', 10), bg='lightgreen').pack()
        tk.Label(header_frame, text="(Niezależne od kart akcji - możliwe w dowolnym momencie)",
                font=('Arial', 9, 'italic'), bg='lightgreen', fg='darkgreen').pack()

        # Obszar przewijania
        canvas = tk.Canvas(popup)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Lista dostępnych konsorcjów
        for project in available_consortiums:
            project_frame = tk.Frame(scrollable_frame, bg='lightcyan', relief='raised', borderwidth=2)
            project_frame.pack(fill='x', padx=5, pady=5)

            # Nagłówek projektu
            header_frame = tk.Frame(project_frame, bg='steelblue')
            header_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(header_frame, text=project.name, font=('Arial', 12, 'bold'),
                    bg='steelblue', fg='white').pack(side='left')
            tk.Label(header_frame, text=f"👑 Kierownik: {project.director.name}",
                    font=('Arial', 10), bg='steelblue', fg='lightgray').pack(side='right')

            # Opis projektu
            if project.description:
                desc_frame = tk.Frame(project_frame, bg='lightcyan')
                desc_frame.pack(fill='x', padx=5, pady=2)
                tk.Label(desc_frame, text=project.description, font=('Arial', 9),
                        bg='lightcyan', wraplength=600, justify='left').pack(anchor='w')

            # Postęp projektu
            progress_frame = tk.Frame(project_frame, bg='lightcyan')
            progress_frame.pack(fill='x', padx=5, pady=2)
            progress_text = f"📊 Postęp: {project.contributed_pb} PB / {project.contributed_credits//1000}K zebrane"
            tk.Label(progress_frame, text=progress_text, font=('Arial', 9), bg='lightcyan').pack(anchor='w')

            # Aktualni członkowie
            if project.members:
                members_frame = tk.Frame(project_frame, bg='lightcyan')
                members_frame.pack(fill='x', padx=5, pady=2)
                members_text = "👥 Członkowie: " + ", ".join([m.name for m in project.members])
                tk.Label(members_frame, text=members_text, font=('Arial', 9),
                        bg='lightcyan', fg='darkgreen').pack(anchor='w')

            # Oczekujący na akceptację
            if hasattr(project, 'pending_members') and project.pending_members:
                pending_frame = tk.Frame(project_frame, bg='lightcyan')
                pending_frame.pack(fill='x', padx=5, pady=2)
                pending_text = "⏳ Oczekują na akceptację: " + ", ".join([m.name for m in project.pending_members])
                tk.Label(pending_frame, text=pending_text, font=('Arial', 9),
                        bg='lightcyan', fg='orange').pack(anchor='w')

            # Nagroda dla członków
            reward_frame = tk.Frame(project_frame, bg='lightcyan')
            reward_frame.pack(fill='x', padx=5, pady=2)
            tk.Label(reward_frame, text=f"🎁 Nagroda członka: {project.member_reward}",
                    font=('Arial', 9, 'bold'), bg='lightcyan', fg='darkblue').pack(anchor='w')

            # Sprawdź status gracza względem tego projektu
            action_frame = tk.Frame(project_frame, bg='lightcyan')
            action_frame.pack(fill='x', padx=5, pady=5)

            if current_player in project.members:
                tk.Label(action_frame, text="✅ Jesteś już członkiem tego konsorcjum",
                        font=('Arial', 10, 'bold'), bg='lightcyan', fg='green').pack()
            elif current_player in project.pending_members:
                tk.Label(action_frame, text="⏳ Twój wniosek oczekuje na akceptację",
                        font=('Arial', 10, 'bold'), bg='lightcyan', fg='orange').pack()
            else:
                join_btn = tk.Button(action_frame, text="📝 Złóż wniosek o dołączenie",
                                   command=lambda p=project: self.request_consortium_membership_independent(p, popup),
                                   bg='lightgreen', font=('Arial', 10, 'bold'))
                join_btn.pack()

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk zamknięcia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def request_consortium_membership_independent(self, project, popup):
        """Składa wniosek o członkostwo niezależnie od kart akcji"""
        current_player = self.players[self.current_player_idx]

        # Sprawdź czy gracz już jest członkiem lub już złożył wniosek
        if current_player in project.members:
            messagebox.showinfo("Info", "Jesteś już członkiem tego konsorcjum!")
            return

        if current_player in project.pending_members:
            messagebox.showinfo("Info", "Już złożyłeś wniosek o dołączenie do tego konsorcjum!")
            return

        # Dodaj gracza do listy oczekujących
        project.pending_members.append(current_player)

        self.log_message(f"{current_player.name} złożył wniosek o dołączenie do konsorcjum: {project.name} (niezależnie)")

        # Powiadomienie kierownika
        if hasattr(self, 'consortium_notifications'):
            self.consortium_notifications.append({
                'type': 'membership_request',
                'project': project,
                'applicant': current_player,
                'director': project.director
            })
        else:
            self.consortium_notifications = [{
                'type': 'membership_request',
                'project': project,
                'applicant': current_player,
                'director': project.director
            }]

        messagebox.showinfo("Sukces", f"Złożono wniosek o dołączenie do konsorcjum '{project.name}'. Kierownik zostanie powiadomiony.")

        popup.destroy()
        self.update_ui()

    def start_consortium(self):
        """Zakłada konsorcjum"""
        current_player = self.players[self.current_player_idx]

        # Sprawdź czy gracz ma kartę konsorcjum w ręce
        consortium_cards = [card for card in current_player.hand_cards
                           if hasattr(card, 'card_type') and card.card_type == "KONSORCJUM"]
        if not consortium_cards:
            messagebox.showwarning("Uwaga", "Musisz mieć Kartę Konsorcjum w ręce, aby założyć konsorcjum!")
            return

        available_projects = [p for p in self.game_data.large_projects if not p.director]
        if not available_projects:
            messagebox.showinfo("Info", "Brak dostępnych Wielkich Projektów do założenia konsorcjum")
            return

        # Pokaż interfejs wyboru projektu
        self.show_project_selection_for_consortium(available_projects, consortium_cards[0])

    def show_project_selection_for_consortium(self, available_projects, consortium_card):
        """Pokazuje interfejs wyboru projektu do założenia konsorcjum"""
        popup = tk.Toplevel(self.root)
        popup.title("Załóż Konsorcjum")
        popup.geometry("600x500")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='gold', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text="🤝 ZAŁÓŻ KONSORCJUM", font=('Arial', 16, 'bold'), bg='gold').pack(pady=5)
        tk.Label(header_frame, text="Wybierz Wielki Projekt do objęcia kierownictwem", font=('Arial', 10), bg='gold').pack()

        # Obszar przewijania
        canvas = tk.Canvas(popup)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Lista projektów
        for project in available_projects:
            project_frame = tk.Frame(scrollable_frame, bg='lightgray', relief='raised', borderwidth=2)
            project_frame.pack(fill='x', padx=5, pady=5)

            # Nazwa i koszt
            name_frame = tk.Frame(project_frame, bg='lightgray')
            name_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(name_frame, text=project.name, font=('Arial', 12, 'bold'), bg='lightgray').pack(side='left')
            tk.Label(name_frame, text=f"💰 {project.cost_pb} PB | {project.cost_credits}K",
                    font=('Arial', 10), bg='lightgray').pack(side='right')

            # Opis
            tk.Label(project_frame, text=project.description, font=('Arial', 9),
                    bg='lightgray', wraplength=500).pack(anchor='w', padx=5, pady=2)

            # Nagroda kierownika
            reward_frame = tk.Frame(project_frame, bg='lightgray')
            reward_frame.pack(fill='x', padx=5, pady=2)
            tk.Label(reward_frame, text=f"👑 Nagroda kierownika: {project.director_reward}",
                    font=('Arial', 9, 'bold'), bg='lightgray').pack(anchor='w')

            # Przycisk założenia
            found_btn = ttk.Button(project_frame, text="Zostań kierownikiem tego projektu",
                                 command=lambda p=project: self.found_consortium_for_project(p, consortium_card, popup))
            found_btn.pack(pady=5)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk anulowania
        tk.Button(popup, text="Anuluj", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def found_consortium_for_project(self, project, consortium_card, popup):
        """Założyć konsorcjum dla wybranego projektu"""
        current_player = self.players[self.current_player_idx]

        # Usuń kartę konsorcjum z ręki
        if consortium_card in current_player.hand_cards:
            current_player.hand_cards.remove(consortium_card)

        # Ustaw kierownika i dodaj do członków
        project.director = current_player
        project.members.append(current_player)

        # Zwiększ punkty aktywności
        current_player.activity_points += 5

        self.log_message(f"{current_player.name} założył konsorcjum: {project.name} (użyto Kartę Konsorcjum)")

        popup.destroy()
        self.update_ui()

    def refresh_market(self):
        """Odświeża rynek"""
        available_journal_count = min(4, len(self.game_data.journals))
        self.available_journals = random.sample(self.game_data.journals, available_journal_count)

        available_scientist_count = min(4, len(self.game_data.scientists))
        self.available_scientists = random.sample(self.game_data.scientists, available_scientist_count)

        self.log_message("Odświeżono rynek czasopism i naukowców")

    def setup_cleanup_phase(self):
        """Konfiguruje interfejs fazy porządkowej"""
        ttk.Label(self.game_tab, text="🔧 Faza Porządkowa", font=('Arial', 14, 'bold')).pack(pady=20)

        cleanup_info = """
        Faza porządkowa:
        1. ✅ Wypłata pensji
        2. ✅ Sprawdzenie celów grantów
        3. ✅ Odświeżenie rynków
        4. ✅ Odzyskanie kart akcji
        5. ✅ Sprawdzenie końca gry
        """

        ttk.Label(self.game_tab, text=cleanup_info, justify='left', font=('Arial', 10)).pack(pady=20)

        # Pokaż wyniki rundy
        results_frame = ttk.LabelFrame(self.game_tab, text="📊 Wyniki rundy")
        results_frame.pack(fill='x', padx=20, pady=10)

        for player in self.players:
            player_result = f"{player.name}: {player.prestige_points} PZ, {player.credits//1000}K, {len(player.completed_research)} badań"
            ttk.Label(results_frame, text=player_result).pack(anchor='w', padx=10, pady=2)

    def setup_research_area(self):
        """Konfiguruje obszar badań"""
        # Wyczyść poprzedni UI
        for widget in self.research_frame.winfo_children():
            widget.destroy()

        if self.current_phase != GamePhase.AKCJE:
            return

        current_player = self.players[self.current_player_idx]

        # Tryb selekcji badania do rozpoczęcia
        if self.research_selection_mode:
            ttk.Label(self.research_frame, text="📋 WYBIERZ BADANIE DO ROZPOCZĘCIA",
                     font=('Arial', 11, 'bold'), foreground='red').pack(pady=5)

            selection_frame = ttk.LabelFrame(self.research_frame, text="🃏 Kliknij kartę aby podejrzeć")
            selection_frame.pack(fill='x', padx=5, pady=5)

            # Filtruj tylko karty badań z ręki
            research_cards_in_hand = [card for card in current_player.hand_cards if isinstance(card, ResearchCard)]

            for card in research_cards_in_hand:
                card_frame = tk.Frame(selection_frame, relief='groove', borderwidth=2, padx=5, pady=5)
                card_frame.pack(fill='x', padx=2, pady=2)

                # Nazwa i podstawowe info
                title_label = tk.Label(card_frame, text=f"{card.name} ({card.field})",
                                     font=('Arial', 10, 'bold'))
                title_label.pack(anchor='w')

                # Przycisk podglądu
                preview_btn = tk.Button(card_frame, text="Podgląd karty",
                                      command=lambda c=card: self.preview_research_card(c),
                                      bg='lightblue')
                preview_btn.pack(side='left', padx=(0, 5))

                # Przycisk wyboru (aktywny tylko jeśli karta jest wybrana)
                select_color = 'lightgreen' if card == self.selected_research_for_start else 'lightgray'
                select_btn = tk.Button(card_frame, text="Wybierz tę kartę",
                                     command=lambda c=card: self.select_research_for_start(c),
                                     bg=select_color)
                select_btn.pack(side='left', padx=(0, 5))

            # Przyciski akcji
            action_frame = tk.Frame(self.research_frame)
            action_frame.pack(fill='x', padx=5, pady=10)

            if self.selected_research_for_start:
                confirm_btn = tk.Button(action_frame, text="ZATWIERDŹ WYBÓR",
                                      command=self.confirm_research_start,
                                      bg='green', fg='white', font=('Arial', 10, 'bold'))
                confirm_btn.pack(side='left', padx=(0, 5))

            cancel_btn = tk.Button(action_frame, text="ANULUJ",
                                 command=self.cancel_research_selection,
                                 bg='red', fg='white')
            cancel_btn.pack(side='left')

        else:
            # Normalny tryb - karty na ręku (tylko podgląd)
            hand_frame = ttk.LabelFrame(self.research_frame, text="🃏 Karty na ręku (tylko podgląd)")
            hand_frame.pack(fill='x', padx=5, pady=5)

            for card in current_player.hand_cards:
                # Stwórz ramkę dla każdej karty
                card_container = tk.Frame(hand_frame)
                card_container.pack(fill='x', padx=2, pady=1)

                # Określ typ karty i odpowiedni tekst
                if hasattr(card, 'field'):  # ResearchCard
                    card_text = f"{card.name} ({card.field})"
                    preview_command = lambda c=card: self.preview_research_card(c)
                    is_intrigue = False
                    is_opportunity = False
                elif hasattr(card, 'card_type'):
                    if card.card_type == "KONSORCJUM":
                        card_text = f"🤝 {card.name}"
                        preview_command = lambda c=card: self.preview_consortium_card(c)
                        is_intrigue = False
                        is_opportunity = False
                    elif card.card_type == "INTRYGA":
                        card_text = f"🎭 {card.name}"
                        preview_command = lambda c=card: self.preview_intrigue_card(c)
                        is_intrigue = True
                        is_opportunity = False
                    elif card.card_type == "OKAZJA":
                        card_text = f"✨ {card.name}"
                        preview_command = lambda c=card: self.preview_opportunity_card(c)
                        is_intrigue = False
                        is_opportunity = True
                    else:
                        card_text = card.name
                        preview_command = lambda c=card: self.preview_generic_card(c)
                        is_intrigue = False
                        is_opportunity = False
                else:
                    card_text = card.name
                    preview_command = lambda c=card: self.preview_generic_card(c)
                    is_intrigue = False
                    is_opportunity = False

                if is_intrigue:
                    # Dla kart intryg: podgląd + czerwony przycisk użycia
                    preview_btn = ttk.Button(card_container, text=card_text,
                                           command=preview_command,
                                           width=25)
                    preview_btn.pack(side='left', fill='x', expand=True)

                    use_btn = tk.Button(card_container, text="UŻYJ",
                                      command=lambda c=card: self.use_intrigue_card(c),
                                      bg='red', fg='white', font=('Arial', 8, 'bold'),
                                      width=6)
                    use_btn.pack(side='right', padx=(2, 0))
                elif is_opportunity:
                    # Dla kart okazji: podgląd + zielony przycisk użycia
                    preview_btn = ttk.Button(card_container, text=card_text,
                                           command=preview_command,
                                           width=25)
                    preview_btn.pack(side='left', fill='x', expand=True)

                    use_btn = tk.Button(card_container, text="UŻYJ",
                                      command=lambda c=card: self.use_opportunity_card(c),
                                      bg='green', fg='white', font=('Arial', 8, 'bold'),
                                      width=6)
                    use_btn.pack(side='right', padx=(2, 0))
                else:
                    # Dla innych kart: tylko podgląd
                    card_btn = ttk.Button(card_container, text=card_text,
                                         command=preview_command)
                    card_btn.pack(fill='x')

        # Aktywne badania z zwijalnymi panelami
        if current_player.active_research:
            active_frame = ttk.LabelFrame(self.research_frame, text="🧪 Aktywne badania")
            active_frame.pack(fill='both', expand=True, padx=5, pady=5)

            # Przechowuj referencje do widgetów badań
            if not hasattr(self, 'research_widgets'):
                self.research_widgets = []

            # Wyczyść poprzednie widgety
            for widget in self.research_widgets:
                widget.destroy()
            self.research_widgets.clear()

            for research in current_player.active_research:
                # Stwórz zwijany widget badania
                research_widget = CollapsibleResearchWidget(
                    active_frame,
                    research,
                    self  # przekaż główny UI
                )
                research_widget.pack(fill='x', padx=2, pady=2)

                # Dodaj do listy referencji
                self.research_widgets.append(research_widget)

                # Auto-expand aktywne badanie (w trybie hex placement)
                if self.hex_placement_mode and research == self.current_research_for_hex:
                    research_widget.expand()

    def start_research(self, card: ResearchCard):
        """Rozpoczyna badanie z panelu kart"""
        current_player = self.players[self.current_player_idx]
        if card in current_player.hand_cards:
            current_player.hand_cards.remove(card)
            current_player.active_research.append(card)
            card.is_active = True

            # Initialize research for hex placement
            card.player_color = current_player.color
            card.player_path = []
            card.hexes_placed = 0

            self.log_message(f"Rozpoczęto badanie: {card.name}")
            self.update_ui()

    def collapse_siblings(self, current_widget):
        """Zwija wszystkie inne widgety badań (accordion behavior)"""
        if hasattr(self, 'research_widgets'):
            for widget in self.research_widgets:
                if widget != current_widget and widget.is_expanded:
                    widget.collapse()

    def auto_expand_research_widget(self, research):
        """Auto-rozwijanie widgetu badania przy rozpoczęciu hex placement"""
        if hasattr(self, 'research_widgets'):
            for widget in self.research_widgets:
                if widget.research == research:
                    widget.expand()
                    break

    def auto_collapse_all_research_widgets(self):
        """Auto-zwijanie wszystkich widgetów po zakończeniu hex placement"""
        if hasattr(self, 'research_widgets'):
            for widget in self.research_widgets:
                if widget.is_expanded:
                    widget.collapse()

    def take_grant(self, grant: GrantCard):
        """Gracz bierze grant"""
        current_player = self.players[self.current_player_idx]

        if current_player.current_grant is None:
            current_player.current_grant = grant
            self.available_grants.remove(grant)
            self.log_message(f"Wzięto grant: {grant.name}")

            # Przejdź do następnego gracza
            self.next_player()
            self.update_ui()
        else:
            messagebox.showwarning("Uwaga", "Masz już grant w tej rundzie!")

    def enter_research_selection_mode(self):
        """Włącza tryb selekcji badania do rozpoczęcia"""
        current_player = self.players[self.current_player_idx]

        if not current_player.hand_cards:
            messagebox.showinfo("Info", "Brak kart badań na ręku!")
            return

        self.research_selection_mode = True
        self.selected_research_for_start = None
        self.log_message(f"{current_player.name} wybiera badanie do rozpoczęcia")
        self.update_ui()

    def select_research_for_start(self, card: ResearchCard):
        """Wybiera kartę badania do rozpoczęcia"""
        self.selected_research_for_start = card
        self.log_message(f"Wybrano kartę: {card.name}")
        self.update_ui()

    def preview_research_card(self, card: ResearchCard):
        """Pokazuje podgląd karty badania"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Podgląd: {card.name}")
        popup.geometry("600x700")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='lightblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=card.name, font=('Arial', 14, 'bold'), bg='lightblue').pack(pady=5)
        tk.Label(header_frame, text=f"Dziedzina: {card.field}", font=('Arial', 10), bg='lightblue').pack()

        # Informacje o badaniu
        info_frame = tk.LabelFrame(popup, text="Informacje o badaniu")
        info_frame.pack(fill='both', expand=True, padx=5, pady=5)

        tk.Label(info_frame, text=f"Długość badania: {card.max_hexes} heksów",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"Nagroda podstawowa: {card.basic_reward}",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"Nagroda bonusowa: {card.bonus_reward}",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        # Opis
        desc_frame = tk.LabelFrame(popup, text="Opis")
        desc_frame.pack(fill='x', padx=5, pady=5)

        desc_text = tk.Text(desc_frame, height=4, wrap='word')
        desc_text.pack(fill='x', padx=5, pady=5)
        desc_text.insert(1.0, card.description)
        desc_text.config(state='disabled')

        # Wizualizacja heksów
        hex_frame = tk.LabelFrame(popup, text="Mapa heksagonalna")
        hex_frame.pack(fill='both', expand=True, padx=5, pady=5)

        if card.hex_research_map:
            # Użyj prawdziwej mapy heksagonalnej
            hex_widget = HexMapWidget(hex_frame, card.hex_research_map)
            hex_widget.pack(fill='both', expand=True, padx=5, pady=5)
        else:
            # Fallback - prosta wizualizacja
            hex_display = tk.Frame(hex_frame)
            hex_display.pack(pady=5)

            for i in range(card.max_hexes):
                color = 'green' if i == 0 else ('red' if i == card.max_hexes - 1 else 'lightgray')
                hex_label = tk.Label(hex_display, text='⬢', font=('Arial', 20), fg=color)
                hex_label.pack(side='left', padx=2)

        # Przycisk zamknięcia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def preview_scientist(self, scientist):
        """Pokazuje podgląd karty naukowca"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Podgląd: {scientist.name}")
        popup.geometry("350x400")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='lightgreen', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=scientist.name, font=('Arial', 14, 'bold'), bg='lightgreen').pack(pady=5)
        tk.Label(header_frame, text=f"Typ: {scientist.type.value}", font=('Arial', 10), bg='lightgreen').pack()

        # Informacje o naukowcu
        info_frame = tk.LabelFrame(popup, text="Informacje o naukowcu")
        info_frame.pack(fill='both', expand=True, padx=5, pady=5)

        tk.Label(info_frame, text=f"🔬 Dziedzina: {scientist.field}",
                font=('Arial', 10, 'bold')).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"💰 Pensja: {scientist.salary}K/rundę",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"⬢ Bonus heksów: {scientist.hex_bonus} heks/akcja",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"⭐ Specjalny bonus: {scientist.special_bonus}",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        # Opis
        desc_frame = tk.LabelFrame(popup, text="Opis")
        desc_frame.pack(fill='x', padx=5, pady=5)

        desc_text = tk.Text(desc_frame, height=4, wrap='word')
        desc_text.pack(fill='x', padx=5, pady=5)
        desc_text.insert(1.0, scientist.description)
        desc_text.config(state='disabled')

        # Przycisk zamknięcia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def preview_journal(self, journal):
        """Pokazuje podgląd karty czasopisma"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Podgląd: {journal.name}")
        popup.geometry("350x400")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='lightyellow', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=journal.name, font=('Arial', 14, 'bold'), bg='lightyellow').pack(pady=5)
        tk.Label(header_frame, text=f"Impact Factor: {journal.impact_factor}", font=('Arial', 10), bg='lightyellow').pack()

        # Informacje o czasopiśmie
        info_frame = tk.LabelFrame(popup, text="Informacje o czasopiśmie")
        info_frame.pack(fill='both', expand=True, padx=5, pady=5)

        tk.Label(info_frame, text=f"📊 Impact Factor: {journal.impact_factor}",
                font=('Arial', 10, 'bold')).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"💎 Koszt publikacji: {journal.pb_cost} PB",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"🏆 Nagroda PZ: {journal.pz_reward} PZ",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"📋 Wymagania: {journal.requirements}",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"⭐ Specjalny bonus: {journal.special_bonus}",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        # Opis
        desc_frame = tk.LabelFrame(popup, text="Opis")
        desc_frame.pack(fill='x', padx=5, pady=5)

        desc_text = tk.Text(desc_frame, height=4, wrap='word')
        desc_text.pack(fill='x', padx=5, pady=5)
        desc_text.insert(1.0, journal.description)
        desc_text.config(state='disabled')

        # Przycisk zamknięcia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def hire_scientist_direct(self, scientist):
        """Zatrudnia konkretnego naukowca bezpośrednio"""
        if not self.players:
            messagebox.showwarning("Błąd", "Brak graczy!")
            return

        current_player = self.players[self.current_player_idx]

        # Sprawdź koszty
        hire_cost = scientist.salary * 2
        if current_player.credits < hire_cost:
            messagebox.showwarning("Błąd", f"Brak środków! Koszt: {hire_cost}K")
            return

        # Zatrudnij
        current_player.credits -= hire_cost
        current_player.scientists.append(scientist)

        # Usuń z rynku
        self.available_scientists.remove(scientist)

        self.log_message(f"Zatrudniono: {scientist.name} za {hire_cost}K")
        self.update_markets()
        self.update_ui()

    def publish_in_journal_direct(self, journal):
        """Publikuje w konkretnym czasopiśmie bezpośrednio"""
        if not self.players:
            messagebox.showwarning("Błąd", "Brak graczy!")
            return

        current_player = self.players[self.current_player_idx]

        # Sprawdź koszty
        if current_player.research_points < journal.pb_cost:
            messagebox.showwarning("Błąd", f"Brak punktów badań! Koszt: {journal.pb_cost} PB")
            return

        # Sprawdź wymagania reputacji (parsuj z requirements)
        rep_required = 0
        if "Reputacja" in journal.requirements:
            try:
                rep_text = journal.requirements.split("Reputacja")[1].strip()
                rep_required = int(rep_text.split("+")[0].strip())
            except:
                rep_required = 0

        if current_player.reputation < rep_required:
            messagebox.showwarning("Błąd", f"Niewystarczająca reputacja! Wymagana: {rep_required}")
            return

        # Publikuj
        current_player.research_points -= journal.pb_cost
        current_player.prestige_points += journal.pz_reward
        current_player.publications += 1
        current_player.activity_points += 3  # Punkt aktywności za publikację

        # Dodaj do historii publikacji
        import copy
        current_player.publication_history.append(copy.deepcopy(journal))

        self.log_message(f"Opublikowano w {journal.name} za {journal.pb_cost} PB, +{journal.pz_reward} PZ")
        self.update_ui()

    def hire_scientist_from_market(self, scientist):
        """Zatrudnia naukowca z rynku podczas akcji ZATRUDNIJ PERSONEL"""
        if not (hasattr(self, 'current_action_card') and self.current_action_card and
                self.current_action_card.action_type == ActionType.ZATRUDNIJ):
            messagebox.showwarning("Błąd", "Musisz najpierw zagrać kartę ZATRUDNIJ PERSONEL!")
            return

        current_player = self.players[self.current_player_idx]

        # Sprawdź koszty w punktach akcji
        pa_cost = 2 if scientist.type == ScientistType.DOKTOR else 3 if scientist.type == ScientistType.PROFESOR else 1
        if self.remaining_action_points < pa_cost:
            messagebox.showwarning("Błąd", f"Brak punktów akcji! Wymagane: {pa_cost} PA")
            return

        # Sprawdź koszty finansowe (koszt zatrudnienia = 2x pensja)
        hire_cost = scientist.salary * 2
        if current_player.credits < hire_cost:
            messagebox.showwarning("Błąd", f"Brak środków! Koszt: {hire_cost}K")
            return

        # Zatrudnij
        current_player.credits -= hire_cost
        current_player.scientists.append(scientist)
        self.remaining_action_points -= pa_cost

        # Usuń z rynku
        self.available_scientists.remove(scientist)

        # Dodaj punkty aktywności
        current_player.activity_points += 2

        self.log_message(f"Zatrudniono {scientist.name} za {hire_cost}K (-{pa_cost} PA)")
        self.update_markets()
        self.update_ui()
        self.update_action_menu()

    def publish_in_journal_from_market(self, journal):
        """Publikuje w czasopiśmie z rynku podczas akcji PUBLIKUJ"""
        if not (hasattr(self, 'current_action_card') and self.current_action_card and
                self.current_action_card.action_type == ActionType.PUBLIKUJ):
            messagebox.showwarning("Błąd", "Musisz najpierw zagrać kartę PUBLIKUJ!")
            return

        current_player = self.players[self.current_player_idx]

        # Sprawdź koszty
        if current_player.research_points < journal.pb_cost:
            messagebox.showwarning("Błąd", f"Brak punktów badań! Koszt: {journal.pb_cost} PB")
            return

        # Sprawdź wymagania reputacji
        rep_required = 0
        if "Reputacja" in journal.requirements:
            try:
                rep_text = journal.requirements.split("Reputacja")[1].strip()
                rep_required = int(rep_text.split("+")[0].strip())
            except:
                rep_required = 0

        if current_player.reputation < rep_required:
            messagebox.showwarning("Błąd", f"Niewystarczająca reputacja! Wymagana: {rep_required}")
            return

        # Publikuj (akcja podstawowa - nie kosztuje PA)
        current_player.research_points -= journal.pb_cost
        current_player.prestige_points += journal.pz_reward
        current_player.publications += 1
        current_player.activity_points += 3  # Punkt aktywności za publikację

        # Dodaj do historii publikacji
        import copy
        current_player.publication_history.append(copy.deepcopy(journal))

        self.log_message(f"Opublikowano w {journal.name} za {journal.pb_cost} PB → +{journal.pz_reward} PZ")
        self.update_ui()

    def show_journal_selection_for_publish(self):
        """Pokazuje okno wyboru czasopisma dla akcji podstawowej PUBLIKUJ"""
        if not self.available_journals:
            messagebox.showinfo("Info", "Brak dostępnych czasopism na rynku")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Wybierz czasopismo do publikacji")
        popup.geometry("500x600")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='lightsteelblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text="Wybierz czasopismo do publikacji",
                font=('Arial', 14, 'bold'), bg='lightsteelblue').pack(pady=5)
        tk.Label(header_frame, text="(Akcja podstawowa - nie kosztuje PA)",
                font=('Arial', 10), bg='lightsteelblue').pack()

        # Scrollable frame dla czasopism
        canvas = tk.Canvas(popup, height=450)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for journal in self.available_journals:
            journal_frame = tk.Frame(scrollable_frame, relief='raised', borderwidth=2, bg='lightyellow')
            journal_frame.pack(fill='x', padx=5, pady=5)

            # Nazwa i impact factor
            name_frame = tk.Frame(journal_frame, bg='lightyellow')
            name_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(name_frame, text=journal.name, font=('Arial', 12, 'bold'), bg='lightyellow').pack(side='left')
            tk.Label(name_frame, text=f"IF: {journal.impact_factor}", font=('Arial', 10), bg='lightyellow').pack(side='right')

            # Szczegóły
            details_frame = tk.Frame(journal_frame, bg='lightyellow')
            details_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(details_frame, text=f"💰 {journal.pb_cost} PB", font=('Arial', 10), bg='lightyellow').pack(side='left')
            tk.Label(details_frame, text=f"⭐ +{journal.pz_reward} PZ", font=('Arial', 10), bg='lightyellow').pack(side='left', padx=(10,0))

            # Wymagania
            if journal.requirements != "Brak wymagań":
                req_frame = tk.Frame(journal_frame, bg='lightyellow')
                req_frame.pack(fill='x', padx=5, pady=2)
                tk.Label(req_frame, text=f"📋 {journal.requirements}", font=('Arial', 9), bg='lightyellow').pack()

            # Bonus specjalny
            if journal.special_bonus != "Brak":
                bonus_frame = tk.Frame(journal_frame, bg='lightyellow')
                bonus_frame.pack(fill='x', padx=5, pady=2)
                tk.Label(bonus_frame, text=f"🎁 {journal.special_bonus}", font=('Arial', 9), bg='lightyellow').pack()

            # Przycisk publikacji
            publish_btn = ttk.Button(journal_frame, text="Publikuj",
                                   command=lambda j=journal: [self.publish_in_journal_from_market(j), popup.destroy()])
            publish_btn.pack(pady=5)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk anulowania
        tk.Button(popup, text="Anuluj", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def show_scientist_selection(self, scientist_type: ScientistType, pa_cost: int):
        """Pokazuje okno wyboru naukowca z rynku dla danego typu"""
        # Filtruj dostępnych naukowców według typu
        available_scientists = [s for s in self.available_scientists if s.type == scientist_type]

        if not available_scientists:
            messagebox.showinfo("Info", f"Brak dostępnych naukowców typu {scientist_type.value} na rynku")
            return

        popup = tk.Toplevel(self.root)
        popup.title(f"Wybierz {scientist_type.value}")
        popup.geometry("400x500")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='lightsteelblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=f"Wybierz {scientist_type.value} do zatrudnienia",
                font=('Arial', 14, 'bold'), bg='lightsteelblue').pack(pady=5)
        tk.Label(header_frame, text=f"Koszt: {pa_cost} PA",
                font=('Arial', 10), bg='lightsteelblue').pack()

        # Scrollable frame dla naukowców
        canvas = tk.Canvas(popup, height=350)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for scientist in available_scientists:
            scientist_frame = tk.Frame(scrollable_frame, relief='raised', borderwidth=2, bg='lightblue')
            scientist_frame.pack(fill='x', padx=5, pady=5)

            # Nazwa i podstawowe info
            name_frame = tk.Frame(scientist_frame, bg='lightblue')
            name_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(name_frame, text=scientist.name, font=('Arial', 12, 'bold'), bg='lightblue').pack(side='left')
            tk.Label(name_frame, text=f"{scientist.field}", font=('Arial', 10), bg='lightblue').pack(side='right')

            # Szczegóły
            details_frame = tk.Frame(scientist_frame, bg='lightblue')
            details_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(details_frame, text=f"💰 {scientist.salary * 2}K (koszt)", font=('Arial', 10), bg='lightblue').pack(side='left')
            tk.Label(details_frame, text=f"⬢ {scientist.hex_bonus} heks", font=('Arial', 10), bg='lightblue').pack(side='left', padx=(10,0))

            # Bonus
            if scientist.special_bonus != "Brak":
                bonus_frame = tk.Frame(scientist_frame, bg='lightblue')
                bonus_frame.pack(fill='x', padx=5, pady=2)
                tk.Label(bonus_frame, text=f"⭐ {scientist.special_bonus}", font=('Arial', 9), bg='lightblue').pack()

            # Przycisk zatrudnienia
            hire_btn = ttk.Button(scientist_frame, text="Zatrudnij",
                                command=lambda s=scientist: [self.hire_scientist_from_action(s, pa_cost), popup.destroy()])
            hire_btn.pack(pady=5)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk anulowania
        tk.Button(popup, text="Anuluj", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def hire_scientist_from_action(self, scientist, pa_cost: int):
        """Zatrudnia naukowca podczas akcji z menu"""
        current_player = self.players[self.current_player_idx]

        # Sprawdź koszty finansowe
        hire_cost = scientist.salary * 2
        if current_player.credits < hire_cost:
            messagebox.showwarning("Błąd", f"Brak środków! Koszt: {hire_cost}K")
            return

        # Zatrudnij (PA zostało już odejmowane w execute_additional_action)
        current_player.credits -= hire_cost
        current_player.scientists.append(scientist)

        # Usuń z rynku
        self.available_scientists.remove(scientist)

        # Dodaj punkty aktywności
        current_player.activity_points += 2

        self.log_message(f"Zatrudniono {scientist.name} za {hire_cost}K")
        self.update_markets()
        self.update_ui()
        self.update_action_menu()

    def show_employed_scientists(self, player):
        """Pokazuje okno z zatrudnionymi naukowcami gracza"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Zatrudnieni naukowcy - {player.name}")
        popup.geometry("500x600")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='lightcyan', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=f"Zespół {player.name}", font=('Arial', 14, 'bold'), bg='lightcyan').pack(pady=5)
        tk.Label(header_frame, text=f"Zatrudnionych: {len(player.scientists)}", font=('Arial', 10), bg='lightcyan').pack()

        # Scrollable frame dla naukowców
        canvas = tk.Canvas(popup, height=450)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        if player.scientists:
            for scientist in player.scientists:
                scientist_frame = tk.Frame(scrollable_frame, relief='raised', borderwidth=2, bg='lightblue')
                scientist_frame.pack(fill='x', padx=5, pady=5)

                # Pierwsza linia - nazwa i typ
                name_frame = tk.Frame(scientist_frame, bg='lightblue')
                name_frame.pack(fill='x', padx=5, pady=2)

                tk.Label(name_frame, text=scientist.name, font=('Arial', 12, 'bold'), bg='lightblue').pack(side='left')
                tk.Label(name_frame, text=f"({scientist.type.value})", font=('Arial', 10), bg='lightblue').pack(side='right')

                # Druga linia - podstawowe info
                info_frame = tk.Frame(scientist_frame, bg='lightblue')
                info_frame.pack(fill='x', padx=5, pady=2)

                tk.Label(info_frame, text=f"🔬 {scientist.field}", font=('Arial', 10), bg='lightblue').pack(side='left')
                tk.Label(info_frame, text=f"💰 {scientist.salary}K/rundę", font=('Arial', 10), bg='lightblue').pack(side='left', padx=(10,0))
                tk.Label(info_frame, text=f"⬢ {scientist.hex_bonus} heks", font=('Arial', 10), bg='lightblue').pack(side='left', padx=(10,0))

                # Trzecia linia - bonus i status
                bonus_frame = tk.Frame(scientist_frame, bg='lightblue')
                bonus_frame.pack(fill='x', padx=5, pady=2)

                tk.Label(bonus_frame, text=f"⭐ {scientist.special_bonus}", font=('Arial', 9), bg='lightblue').pack(side='left')

                # Status opłacenia
                status = "✅ Opłacony" if scientist.is_paid else "❌ Nieopłacony"
                status_color = 'green' if scientist.is_paid else 'red'
                tk.Label(bonus_frame, text=status, font=('Arial', 9, 'bold'), fg=status_color, bg='lightblue').pack(side='right')

                # Przycisk podglądu szczegółowego
                preview_btn = ttk.Button(scientist_frame, text="👁️ Szczegóły",
                                       command=lambda s=scientist: self.preview_scientist(s))
                preview_btn.pack(pady=5)

        else:
            tk.Label(scrollable_frame, text="Brak zatrudnionych naukowców",
                    font=('Arial', 12), fg='gray').pack(pady=50)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk zamknięcia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def confirm_research_start(self):
        """Zatwierdza rozpoczęcie wybranego badania"""
        if not self.selected_research_for_start:
            messagebox.showwarning("Uwaga", "Nie wybrano karty badania!")
            return

        current_player = self.players[self.current_player_idx]
        card = self.selected_research_for_start

        # Rozpocznij badanie
        current_player.hand_cards.remove(card)
        current_player.active_research.append(card)
        card.is_active = True

        self.log_message(f"Rozpoczęto badanie: {card.name}")

        # Wyjdź z trybu selekcji
        self.research_selection_mode = False
        self.selected_research_for_start = None

        self.update_ui()

    def cancel_research_selection(self):
        """Anuluje selekcję badania"""
        self.research_selection_mode = False
        self.selected_research_for_start = None

        # Zwróć punkt akcji
        self.remaining_action_points += 1

        self.log_message("Anulowano wybór badania")
        self.update_ui()

    def select_scenario(self):
        """Pozwala graczowi wybrać scenariusz gry"""
        scenario_popup = tk.Toplevel(self.root)
        scenario_popup.title("Wybór Scenariusza")
        scenario_popup.geometry("800x600")
        scenario_popup.grab_set()  # Modal dialog

        # Nagłówek
        header_frame = tk.Frame(scenario_popup, bg='darkblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text="🎭 WYBÓR SCENARIUSZA GRY",
                font=('Arial', 18, 'bold'), bg='darkblue', fg='white').pack(pady=10)

        tk.Label(header_frame, text="Wybierz scenariusz, który określi warunki tej rozgrywki",
                font=('Arial', 12), bg='darkblue', fg='lightgray').pack(pady=(0, 10))

        # Scrollable frame dla scenariuszy
        canvas = tk.Canvas(scenario_popup, height=450)
        scrollbar = ttk.Scrollbar(scenario_popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        selected_scenario = [None]  # Lista do przechowania wyboru (mutable)

        for scenario in self.game_data.scenarios:
            scenario_frame = tk.Frame(scrollable_frame, relief='raised', borderwidth=2, bg='lightblue')
            scenario_frame.pack(fill='x', padx=10, pady=5)

            # Nagłówek scenariusza
            header = tk.Frame(scenario_frame, bg='steelblue')
            header.pack(fill='x', padx=5, pady=5)

            tk.Label(header, text=scenario.name, font=('Arial', 14, 'bold'),
                    bg='steelblue', fg='white').pack(pady=5)

            # Element fabularny
            story_frame = tk.Frame(scenario_frame, bg='lightblue')
            story_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(story_frame, text="📖 FABUŁA:", font=('Arial', 10, 'bold'),
                    bg='lightblue').pack(anchor='w')
            tk.Label(story_frame, text=scenario.story_element, font=('Arial', 10),
                    bg='lightblue', wraplength=700, justify='left').pack(anchor='w', padx=20)

            # Modyfikatory globalne
            mods_frame = tk.Frame(scenario_frame, bg='lightblue')
            mods_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(mods_frame, text="⚙️ MODYFIKATORY:", font=('Arial', 10, 'bold'),
                    bg='lightblue').pack(anchor='w')
            tk.Label(mods_frame, text=scenario.global_modifiers, font=('Arial', 10),
                    bg='lightblue', wraplength=700, justify='left').pack(anchor='w', padx=20)

            # Informacje o grze
            info_frame = tk.Frame(scenario_frame, bg='lightblue')
            info_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(info_frame, text="🎯 WARUNKI GRY:", font=('Arial', 10, 'bold'),
                    bg='lightblue').pack(anchor='w')
            tk.Label(info_frame, text=f"Maksymalnie rund: {scenario.max_rounds}",
                    font=('Arial', 10), bg='lightblue').pack(anchor='w', padx=20)
            tk.Label(info_frame, text=f"Zwycięstwo: {scenario.victory_conditions}",
                    font=('Arial', 10), bg='lightblue').pack(anchor='w', padx=20)
            tk.Label(info_frame, text=f"Kryzysy: {scenario.crisis_count} kart w rundach {scenario.crisis_rounds}",
                    font=('Arial', 10), bg='lightblue').pack(anchor='w', padx=20)

            # Przycisk wyboru
            select_btn = ttk.Button(scenario_frame, text="WYBIERZ TEN SCENARIUSZ",
                                  command=lambda s=scenario: [selected_scenario.__setitem__(0, s), scenario_popup.destroy()])
            select_btn.pack(pady=10)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Czekaj na wybór scenariusza
        scenario_popup.wait_window()

        if selected_scenario[0]:
            self.current_scenario = selected_scenario[0]
            self.prepare_crisis_deck()
            self.log_message(f"Wybrano scenariusz: {self.current_scenario.name}")
        else:
            # Jeśli nie wybrano, użyj pierwszego scenariusza
            self.current_scenario = self.game_data.scenarios[0]
            self.prepare_crisis_deck()
            self.log_message(f"Użyto domyślnego scenariusza: {self.current_scenario.name}")

        # Aktualizuj wyświetlanie scenariusza
        self.update_scenario_display()
        self.update_round_display()
        self.update_crisis_display()

    def prepare_crisis_deck(self):
        """Przygotowuje talię kryzysów na podstawie wybranego scenariusza"""
        if not self.current_scenario:
            return

        # Wybierz losowe kryzysy z dostępnej puli
        available_crises = self.game_data.crisis_cards.copy()
        random.shuffle(available_crises)

        # Dobierz odpowiednią liczbę kryzysów
        self.crisis_deck = available_crises[:self.current_scenario.crisis_count]

        self.log_message(f"Przygotowano {len(self.crisis_deck)} kryzysów na rundy {self.current_scenario.crisis_rounds}")

    def check_for_crisis(self):
        """Sprawdza czy w aktualnej rundzie powinien zostać odkryty kryzys"""
        if not self.current_scenario or not self.crisis_deck:
            return

        # Sprawdź czy aktualna runda jest w liście rund kryzysowych
        if self.game_data.current_round in self.current_scenario.crisis_rounds:
            # Znajdź indeks rundy w liście
            crisis_index = self.current_scenario.crisis_rounds.index(self.game_data.current_round)

            # Sprawdź czy mamy jeszcze kryzysy do odkrycia
            if crisis_index < len(self.crisis_deck):
                crisis = self.crisis_deck[crisis_index]
                self.reveal_crisis(crisis)

    def reveal_crisis(self, crisis: CrisisCard):
        """Odkrywa i aktywuje kryzys"""
        self.game_data.revealed_crises.append(crisis)

        # Pokaż informację o kryzysie
        messagebox.showinfo(
            f"KRYZYS - Runda {self.game_data.current_round}",
            f"🚨 {crisis.name}\n\n{crisis.description}\n\nEfekt: {crisis.effect}\n\nEfekt jest aktywny natychmiast!"
        )

        # Zastosuj efekt kryzysu
        self.apply_crisis_effect(crisis)

        # Aktualizuj interfejs
        self.update_crisis_display()
        self.log_message(f"KRYZYS AKTYWOWANY: {crisis.name}")

    def apply_crisis_effect(self, crisis: CrisisCard):
        """Stosuje efekt kryzysu do wszystkich graczy"""
        # Tutaj można dodać konkretną logikę dla różnych typów kryzysów
        # Na razie tylko logujemy efekt
        self.log_message(f"Efekt kryzysu: {crisis.effect}")

        # Przykłady możliwych efektów (do rozwinięcia w przyszłości):
        if "pensje" in crisis.effect.lower():
            self.log_message("💰 Wszystkie pensje kosztują więcej w tej rundzie")
        elif "badania" in crisis.effect.lower():
            self.log_message("🔬 Badania są trudniejsze w tej rundzie")
        elif "reputacja" in crisis.effect.lower():
            self.log_message("⭐ Wpływ na reputację wszystkich graczy")

    def advance_round(self):
        """Rozpoczyna nową rundę i sprawdza kryzysy"""
        self.game_data.current_round += 1
        self.log_message(f"\n🕒 RUNDA {self.game_data.current_round}")

        # Sprawdź czy kończymy grę
        if self.current_scenario and self.game_data.current_round > self.current_scenario.max_rounds:
            self.end_game()
            return

        # Sprawdź kryzysy na początek rundy
        self.check_for_crisis()

        # Aktualizuj interfejs
        self.update_round_display()

    def update_round_display(self):
        """Aktualizuje wyświetlanie informacji o rundzie"""
        round_info = f"Runda: {self.game_data.current_round}"
        if self.current_scenario:
            round_info += f"/{self.current_scenario.max_rounds}"

        self.round_label.config(text=round_info)

    def update_crisis_display(self):
        """Aktualizuje wyświetlanie aktywnych kryzysów"""
        if not self.game_data.revealed_crises:
            self.active_crisis_text.config(text="Brak", foreground='green')
        else:
            crisis_names = [crisis.name for crisis in self.game_data.revealed_crises]
            crisis_text = ", ".join(crisis_names)
            self.active_crisis_text.config(text=crisis_text, foreground='red')

    def update_scenario_display(self):
        """Aktualizuje wyświetlanie informacji o scenariuszu"""
        if self.current_scenario:
            scenario_text = f"Scenariusz: {self.current_scenario.name}"
            self.scenario_label.config(text=scenario_text)
        else:
            self.scenario_label.config(text="Scenariusz: Brak")

    def end_game(self):
        """Kończy grę i podsumowuje wyniki"""
        messagebox.showinfo(
            "Koniec gry",
            f"Gra zakończona po {self.current_scenario.max_rounds} rundach!\n\n"
            f"Scenariusz: {self.current_scenario.name}\n"
            f"Warunki zwycięstwa: {self.current_scenario.victory_conditions}"
        )

    def hire_scientist(self, scientist_type: ScientistType):
        """Zatrudnia naukowca bezpośrednio (np. doktoranta)"""
        current_player = self.players[self.current_player_idx]

        # Utwórz nowego naukowca odpowiedniego typu
        if scientist_type == ScientistType.DOKTORANT:
            new_scientist = Scientist("Doktorant", ScientistType.DOKTORANT, "Uniwersalny", 0, 1, "Brak", "Młody naukowiec")
            hire_cost = 0  # Doktorant nie kosztuje pieniędzy
        elif scientist_type == ScientistType.DOKTOR:
            new_scientist = Scientist("Dr Nowy", ScientistType.DOKTOR, "Uniwersalny", 2000, 2, "Brak", "Nowo zatrudniony doktor")
            hire_cost = 4000  # 2x pensja
        elif scientist_type == ScientistType.PROFESOR:
            new_scientist = Scientist("Prof. Nowy", ScientistType.PROFESOR, "Uniwersalny", 3000, 3, "Brak", "Nowo zatrudniony profesor")
            hire_cost = 6000  # 2x pensja
        else:
            messagebox.showwarning("Błąd", f"Nieznany typ naukowca: {scientist_type}")
            return

        # Sprawdź koszty finansowe
        if current_player.credits < hire_cost:
            messagebox.showwarning("Błąd", f"Brak środków! Koszt: {hire_cost//1000}K")
            return

        # Zatrudnij
        current_player.credits -= hire_cost
        current_player.scientists.append(new_scientist)

        # Dodaj punkty aktywności
        current_player.activity_points += 2

        if hire_cost > 0:
            self.log_message(f"Zatrudniono {new_scientist.name} za {hire_cost//1000}K")
        else:
            self.log_message(f"Zatrudniono {new_scientist.name} (bez kosztów)")

        self.update_ui()
        self.update_action_menu()

    def preview_research_card(self, card):
        """Pokazuje podgląd karty badania"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Podgląd: {card.name}")
        popup.geometry("600x700")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='lightblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=card.name, font=('Arial', 16, 'bold'), bg='lightblue').pack(pady=5)
        tk.Label(header_frame, text=f"Dziedzina: {card.field}", font=('Arial', 12), bg='lightblue').pack()

        # Szczegóły
        details_frame = tk.Frame(popup)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)

        tk.Label(details_frame, text=f"Nagroda podstawowa: {card.basic_reward}", font=('Arial', 11)).pack(anchor='w')
        tk.Label(details_frame, text=f"Nagroda bonusowa: {card.bonus_reward}", font=('Arial', 11)).pack(anchor='w')
        tk.Label(details_frame, text=f"Maksymalne heksy: {card.max_hexes}", font=('Arial', 11)).pack(anchor='w')

        # Opis
        if card.description:
            desc_frame = tk.LabelFrame(details_frame, text="Opis")
            desc_frame.pack(fill='x', pady=10)
            tk.Label(desc_frame, text=card.description, font=('Arial', 10), wraplength=500, justify='left').pack(padx=5, pady=5)

        # Mapa heksagonalna (jeśli istnieje)
        if card.hex_research_map:
            map_frame = tk.LabelFrame(details_frame, text="Mapa badania")
            map_frame.pack(fill='both', expand=True, pady=10)
            hex_widget = HexMapWidget(map_frame, card.hex_research_map)
            hex_widget.pack(fill='both', expand=True)

        # Przycisk zamknięcia
        tk.Button(popup, text="Zamknij", command=popup.destroy, font=('Arial', 10)).pack(pady=10)

    def preview_consortium_card(self, card):
        """Pokazuje podgląd karty konsorcjum"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Podgląd: {card.name}")
        popup.geometry("400x300")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='gold', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text="🤝 KARTA KONSORCJUM", font=('Arial', 16, 'bold'), bg='gold').pack(pady=5)

        # Szczegóły
        details_frame = tk.Frame(popup)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)

        tk.Label(details_frame, text="Ta karta umożliwia zostanie kierownikiem konsorcjum.",
                font=('Arial', 12), wraplength=350, justify='center').pack(pady=20)

        tk.Label(details_frame, text="• Pozwala zostać kierownikiem konsorcjum", font=('Arial', 10)).pack(anchor='w', pady=2)
        tk.Label(details_frame, text="• Umożliwia założenie nowego konsorcjum", font=('Arial', 10)).pack(anchor='w', pady=2)
        tk.Label(details_frame, text="• Do dołączenia do istniejącego konsorcjum nie jest potrzebna", font=('Arial', 10)).pack(anchor='w', pady=2)

        # Przycisk zamknięcia
        tk.Button(popup, text="Zamknij", command=popup.destroy, font=('Arial', 10)).pack(pady=10)

    def preview_intrigue_card(self, card):
        """Pokazuje podgląd karty intryg"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Podgląd: {card.name}")
        popup.geometry("450x350")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='darkred', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=f"🎭 {card.name}", font=('Arial', 16, 'bold'), bg='darkred', fg='white').pack(pady=5)

        # Szczegóły
        details_frame = tk.Frame(popup)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Cel
        target_text = {
            "opponent": "Przeciwnik",
            "all": "Wszyscy gracze",
            "self": "Ty"
        }.get(card.target, card.target)

        tk.Label(details_frame, text=f"Cel: {target_text}", font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)

        # Efekt
        tk.Label(details_frame, text=f"Efekt: {card.effect}", font=('Arial', 11),
                wraplength=400, justify='left').pack(anchor='w', pady=5)

        # Opis
        if card.description:
            desc_frame = tk.LabelFrame(details_frame, text="Opis")
            desc_frame.pack(fill='x', pady=10)
            tk.Label(desc_frame, text=card.description, font=('Arial', 10),
                    wraplength=400, justify='left').pack(padx=5, pady=5)

        # Przycisk zamknięcia
        tk.Button(popup, text="Zamknij", command=popup.destroy, font=('Arial', 10)).pack(pady=10)

    def preview_opportunity_card(self, card):
        """Pokazuje podgląd karty okazji"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Podgląd: {card.name}")
        popup.geometry("450x350")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='green', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=f"✨ {card.name}", font=('Arial', 16, 'bold'), bg='green', fg='white').pack(pady=5)

        # Szczegóły
        details_frame = tk.Frame(popup)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Typ bonusu
        bonus_types = {
            "credits": "Kredyty",
            "research_points": "Punkty badań",
            "reputation": "Reputacja",
            "hex": "Heksy",
            "action_points": "Punkty akcji"
        }
        bonus_name = bonus_types.get(card.bonus_type, card.bonus_type)

        tk.Label(details_frame, text=f"Bonus: +{card.bonus_value} {bonus_name}",
                font=('Arial', 12, 'bold'), fg='green').pack(anchor='w', pady=5)

        # Wymagania
        tk.Label(details_frame, text=f"Wymagania: {card.requirements}",
                font=('Arial', 11)).pack(anchor='w', pady=5)

        # Opis
        if card.description:
            desc_frame = tk.LabelFrame(details_frame, text="Opis")
            desc_frame.pack(fill='x', pady=10)
            tk.Label(desc_frame, text=card.description, font=('Arial', 10),
                    wraplength=400, justify='left').pack(padx=5, pady=5)

        # Przycisk zamknięcia
        tk.Button(popup, text="Zamknij", command=popup.destroy, font=('Arial', 10)).pack(pady=10)

    def preview_generic_card(self, card):
        """Pokazuje podgląd karty ogólnej"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Podgląd: {card.name}")
        popup.geometry("400x300")

        # Nagłówek
        header_frame = tk.Frame(popup, bg='lightgray', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=card.name, font=('Arial', 16, 'bold'), bg='lightgray').pack(pady=5)

        # Szczegóły
        details_frame = tk.Frame(popup)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Wyświetl wszystkie dostępne atrybuty
        for attr_name in dir(card):
            if not attr_name.startswith('_') and hasattr(card, attr_name):
                attr_value = getattr(card, attr_name)
                if not callable(attr_value):
                    tk.Label(details_frame, text=f"{attr_name}: {attr_value}",
                            font=('Arial', 10)).pack(anchor='w', pady=2)

        # Przycisk zamknięcia
        tk.Button(popup, text="Zamknij", command=popup.destroy, font=('Arial', 10)).pack(pady=10)

    def use_intrigue_card(self, card: IntrigueCard):
        """Używa kartę intrygi - wybiera cel i wykonuje efekt"""
        current_player = self.players[self.current_player_idx]

        # Sprawdź czy karta wymaga wyboru celu
        if card.target == "opponent" or any(effect.target_type == "opponent" for effect in card.effects):
            self.select_target_for_intrigue(card)
        elif card.target == "all" or any(effect.target_type in ["all_players", "all_opponents"] for effect in card.effects):
            self.confirm_intrigue_usage(card, None)  # Brak konkretnego celu
        else:  # self
            self.confirm_intrigue_usage(card, current_player)

    def select_target_for_intrigue(self, card: IntrigueCard):
        """Pozwala wybrać gracza jako cel karty intrygi"""
        current_player = self.players[self.current_player_idx]

        # Popup do wyboru celu
        target_popup = tk.Toplevel(self.root)
        target_popup.title("Wybierz cel")
        target_popup.geometry("400x300")
        target_popup.grab_set()

        # Nagłówek
        tk.Label(target_popup, text=f"Karta: {card.name}",
                font=('Arial', 14, 'bold')).pack(pady=10)
        tk.Label(target_popup, text="Wybierz gracza docelowego:",
                font=('Arial', 12)).pack(pady=5)

        # Lista dostępnych celów (przeciwnicy)
        for player in self.players:
            if player != current_player:  # Nie można wybrać siebie jako celu
                player_frame = tk.Frame(target_popup, relief='groove', borderwidth=2)
                player_frame.pack(fill='x', padx=20, pady=5)

                # Informacje o graczu
                info_text = f"{player.name} ({player.color})"
                if player.institute:
                    info_text += f" - {player.institute.name}"
                info_text += f"\n💰{player.credits//1000}K ⭐{player.prestige_points}PZ 🔬{player.research_points}PB"

                tk.Label(player_frame, text=info_text, font=('Arial', 10)).pack(pady=5)

                # Przycisk wyboru
                select_btn = tk.Button(player_frame, text="WYBIERZ TEGO GRACZA",
                                     command=lambda p=player: [target_popup.destroy(), self.confirm_intrigue_usage(card, p)],
                                     bg='red', fg='white')
                select_btn.pack(pady=5)

        # Przycisk anulowania
        tk.Button(target_popup, text="Anuluj", command=target_popup.destroy).pack(pady=20)

    def confirm_intrigue_usage(self, card: IntrigueCard, target_player):
        """Potwierdza użycie karty intrygi i wykonuje efekt"""
        current_player = self.players[self.current_player_idx]

        # Przygotuj tekst potwierdzenia
        if target_player:
            target_text = f"na gracza {target_player.name}"
        elif card.target == "all":
            target_text = "na wszystkich graczy"
        else:
            target_text = "na siebie"

        # Popup potwierdzenia
        confirm = messagebox.askyesno(
            "Potwierdzenie",
            f"Czy na pewno chcesz użyć kartę '{card.name}' {target_text}?\n\n"
            f"Efekt: {card.effect}",
            icon='question'
        )

        if confirm:
            self.execute_intrigue_effects(card, target_player)
            # Usuń kartę z ręki gracza
            current_player.hand_cards.remove(card)
            self.log_message(f"{current_player.name} użył karty intrygi: {card.name}")
            self.update_ui()

    def execute_intrigue_effects(self, card: IntrigueCard, target_player):
        """Wykonuje wszystkie efekty karty intrygi"""
        current_player = self.players[self.current_player_idx]

        for effect in card.effects:
            # Określ listę graczy docelowych
            targets = []
            if effect.target_type == "opponent" and target_player:
                targets = [target_player]
            elif effect.target_type == "all_opponents":
                targets = [p for p in self.players if p != current_player]
            elif effect.target_type == "all_players":
                targets = self.players
            elif effect.target_type == "self":
                targets = [current_player]

            # Wykonaj efekt na każdym celu
            for target in targets:
                self.apply_intrigue_effect(effect, target, current_player)

    def use_opportunity_card(self, card: OpportunityCard):
        """Używa kartę okazji - sprawdza warunki i wykonuje efekt na graczu"""
        current_player = self.players[self.current_player_idx]

        # Sprawdź warunki karty
        if not self.check_opportunity_conditions(card, current_player):
            messagebox.showwarning("Warunki niezpełnione",
                                 f"Nie spełniasz warunków karty '{card.name}'.\n"
                                 f"Wymagania: {card.requirements}")
            return

        # Popup potwierdzenia
        confirm = messagebox.askyesno(
            "Potwierdzenie",
            f"Czy na pewno chcesz użyć kartę '{card.name}'?\n\n"
            f"Efekt: {card.bonus_value} {card.bonus_type}\n"
            f"Opis: {card.description}",
            icon='question'
        )

        if confirm:
            self.execute_opportunity_effects(card, current_player)
            # Usuń kartę z ręki gracza
            current_player.hand_cards.remove(card)
            self.log_message(f"{current_player.name} użył karty okazji: {card.name}")
            self.update_ui()

    def check_opportunity_conditions(self, card: OpportunityCard, player) -> bool:
        """Sprawdza czy gracz spełnia warunki użycia karty okazji"""
        condition = card.requirements.lower()

        if condition == "brak":
            return True
        elif "min. 1 publikacja" in condition:
            return player.publications >= 1
        elif "aktywne badanie" in condition:
            return len(player.active_research) > 0
        elif "reputacja 3+" in condition:
            return player.reputation >= 3
        elif "ukończone badanie" in condition:
            return len(player.completed_research) > 0
        elif "min. 1 profesor" in condition:
            return any(scientist.type == ScientistType.PROFESOR for scientist in player.scientists)
        elif "badanie chemiczne lub fizyczne" in condition:
            return any(research.field in ["Chemia", "Fizyka"] for research in player.active_research + player.completed_research)
        else:
            return True  # Domyślnie pozwól

    def execute_opportunity_effects(self, card: OpportunityCard, target_player):
        """Wykonuje wszystkie efekty karty okazji"""
        for effect in card.effects:
            self.apply_opportunity_effect(effect, target_player)

    def apply_opportunity_effect(self, effect: OpportunityEffect, target_player):
        """Stosuje pojedynczy efekt okazji na graczu"""
        if effect.operation == "add":
            if effect.parameter == "credits":
                target_player.credits += effect.value
                self.log_message(f"{target_player.name} zyskuje {effect.value//1000}K")
            elif effect.parameter == "research_points":
                target_player.research_points += effect.value
                self.log_message(f"{target_player.name} zyskuje {effect.value} PB")
            elif effect.parameter == "reputation":
                target_player.reputation += effect.value
                self.log_message(f"{target_player.name} zyskuje {effect.value} reputacji")
            elif effect.parameter == "hex_tokens":
                target_player.hex_tokens += effect.value
                self.log_message(f"{target_player.name} zyskuje {effect.value} heksów")
            elif effect.parameter == "action_points":
                target_player.action_points += effect.value
                self.log_message(f"{target_player.name} zyskuje {effect.value} punktów akcji")
            elif effect.parameter == "prestige_points":
                target_player.prestige_points += effect.value
                self.log_message(f"{target_player.name} zyskuje {effect.value} PZ")

    def apply_intrigue_effect(self, effect: IntrigueEffect, target_player, source_player):
        """Stosuje pojedynczy efekt intrygi na graczu"""
        if effect.operation == "subtract":
            if effect.parameter == "credits":
                target_player.credits = max(0, target_player.credits - effect.value)
                self.log_message(f"{target_player.name} traci {effect.value//1000}K")
            elif effect.parameter == "reputation":
                target_player.reputation = max(0, target_player.reputation - effect.value)
                self.log_message(f"{target_player.name} traci {effect.value} reputacji")
            elif effect.parameter == "research_points":
                target_player.research_points = max(0, target_player.research_points - effect.value)
                self.log_message(f"{target_player.name} traci {effect.value} PB")
            elif effect.parameter == "publications":
                target_player.publications = max(0, target_player.publications - effect.value)
                self.log_message(f"{target_player.name} traci {effect.value} publikacji")

        elif effect.operation == "add":
            if effect.parameter == "credits":
                target_player.credits += effect.value
                self.log_message(f"{target_player.name} zyskuje {effect.value//1000}K")
            elif effect.parameter == "reputation":
                target_player.reputation = min(5, target_player.reputation + effect.value)
                self.log_message(f"{target_player.name} zyskuje {effect.value} reputacji")
            elif effect.parameter == "research_points":
                target_player.research_points += effect.value
                self.log_message(f"{target_player.name} zyskuje {effect.value} PB")

        elif effect.operation == "steal":
            if effect.special_type == "scientist" and target_player.scientists:
                # Przejmij naukowca
                stolen_scientist = target_player.scientists.pop()
                source_player.scientists.append(stolen_scientist)
                self.log_message(f"{source_player.name} przejmuje naukowca {stolen_scientist.name} od {target_player.name}")

        elif effect.operation == "remove":
            if effect.parameter == "current_grant" and target_player.current_grant:
                grant_name = target_player.current_grant.name
                target_player.current_grant = None
                self.log_message(f"{target_player.name} traci grant: {grant_name}")

        elif effect.operation == "reveal":
            if effect.parameter == "hand_cards":
                card_names = [card.name for card in target_player.hand_cards]
                messagebox.showinfo(
                    f"Ręka gracza {target_player.name}",
                    f"Karty w ręce:\n" + "\n".join(card_names) if card_names else "Brak kart w ręce"
                )

        # TODO: Dodać obsługę pozostałych operacji (block, copy, itp.)

    def update_dev_resource_displays(self):
        """Update the resource displays in developer tools"""
        if not self.players or not hasattr(self, 'dev_player_combo'):
            return

        try:
            player_selection = self.dev_player_var.get()
            if not player_selection:
                return

            player_index = self.dev_player_combo['values'].index(player_selection)
            player = self.players[player_index]

            # Update each resource display
            resources = ['credits', 'research_points', 'prestige_points', 'reputation', 'hex_tokens', 'activity_points']
            for resource in resources:
                label_attr = f"dev_{resource}_label"
                if hasattr(self, label_attr):
                    label = getattr(self, label_attr)
                    current_value = getattr(player, resource, 0)
                    label.config(text=str(current_value))

        except (ValueError, IndexError):
            pass  # Player selection invalid

    def toggle_developer_mode(self, event=None):
        """Toggle developer mode on/off"""
        self.developer_mode = not self.developer_mode

        if self.developer_mode:
            # Enable developer mode
            self.dev_mode_label.pack(side='right', padx=(20, 0))
            self.main_notebook.add(self.developer_tab, text="🔧 Developer")
            self.setup_developer_tab()
            self.log_message("🔧 Developer mode ENABLED")
        else:
            # Disable developer mode
            self.dev_mode_label.pack_forget()
            # Remove developer tab
            try:
                self.main_notebook.forget(self.developer_tab)
            except:
                pass  # Tab might not be added yet
            self.log_message("🔧 Developer mode DISABLED")

    def setup_developer_tab(self):
        """Sets up the developer tools tab"""
        # Clear existing content
        for widget in self.developer_tab.winfo_children():
            widget.destroy()

        # Main developer frame with red border to indicate dev mode
        dev_main_frame = tk.Frame(self.developer_tab, bg='#ffeeee', relief='solid', borderwidth=2)
        dev_main_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Warning header
        warning_label = tk.Label(dev_main_frame,
                               text="⚠️ DEVELOPER MODE - FOR TESTING ONLY ⚠️",
                               font=('Arial', 14, 'bold'),
                               fg='red', bg='#ffeeee')
        warning_label.pack(pady=10)

        # Create notebook for different dev tool categories
        dev_notebook = ttk.Notebook(dev_main_frame)
        dev_notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Setup different developer tool tabs
        self.setup_resource_dev_tab(dev_notebook)
        self.setup_cards_dev_tab(dev_notebook)
        self.setup_gamestate_dev_tab(dev_notebook)
        self.setup_scientists_dev_tab(dev_notebook)

    def setup_resource_dev_tab(self, parent_notebook):
        """Setup resource manipulation tools"""
        resource_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(resource_frame, text="Resources")

        # Player selection
        tk.Label(resource_frame, text="Select Player:", font=('Arial', 12, 'bold')).pack(pady=5)

        self.dev_player_var = tk.StringVar()
        self.dev_player_combo = ttk.Combobox(resource_frame, textvariable=self.dev_player_var, state='readonly')
        self.dev_player_combo.pack(pady=5)

        # Update player list
        self.update_dev_player_list()

        # Resource controls frame
        resources_frame = tk.Frame(resource_frame)
        resources_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Credits
        self.setup_resource_control(resources_frame, "Credits", "credits", 0)
        # Research Points
        self.setup_resource_control(resources_frame, "Research Points", "research_points", 1)
        # Prestige Points
        self.setup_resource_control(resources_frame, "Prestige Points", "prestige_points", 2)
        # Reputation (0-5)
        self.setup_resource_control(resources_frame, "Reputation", "reputation", 3, max_val=5)
        # Hex Tokens
        self.setup_resource_control(resources_frame, "Hex Tokens", "hex_tokens", 4)
        # Activity Points
        self.setup_resource_control(resources_frame, "Activity Points", "activity_points", 5)

    def setup_resource_control(self, parent, label_text, attr_name, row, max_val=9999):
        """Create a resource control widget"""
        tk.Label(parent, text=f"{label_text}:", width=15, anchor='w').grid(row=row, column=0, padx=5, pady=2, sticky='w')

        # Current value display
        current_label = tk.Label(parent, text="0", width=8, relief='sunken')
        current_label.grid(row=row, column=1, padx=5, pady=2)

        # Input field
        entry_var = tk.StringVar()
        entry = tk.Entry(parent, textvariable=entry_var, width=8)
        entry.grid(row=row, column=2, padx=5, pady=2)

        # Set button
        set_btn = tk.Button(parent, text="Set",
                           command=lambda: self.dev_set_resource(attr_name, entry_var.get(), current_label))
        set_btn.grid(row=row, column=3, padx=5, pady=2)

        # Store references for updates
        setattr(self, f"dev_{attr_name}_label", current_label)
        setattr(self, f"dev_{attr_name}_entry", entry)

    def setup_cards_dev_tab(self, parent_notebook):
        """Setup card manipulation tools"""
        cards_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(cards_frame, text="Cards")

        # Player selection for card operations
        player_frame = tk.Frame(cards_frame)
        player_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(player_frame, text="Target Player:", font=('Arial', 12, 'bold')).pack(side='left')
        self.dev_card_player_var = tk.StringVar()
        self.dev_card_player_combo = ttk.Combobox(player_frame, textvariable=self.dev_card_player_var, state='readonly', width=20)
        self.dev_card_player_combo.pack(side='left', padx=10)

        # Card type selection
        card_type_frame = tk.Frame(cards_frame)
        card_type_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(card_type_frame, text="Card Type:", font=('Arial', 12, 'bold')).pack(side='left')
        self.dev_card_type_var = tk.StringVar()
        card_types = ["Research", "Consortium", "Intrigue", "Opportunity"]
        self.dev_card_type_combo = ttk.Combobox(card_type_frame, textvariable=self.dev_card_type_var, values=card_types, state='readonly', width=15)
        self.dev_card_type_combo.pack(side='left', padx=10)
        self.dev_card_type_combo.bind('<<ComboboxSelected>>', self.update_dev_card_list)

        # Specific card selection
        card_select_frame = tk.Frame(cards_frame)
        card_select_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(card_select_frame, text="Specific Card:", font=('Arial', 12, 'bold')).pack(side='left')
        self.dev_specific_card_var = tk.StringVar()
        self.dev_specific_card_combo = ttk.Combobox(card_select_frame, textvariable=self.dev_specific_card_var, state='readonly', width=30)
        self.dev_specific_card_combo.pack(side='left', padx=10)

        # Card action buttons
        button_frame = tk.Frame(cards_frame)
        button_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(button_frame, text="Add to Hand", command=self.dev_add_card_to_hand,
                 bg='lightgreen', width=15).pack(side='left', padx=5)
        tk.Button(button_frame, text="Remove from Hand", command=self.dev_remove_card_from_hand,
                 bg='lightcoral', width=15).pack(side='left', padx=5)

        # Hand management
        hand_frame = ttk.LabelFrame(cards_frame, text="Current Hand")
        hand_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Hand display with scrollbar
        hand_canvas = tk.Canvas(hand_frame, height=200)
        hand_scrollbar = ttk.Scrollbar(hand_frame, orient="vertical", command=hand_canvas.yview)
        self.dev_hand_frame = ttk.Frame(hand_canvas)

        self.dev_hand_frame.bind(
            "<Configure>",
            lambda e: hand_canvas.configure(scrollregion=hand_canvas.bbox("all"))
        )

        hand_canvas.create_window((0, 0), window=self.dev_hand_frame, anchor="nw")
        hand_canvas.configure(yscrollcommand=hand_scrollbar.set)

        hand_canvas.pack(side="left", fill="both", expand=True)
        hand_scrollbar.pack(side="right", fill="y")

        # Initialize
        self.update_dev_card_players()
        self.dev_card_type_combo.set("Research")
        self.update_dev_card_list()

    def setup_gamestate_dev_tab(self, parent_notebook):
        """Setup game state manipulation tools"""
        gamestate_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(gamestate_frame, text="Game State")

        # Current player control
        player_control_frame = ttk.LabelFrame(gamestate_frame, text="Player Control")
        player_control_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(player_control_frame, text="Current Player:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.dev_current_player_var = tk.StringVar()
        self.dev_current_player_combo = ttk.Combobox(player_control_frame, textvariable=self.dev_current_player_var, state='readonly', width=20)
        self.dev_current_player_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(player_control_frame, text="Set Current Player", command=self.dev_set_current_player).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(player_control_frame, text="Next Player", command=self.dev_next_player).grid(row=0, column=3, padx=5, pady=5)

        # Phase control
        phase_control_frame = ttk.LabelFrame(gamestate_frame, text="Phase Control")
        phase_control_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(phase_control_frame, text="Current Phase:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.dev_phase_var = tk.StringVar()
        phases = ["GRANTY", "AKCJE", "PORZADKOWA"]
        self.dev_phase_combo = ttk.Combobox(phase_control_frame, textvariable=self.dev_phase_var, values=phases, state='readonly', width=15)
        self.dev_phase_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(phase_control_frame, text="Set Phase", command=self.dev_set_phase).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(phase_control_frame, text="Next Phase", command=self.dev_next_phase).grid(row=0, column=3, padx=5, pady=5)

        # Round control
        round_control_frame = ttk.LabelFrame(gamestate_frame, text="Round Control")
        round_control_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(round_control_frame, text="Current Round:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.dev_round_var = tk.StringVar()
        self.dev_round_entry = tk.Entry(round_control_frame, textvariable=self.dev_round_var, width=5)
        self.dev_round_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(round_control_frame, text="Set Round", command=self.dev_set_round).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(round_control_frame, text="Next Round", command=self.dev_next_round).grid(row=0, column=3, padx=5, pady=5)

        # Action points control
        ap_control_frame = ttk.LabelFrame(gamestate_frame, text="Action Points Control")
        ap_control_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(ap_control_frame, text="Remaining AP:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.dev_ap_var = tk.StringVar()
        self.dev_ap_entry = tk.Entry(ap_control_frame, textvariable=self.dev_ap_var, width=5)
        self.dev_ap_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(ap_control_frame, text="Set AP", command=self.dev_set_action_points).grid(row=0, column=2, padx=5, pady=5)

        # Initialize values
        self.update_dev_gamestate_displays()

    def setup_scientists_dev_tab(self, parent_notebook):
        """Setup scientist manipulation tools"""
        scientists_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(scientists_frame, text="Scientists")

        # Player selection for scientist operations
        player_frame = tk.Frame(scientists_frame)
        player_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(player_frame, text="Target Player:", font=('Arial', 12, 'bold')).pack(side='left')
        self.dev_scientist_player_var = tk.StringVar()
        self.dev_scientist_player_combo = ttk.Combobox(player_frame, textvariable=self.dev_scientist_player_var, state='readonly', width=20)
        self.dev_scientist_player_combo.pack(side='left', padx=10)

        # Scientist type for hiring
        hire_frame = ttk.LabelFrame(scientists_frame, text="Hire Scientists")
        hire_frame.pack(fill='x', padx=10, pady=5)

        scientist_types = ["DOKTORANT", "DOKTOR", "PROFESOR"]
        for i, sci_type in enumerate(scientist_types):
            btn = tk.Button(hire_frame, text=f"Hire {sci_type}",
                           command=lambda t=sci_type: self.dev_hire_scientist(t),
                           bg='lightgreen', width=15)
            btn.grid(row=0, column=i, padx=5, pady=5)

        # Research manipulation
        research_frame = ttk.LabelFrame(scientists_frame, text="Research Manipulation")
        research_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(research_frame, text="Add Hexes to Research:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.dev_hex_count_var = tk.StringVar(value="1")
        hex_entry = tk.Entry(research_frame, textvariable=self.dev_hex_count_var, width=5)
        hex_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(research_frame, text="Add Hexes", command=self.dev_add_hexes_to_research).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(research_frame, text="Complete Active Research", command=self.dev_complete_research).grid(row=0, column=3, padx=5, pady=5)

        # Current scientists display
        current_frame = ttk.LabelFrame(scientists_frame, text="Current Scientists")
        current_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Scientists display with scrollbar
        scientists_canvas = tk.Canvas(current_frame, height=200)
        scientists_scrollbar = ttk.Scrollbar(current_frame, orient="vertical", command=scientists_canvas.yview)
        self.dev_scientists_frame = ttk.Frame(scientists_canvas)

        self.dev_scientists_frame.bind(
            "<Configure>",
            lambda e: scientists_canvas.configure(scrollregion=scientists_canvas.bbox("all"))
        )

        scientists_canvas.create_window((0, 0), window=self.dev_scientists_frame, anchor="nw")
        scientists_canvas.configure(yscrollcommand=scientists_scrollbar.set)

        scientists_canvas.pack(side="left", fill="both", expand=True)
        scientists_scrollbar.pack(side="right", fill="y")

        # Initialize
        self.update_dev_scientist_players()

    def update_dev_player_list(self):
        """Update the player list in developer tools"""
        if hasattr(self, 'dev_player_combo') and self.players:
            player_names = [f"{p.name} ({p.color})" for p in self.players]
            self.dev_player_combo['values'] = player_names
            if player_names:
                self.dev_player_combo.set(player_names[0])

    def dev_set_resource(self, attr_name, value_str, label_widget):
        """Set a resource value for the selected player"""
        if not self.players or not hasattr(self, 'dev_player_combo'):
            return

        try:
            # Get selected player
            player_selection = self.dev_player_var.get()
            if not player_selection:
                return

            player_index = self.dev_player_combo['values'].index(player_selection)
            player = self.players[player_index]

            # Parse and validate value
            new_value = int(value_str)
            if attr_name == "reputation":
                new_value = max(0, min(5, new_value))  # Clamp reputation to 0-5
            else:
                new_value = max(0, new_value)  # Other resources can't be negative

            # Set the resource
            setattr(player, attr_name, new_value)

            # Update display
            label_widget.config(text=str(new_value))

            # Log the change
            self.log_message(f"🔧 DEV: Set {player.name} {attr_name} to {new_value}")

            # Update main UI
            self.update_ui()

        except (ValueError, IndexError):
            self.log_message(f"🔧 DEV ERROR: Invalid value for {attr_name}")

    def update_dev_card_players(self):
        """Update player list for card operations"""
        if hasattr(self, 'dev_card_player_combo') and self.players:
            player_names = [f"{p.name} ({p.color})" for p in self.players]
            self.dev_card_player_combo['values'] = player_names
            if player_names:
                self.dev_card_player_combo.set(player_names[0])

    def update_dev_card_list(self, event=None):
        """Update available cards list based on selected type"""
        if not hasattr(self, 'dev_specific_card_combo'):
            return

        card_type = self.dev_card_type_var.get()
        card_names = []

        if card_type == "Research" and hasattr(self.game_data, 'research_cards'):
            card_names = [card.name for card in self.game_data.research_cards]
        elif card_type == "Consortium" and hasattr(self.game_data, 'consortium_cards'):
            card_names = [card.name for card in self.game_data.consortium_cards]
        elif card_type == "Intrigue" and hasattr(self.game_data, 'intrigue_cards'):
            card_names = [card.name for card in self.game_data.intrigue_cards]
        elif card_type == "Opportunity" and hasattr(self.game_data, 'opportunity_cards'):
            card_names = [card.name for card in self.game_data.opportunity_cards]

        self.dev_specific_card_combo['values'] = card_names
        if card_names:
            self.dev_specific_card_combo.set(card_names[0])

    def dev_add_card_to_hand(self):
        """Add selected card to selected player's hand"""
        if not self.players:
            return

        try:
            # Get selected player
            player_selection = self.dev_card_player_var.get()
            if not player_selection:
                return

            player_index = self.dev_card_player_combo['values'].index(player_selection)
            player = self.players[player_index]

            # Get selected card
            card_type = self.dev_card_type_var.get()
            card_name = self.dev_specific_card_var.get()
            if not card_name:
                return

            # Find the card object
            card_obj = None
            if card_type == "Research" and hasattr(self.game_data, 'research_cards'):
                card_obj = next((card for card in self.game_data.research_cards if card.name == card_name), None)
            elif card_type == "Consortium" and hasattr(self.game_data, 'consortium_cards'):
                card_obj = next((card for card in self.game_data.consortium_cards if card.name == card_name), None)
            elif card_type == "Intrigue" and hasattr(self.game_data, 'intrigue_cards'):
                card_obj = next((card for card in self.game_data.intrigue_cards if card.name == card_name), None)
            elif card_type == "Opportunity" and hasattr(self.game_data, 'opportunity_cards'):
                card_obj = next((card for card in self.game_data.opportunity_cards if card.name == card_name), None)

            if card_obj:
                # Create a copy to avoid modifying the original
                import copy
                card_copy = copy.deepcopy(card_obj)
                player.hand_cards.append(card_copy)

                self.log_message(f"🔧 DEV: Added {card_name} to {player.name}'s hand")
                self.update_ui()
            else:
                self.log_message(f"🔧 DEV ERROR: Card {card_name} not found")

        except (ValueError, IndexError) as e:
            self.log_message(f"🔧 DEV ERROR: {e}")

    def dev_remove_card_from_hand(self):
        """Remove selected card from selected player's hand"""
        if not self.players:
            return

        try:
            # Get selected player
            player_selection = self.dev_card_player_var.get()
            if not player_selection:
                return

            player_index = self.dev_card_player_combo['values'].index(player_selection)
            player = self.players[player_index]

            # Get selected card name
            card_name = self.dev_specific_card_var.get()
            if not card_name:
                return

            # Find and remove the card
            for i, card in enumerate(player.hand_cards):
                if card.name == card_name:
                    removed_card = player.hand_cards.pop(i)
                    self.log_message(f"🔧 DEV: Removed {card_name} from {player.name}'s hand")
                    self.update_ui()
                    return

            self.log_message(f"🔧 DEV ERROR: {card_name} not found in {player.name}'s hand")

        except (ValueError, IndexError) as e:
            self.log_message(f"🔧 DEV ERROR: {e}")

    def update_dev_gamestate_displays(self):
        """Update game state displays in developer tools"""
        if hasattr(self, 'dev_current_player_combo') and self.players:
            # Update player list
            player_names = [f"{p.name} ({p.color})" for p in self.players]
            self.dev_current_player_combo['values'] = player_names
            if self.current_player_idx < len(player_names):
                self.dev_current_player_combo.set(player_names[self.current_player_idx])

        if hasattr(self, 'dev_phase_combo'):
            self.dev_phase_combo.set(self.current_phase.value)

        if hasattr(self, 'dev_round_var'):
            self.dev_round_var.set(str(self.current_round))

        if hasattr(self, 'dev_ap_var'):
            self.dev_ap_var.set(str(self.remaining_action_points))

    def dev_set_current_player(self):
        """Set the current player"""
        try:
            player_selection = self.dev_current_player_var.get()
            if not player_selection:
                return

            player_index = self.dev_current_player_combo['values'].index(player_selection)
            old_player = self.players[self.current_player_idx].name
            self.current_player_idx = player_index
            new_player = self.players[self.current_player_idx].name

            self.log_message(f"🔧 DEV: Changed current player from {old_player} to {new_player}")
            self.update_ui()

        except (ValueError, IndexError) as e:
            self.log_message(f"🔧 DEV ERROR: {e}")

    def dev_next_player(self):
        """Advance to next player"""
        old_player = self.players[self.current_player_idx].name
        self.next_player()
        new_player = self.players[self.current_player_idx].name
        self.log_message(f"🔧 DEV: Advanced from {old_player} to {new_player}")

    def dev_set_phase(self):
        """Set the current game phase"""
        try:
            phase_name = self.dev_phase_var.get()
            if phase_name == "GRANTY":
                self.current_phase = GamePhase.GRANTY
            elif phase_name == "AKCJE":
                self.current_phase = GamePhase.AKCJE
            elif phase_name == "PORZADKOWA":
                self.current_phase = GamePhase.PORZADKOWA

            self.log_message(f"🔧 DEV: Set phase to {phase_name}")
            self.update_ui()

        except Exception as e:
            self.log_message(f"🔧 DEV ERROR: {e}")

    def dev_next_phase(self):
        """Advance to next phase"""
        old_phase = self.current_phase.value
        self.next_phase()
        new_phase = self.current_phase.value
        self.log_message(f"🔧 DEV: Advanced from {old_phase} to {new_phase}")

    def dev_set_round(self):
        """Set the current round"""
        try:
            new_round = int(self.dev_round_var.get())
            if new_round < 1:
                new_round = 1

            old_round = self.current_round
            self.current_round = new_round
            self.log_message(f"🔧 DEV: Set round from {old_round} to {new_round}")
            self.update_ui()

        except ValueError:
            self.log_message("🔧 DEV ERROR: Invalid round number")

    def dev_next_round(self):
        """Advance to next round"""
        old_round = self.current_round
        self.advance_round()
        self.log_message(f"🔧 DEV: Advanced from round {old_round} to {self.current_round}")

    def dev_set_action_points(self):
        """Set remaining action points"""
        try:
            new_ap = int(self.dev_ap_var.get())
            if new_ap < 0:
                new_ap = 0

            old_ap = self.remaining_action_points
            self.remaining_action_points = new_ap
            self.log_message(f"🔧 DEV: Set action points from {old_ap} to {new_ap}")
            self.update_ui()

        except ValueError:
            self.log_message("🔧 DEV ERROR: Invalid action points value")

    def update_dev_scientist_players(self):
        """Update player list for scientist operations"""
        if hasattr(self, 'dev_scientist_player_combo') and self.players:
            player_names = [f"{p.name} ({p.color})" for p in self.players]
            self.dev_scientist_player_combo['values'] = player_names
            if player_names:
                self.dev_scientist_player_combo.set(player_names[0])

    def dev_hire_scientist(self, scientist_type):
        """Hire a scientist for the selected player"""
        if not self.players:
            return

        try:
            # Get selected player
            player_selection = self.dev_scientist_player_var.get()
            if not player_selection:
                return

            player_index = self.dev_scientist_player_combo['values'].index(player_selection)
            player = self.players[player_index]

            # Create scientist based on type
            if scientist_type == "DOKTORANT":
                new_scientist = Scientist("Dev Doktorant", ScientistType.DOKTORANT, "Uniwersalny", 0, 1, "Brak", "Dev hired")
            elif scientist_type == "DOKTOR":
                new_scientist = Scientist("Dev Doktor", ScientistType.DOKTOR, "Uniwersalny", 2000, 2, "Brak", "Dev hired")
            elif scientist_type == "PROFESOR":
                new_scientist = Scientist("Dev Profesor", ScientistType.PROFESOR, "Uniwersalny", 3000, 3, "Brak", "Dev hired")
            else:
                return

            player.scientists.append(new_scientist)
            self.log_message(f"🔧 DEV: Hired {scientist_type} for {player.name}")
            self.update_ui()

        except (ValueError, IndexError) as e:
            self.log_message(f"🔧 DEV ERROR: {e}")

    def dev_add_hexes_to_research(self):
        """Add hexes to active research for selected player"""
        if not self.players:
            return

        try:
            # Get selected player
            player_selection = self.dev_scientist_player_var.get()
            if not player_selection:
                return

            player_index = self.dev_scientist_player_combo['values'].index(player_selection)
            player = self.players[player_index]

            # Get hex count
            hex_count = int(self.dev_hex_count_var.get())
            if hex_count < 1:
                return

            # Add hexes to first active research
            if player.active_research:
                research = player.active_research[0]
                old_hexes = research.hexes_placed
                research.hexes_placed = min(research.max_hexes, research.hexes_placed + hex_count)
                added = research.hexes_placed - old_hexes

                self.log_message(f"🔧 DEV: Added {added} hexes to {research.name} for {player.name}")

                # Check if research is complete
                if research.hexes_placed >= research.max_hexes:
                    self.complete_research(player, research)

                self.update_ui()
            else:
                self.log_message(f"🔧 DEV ERROR: {player.name} has no active research")

        except (ValueError, IndexError) as e:
            self.log_message(f"🔧 DEV ERROR: {e}")

    def dev_complete_research(self):
        """Complete first active research for selected player"""
        if not self.players:
            return

        try:
            # Get selected player
            player_selection = self.dev_scientist_player_var.get()
            if not player_selection:
                return

            player_index = self.dev_scientist_player_combo['values'].index(player_selection)
            player = self.players[player_index]

            # Complete first active research
            if player.active_research:
                research = player.active_research[0]
                self.complete_research(player, research)
                self.log_message(f"🔧 DEV: Completed research {research.name} for {player.name}")
                self.update_ui()
            else:
                self.log_message(f"🔧 DEV ERROR: {player.name} has no active research")

        except (ValueError, IndexError) as e:
            self.log_message(f"🔧 DEV ERROR: {e}")

    def update_notifications(self):
        """Aktualizuje panel powiadomień"""
        current_player = self.players[self.current_player_idx] if self.players else None

        if not current_player:
            return

        # Sprawdź czy obecny gracz ma jakieś powiadomienia jako kierownik
        player_notifications = []

        if hasattr(self, 'consortium_notifications'):
            player_notifications = [
                notif for notif in self.consortium_notifications
                if notif.get('director') == current_player
            ]

        # Jeśli są powiadomienia, pokaż panel
        if player_notifications:
            # Pokaż panel powiadomień
            self.notifications_frame.pack(fill='x', pady=(0, 10), after=self.info_frame)

            # Wyczyść poprzednie powiadomienia
            for widget in self.notifications_frame.winfo_children():
                widget.destroy()

            # Nagłówek
            header_frame = tk.Frame(self.notifications_frame, bg='orange', relief='raised', borderwidth=2)
            header_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(header_frame, text=f"🔔 POWIADOMIENIA DLA {current_player.name}",
                    font=('Arial', 12, 'bold'), bg='orange', fg='white').pack(pady=3)

            # Lista powiadomień
            for notif in player_notifications:
                if notif.get('type') == 'membership_request':
                    project = notif.get('project')
                    applicant = notif.get('applicant')

                    notif_frame = tk.Frame(self.notifications_frame, bg='lightyellow', relief='groove', borderwidth=2)
                    notif_frame.pack(fill='x', padx=5, pady=2)

                    # Tekst powiadomienia
                    info_frame = tk.Frame(notif_frame, bg='lightyellow')
                    info_frame.pack(fill='x', padx=5, pady=3)

                    tk.Label(info_frame, text=f"👤 {applicant.name} chce dołączyć do konsorcjum:",
                            font=('Arial', 10, 'bold'), bg='lightyellow').pack(anchor='w')
                    tk.Label(info_frame, text=f"🏛️ {project.name}",
                            font=('Arial', 10), bg='lightyellow').pack(anchor='w', padx=20)

                    # Przyciski akcji
                    button_frame = tk.Frame(notif_frame, bg='lightyellow')
                    button_frame.pack(fill='x', padx=5, pady=3)

                    accept_btn = tk.Button(button_frame, text="✅ Akceptuj",
                                         command=lambda p=project, a=applicant: self.approve_consortium_membership(p, a),
                                         bg='lightgreen', font=('Arial', 9, 'bold'))
                    accept_btn.pack(side='left', padx=2)

                    reject_btn = tk.Button(button_frame, text="❌ Odrzuć",
                                         command=lambda p=project, a=applicant: self.reject_consortium_membership(p, a),
                                         bg='lightcoral', font=('Arial', 9, 'bold'))
                    reject_btn.pack(side='left', padx=2)

                    # Przycisk zarządzania
                    manage_btn = tk.Button(button_frame, text="👑 Zarządzaj konsorcjami",
                                         command=self.show_consortium_management_panel,
                                         bg='gold', font=('Arial', 9, 'bold'))
                    manage_btn.pack(side='right', padx=2)

        else:
            # Ukryj panel jeśli brak powiadomień
            self.notifications_frame.pack_forget()

    def run(self):
        """Uruchamia grę"""
        self.root.mainloop()

class CollapsibleResearchWidget(tk.Frame):
    """Widget dla zwijanych/rozwijanych paneli badań"""

    def __init__(self, parent, research, game_instance, **kwargs):
        super().__init__(parent, **kwargs)

        self.research = research
        self.game = game_instance
        self.is_expanded = False
        self.hex_widget = None

        # Konfiguracja stylu
        self.configure(relief='raised', borderwidth=2, bg='lightblue')

        # Tworzenie struktury
        self.create_header()
        self.create_content_frame()

        # Inicjalny stan - zwinięte
        self.content_frame.pack_forget()

    def create_header(self):
        """Tworzy zawsze widoczny nagłówek"""
        self.header_frame = tk.Frame(self, bg='steelblue', relief='raised', borderwidth=1)
        self.header_frame.pack(fill='x', padx=2, pady=2)

        # Lewy panel - przycisk expand i nazwa
        left_panel = tk.Frame(self.header_frame, bg='steelblue')
        left_panel.pack(side='left', fill='x', expand=True)

        # Przycisk expand/collapse
        self.toggle_btn = tk.Button(left_panel, text="▶",
                                   command=self.toggle_expanded,
                                   bg='darkblue', fg='white',
                                   font=('Arial', 8, 'bold'),
                                   relief='flat', width=3)
        self.toggle_btn.pack(side='left', padx=(5, 2), pady=2)

        # Nazwa i dziedzina
        name_frame = tk.Frame(left_panel, bg='steelblue')
        name_frame.pack(side='left', fill='x', expand=True, padx=(5, 0))

        tk.Label(name_frame, text=f"🔬 {self.research.name}",
                font=('Arial', 11, 'bold'), bg='steelblue', fg='white').pack(anchor='w')
        tk.Label(name_frame, text=f"📚 {self.research.field}",
                font=('Arial', 8), bg='steelblue', fg='lightgray').pack(anchor='w')

        # Prawy panel - postęp i status
        right_panel = tk.Frame(self.header_frame, bg='steelblue')
        right_panel.pack(side='right', padx=5)

        # Progress info
        progress_text = f"{self.get_progress()}/{self.research.max_hexes}"
        self.progress_label = tk.Label(right_panel, text=progress_text,
                                     font=('Arial', 10, 'bold'),
                                     bg='steelblue', fg='lightgreen')
        self.progress_label.pack(side='right', padx=5)

        # Status indicator
        self.status_label = tk.Label(right_panel, text="",
                                   font=('Arial', 8, 'bold'),
                                   bg='steelblue', fg='yellow')
        self.status_label.pack(side='right', padx=5)

        self.update_header_status()

    def create_content_frame(self):
        """Tworzy rozwijany content frame"""
        self.content_frame = tk.Frame(self, bg='lightblue')

        # Informacje o nagrodach
        rewards_frame = tk.Frame(self.content_frame, bg='lightblue')
        rewards_frame.pack(fill='x', padx=5, pady=2)

        tk.Label(rewards_frame, text=f"🏆 Podstawowa: {self.research.basic_reward}",
                font=('Arial', 9), bg='lightblue', fg='darkgreen').pack(side='left')
        if self.research.bonus_reward and self.research.bonus_reward != "Brak":
            tk.Label(rewards_frame, text=f"⭐ Bonusowa: {self.research.bonus_reward}",
                    font=('Arial', 9), bg='lightblue', fg='orange').pack(side='right')

        # Szczegółowy status
        self.detail_status_frame = tk.Frame(self.content_frame, bg='lightblue')
        self.detail_status_frame.pack(fill='x', padx=5, pady=2)

        # Container dla mapy heksagonalnej
        self.hex_container = tk.Frame(self.content_frame, bg='lightblue')
        self.hex_container.pack(fill='both', expand=True, padx=5, pady=5)

    def toggle_expanded(self):
        """Przełącza stan rozwinięcia"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        """Rozwija panel"""
        if not self.is_expanded:
            # Collapse inne panele w tym samym parent
            self.collapse_siblings()

            # Rozwijn ten panel
            self.is_expanded = True
            self.toggle_btn.config(text="▼")
            self.content_frame.pack(fill='both', expand=True, padx=2, pady=(0, 2))

            # Stwórz/odśwież mapę heksagonalną
            self.create_hex_widget()

            # Aktualizuj szczegółowy status
            self.update_detail_status()

            # Auto-scroll do tego panelu jeśli potrzeba
            self.bring_to_top()

    def collapse(self):
        """Zwija panel"""
        if self.is_expanded:
            self.is_expanded = False
            self.toggle_btn.config(text="▶")
            self.content_frame.pack_forget()

            # Usuń hex widget aby zwolnić pamięć
            if self.hex_widget:
                self.hex_widget.destroy()
                self.hex_widget = None

    def collapse_siblings(self):
        """Zwija inne panele w tym samym parent"""
        for sibling in self.master.winfo_children():
            if isinstance(sibling, CollapsibleResearchWidget) and sibling != self:
                sibling.collapse()

    def create_hex_widget(self):
        """Tworzy widget mapy heksagonalnej"""
        # Usuń poprzedni widget jeśli istnieje
        for widget in self.hex_container.winfo_children():
            widget.destroy()

        if self.research.hex_research_map:
            self.hex_widget = HexMapWidget(self.hex_container, self.research.hex_research_map)

            # Ustawienia callback
            self.hex_widget.on_hex_click_callback = lambda pos: self.game.on_hex_clicked(pos, self.research)

            # Odtwórz postęp gracza
            current_player = self.game.players[self.game.current_player_idx]
            if not self.research.player_color:
                self.research.player_color = current_player.color

            # Restore player's progress on the map
            if hasattr(self.research, 'player_path'):
                self.research.hex_research_map.player_path = self.research.player_path[:]
                for path_pos in self.research.player_path:
                    if path_pos in self.research.hex_research_map.tiles:
                        self.research.hex_research_map.tiles[path_pos].is_occupied = True
                        self.research.hex_research_map.tiles[path_pos].player_color = current_player.color

            self.hex_widget.update_display()
            self.hex_widget.pack(fill='both', expand=True)
        else:
            # Fallback dla badań bez map heksowych
            fallback_label = tk.Label(self.hex_container,
                                    text="Mapa heksagonalna niedostępna",
                                    bg='lightblue', fg='gray')
            fallback_label.pack(expand=True)

    def update_header_status(self):
        """Aktualizuje status w nagłówku"""
        # Progress
        progress_text = f"{self.get_progress()}/{self.research.max_hexes}"
        self.progress_label.config(text=progress_text)

        # Status indicator
        if (hasattr(self.game, 'hex_placement_mode') and
            self.game.hex_placement_mode and
            self.research == getattr(self.game, 'current_research_for_hex', None)):
            self.status_label.config(text="🎯 AKTYWNE", fg='red')
        else:
            self.status_label.config(text="", fg='yellow')

    def update_detail_status(self):
        """Aktualizuje szczegółowy status w rozwiniętym panelu"""
        # Wyczyść poprzedni status
        for widget in self.detail_status_frame.winfo_children():
            widget.destroy()

        if (hasattr(self.game, 'hex_placement_mode') and
            self.game.hex_placement_mode and
            self.research == getattr(self.game, 'current_research_for_hex', None)):

            pending = getattr(self.game, 'pending_hex_placements', 0)
            status_text = f"🎯 UŁÓŻ {pending} HEKS(ÓW) - Kliknij na mapę!"
            status_label = tk.Label(self.detail_status_frame, text=status_text,
                                  font=('Arial', 10, 'bold'), bg='yellow', fg='red')
            status_label.pack(pady=2)

    def get_progress(self):
        """Zwraca aktualny postęp badania"""
        if hasattr(self.research, 'player_path'):
            return len(self.research.player_path)
        return getattr(self.research, 'hexes_placed', 0)

    def bring_to_top(self):
        """Przewija do tego panelu jeśli jest poza ekranem"""
        # To można zaimplementować później dla auto-scroll
        pass

    def auto_expand_if_active(self):
        """Auto-rozwija jeśli to badanie jest aktywne"""
        if (hasattr(self.game, 'hex_placement_mode') and
            self.game.hex_placement_mode and
            self.research == getattr(self.game, 'current_research_for_hex', None)):
            self.expand()

    def refresh(self):
        """Odświeża cały widget"""
        self.update_header_status()
        if self.is_expanded:
            self.update_detail_status()
            if self.hex_widget:
                self.hex_widget.update_display()

if __name__ == "__main__":
    try:
        game = PrincipiaGame()
        game.run()
    except Exception as e:
        print(f"Błąd uruchomienia gry: {e}")
        import traceback
        traceback.print_exc()