#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRINCIPIA - Ulepszona wersja z wyraĹşnymi kartami akcji
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import random
import math
import socket as socket_lib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Union
from enum import Enum
from hex_research_system import HexResearchMap, HexMapWidget, HexPosition
from network_game import GameServer, GameClient, NetworkMessage, MessageType

# Modern Design System
class ModernTheme:
    """Modern design system for PRINCIPIA"""

    # Colors - Material Design inspired light theme
    PRIMARY = '#2196F3'          # Material Blue
    PRIMARY_DARK = '#1976D2'     # Darker Blue
    PRIMARY_LIGHT = '#BBDEFB'    # Light Blue

    SECONDARY = '#4CAF50'        # Material Green
    SECONDARY_DARK = '#388E3C'   # Darker Green
    SECONDARY_LIGHT = '#C8E6C9'  # Light Green

    ACCENT = '#FF9800'           # Material Orange
    ACCENT_DARK = '#F57C00'      # Darker Orange
    ACCENT_LIGHT = '#FFE0B2'     # Light Orange

    SUCCESS = '#4CAF50'          # Green
    WARNING = '#FF9800'          # Orange
    ERROR = '#F44336'            # Red
    INFO = '#2196F3'             # Blue

    # Backgrounds
    BACKGROUND = '#FAFAFA'       # Light Gray Background
    SURFACE = '#FFFFFF'          # White Surface
    SURFACE_VARIANT = '#F5F5F5'  # Light Gray Surface

    # Text Colors
    TEXT_PRIMARY = '#212121'     # Dark Gray
    TEXT_SECONDARY = '#757575'   # Medium Gray
    TEXT_DISABLED = '#BDBDBD'    # Light Gray
    TEXT_ON_PRIMARY = '#FFFFFF'  # White on colored backgrounds

    # Border Colors
    BORDER_LIGHT = '#E0E0E0'     # Light border
    BORDER_MEDIUM = '#BDBDBD'    # Medium border
    BORDER_DARK = '#9E9E9E'      # Dark border

    # Typography
    FONT_FAMILY = ('Segoe UI', 'Arial', 'sans-serif')

    # Font Sizes (minimum 11px for legibility)
    FONT_SIZE_HUGE = 20          # Major headings
    FONT_SIZE_LARGE = 16         # Section headers
    FONT_SIZE_MEDIUM = 14        # Primary content
    FONT_SIZE_NORMAL = 12        # Secondary content
    FONT_SIZE_SMALL = 11         # Captions, minimum size

    # Spacing System
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 24
    SPACING_XXL = 32

    # Border Radius (for future CSS-like styling)
    RADIUS_SM = 4
    RADIUS_MD = 8
    RADIUS_LG = 12

    @classmethod
    def configure_style(cls, widget_type='default'):
        """Returns style configuration for different widget types"""
        base_style = {
            'font': ('Segoe UI', cls.FONT_SIZE_MEDIUM),
            'bg': cls.SURFACE,
            'fg': cls.TEXT_PRIMARY
        }

        if widget_type == 'header':
            return {**base_style, 'font': ('Segoe UI', cls.FONT_SIZE_LARGE, 'bold')}
        elif widget_type == 'title':
            return {**base_style, 'font': ('Segoe UI', cls.FONT_SIZE_HUGE, 'bold')}
        elif widget_type == 'button':
            return {
                'font': ('Segoe UI', cls.FONT_SIZE_MEDIUM, 'bold'),
                'bg': cls.PRIMARY,
                'fg': cls.TEXT_ON_PRIMARY,
                'relief': 'flat',
                'bd': 0,
                'padx': cls.SPACING_LG,
                'pady': cls.SPACING_SM
            }
        elif widget_type == 'button_secondary':
            return {
                'font': ('Segoe UI', cls.FONT_SIZE_MEDIUM),
                'bg': cls.SURFACE_VARIANT,
                'fg': cls.TEXT_PRIMARY,
                'relief': 'flat',
                'bd': 1,
                'padx': cls.SPACING_LG,
                'pady': cls.SPACING_SM
            }
        elif widget_type == 'card':
            return {
                **base_style,
                'bg': cls.SURFACE,
                'relief': 'solid',
                'bd': 1,
                'highlightbackground': cls.BORDER_LIGHT
            }

        return base_style

# Enums i staĹ‚e
class ActionType(Enum):
    PROWADZ_BADANIA = "PROWADĹą BADANIA"
    ZATRUDNIJ = "ZATRUDNIJ PERSONEL"
    PUBLIKUJ = "PUBLIKUJ"
    FINANSUJ = "FINANSUJ PROJEKT"
    ZARZADZAJ = "ZARZÄ„DZAJ"

class GamePhase(Enum):
    GRANTY = "Faza GrantĂłw"
    AKCJE = "Faza Akcji"
    PORZADKOWA = "Faza PorzÄ…dkowa"

class ScientistType(Enum):
    DOKTORANT = "Doktorant"
    DOKTOR = "Doktor"
    PROFESOR = "Profesor"

@dataclass
class ActionCard:
    """Klasa reprezentujÄ…ca kartÄ™ akcji"""
    action_type: ActionType
    action_points: int
    basic_action: str
    additional_actions: List[Tuple[str, int]]  # (opis, koszt PA)
    is_used: bool = False

# Klasy danych (jak wczeĹ›niej)
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
        """Inicjalizuje mapÄ™ heksagonalnÄ… po utworzeniu obiektu"""
        if self.hex_map and not self.hex_research_map:
            try:
                self.hex_research_map = HexResearchMap(self.hex_map)
            except Exception as e:
                print(f"BĹ‚Ä…d parsowania mapy heksagonalnej dla {self.name}: {e}")
                # StwĂłrz prostÄ… mapÄ™ fallback
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
    """Karta konsorcjum - pozwala rozpoczÄ…Ä‡ wielki projekt"""
    name: str = "Karta Konsorcjum"
    description: str = "UmoĹĽliwia rozpoczÄ™cie Wielkiego Projektu"
    card_type: str = "KONSORCJUM"

@dataclass
class IntrigueEffect:
    """Efekt karty intryg - metadane dla automatycznego wykonania"""
    target_type: str     # "opponent", "all_opponents", "all_players", "self"
    parameter: str       # "credits", "reputation", "prestige_points", "research_points", "hex_tokens", etc.
    operation: str       # "subtract", "add", "set", "steal", "block", "copy", "reveal"
    value: int = 0       # wartoĹ›Ä‡ liczbowa (jeĹ›li dotyczy)
    special_type: str = ""  # typ specjalny: "scientist", "research_hex", "publication", "grant", "consortium", "card"
    duration: int = 1    # czas trwania efektu w rundach (1 = natychmiastowy)
    condition: str = ""  # dodatkowy warunek

@dataclass
class OpportunityEffect:
    """Efekt karty okazji - metadane dla automatycznego wykonania"""
    parameter: str       # "credits", "reputation", "prestige_points", "research_points", "hex_tokens", "action_points"
    operation: str       # "add", "multiply", "set"
    value: int = 0       # wartoĹ›Ä‡ liczbowa
    special_type: str = ""  # typ specjalny: "scientist", "research_hex", "publication", "grant", "consortium", "card"
    duration: int = 1    # czas trwania efektu w rundach (1 = natychmiastowy)
    condition: str = ""  # dodatkowy warunek np. "Min. 1 publikacja"

@dataclass
class IntrigueCard:
    """Karta intryg - pozwala oddziaĹ‚ywaÄ‡ na przeciwnikĂłw"""
    name: str
    effect: str
    target: str  # "opponent", "all", "self" (backward compatibility)
    description: str
    effects: List[IntrigueEffect] = field(default_factory=list)  # nowa struktura efektĂłw
    card_type: str = "INTRYGA"

@dataclass
class OpportunityCard:
    """Karta okazji - daje rĂłĹĽne bonusy"""
    name: str
    bonus_type: str  # "credits", "research_points", "reputation", "hex", "action_points"
    bonus_value: str
    requirements: str
    description: str
    card_type: str = "OKAZJA"
    effects: List[OpportunityEffect] = field(default_factory=list)  # nowa struktura efektĂłw

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
    max_rounds: int  # Maksymalna iloĹ›Ä‡ rund
    victory_conditions: str  # Warunki zwyciÄ™stwa
    crisis_count: int  # Ile kart kryzysĂłw dobieraÄ‡
    crisis_rounds: List[int] = field(default_factory=list)  # W ktĂłrych rundach odkrywaÄ‡ kryzysy
    description: str = ""

@dataclass
class LargeProject:
    name: str
    requirements: str
    director_reward: str
    member_reward: str
    description: str
    cost_pb: int = 20  # Koszt w punktach badawczych
    cost_credits: int = 50  # Koszt w kredytach (w tysiÄ…cach)
    contributed_pb: int = 0
    contributed_credits: int = 0
    director: Optional['Player'] = None
    members: List['Player'] = field(default_factory=list)
    pending_members: List['Player'] = field(default_factory=list)  # Gracze oczekujÄ…cy na akceptacjÄ™
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
    round_activity_points: int = 0
    has_passed: bool = False
    publication_history: List[JournalCard] = field(default_factory=list)  # Historia publikacji

class ActionCardWidget(tk.Frame):
    """Widget reprezentujÄ…cy kartÄ™ akcji"""

    def __init__(self, parent, action_card: ActionCard, on_play_callback=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.action_card = action_card
        self.on_play_callback = on_play_callback

        self.setup_ui()

    def setup_ui(self):
        """Tworzy interfejs karty akcji"""
        # Ustaw styl karty
        self.configure(relief='raised', borderwidth=2, padx=10, pady=10)

        # Kolor tĹ‚a zaleĹĽny od statusu
        if self.action_card.is_used:
            self.configure(bg='lightgray')
        else:
            self.configure(bg='lightblue')

        # NagĹ‚Ăłwek karty
        header_frame = tk.Frame(self, bg=self['bg'])
        header_frame.pack(fill='x', pady=(0, 5))

        title_label = tk.Label(header_frame, text=self.action_card.action_type.value,
                              font=('Arial', 12, 'bold'), bg=self['bg'])
        title_label.pack(side='top')

        points_label = tk.Label(header_frame, text=f"âšˇ {self.action_card.action_points} PA",
                               font=('Arial', 10, 'bold'), fg='red', bg=self['bg'])
        points_label.pack(side='top')

        # Akcja podstawowa
        basic_frame = tk.LabelFrame(self, text="đź”ą AKCJA PODSTAWOWA (DARMOWA)",
                                   font=('Arial', 9, 'bold'), bg=self['bg'])
        basic_frame.pack(fill='x', pady=(0, 5))

        basic_label = tk.Label(basic_frame, text=self.action_card.basic_action,
                              wraplength=250, justify='left', bg=self['bg'])
        basic_label.pack(padx=5, pady=2)

        # Akcje dodatkowe
        if self.action_card.additional_actions:
            additional_frame = tk.LabelFrame(self, text="âšˇ AKCJE DODATKOWE",
                                           font=('Arial', 9, 'bold'), bg=self['bg'])
            additional_frame.pack(fill='x', pady=(0, 5))

            for action_desc, cost in self.action_card.additional_actions:
                action_text = f"â€˘ {action_desc} ({cost} PA)"
                action_label = tk.Label(additional_frame, text=action_text,
                                       wraplength=250, justify='left', bg=self['bg'])
                action_label.pack(anchor='w', padx=5, pady=1)

        # Przycisk zagrania karty
        if not self.action_card.is_used and self.on_play_callback:
            play_button = tk.Button(self, text="ZAGRAJ KARTÄ",
                                   command=self.play_card,
                                   font=('Arial', 10, 'bold'),
                                   bg='green', fg='white',
                                   relief='raised', borderwidth=2)
            play_button.pack(pady=(5, 0))
        elif self.action_card.is_used:
            used_label = tk.Label(self, text="KARTA UĹ»YTA",
                                 font=('Arial', 10, 'bold'),
                                 fg='gray', bg=self['bg'])
            used_label.pack(pady=(5, 0))

    def play_card(self):
        """ObsĹ‚uguje zagranie karty"""
        if self.on_play_callback:
            self.on_play_callback(self.action_card)

    def update_display(self):
        """Aktualizuje wyĹ›wietlanie karty"""
        # WyczyĹ›Ä‡ i odbuduj UI
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()

class GameData:
    """Klasa do zarzÄ…dzania danymi gry"""
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
        self.main_deck = []  # Zmieszana talia wszystkich kart rÄ™ki
        self.scenarios = []
        self.crisis_cards = []
        self.active_scenario = None
        self.crisis_deck = []  # Talia kryzysĂłw dla aktualnego scenariusza
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
        """GĹ‚Ăłwna metoda Ĺ‚adowania danych gry"""
        try:
            # PrĂłbuj zaĹ‚adowaÄ‡ dane z CSV
            # (w przyszĹ‚oĹ›ci moĹĽna tutaj dodaÄ‡ Ĺ‚adowanie z plikĂłw CSV)

            # Na razie uĹĽywamy danych fallback
            self.load_fallback_data()

        except Exception as e:
            print(f"BĹ‚Ä…d Ĺ‚adowania danych: {e}")
            self.load_fallback_data()

    def create_action_cards(self) -> List[ActionCard]:
        """Tworzy standardowy zestaw 5 kart akcji"""
        return [
            ActionCard(
                action_type=ActionType.PROWADZ_BADANIA,
                action_points=3,
                basic_action="Aktywuj 1 doktoranta â†’ +1 heks na badanie",
                additional_actions=[
                    ("Aktywuj doktora â†’ +2 heksy na badanie", 2),
                    ("Aktywuj profesora â†’ +3 heksy na badanie", 2),
                    ("Rozpocznij nowe badanie â†’ wyĹ‚ĂłĹĽ kartÄ™ z rÄ™ki", 1)
                ]
            ),
            ActionCard(
                action_type=ActionType.ZATRUDNIJ,
                action_points=3,
                basic_action="WeĹş 1K z banku",
                additional_actions=[
                    ("Zatrudnij doktora z rynku â†’ pensja 2K/rundÄ™", 2),
                    ("Zatrudnij profesora z rynku â†’ pensja 3K/rundÄ™", 3),
                    ("Zatrudnij doktoranta â†’ brak pensji", 1),
                    ("Kup kartÄ™ 'Projekty Badawcze' â†’ 2 PB", 1),
                    ("Kup kartÄ™ 'MoĹĽliwoĹ›ci' â†’ 1 PB", 1)
                ]
            ),
            ActionCard(
                action_type=ActionType.PUBLIKUJ,
                action_points=2,
                basic_action="Opublikuj 1 artykuĹ‚",
                additional_actions=[
                    ("WeĹş 3K z banku", 1),
                    ("Kup kartÄ™ 'MoĹĽliwoĹ›ci' â†’ 1 PB", 1),
                    ("Konsultacje komercyjne â†’ aktywuj profesora za 4K", 1)
                ]
            ),
            ActionCard(
                action_type=ActionType.FINANSUJ,
                action_points=3,
                basic_action="WeĹş 2K z banku",
                additional_actions=[
                    ("WpĹ‚aÄ‡ do konsorcjum â†’ 1 PB lub 3K na wybrany projekt", 1),
                    ("ZaĹ‚ĂłĹĽ konsorcjum â†’ zagraj kartÄ™ konsorcjum z rÄ™ki", 1),
                    ("Kredyt awaryjny â†’ +5K, ale -1 Reputacja", 2)
                ]
            ),
            ActionCard(
                action_type=ActionType.ZARZADZAJ,
                action_points=2,
                basic_action="WeĹş 2K z banku",
                additional_actions=[
                    ("OdĹ›wieĹĽ rynek â†’ czasopisma lub badania", 2),
                    ("Kampania PR â†’ wydaj 4K za +1 Reputacja", 1),
                    ("Poprawa wizerunku â†’ wydaj 2 PB za +1 Reputacja", 1)
                ]
            )
        ]

    def load_research_from_csv(self):
        """Wczytuje karty badaĹ„ z pliku CSV"""
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
        """Wczytuje naukowcĂłw z pliku CSV"""
        self.scientists = []
        with open('karty_naukowcy.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                scientist_type = ScientistType.DOKTORANT if 'doktorant' in row['Typ'].lower() else \
                               ScientistType.DOKTOR if 'doktor' in row['Typ'].lower() else \
                               ScientistType.PROFESOR

                scientist = Scientist(
                    name=row['ImiÄ™ i Nazwisko'],
                    type=scientist_type,
                    field=row['Dziedzina'],
                    salary=self.safe_int_parse(row['Pensja']),
                    hex_bonus=self.safe_int_parse(row['Bonus HeksĂłw']),
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
                    member_reward=row['Nagroda_CzĹ‚onkĂłw'],
                    description=row['Opis']
                )
                self.large_projects.append(project)

    def load_scenarios_from_csv(self):
        """Wczytuje scenariusze z pliku CSV"""
        self.scenarios = []
        try:
            with open('karty_scenariusze.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Parse crisis rounds from description or default values
                    crisis_rounds = [3, 5, 7]  # Default pattern
                    crisis_count = 3  # Default count
                    max_rounds = 8  # Default rounds

                    scenario = ScenarioCard(
                        name=row['Nazwa'],
                        story_element=row['Opis_Motywacyjny'],
                        global_modifiers=row['Modyfikator_Punktacji'],
                        max_rounds=max_rounds,
                        victory_conditions=row['Warunek_KoĹ„ca'],
                        crisis_count=crisis_count,
                        crisis_rounds=crisis_rounds,
                        description=f"Scenariusz: {row['Nazwa']}"
                    )
                    self.scenarios.append(scenario)
        except FileNotFoundError:
            print("Nie znaleziono pliku karty_scenariusze.csv")
        except Exception as e:
            print(f"BĹ‚Ä…d wczytywania scenariuszy: {e}")

    def load_data(self):
        """Wczytuje dane gry"""
        try:
            # Wczytaj wszystkie dane z CSV
            self.load_research_from_csv()
            print("Wczytano karty badaĹ„ z CSV")

            self.load_scientists_from_csv()
            print("Wczytano naukowcĂłw z CSV")

            self.load_journals_from_csv()
            print("Wczytano czasopisma z CSV")

            self.load_grants_from_csv()
            print("Wczytano granty z CSV")

            self.load_large_projects_from_csv()
            print("Wczytano wielkie projekty z CSV")

            self.load_scenarios_from_csv()
            print("Wczytano scenariusze z CSV")

            # Dla pozostaĹ‚ych danych uĹĽyj przykĹ‚adowych (na razie)
            self.load_fallback_data()

        except Exception as e:
            print(f"BĹ‚Ä…d wczytywania CSV: {e}, uĹĽywam danych przykĹ‚adowych")
            self.load_fallback_data()

    def load_fallback_data(self):
        # StwĂłrz przykĹ‚adowych naukowcĂłw tylko jeĹ›li nie zostali wczytani z CSV
        if not hasattr(self, 'scientists') or not self.scientists:
            self.scientists = [
                Scientist("Dr Jan Kowalski", ScientistType.DOKTOR, "Fizyka", 2000, 2, "+1PB przy publikacji", "Fizyk teoretyczny"),
                Scientist("Prof. Anna Nowak", ScientistType.PROFESOR, "Fizyka", 3000, 3, "+2K za badanie", "Ekspert w fizyce kwantowej"),
                Scientist("Dr Maria WiĹ›niewska", ScientistType.DOKTOR, "Biologia", 2000, 2, "+1PB przy publikacji", "Biolog molekularny"),
                Scientist("Prof. Piotr ZieliĹ„ski", ScientistType.PROFESOR, "Chemia", 3000, 3, "+1 heks przy badaniach", "Chemik organiczny"),
                Scientist("Dr Tomasz Nowicki", ScientistType.DOKTOR, "Fizyka", 2000, 2, "Konsorcja -1 PA", "Specjalista detektorĂłw"),
                Scientist("Prof. Ewa Kowalska", ScientistType.PROFESOR, "Biologia", 3000, 3, "+3K za badanie", "Genetyk")
            ]

        # NIE nadpisuj research_cards - zostaw te z CSV
        # JeĹ›li research_cards nie zostaĹ‚y wczytane, stwĂłrz przykĹ‚adowe
        try:
            if not hasattr(self, 'research_cards') or not self.research_cards:
                self.research_cards = [
                    ResearchCard("Bozon Higgsa", "Fizyka", "simple", "4 PB, 2 PZ", "Publikacja w Nature", "Poszukiwanie czÄ…stki Boga", max_hexes=6),
                    ResearchCard("Algorytm Deep Learning", "Fizyka", "simple", "3 PB, 2 PZ", "+1K za publikacjÄ™", "Sztuczna inteligencja", max_hexes=4),
                    ResearchCard("Synteza Organiczna", "Chemia", "simple", "2 PB, 3 PZ", "DostÄ™p do grantĂłw", "Nowe zwiÄ…zki chemiczne", max_hexes=5),
                    ResearchCard("Terapia Genowa", "Biologia", "simple", "5 PB, 4 PZ", "10K natychmiast", "Leczenie genĂłw", max_hexes=7),
                    ResearchCard("Teoria Strun", "Fizyka", "simple", "6 PB, 3 PZ", "DostÄ™p do Uniwersum", "Unifikacja siĹ‚", max_hexes=8),
                    ResearchCard("Superprzewodnik", "Fizyka", "simple", "2 PB, 2 PZ", "+3K za badanie", "Zerowa rezystancja", max_hexes=4),
                    ResearchCard("Fuzja JÄ…drowa", "Fizyka", "simple", "5 PB, 4 PZ", "10K + energia", "Reaktor fuzji", max_hexes=6),
                    ResearchCard("NanomateriaĹ‚y", "Chemia", "simple", "4 PB, 3 PZ", "Specjalne wĹ‚aĹ›ciwoĹ›ci", "Rewolucyjne materiaĹ‚y", max_hexes=5)
                ]

                # StwĂłrz czasopisma tylko jeĹ›li nie zostaĹ‚y wczytane z CSV
                if not hasattr(self, 'journals') or not self.journals:
                    self.journals = [
                        JournalCard("Nature", 10, 15, "Reputacja 4+", 5, "PrestiĹĽ miÄ™dzynarodowy", "Najlepsze czasopismo Ĺ›wiata"),
                        JournalCard("Science", 9, 14, "Reputacja 4+", 5, "DostÄ™p do konferencji", "AmerykaĹ„ski odpowiednik Nature"),
                        JournalCard("Physical Review", 8, 12, "1 badanie fizyczne", 4, "WspĂłĹ‚praca fizyczna", "Czasopismo fizyczne"),
                        JournalCard("Cell", 8, 12, "1 badanie biologiczne", 4, "PrzeĹ‚om medyczny", "Czasopismo biologiczne"),
                        JournalCard("Journal of Chemistry", 7, 10, "1 badanie chemiczne", 4, "Innowacje chemiczne", "Czasopismo chemiczne"),
                        JournalCard("Local Journal", 3, 5, "Brak", 2, "Brak", "Lokalne czasopismo"),
                        JournalCard("Research Today", 4, 6, "Brak", 2, "DostÄ™p do sieci", "OgĂłlne czasopismo"),
                        JournalCard("Innovation Weekly", 5, 8, "1 publikacja", 3, "Networking", "Czasopismo innowacji")
                    ]

                # StwĂłrz granty tylko jeĹ›li nie zostaĹ‚y wczytane z CSV
                if not hasattr(self, 'grants') or not self.grants:
                    self.grants = [
                        GrantCard("Grant Startup", "Brak wymagaĹ„", "10 punktĂłw aktywnoĹ›ci", "8K", "+2K/rundÄ™", "Grant dla poczÄ…tkujÄ…cych"),
                        GrantCard("Grant Badawczy", "Min. 1 doktor", "2 publikacje", "12K", "+2K/rundÄ™", "Standardowy grant badawczy"),
                        GrantCard("Grant Fizyczny", "Spec. Fizyka", "1 badanie fizyczne", "14K", "+2K/rundÄ™", "Grant dla fizykĂłw"),
                        GrantCard("Grant Biologiczny", "Spec. Biologia", "1 badanie biologiczne", "14K", "+2K/rundÄ™", "Grant dla biologĂłw"),
                        GrantCard("Grant Chemiczny", "Spec. Chemia", "1 badanie chemiczne", "14K", "+2K/rundÄ™", "Grant dla chemikĂłw"),
                        GrantCard("Grant PrestiĹĽowy", "Reputacja 4+", "Publikacja w Nature", "18K", "+2K/rundÄ™", "Elitarny grant"),
                        GrantCard("Grant WspĂłĹ‚pracy", "Brak", "ZaĹ‚ĂłĹĽ konsorcjum", "15K", "+2K/rundÄ™", "Grant na wspĂłĹ‚pracÄ™"),
                        GrantCard("Grant Kryzysowy", "Brak", "Utrzymaj pensje", "10K", "+2K/rundÄ™", "Grant awaryjny"),
                        GrantCard("Grant Technologiczny", "Min. 1 profesor", "2 ukoĹ„czone badania", "16K", "+2K/rundÄ™", "Grant technologiczny"),
                        GrantCard("Grant Interdyscyplinarny", "2 rĂłĹĽne dziedziny", "1 badanie z kaĹĽdej dziedziny", "24K", "+2K/rundÄ™", "Grant interdyscyplinarny")
                    ]

            # StwĂłrz instytuty (zawsze)
            self.institutes = [
                InstituteCard("MIT", "8K, 2 PZ", 3, "+1 heks przy fizyce", "4. naukowiec bez kary", "CzoĹ‚owa uczelnia techniczna"),
                InstituteCard("CERN", "6K, 4 PZ", 3, "Konsorcja -1 PA", "Granty konsorcjĂłw zawsze dostÄ™pne", "NajwiÄ™ksze lab fizyki"),
                InstituteCard("Max Planck", "7K, 3 PZ", 3, "+1 PB za badanie", "Limit rÄ™ki +2", "Niemiecki instytut badawczy"),
                InstituteCard("Harvard University", "10K, 1 PZ", 3, "+1 Rep za publikacjÄ™ IF 6+", "5. naukowiec bez kary", "PrestiĹĽowa uczelnia"),
                InstituteCard("Cambridge", "7K, 3 PZ", 4, "+2K za badanie", "Wszystkie publikacje +1 PZ", "Brytyjska tradycja"),
                InstituteCard("Stanford", "9K, 2 PZ", 3, "+1 heks fizyka", "Karty Okazji podwĂłjne bonusy", "Dolina Krzemowa")
            ]

            # StwĂłrz Wielkie Projekty tylko jeĹ›li nie zostaĹ‚y wczytane z CSV
            if not hasattr(self, 'large_projects') or not self.large_projects:
                self.large_projects = [
                LargeProject(
                        name="FUZJA JÄ„DROWA",
                        requirements="22 PB + 20K + 2 ukoĹ„czone badania fizyczne",
                        director_reward="+10 PZ + wszystkie akcje kosztujÄ… -1 PA",
                        member_reward="+4 PZ kaĹĽdy",
                        description="Reaktor fuzji jÄ…drowej - przeĹ‚om energetyczny"
                    ),
                    LargeProject(
                        name="SUPERPRZEWODNIK",
                        requirements="18 PB + 25K + 2 ukoĹ„czone badania fizyczne",
                        director_reward="+8 PZ + karta Superprzewodnik",
                        member_reward="+3 PZ kaĹĽdy",
                        description="MateriaĹ‚ o zerowej rezystancji"
                    ),
                    LargeProject(
                        name="TERAPIA GENOWA",
                        requirements="15 PB + 30K + 1 profesor + 1 badanie biologiczne",
                        director_reward="+6 PZ + karta Terapia genowa",
                        member_reward="+2 PZ + 5K kaĹĽdy",
                        description="Uniwersalna terapia genowa"
                    ),
                    LargeProject(
                        name="EKSPLORACJA MARSA",
                        requirements="20 PB + 35K + 3 ukoĹ„czone badania",
                        director_reward="+7 PZ + dostÄ™p do Mars Journal",
                        member_reward="+3 PZ + 1 dodatkowa karta",
                        description="Pierwsza staĹ‚a baza na Marsie"
                    ),
                    LargeProject(
                        name="NANOMATERIAĹY",
                        requirements="16 PB + 15K + 2 badania chemiczne + 1 fizyczne",
                        director_reward="+5 PZ + granty chemiczne +3K",
                        member_reward="+2 PZ + ochrona przed kryzysem",
                        description="Rewolucyjne nanomateriaĹ‚y"
                )
            ]

            print("Dane gry zaĹ‚adowane pomyĹ›lnie!")

        except Exception as e:
            print(f"BĹ‚Ä…d podczas wczytywania danych: {e}")

        # StwĂłrz karty konsorcjĂłw (15 sztuk) - zawsze
        if not hasattr(self, 'consortium_cards') or not self.consortium_cards:
            self.consortium_cards = [ConsortiumCard() for _ in range(15)]

        # StwĂłrz karty intryg (20 sztuk) - zawsze
        if not hasattr(self, 'intrigue_cards') or not self.intrigue_cards:
            self.intrigue_cards = [
                IntrigueCard("SabotaĹĽ", "Przeciwnik traci 1 heks z badania", "opponent", "ZakĹ‚Ăłcenie prac badawczych przeciwnika",
                    [IntrigueEffect("opponent", "research_hex", "subtract", 1, "research_hex")]),

                IntrigueCard("Szpiegostwo", "Skopiuj kartÄ™ badania przeciwnika", "opponent", "KradzieĹĽ pomysĹ‚Ăłw naukowych",
                    [IntrigueEffect("opponent", "research_card", "copy", 1, "research_card")]),

                IntrigueCard("Skandal", "Przeciwnik traci 1 punkt reputacji", "opponent", "Ujawnienie kompromitujÄ…cych faktĂłw",
                    [IntrigueEffect("opponent", "reputation", "subtract", 1)]),

                IntrigueCard("Poaching", "Przejmij naukowca od przeciwnika", "opponent", "Przeteapranie cennego pracownika",
                    [IntrigueEffect("opponent", "scientist", "steal", 1, "scientist")]),

                IntrigueCard("Blokada grantu", "Zablokuj grant przeciwnika na 1 rundÄ™", "opponent", "Lobbowanie przeciw konkurencji",
                    [IntrigueEffect("opponent", "grant", "block", 1, "grant", 1)]),

                IntrigueCard("PrzejÄ™cie publikacji", "Przejmij pierwszeĹ„stwo publikacji", "opponent", "Szybsza publikacja tego samego tematu",
                    [IntrigueEffect("opponent", "publication", "steal", 1, "publication")]),

                IntrigueCard("Audit finansowy", "Przeciwnik traci 3K", "opponent", "Nieprzewidziane koszty kontroli",
                    [IntrigueEffect("opponent", "credits", "subtract", 3000)]),

                IntrigueCard("Atak hakera", "Przeciwnik traci 2 PB", "opponent", "Cyberatak na systemy badawcze",
                    [IntrigueEffect("opponent", "research_points", "subtract", 2)]),

                IntrigueCard("Kryzys wizerunkowy", "Wszystkich przeciwnikĂłw -1 reputacja", "all", "Skandal dotyczÄ…cy caĹ‚ej branĹĽy",
                    [IntrigueEffect("all_opponents", "reputation", "subtract", 1)]),

                IntrigueCard("MiÄ™dzynarodowy bojkot", "Wszyscy tracÄ… dostÄ™p do konsorcjĂłw na rundÄ™", "all", "Polityczny kryzys naukowy",
                    [IntrigueEffect("all_players", "consortium_access", "block", 1, "consortium", 1)]),

                IntrigueCard("KradzieĹĽ IP", "Skopiuj kartÄ™ okazji przeciwnika", "opponent", "PrzemysĹ‚owe szpiegostwo",
                    [IntrigueEffect("opponent", "opportunity_card", "copy", 1, "opportunity_card")]),

                IntrigueCard("Podkupstwo", "Przejmij czĹ‚onkostwo w konsorcjum", "opponent", "Nieczyste zagrania finansowe",
                    [IntrigueEffect("opponent", "consortium_membership", "steal", 1, "consortium")]),

                IntrigueCard("Dezinformacja", "Przeciwnik nie moĹĽe publikowaÄ‡ przez rundÄ™", "opponent", "FaĹ‚szywe doniesienia o wynikach",
                    [IntrigueEffect("opponent", "publication_ability", "block", 1, "publication", 1)]),

                IntrigueCard("Przeciek", "Ujawnij rÄ™kÄ™ przeciwnika", "opponent", "Wyciek poufnych informacji",
                    [IntrigueEffect("opponent", "hand_cards", "reveal", 0, "cards")]),

                IntrigueCard("Awaria sprzÄ™tu", "Przeciwnik traci 2 heksy z aktywnego badania", "opponent", "SabotaĹĽ laboratorium",
                    [IntrigueEffect("opponent", "research_hex", "subtract", 2, "research_hex")]),

                IntrigueCard("Strajk pracownikĂłw", "Przeciwnik traci akcjÄ™ na rundÄ™", "opponent", "Niepokoje spoĹ‚eczne w instytucie",
                    [IntrigueEffect("opponent", "action_ability", "block", 1, "action", 1)]),

                IntrigueCard("Epidemia", "Wszyscy tracÄ… po 1 naukowcu", "all", "Choroba dziesiÄ…tkuje kadry naukowe",
                    [IntrigueEffect("all_players", "scientist", "subtract", 1, "scientist")]),

                IntrigueCard("Kryzys energetyczny", "Wszyscy tracÄ… 2K", "all", "RosnÄ…ce koszty energii",
                    [IntrigueEffect("all_players", "credits", "subtract", 2000)]),

                IntrigueCard("Oszustwo naukowe", "Przeciwnik traci jednÄ… publikacjÄ™", "opponent", "Ujawnienie faĹ‚szowanych danych",
                    [IntrigueEffect("opponent", "publications", "subtract", 1)]),

                IntrigueCard("Afera korupcyjna", "Przeciwnik traci aktualny grant", "opponent", "Skandal finansowy w instytucie",
                    [IntrigueEffect("opponent", "current_grant", "remove", 1, "grant")])
            ]

        # StwĂłrz karty okazji (10 sztuk) - zawsze
        if not hasattr(self, 'opportunity_cards') or not self.opportunity_cards:
            self.opportunity_cards = [
                OpportunityCard("Niespodziana dotacja", "credits", "5K", "Brak", "RzÄ…dowe wsparcie dla nauki", "OKAZJA", [
                    OpportunityEffect("credits", "add", 5000, condition="Brak")
                ]),
                OpportunityCard("Odkrycie w laboratorium", "research_points", "3PB", "Brak", "Przypadkowe odkrycie podczas rutynowych badaĹ„", "OKAZJA", [
                    OpportunityEffect("research_points", "add", 3, condition="Brak")
                ]),
                OpportunityCard("Nagroda naukowa", "reputation", "2", "Min. 1 publikacja", "PrestiĹĽowe wyrĂłĹĽnienie za osiÄ…gniÄ™cia", "OKAZJA", [
                    OpportunityEffect("reputation", "add", 2, condition="Min. 1 publikacja")
                ]),
                OpportunityCard("Dodatkowe finansowanie", "credits", "7K", "Aktywne badanie", "Dofinansowanie trwajÄ…cego projektu", "OKAZJA", [
                    OpportunityEffect("credits", "add", 7000, condition="Aktywne badanie")
                ]),
                OpportunityCard("PrzeĹ‚om metodologiczny", "hex_tokens", "2", "Aktywne badanie", "Nowa metoda przyspiesza badania", "OKAZJA", [
                    OpportunityEffect("hex_tokens", "add", 2, condition="Aktywne badanie")
                ]),
                OpportunityCard("WspĂłĹ‚praca miÄ™dzynarodowa", "action_points", "2", "Reputacja 3+", "Dodatkowe moĹĽliwoĹ›ci dziaĹ‚ania", "OKAZJA", [
                    OpportunityEffect("action_points", "add", 2, condition="Reputacja 3+")
                ]),
                OpportunityCard("Patent komercyjny", "credits", "10K", "UkoĹ„czone badanie", "SprzedaĹĽ praw do wynalazku", "OKAZJA", [
                    OpportunityEffect("credits", "add", 10000, condition="UkoĹ„czone badanie")
                ]),
                OpportunityCard("Visiting professor", "research_points", "5PB", "Min. 1 profesor", "Wizyta wybitnego naukowca", "OKAZJA", [
                    OpportunityEffect("research_points", "add", 5, condition="Min. 1 profesor")
                ]),
                OpportunityCard("Technologiczny venture", "credits", "8K", "Badanie chemiczne lub fizyczne", "Inwestycja w start-up", "OKAZJA", [
                    OpportunityEffect("credits", "add", 8000, condition="Badanie chemiczne lub fizyczne")
                ]),
                OpportunityCard("SzczÄ™Ĺ›liwy przypadek", "research_points", "4PB", "Brak", "Nieoczekiwane odkrycie", "OKAZJA", [
                    OpportunityEffect("research_points", "add", 4, condition="Brak")
                ])
            ]

        # StwĂłrz scenariusze fallback tylko jeĹ›li nie wczytano z CSV
        if not hasattr(self, 'scenarios') or not self.scenarios:
            print("UĹĽywam domyĹ›lnego scenariusza fallback")
            self.scenarios = [
                ScenarioCard(
                    name="Podstawowy Scenariusz",
                    story_element="Standardowa rozgrywka naukowa bez specjalnych modyfikatorĂłw.",
                    global_modifiers="Brak modyfikatorĂłw",
                    max_rounds=8,
                    victory_conditions="100 PZ",
                    crisis_count=2,
                    crisis_rounds=[4, 7],
                    description="DomyĹ›lny scenariusz uĹĽywany gdy CSV nie jest dostÄ™pny."
                )
            ]

        # StwĂłrz karty kryzysĂłw - zawsze
        if not hasattr(self, 'crisis_cards') or not self.crisis_cards:
            self.crisis_cards = [
                CrisisCard("Krach Finansowy", "Wszyscy gracze tracÄ… 50% kredytĂłw",
                          "Globalny kryzys ekonomiczny wpĹ‚ywa na finansowanie nauki", "Kredyty: -50%"),
                CrisisCard("Cyberatak", "Wszyscy gracze tracÄ… 2 PB",
                          "Hakerzy zaatakowali systemy badawcze na caĹ‚ym Ĺ›wiecie", "Badania: -2 PB"),
                CrisisCard("Pandemia", "Wszyscy gracze tracÄ… 1 naukowca (losowo)",
                          "Choroba dziesiÄ…tkuje kadry naukowe", "Personel: -1 naukowiec"),
                CrisisCard("Protest SpoĹ‚eczny", "Wszyscy gracze: -1 Reputacja",
                          "SpoĹ‚eczeĹ„stwo protestuje przeciwko niektĂłrym badaniom", "Reputacja: -1"),
                CrisisCard("Kryzys Energetyczny", "Wszystkie akcje kosztujÄ… +1 PA",
                          "Niedobory energii spowalniajÄ… wszystkie dziaĹ‚ania", "Akcje: +1 PA"),
                CrisisCard("Regulacje Prawne", "Nowe badania kosztujÄ… +2K",
                          "Nowe przepisy zwiÄ™kszajÄ… koszty rozpoczynania badaĹ„", "Badania: +2K koszt"),
                CrisisCard("Strajk PracownikĂłw", "Pensje naukowcĂłw podwojone na 2 rundy",
                          "Naukowcy domagajÄ… siÄ™ wyĹĽszych pensji", "Pensje: x2 przez 2 rundy"),
                CrisisCard("Katastrofa Naturalna", "Wszyscy gracze tracÄ… 1 aktywne badanie",
                          "KlÄ™ska ĹĽywioĹ‚owa niszczy laboratoria", "Badania: -1 aktywne"),
                CrisisCard("Skandal Korupcyjny", "Gracz z najwyĹĽszÄ… reputacjÄ… traci 2 punkty",
                          "Ujawniono aferÄ™ w najwiÄ™kszej instytucji", "Lider: -2 Reputacja"),
                CrisisCard("Wojna Handlowa", "Konsorcja miÄ™dzynarodowe: +3K koszt doĹ‚Ä…czenia",
                          "Konflikty geopolityczne utrudniajÄ… wspĂłĹ‚pracÄ™", "Konsorcja: +3K"),
                CrisisCard("Kryzys Zaufania", "Publikacje: -1 PZ przez 2 rundy",
                          "SpoĹ‚eczeĹ„stwo traci zaufanie do nauki", "Publikacje: -1 PZ"),
                CrisisCard("NiedobĂłr MateriaĹ‚Ăłw", "Wszystkie zakupy kosztujÄ… +1K",
                          "Problemy z Ĺ‚aĹ„cuchem dostaw zwiÄ™kszajÄ… koszty", "Zakupy: +1K"),
                CrisisCard("Exodus TalentĂłw", "KaĹĽdy gracz moĹĽe straciÄ‡ 1 profesora (50% szans)",
                          "Najlepsi naukowcy emigrujÄ… za granicÄ™", "Profesorowie: 50% utraty"),
                CrisisCard("Kryzys Polityczny", "Granty rzÄ…dowe niedostÄ™pne przez 2 rundy",
                          "NiestabilnoĹ›Ä‡ polityczna wstrzymuje finansowanie", "Granty: STOP na 2 rundy"),
                CrisisCard("Awaria Internetu", "WspĂłĹ‚praca miÄ™dzynarodowa niemoĹĽliwa przez rundÄ™",
                          "Globalna awaria sieci paraliĹĽuje komunikacjÄ™", "Konsorcja: STOP na rundÄ™")
            ]

        # Zmieszaj gĹ‚ĂłwnÄ… taliÄ™ (badania + konsorcja + intrygi + okazje) - zawsze
        self.main_deck = (
            self.research_cards.copy() +
            self.consortium_cards.copy() +
            self.intrigue_cards.copy() +
            self.opportunity_cards.copy()
        )
        random.shuffle(self.main_deck)

class SimpleHexWidget(tk.Frame):
    """Uproszczony widget do wizualizacji postÄ™pu badaĹ„"""

    def __init__(self, parent, research: ResearchCard, **kwargs):
        super().__init__(parent, **kwargs)
        self.research = research
        self.setup_ui()

    def setup_ui(self):
        """Tworzy prosty interfejs badania"""
        # Nazwa badania
        title_label = tk.Label(self, text=self.research.name, font=('Arial', 10, 'bold'))
        title_label.pack(pady=2)

        # Pasek postÄ™pu
        progress_frame = tk.Frame(self)
        progress_frame.pack(fill='x', padx=5, pady=2)

        for i in range(self.research.max_hexes):
            color = 'lightgreen' if i < self.research.hexes_placed else 'lightgray'
            if i == 0:
                color = 'green'  # Start
            elif i == self.research.max_hexes - 1:
                color = 'red' if i < self.research.hexes_placed else 'pink'  # End

            hex_label = tk.Label(progress_frame, text='â¬˘', font=('Arial', 16), fg=color)
            hex_label.pack(side='left', padx=1)

        # PostÄ™p
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

            # OdĹ›wieĹĽ widok
            for widget in self.winfo_children():
                widget.destroy()
            self.setup_ui()

            # Powiadom o ukoĹ„czeniu
            if self.research.is_completed:
                messagebox.showinfo("Sukces!", f"Badanie '{self.research.name}' zostaĹ‚o ukoĹ„czone!")

class PrincipiaGame:
    """GĹ‚Ăłwna klasa gry Principia"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PRINCIPIA - Gra Planszowa")
        self.root.geometry("1800x1000")

        # Apply modern theme to root window
        self.root.configure(bg=ModernTheme.BACKGROUND)

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
        self.active_crises = []  # Aktywne kryzysy wpĹ‚ywajÄ…ce na grÄ™
        self.crisis_deck = []  # Talia kryzysĂłw dla obecnego scenariusza

        # Zmienne sieciowe
        self.is_network_game = False
        self.is_host = False
        self.game_server = None
        self.game_client = None
        self.network_player_id = None

        # Aktualna aktywnoĹ›Ä‡
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
        """Tworzy interfejs uĹĽytkownika"""
        # GĹ‚Ăłwny kontener z modernymi spacingami
        main_frame = tk.Frame(self.root, bg=ModernTheme.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=ModernTheme.SPACING_LG, pady=ModernTheme.SPACING_LG)

        # Panel informacji o grze - zmodernizowany
        self.info_frame = tk.LabelFrame(main_frame,
                                      text="đź“Š Informacje o grze",
                                      bg=ModernTheme.SURFACE,
                                      fg=ModernTheme.TEXT_PRIMARY,
                                      relief='flat',
                                      bd=1,
                                      highlightbackground=ModernTheme.BORDER_LIGHT)
        self.info_frame.pack(fill='x', pady=(0, ModernTheme.SPACING_LG))

        info_row = tk.Frame(self.info_frame, bg=ModernTheme.SURFACE)
        info_row.pack(fill='x', padx=ModernTheme.SPACING_LG, pady=ModernTheme.SPACING_MD)

        # Ulepszony typography dla labelĂłw
        self.round_label = tk.Label(info_row, text="Runda: 1",
                                   **ModernTheme.configure_style('header'))
        self.round_label.pack(side='left')

        self.phase_label = tk.Label(info_row, text="Faza: GrantĂłw",
                                   **ModernTheme.configure_style('header'))
        self.phase_label.pack(side='left', padx=(ModernTheme.SPACING_XL, 0))

        self.current_player_label = tk.Label(info_row, text="Gracz: -",
                                           **ModernTheme.configure_style('header'))
        self.current_player_label.pack(side='left', padx=(ModernTheme.SPACING_XL, 0))

        self.action_points_label = tk.Label(info_row, text="PA: 0/0",
                                          **ModernTheme.configure_style('header'))
        self.action_points_label.pack(side='left', padx=(ModernTheme.SPACING_XL, 0))

        # Developer mode indicator (initially hidden) - z lepszymi kolorami
        self.dev_mode_label = tk.Label(info_row, text="đź”§ DEVELOPER MODE",
                                     font=('Segoe UI', ModernTheme.FONT_SIZE_MEDIUM, 'bold'),
                                     bg=ModernTheme.ERROR,
                                     fg=ModernTheme.TEXT_ON_PRIMARY,
                                     padx=ModernTheme.SPACING_MD,
                                     pady=ModernTheme.SPACING_XS)
        self.dev_mode_label.pack(side='right', padx=(ModernTheme.SPACING_XL, 0))
        self.dev_mode_label.pack_forget()  # Hide initially

        # Panel powiadomieĹ„ konsorcjĂłw (poczÄ…tkowo ukryty) - zmodernizowany
        self.notifications_frame = tk.LabelFrame(main_frame,
                                               text="đź”” Powiadomienia",
                                               bg=ModernTheme.ACCENT_LIGHT,
                                               fg=ModernTheme.TEXT_PRIMARY,
                                               relief='flat',
                                               bd=1,
                                               highlightbackground=ModernTheme.ACCENT)
        # Nie packujemy go od razu - bÄ™dzie pokazywany tylko gdy sÄ… powiadomienia

        # Inicjalizacja systemu powiadomieĹ„
        if not hasattr(self, 'consortium_notifications'):
            self.consortium_notifications = []

        # Panel scenariusza i kryzysĂłw - zmodernizowany
        scenario_row = tk.Frame(self.info_frame, bg=ModernTheme.SURFACE)
        scenario_row.pack(fill='x', padx=ModernTheme.SPACING_LG, pady=ModernTheme.SPACING_SM)

        self.scenario_label = tk.Label(scenario_row, text="đźŽ­ Scenariusz: Brak",
                                     font=('Segoe UI', ModernTheme.FONT_SIZE_NORMAL),
                                     bg=ModernTheme.SURFACE,
                                     fg=ModernTheme.TEXT_SECONDARY)
        self.scenario_label.pack(side='left')

        # Panel aktywnych kryzysĂłw
        self.crisis_frame = tk.Frame(scenario_row, bg=ModernTheme.SURFACE)
        self.crisis_frame.pack(side='right', padx=(ModernTheme.SPACING_XL, 0))

        self.crisis_label = tk.Label(self.crisis_frame, text="âš ď¸Ź Aktywne kryzysy: ",
                                   font=('Segoe UI', ModernTheme.FONT_SIZE_NORMAL, 'bold'),
                                   bg=ModernTheme.SURFACE,
                                   fg=ModernTheme.TEXT_SECONDARY)
        self.crisis_label.pack(side='left')

        self.active_crisis_text = tk.Label(self.crisis_frame, text="Brak",
                                         font=('Segoe UI', ModernTheme.FONT_SIZE_NORMAL),
                                         bg=ModernTheme.SURFACE,
                                         fg=ModernTheme.ERROR)
        self.active_crisis_text.pack(side='left')

        # Kontener gĹ‚Ăłwny - zmodernizowany
        content_frame = tk.Frame(main_frame, bg=ModernTheme.BACKGROUND)
        content_frame.pack(fill='both', expand=True)

        # Panel graczy (lewa strona) - zmodernizowany
        self.players_frame = tk.LabelFrame(content_frame,
                                         text="đź‘Ą Gracze",
                                         bg=ModernTheme.SURFACE,
                                         fg=ModernTheme.TEXT_PRIMARY,
                                         relief='flat',
                                         bd=1,
                                         highlightbackground=ModernTheme.BORDER_LIGHT)
        self.players_frame.pack(side='left', fill='y', padx=(0, ModernTheme.SPACING_MD))

        # Notebook dla gĹ‚Ăłwnej gry (Ĺ›rodek) - pozostajemy z ttk dla lepszej funkcjonalnoĹ›ci
        self.main_notebook = ttk.Notebook(content_frame)
        self.main_notebook.pack(side='left', fill='both', expand=True, padx=(0, ModernTheme.SPACING_MD))

        # ZakĹ‚adki - z lepszymi ikonami
        self.game_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.game_tab, text="đźŽ® GĹ‚Ăłwna gra")

        self.markets_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.markets_tab, text="đźŹŞ Rynki")

        self.projects_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.projects_tab, text="đźŹ›ď¸Ź Wielkie Projekty")

        self.achievements_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.achievements_tab, text="đźŹ† OsiÄ…gniÄ™cia")

        # ZakĹ‚adka Developer (initially hidden)
        self.developer_tab = ttk.Frame(self.main_notebook)
        # Tab will be added dynamically when developer mode is enabled

        # Panel badaĹ„ (prawa strona) - zmodernizowany
        self.research_frame = tk.LabelFrame(content_frame,
                                          text="đź”¬ Badania",
                                          bg=ModernTheme.SURFACE,
                                          fg=ModernTheme.TEXT_PRIMARY,
                                          relief='flat',
                                          bd=1,
                                          highlightbackground=ModernTheme.BORDER_LIGHT)
        self.research_frame.pack(side='right', fill='y')

        # Panel kontroli na dole - zmodernizowany
        self.control_frame = tk.LabelFrame(main_frame,
                                         text="âš™ď¸Ź Kontrola",
                                         bg=ModernTheme.SURFACE,
                                         fg=ModernTheme.TEXT_PRIMARY,
                                         relief='flat',
                                         bd=1,
                                         highlightbackground=ModernTheme.BORDER_LIGHT)
        self.control_frame.pack(fill='x', pady=(ModernTheme.SPACING_LG, 0))

        control_buttons = tk.Frame(self.control_frame, bg=ModernTheme.SURFACE)
        control_buttons.pack(side='left', padx=ModernTheme.SPACING_LG, pady=ModernTheme.SPACING_MD)

        # Modernized buttons with better styling
        setup_btn = tk.Button(control_buttons,
                             text="đźŽ® Nowa Gra",
                             command=self.show_game_config_dialog,
                             **ModernTheme.configure_style('button'))
        setup_btn.pack(side='left', padx=(0, ModernTheme.SPACING_MD))

        self.next_phase_btn = tk.Button(control_buttons,
                                       text="âŹ­ď¸Ź NastÄ™pna faza",
                                       command=self.next_phase,
                                       state='disabled',
                                       **ModernTheme.configure_style('button_secondary'))
        self.next_phase_btn.pack(side='left', padx=(0, ModernTheme.SPACING_MD))

        self.pass_btn = tk.Button(control_buttons,
                                 text="âŹ¸ď¸Ź Pas",
                                 command=self.player_pass,
                                 state='disabled',
                                 bg=ModernTheme.WARNING,
                                 fg=ModernTheme.TEXT_ON_PRIMARY,
                                 font=('Segoe UI', ModernTheme.FONT_SIZE_MEDIUM, 'bold'),
                                 relief='flat',
                                 bd=0,
                                 padx=ModernTheme.SPACING_LG,
                                 pady=ModernTheme.SPACING_SM)
        self.pass_btn.pack(side='left', padx=(0, ModernTheme.SPACING_MD))

        self.end_action_btn = tk.Button(control_buttons,
                                       text="đź”š ZakoĹ„cz akcjÄ™",
                                       command=self.end_current_action,
                                       state='disabled',
                                       **ModernTheme.configure_style('button_secondary'))
        self.end_action_btn.pack(side='left', padx=(0, ModernTheme.SPACING_MD))

        self.next_round_btn = tk.Button(control_buttons,
                                       text="đź”„ NastÄ™pna runda",
                                       command=self.advance_round,
                                       state='disabled',
                                       bg=ModernTheme.SUCCESS,
                                       fg=ModernTheme.TEXT_ON_PRIMARY,
                                       font=('Segoe UI', ModernTheme.FONT_SIZE_MEDIUM, 'bold'),
                                       relief='flat',
                                       bd=0,
                                       padx=ModernTheme.SPACING_LG,
                                       pady=ModernTheme.SPACING_SM)
        self.next_round_btn.pack(side='left', padx=(0, ModernTheme.SPACING_MD))

        # Log gry - zmodernizowany
        log_frame = tk.LabelFrame(self.control_frame,
                                 text="đź“ś Log gry",
                                 bg=ModernTheme.SURFACE,
                                 fg=ModernTheme.TEXT_PRIMARY,
                                 relief='flat',
                                 bd=1,
                                 highlightbackground=ModernTheme.BORDER_LIGHT)
        log_frame.pack(side='right', fill='both', expand=True,
                      padx=ModernTheme.SPACING_LG, pady=ModernTheme.SPACING_MD)

        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                 width=50, height=6,
                                                 font=('Segoe UI', ModernTheme.FONT_SIZE_SMALL),
                                                 bg=ModernTheme.SURFACE_VARIANT,
                                                 fg=ModernTheme.TEXT_PRIMARY,
                                                 relief='flat',
                                                 bd=1,
                                                 highlightbackground=ModernTheme.BORDER_LIGHT)
        self.log_text.pack(fill='both', expand=True,
                          padx=ModernTheme.SPACING_SM, pady=ModernTheme.SPACING_SM)

        # Skonfiguruj zakĹ‚adki
        self.setup_game_tab()
        self.setup_markets_tab()
        self.setup_projects_tab()
        self.setup_achievements_tab()

        # Bind keyboard shortcut for developer mode (Ctrl+Shift+D)
        self.root.bind('<Control-Shift-D>', self.toggle_developer_mode)
        self.root.focus_set()  # Ensure window can receive key events

    def setup_game_tab(self):
        """Konfiguruje zakĹ‚adkÄ™ gĹ‚Ăłwnej gry"""
        # ZakĹ‚adka gĹ‚Ăłwnej gry bÄ™dzie zawieraÄ‡ karty akcji i fazy gry
        pass  # ZawartoĹ›Ä‡ bÄ™dzie dodawana dynamicznie przez update_ui


    def setup_markets_tab(self):
        """Konfiguruje zakĹ‚adkÄ™ rynkĂłw"""
        # Kontener gĹ‚Ăłwny
        markets_main = ttk.Frame(self.markets_tab)
        markets_main.pack(fill='both', expand=True, padx=5, pady=5)

        # PodziaĹ‚ na kolumny
        left_markets = ttk.Frame(markets_main)
        left_markets.pack(side='left', fill='both', expand=True, padx=(0, 5))

        right_markets = ttk.Frame(markets_main)
        right_markets.pack(side='right', fill='both', expand=True)

        # Rynek naukowcĂłw
        scientists_frame = ttk.LabelFrame(left_markets, text="Rynek naukowcĂłw")
        scientists_frame.pack(fill='both', expand=True, pady=(0, 5))

        # Scrollable frame dla naukowcĂłw
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
        journals_frame = ttk.LabelFrame(right_markets, text="DostÄ™pne czasopisma")
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
        """Konfiguruje zakĹ‚adkÄ™ Wielkich ProjektĂłw"""
        # WyczyĹ›Ä‡ poprzedniÄ… zawartoĹ›Ä‡
        for widget in self.projects_tab.winfo_children():
            widget.destroy()

        # Kontener gĹ‚Ăłwny z przewijaniem
        projects_canvas = tk.Canvas(self.projects_tab)
        projects_scrollbar = ttk.Scrollbar(self.projects_tab, orient="vertical", command=projects_canvas.yview)
        scrollable_projects_frame = ttk.Frame(projects_canvas)

        scrollable_projects_frame.bind(
            "<Configure>",
            lambda e: projects_canvas.configure(scrollregion=projects_canvas.bbox("all"))
        )

        projects_canvas.create_window((0, 0), window=scrollable_projects_frame, anchor="nw")
        projects_canvas.configure(yscrollcommand=projects_scrollbar.set)

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(scrollable_projects_frame, bg='darkblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text="đźŹ›ď¸Ź WIELKIE PROJEKTY NAUKOWE",
                font=('Arial', 16, 'bold'), bg='darkblue', fg='white').pack(pady=10)

        tk.Label(header_frame, text="DostÄ™pne projekty do realizacji w konsorcjach",
                font=('Arial', 10), bg='darkblue', fg='lightgray').pack(pady=(0, 10))

        # Przyciski zarzÄ…dzania konsorcjami
        management_frame = tk.Frame(header_frame, bg='darkblue')
        management_frame.pack(pady=5)

        # Przycisk zarzÄ…dzania dla kierownikĂłw
        manage_btn = tk.Button(management_frame, text="đź‘‘ ZarzÄ…dzaj swoimi konsorcjami",
                             command=self.show_consortium_management_panel,
                             bg='gold', font=('Arial', 10, 'bold'),
                             relief='raised', borderwidth=2)
        manage_btn.pack(pady=2)

        # Przycisk doĹ‚Ä…czania do konsorcjĂłw (niezaleĹĽny od kart akcji)
        join_btn = tk.Button(management_frame, text="đź¤ť DoĹ‚Ä…cz do konsorcjum",
                           command=self.show_independent_consortium_join,
                           bg='lightgreen', font=('Arial', 10, 'bold'),
                           relief='raised', borderwidth=2)
        join_btn.pack(pady=2)

        # WyĹ›wietl wszystkie Wielkie Projekty
        for project in self.game_data.large_projects:
            project_frame = tk.Frame(scrollable_projects_frame, relief='raised', borderwidth=2, bg='lightcyan')
            project_frame.pack(fill='x', padx=10, pady=5)

            # NagĹ‚Ăłwek projektu
            project_header = tk.Frame(project_frame, bg='steelblue')
            project_header.pack(fill='x', padx=5, pady=5)

            tk.Label(project_header, text=project.name, font=('Arial', 14, 'bold'),
                    bg='steelblue', fg='white').pack(pady=5)

            # Wymagania
            req_frame = tk.Frame(project_frame, bg='lightcyan')
            req_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(req_frame, text="đź“‹ WYMAGANIA:", font=('Arial', 11, 'bold'),
                    bg='lightcyan').pack(anchor='w')
            tk.Label(req_frame, text=project.requirements, font=('Arial', 10),
                    bg='lightcyan', wraplength=600, justify='left').pack(anchor='w', padx=20)

            # Nagrody
            rewards_frame = tk.Frame(project_frame, bg='lightcyan')
            rewards_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(rewards_frame, text="đźŹ† NAGRODY:", font=('Arial', 11, 'bold'),
                    bg='lightcyan').pack(anchor='w')

            # Nagroda dyrektora
            tk.Label(rewards_frame, text=f"đź‘‘ Dyrektor: {project.director_reward}",
                    font=('Arial', 10, 'bold'), bg='lightcyan', fg='darkblue').pack(anchor='w', padx=20)

            # Nagroda czĹ‚onkĂłw
            tk.Label(rewards_frame, text=f"đź‘Ą CzĹ‚onkowie: {project.member_reward}",
                    font=('Arial', 10), bg='lightcyan', fg='darkgreen').pack(anchor='w', padx=20)

            # Opis
            if project.description:
                desc_frame = tk.Frame(project_frame, bg='lightcyan')
                desc_frame.pack(fill='x', padx=10, pady=5)

                tk.Label(desc_frame, text="đź“– OPIS:", font=('Arial', 11, 'bold'),
                        bg='lightcyan').pack(anchor='w')
                tk.Label(desc_frame, text=project.description, font=('Arial', 10),
                        bg='lightcyan', wraplength=600, justify='left', fg='gray').pack(anchor='w', padx=20)

            # Status projektu
            status_frame = tk.Frame(project_frame, bg='lightcyan')
            status_frame.pack(fill='x', padx=10, pady=5)

            if project.director:
                if project.is_completed:
                    status_text = f"âś… UKOĹCZONY - đź‘‘ Kierownik: {project.director.name}"
                    status_color = 'green'
                    bg_color = 'lightgreen'
                else:
                    status_text = f"đź”¨ W REALIZACJI - đź‘‘ Kierownik: {project.director.name}"
                    status_color = 'darkblue'
                    bg_color = 'lightyellow'
            else:
                status_text = "âŹł OCZEKUJE NA KIEROWNIKA KONSORCJUM"
                status_color = 'gray'
                bg_color = 'lightgray'

            # UtwĂłrz ramkÄ™ statusu z kolorowym tĹ‚em
            status_label_frame = tk.Frame(status_frame, bg=bg_color, relief='raised', borderwidth=2)
            status_label_frame.pack(fill='x', pady=2)

            tk.Label(status_label_frame, text=status_text, font=('Arial', 11, 'bold'),
                    bg=bg_color, fg=status_color).pack(pady=5)

            # PostÄ™p (jeĹ›li projekt ma dyrektora)
            if project.director and hasattr(project, 'contributed_pb'):
                progress_frame = tk.Frame(project_frame, bg='lightcyan')
                progress_frame.pack(fill='x', padx=10, pady=(0, 5))

                progress_text = f"đź“Š PostÄ™p: {project.contributed_pb} PB, {project.contributed_credits//1000} K"
                tk.Label(progress_frame, text=progress_text, font=('Arial', 9),
                        bg='lightcyan', fg='darkblue').pack(anchor='w', padx=20)

                # Lista czĹ‚onkĂłw
                if project.members:
                    members_text = "đź‘Ą CzĹ‚onkowie: " + ", ".join([m.name for m in project.members])
                    tk.Label(progress_frame, text=members_text, font=('Arial', 9),
                            bg='lightcyan', fg='darkgreen').pack(anchor='w', padx=20)

                # Lista oczekujÄ…cych na akceptacjÄ™
                if hasattr(project, 'pending_members') and project.pending_members:
                    pending_text = "âŹł OczekujÄ… na akceptacjÄ™: " + ", ".join([m.name for m in project.pending_members])
                    tk.Label(progress_frame, text=pending_text, font=('Arial', 9),
                            bg='lightcyan', fg='orange').pack(anchor='w', padx=20)

        projects_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        projects_scrollbar.pack(side="right", fill="y")

    def setup_achievements_tab(self):
        """Konfiguruje zakĹ‚adkÄ™ OsiÄ…gniÄ™Ä‡ (ukoĹ„czone badania i publikacje)"""
        # WyczyĹ›Ä‡ poprzedniÄ… zawartoĹ›Ä‡
        for widget in self.achievements_tab.winfo_children():
            widget.destroy()

        # GĹ‚Ăłwny kontener z przewijaniem
        main_canvas = tk.Canvas(self.achievements_tab)
        main_scrollbar = ttk.Scrollbar(self.achievements_tab, orient="vertical", command=main_canvas.yview)
        scrollable_main_frame = ttk.Frame(main_canvas)

        scrollable_main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_main_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)

        # NagĹ‚Ăłwek gĹ‚Ăłwny
        header_frame = tk.Frame(scrollable_main_frame, bg='darkgreen', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text="đźŹ† OSIÄ„GNIÄCIA GRACZY",
                font=('Arial', 16, 'bold'), bg='darkgreen', fg='white').pack(pady=10)

        # Panel dla kaĹĽdego gracza
        if self.players:
            for i, player in enumerate(self.players):
                self.create_player_achievements_section(scrollable_main_frame, player)

        main_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        main_scrollbar.pack(side="right", fill="y")

    def create_player_achievements_section(self, parent, player):
        """Tworzy sekcjÄ™ osiÄ…gniÄ™Ä‡ dla konkretnego gracza"""
        # Frame gracza
        player_frame = tk.Frame(parent, relief='raised', borderwidth=2, bg='lightyellow')
        player_frame.pack(fill='x', padx=10, pady=5)

        # NagĹ‚Ăłwek gracza
        player_header = tk.Frame(player_frame, bg=player.color)
        player_header.pack(fill='x', padx=5, pady=5)

        tk.Label(player_header, text=f"đźŽ“ {player.name} ({player.institute.name if player.institute else 'Brak instytutu'})",
                font=('Arial', 14, 'bold'), bg=player.color, fg='white').pack(pady=5)

        # Statystyki gracza
        stats_frame = tk.Frame(player_frame, bg='lightyellow')
        stats_frame.pack(fill='x', padx=10, pady=5)

        stats_text = f"đź“Š PZ: {player.prestige_points} | Badania: {len(player.completed_research)} | Publikacje: {player.publications} | Reputacja: {player.reputation}"
        tk.Label(stats_frame, text=stats_text, font=('Arial', 11, 'bold'),
                bg='lightyellow', fg='darkblue').pack(anchor='w')

        # Sekcja ukoĹ„czonych badaĹ„
        if player.completed_research:
            research_frame = tk.LabelFrame(player_frame, text="đź§Ş UkoĹ„czone Badania", bg='lightyellow')
            research_frame.pack(fill='x', padx=10, pady=5)

            for research in player.completed_research:
                research_item = tk.Frame(research_frame, bg='lightcyan', relief='ridge', borderwidth=1)
                research_item.pack(fill='x', padx=5, pady=2)

                tk.Label(research_item, text=f"đź”¬ {research.name} ({research.field})",
                        font=('Arial', 10, 'bold'), bg='lightcyan').pack(anchor='w', padx=5, pady=2)

                tk.Label(research_item, text=f"Nagroda: {research.basic_reward}",
                        font=('Arial', 9), bg='lightcyan', fg='darkgreen').pack(anchor='w', padx=15)

        # Sekcja publikacji
        if player.publication_history:
            publications_frame = tk.LabelFrame(player_frame, text="đź“– Historia Publikacji", bg='lightyellow')
            publications_frame.pack(fill='x', padx=10, pady=5)

            for journal in player.publication_history:
                pub_item = tk.Frame(publications_frame, bg='lightsteelblue', relief='ridge', borderwidth=1)
                pub_item.pack(fill='x', padx=5, pady=2)

                tk.Label(pub_item, text=f"đź“„ {journal.name} (IF: {journal.impact_factor})",
                        font=('Arial', 10, 'bold'), bg='lightsteelblue').pack(anchor='w', padx=5, pady=2)

                tk.Label(pub_item, text=f"Koszt: {journal.pb_cost} PB â†’ Nagroda: {journal.pz_reward} PZ",
                        font=('Arial', 9), bg='lightsteelblue', fg='darkred').pack(anchor='w', padx=15)

        # JeĹ›li gracz nie ma ĹĽadnych osiÄ…gniÄ™Ä‡
        if not player.completed_research and not player.publication_history:
            tk.Label(player_frame, text="Brak osiÄ…gniÄ™Ä‡ do wyĹ›wietlenia",
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

            # SprawdĹş koszty
            eff_salary = scientist.salary if scientist.salary >= 100 else scientist.salary * 1000
            hire_cost = eff_salary * 2
            if current_player.credits < hire_cost:
                messagebox.showwarning("BĹ‚Ä…d", f"Brak Ĺ›rodkĂłw! Koszt: {hire_cost}K")
                return

            # Zatrudnij
            current_player.credits -= hire_cost
            current_player.scientists.append(scientist)

            # UsuĹ„ z rynku
            self.available_scientists.remove(scientist)

            self.log_message(f"Zatrudniono: {scientist.name} za {hire_cost//1000}K")
            self.update_markets()
            self.update_ui()

    def publish_article(self):
        """Publikuje artykuĹ‚ w wybranym czasopiĹ›mie"""
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

            # SprawdĹş koszty
            if current_player.research_points < journal.pb_cost:
                messagebox.showwarning("BĹ‚Ä…d", f"Brak punktĂłw badaĹ„! Koszt: {journal.pb_cost} PB")
                return

            # SprawdĹş wymagania reputacji (parsuj z requirements)
            rep_required = 0
            if 'Rep' in journal.requirements:
                try:
                    rep_required = int(journal.requirements.replace('Rep', '').strip())
                except:
                    rep_required = 0
            if current_player.reputation < rep_required:
                messagebox.showwarning("BĹ‚Ä…d", f"Za niska reputacja! Wymagane: {rep_required}")
                return

            # Publikuj
            current_player.research_points -= journal.pb_cost
            current_player.prestige_points += journal.pz_reward
            current_player.activity_points += 3  # Punkt aktywnoĹ›ci za publikacjÄ™
            try:
                current_player.round_activity_points += 3
            except Exception:
                pass
            self.log_message(f"Opublikowano w {journal.name} za {journal.pb_cost} PB, +{journal.pz_reward} PZ")
            self.update_ui()

    def take_selected_grant(self):
        """Bierze wybrany grant z listy"""
        if not hasattr(self, 'grants_listbox'):
            return

        selection = self.grants_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Wybierz grant do wziÄ™cia")
            return

        grant_idx = selection[0]
        available_grants = [g for g in self.game_data.grants if not any(p.current_grant and p.current_grant.name == g.name for p in self.players)]

        if grant_idx < len(available_grants):
            grant = available_grants[grant_idx]
            current_player = self.players[self.current_player_idx]

            if current_player.current_grant:
                messagebox.showwarning("BĹ‚Ä…d", "Masz juĹĽ aktywny grant!")
                return

            # WeĹş grant
            current_player.current_grant = grant
            self.log_message(f"WziÄ™to grant: {grant.name}")
            self.update_markets()
            self.update_ui()


    def update_markets(self):
        """Aktualizuje zawartoĹ›Ä‡ rynkĂłw"""
        # Aktualizuj naukowcĂłw na rynku
        if hasattr(self, 'scientists_scrollable_frame'):
            # UsuĹ„ wszystkie istniejÄ…ce przyciski
            for widget in self.scientists_scrollable_frame.winfo_children():
                widget.destroy()

            # Dodaj przyciski dla kaĹĽdego dostÄ™pnego naukowca
            for scientist in self.available_scientists:
                scientist_frame = tk.Frame(self.scientists_scrollable_frame, relief='raised', borderwidth=1)
                scientist_frame.pack(fill='x', padx=2, pady=2)

                # Przycisk podglÄ…du
                preview_btn = ttk.Button(scientist_frame,
                                       text=f"đź‘ď¸Ź {scientist.name}",
                                       command=lambda s=scientist: self.preview_scientist(s))
                preview_btn.pack(side='left', padx=2)

                # Informacje podstawowe
                info_label = tk.Label(scientist_frame,
                                    text=f"{scientist.field} | {scientist.salary}K/rundÄ™ | {scientist.hex_bonus}â¬˘",
                                    font=('Arial', 9))
                info_label.pack(side='left', padx=5)

                # Przycisk zatrudnienia - tylko jeĹ›li gracz ma aktywnÄ… akcjÄ™ ZATRUDNIJ
                if (hasattr(self, 'current_action_card') and self.current_action_card and
                    self.current_action_card.action_type == ActionType.ZATRUDNIJ and
                    self.remaining_action_points >= (2 if scientist.type == ScientistType.DOKTOR else 3 if scientist.type == ScientistType.PROFESOR else 1)):
                    hire_btn = ttk.Button(scientist_frame,
                                        text="Zatrudnij",
                                        command=lambda s=scientist: self.hire_scientist_from_market(s))
                    hire_btn.pack(side='right', padx=2)
                else:
                    # Informacja o wymaganiu karty akcji
                    req_text = "Zagraj kartÄ™ ZATRUDNIJ PERSONEL" if not (hasattr(self, 'current_action_card') and self.current_action_card) else "Brak PA"
                    tk.Label(scientist_frame, text=req_text, font=('Arial', 8), fg='gray').pack(side='right', padx=2)

        # Aktualizuj czasopisma na rynku
        if hasattr(self, 'journals_scrollable_frame'):
            # UsuĹ„ wszystkie istniejÄ…ce przyciski
            for widget in self.journals_scrollable_frame.winfo_children():
                widget.destroy()

            # Dodaj przyciski dla kaĹĽdego dostÄ™pnego czasopisma
            for journal in self.available_journals:
                journal_frame = tk.Frame(self.journals_scrollable_frame, relief='raised', borderwidth=1)
                journal_frame.pack(fill='x', padx=2, pady=2)

                # Przycisk podglÄ…du
                preview_btn = ttk.Button(journal_frame,
                                       text=f"đź‘ď¸Ź {journal.name}",
                                       command=lambda j=journal: self.preview_journal(j))
                preview_btn.pack(side='left', padx=2)

                # Informacje podstawowe
                info_label = tk.Label(journal_frame,
                                    text=f"IF:{journal.impact_factor} | {journal.pb_cost}PB â†’ {journal.pz_reward}PZ",
                                    font=('Arial', 9))
                info_label.pack(side='left', padx=5)

                # Przycisk publikacji - tylko jeĹ›li gracz ma aktywnÄ… akcjÄ™ PUBLIKUJ
                if (hasattr(self, 'current_action_card') and self.current_action_card and
                    self.current_action_card.action_type == ActionType.PUBLIKUJ):
                    publish_btn = ttk.Button(journal_frame,
                                           text="Publikuj",
                                           command=lambda j=journal: self.publish_in_journal_from_market(j))
                    publish_btn.pack(side='right', padx=2)
                else:
                    # Informacja o wymaganiu karty akcji
                    req_text = "Zagraj kartÄ™ PUBLIKUJ"
                    tk.Label(journal_frame, text=req_text, font=('Arial', 8), fg='gray').pack(side='right', padx=2)

    def log_message(self, message: str):
        """Dodaje wiadomoĹ›Ä‡ do logu gry"""
        self.log_text.insert(tk.END, f"[R{self.current_round}] {message}\n")
        self.log_text.see(tk.END)

    def show_game_config_dialog(self):
        """Pokazuje dialog konfiguracji gry"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Konfiguracja nowej gry")
        config_window.geometry("500x400")
        config_window.transient(self.root)
        config_window.grab_set()

        # WybĂłr trybu gry
        mode_frame = ttk.LabelFrame(config_window, text="Tryb gry")
        mode_frame.pack(fill='x', padx=10, pady=10)

        self.game_mode = tk.StringVar(value="local")
        ttk.Radiobutton(mode_frame, text="Gra lokalna", variable=self.game_mode, value="local").pack(anchor='w', padx=5, pady=2)
        ttk.Radiobutton(mode_frame, text="Hostuj grÄ™ sieciowÄ…", variable=self.game_mode, value="host").pack(anchor='w', padx=5, pady=2)
        ttk.Radiobutton(mode_frame, text="DoĹ‚Ä…cz do gry", variable=self.game_mode, value="join").pack(anchor='w', padx=5, pady=2)

        # Konfiguracja graczy (tylko dla lokalnej i hostowania)
        players_frame = ttk.LabelFrame(config_window, text="Gracze")
        players_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Liczba graczy
        count_frame = tk.Frame(players_frame)
        count_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(count_frame, text="Liczba graczy:").pack(side='left')
        self.player_count = tk.IntVar(value=3)
        tk.Spinbox(count_frame, from_=2, to=4, textvariable=self.player_count,
                  command=self.update_player_entries, width=5).pack(side='left', padx=5)

        # Ramka na imiona graczy
        self.names_frame = tk.Frame(players_frame)
        self.names_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.player_name_vars = []
        self.player_entries = []
        self.update_player_entries()

        # Konfiguracja sieciowa (dla trybu doĹ‚Ä…czania)
        network_frame = ttk.LabelFrame(config_window, text="PoĹ‚Ä…czenie sieciowe")
        network_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(network_frame, text="Adres hosta:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.host_address = tk.StringVar(value="localhost")
        tk.Entry(network_frame, textvariable=self.host_address, width=20).grid(row=0, column=1, padx=5, pady=2)

        tk.Label(network_frame, text="Port:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.host_port = tk.IntVar(value=8888)
        tk.Entry(network_frame, textvariable=self.host_port, width=10).grid(row=1, column=1, padx=5, pady=2)

        # Przyciski
        button_frame = tk.Frame(config_window)
        button_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(button_frame, text="Rozpocznij grÄ™",
                 command=lambda: self.start_configured_game(config_window),
                 bg='green', fg='white', font=('Arial', 12, 'bold')).pack(side='right', padx=5)
        tk.Button(button_frame, text="Anuluj",
                 command=config_window.destroy).pack(side='right')

    def update_player_entries(self):
        """Aktualizuje pola do wprowadzania imion graczy"""
        # WyczyĹ›Ä‡ poprzednie pola
        for widget in self.names_frame.winfo_children():
            widget.destroy()

        self.player_name_vars.clear()
        self.player_entries.clear()

        # Kolory dostÄ™pne dla graczy
        colors = ['red', 'blue', 'green', 'purple']
        default_names = ['Gracz 1', 'Gracz 2', 'Gracz 3', 'Gracz 4']

        for i in range(self.player_count.get()):
            row_frame = tk.Frame(self.names_frame)
            row_frame.pack(fill='x', pady=2)

            # Kolor gracza
            color_label = tk.Label(row_frame, text=f"â—Ź", fg=colors[i], font=('Arial', 16))
            color_label.pack(side='left', padx=5)

            # Nazwa gracza
            tk.Label(row_frame, text=f"Gracz {i+1}:", width=8).pack(side='left')
            name_var = tk.StringVar(value=default_names[i])
            entry = tk.Entry(row_frame, textvariable=name_var, width=20)
            entry.pack(side='left', padx=5)

            self.player_name_vars.append(name_var)
            self.player_entries.append(entry)

    def start_configured_game(self, config_window):
        """Rozpoczyna grÄ™ z podanÄ… konfiguracjÄ…"""
        # Pobierz konfiguracjÄ™
        mode = self.game_mode.get()
        player_count = self.player_count.get()
        player_names = [var.get().strip() or f"Gracz {i+1}" for i, var in enumerate(self.player_name_vars)]

        config_window.destroy()

        if mode == "local":
            self.setup_local_game(player_count, player_names)
        elif mode == "host":
            self.setup_host_game(player_count, player_names)
        elif mode == "join":
            self.join_network_game()

    def setup_local_game(self, player_count, player_names):
        """Konfiguruje grÄ™ lokalnÄ…"""
        self.is_network_game = False
        self.setup_game(player_count, player_names)

    def setup_host_game(self, player_count, player_names):
        """Konfiguruje grÄ™ jako host sieciowy"""
        self.is_network_game = True
        self.is_host = True

        # Uruchom serwer gry
        self.game_server = GameServer(port=self.host_port.get())
        if self.game_server.start(self):
            # Pobierz lokalne IP
            local_ip = self.get_local_ip()
            port = self.host_port.get()

            self.log_message(f"đźŽ® Serwer uruchomiony na porcie {port}")
            self.log_message(f"đź”— Twoje IP: {local_ip}")
            self.log_message(f"đź“‹ Gracze mogÄ… siÄ™ Ĺ‚Ä…czyÄ‡ uĹĽywajÄ…c: {local_ip}:{port}")

            # PokaĹĽ dialog z informacjami o serwerze
            self.show_server_info_dialog(local_ip, port)

            self.setup_game(player_count, player_names)
        else:
            messagebox.showerror("BĹ‚Ä…d", "Nie udaĹ‚o siÄ™ uruchomiÄ‡ serwera gry")
            self.is_network_game = False
            self.is_host = False

    def get_local_ip(self):
        """Pobiera lokalne IP komputera"""
        try:
            # PoĹ‚Ä…cz siÄ™ z zewnÄ™trznym serwerem aby znaleĹşÄ‡ lokalne IP
            with socket_lib.socket(socket_lib.AF_INET, socket_lib.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    def show_server_info_dialog(self, ip, port):
        """Pokazuje dialog z informacjami o serwerze"""
        info_dialog = tk.Toplevel(self.root)
        info_dialog.title("Serwer gry uruchomiony")
        info_dialog.geometry("450x300")
        info_dialog.transient(self.root)
        info_dialog.grab_set()

        # TytuĹ‚
        tk.Label(info_dialog, text="đźŽ® Serwer gry uruchomiony!",
                font=('Arial', 16, 'bold'), fg='green').pack(pady=10)

        # Informacje o poĹ‚Ä…czeniu
        info_frame = ttk.LabelFrame(info_dialog, text="Informacje dla graczy")
        info_frame.pack(fill='both', expand=True, padx=20, pady=10)

        tk.Label(info_frame, text="Gracze mogÄ… siÄ™ Ĺ‚Ä…czyÄ‡ uĹĽywajÄ…c:",
                font=('Arial', 12, 'bold')).pack(pady=5)

        # IP i port do skopiowania
        connection_text = f"{ip}:{port}"
        connection_var = tk.StringVar(value=connection_text)
        connection_entry = tk.Entry(info_frame, textvariable=connection_var,
                                   font=('Arial', 14, 'bold'), width=20,
                                   justify='center', state='readonly')
        connection_entry.pack(pady=10)

        # Przycisk kopiowania
        def copy_to_clipboard():
            info_dialog.clipboard_clear()
            info_dialog.clipboard_append(connection_text)
            messagebox.showinfo("Skopiowano", f"Adres {connection_text} zostaĹ‚ skopiowany do schowka!")

        tk.Button(info_frame, text="đź“‹ Skopiuj adres", command=copy_to_clipboard,
                 bg='lightblue', font=('Arial', 10)).pack(pady=5)

        # Instrukcje
        instructions = tk.Text(info_frame, height=6, width=50, wrap=tk.WORD,
                              font=('Arial', 10), bg='lightyellow')
        instructions.pack(pady=10, padx=10)
        instructions.insert(tk.END,
                          f"1. PrzekaĹĽ ten adres innym graczom: {connection_text}\n\n"
                          "2. Gracze powinni wybraÄ‡ 'DoĹ‚Ä…cz do gry' w menu\n\n"
                          "3. WpisaÄ‡ powyĹĽszy adres w polu 'Adres hosta'\n\n"
                          "4. Gdy wszyscy siÄ™ poĹ‚Ä…czÄ…, moĹĽesz rozpoczÄ…Ä‡ grÄ™")
        instructions.config(state='disabled')

        # Przycisk zamkniÄ™cia
        tk.Button(info_dialog, text="OK", command=info_dialog.destroy,
                 bg='green', fg='white', font=('Arial', 12)).pack(pady=10)

    def join_network_game(self):
        """DoĹ‚Ä…cza do gry sieciowej"""
        # Dialog nazwy gracza
        name_dialog = tk.Toplevel(self.root)
        name_dialog.title("Twoja nazwa")
        name_dialog.geometry("300x150")
        name_dialog.transient(self.root)
        name_dialog.grab_set()

        tk.Label(name_dialog, text="Podaj swojÄ… nazwÄ™:", font=('Arial', 12)).pack(pady=10)
        name_var = tk.StringVar(value="Gracz_Sieciowy")
        name_entry = tk.Entry(name_dialog, textvariable=name_var, font=('Arial', 12), width=20)
        name_entry.pack(pady=10)
        name_entry.select_range(0, tk.END)
        name_entry.focus()

        result = {'confirmed': False}

        def confirm_name():
            result['confirmed'] = True
            result['name'] = name_var.get().strip() or "Gracz_Sieciowy"
            name_dialog.destroy()

        def cancel_join():
            name_dialog.destroy()

        button_frame = tk.Frame(name_dialog)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="PoĹ‚Ä…cz", command=confirm_name,
                 bg='green', fg='white').pack(side='left', padx=5)
        tk.Button(button_frame, text="Anuluj", command=cancel_join).pack(side='left', padx=5)

        # ObsĹ‚uga Enter
        name_entry.bind('<Return>', lambda e: confirm_name())
        name_dialog.bind('<Escape>', lambda e: cancel_join())

        # Czekaj na zamkniÄ™cie dialogu
        name_dialog.wait_window()

        if not result['confirmed']:
            return

        # PoĹ‚Ä…cz z serwerem
        player_name = result['name']
        host = self.host_address.get()
        port = self.host_port.get()

        self.is_network_game = True
        self.is_host = False

        # UtwĂłrz klienta i poĹ‚Ä…cz
        self.game_client = GameClient()
        if self.game_client.connect(host, port, player_name, self):
            self.log_message(f"đź”— PoĹ‚Ä…czono z grÄ… na {host}:{port} jako {player_name}")
            self.log_message("âŹł Oczekiwanie na rozpoczÄ™cie gry...")

            # Ukryj normalny interfejs gry do czasu synchronizacji
            self.show_network_waiting_ui()
        else:
            messagebox.showerror("BĹ‚Ä…d", f"Nie udaĹ‚o siÄ™ poĹ‚Ä…czyÄ‡ z serwerem {host}:{port}")
            self.is_network_game = False

    def show_network_waiting_ui(self):
        """Pokazuje interfejs oczekiwania na grÄ™ sieciowÄ…"""
        # WyczyĹ›Ä‡ gĹ‚Ăłwny interfejs
        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)

        # Dodaj zakĹ‚adkÄ™ oczekiwania
        waiting_frame = ttk.Frame(self.notebook)
        self.notebook.add(waiting_frame, text="đźŚ Gra sieciowa")

        # Komunikat oczekiwania
        tk.Label(waiting_frame, text="đź”— PoĹ‚Ä…czono z grÄ… sieciowÄ…",
                font=('Arial', 16, 'bold'), fg='green').pack(pady=20)
        tk.Label(waiting_frame, text="âŹł Oczekiwanie na rozpoczÄ™cie gry przez hosta...",
                font=('Arial', 12)).pack(pady=10)

        # Informacje o poĹ‚Ä…czeniu
        info_frame = ttk.LabelFrame(waiting_frame, text="Informacje o poĹ‚Ä…czeniu")
        info_frame.pack(padx=20, pady=20, fill='x')

        tk.Label(info_frame, text=f"Serwer: {self.host_address.get()}:{self.host_port.get()}",
                font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        tk.Label(info_frame, text=f"Twoja nazwa: {self.game_client.player_id if self.game_client else 'Nieznana'}",
                font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)

        # Przycisk rozĹ‚Ä…czenia
        tk.Button(waiting_frame, text="RozĹ‚Ä…cz siÄ™", command=self.disconnect_from_network,
                 bg='red', fg='white', font=('Arial', 12)).pack(pady=20)

    def disconnect_from_network(self):
        """RozĹ‚Ä…cza siÄ™ z gry sieciowej"""
        if self.game_client:
            self.game_client.disconnect()
            self.game_client = None

        self.is_network_game = False
        self.log_message("đź‘‹ RozĹ‚Ä…czono z gry sieciowej")

        # PrzywrĂłÄ‡ normalny interfejs
        self.create_interface()

    def setup_game(self, player_count=3, player_names=None):
        """Konfiguruje nowÄ… grÄ™"""
        try:
            self.game_data.load_data()
            self.log_message("Wczytano dane gry")

            # WybĂłr scenariusza
            self.select_scenario()

            # StwĂłrz graczy z podanÄ… konfiguracjÄ…
            colors = ['red', 'blue', 'green', 'purple']
            if player_names is None:
                player_names = [f'Gracz {i+1}' for i in range(player_count)]

            self.players = []
            for i in range(player_count):
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

                # Daj startowe karty badaĹ„ (maksymalnie 5)
                if self.game_data.main_deck:
                    start_cards = min(5, len(self.game_data.main_deck))
                    player.hand_cards = self.game_data.main_deck[:start_cards]
                    # UsuĹ„ rozdane karty z talii
                    self.game_data.main_deck = self.game_data.main_deck[start_cards:]

                # Daj kaĹĽdemu graczowi jednÄ… kartÄ™ konsorcjum na start
                if self.game_data.consortium_cards:
                    player.hand_cards.append(ConsortiumCard())

                # Daj startowego doktoranta
                player.scientists.append(Scientist("Doktorant", ScientistType.DOKTORANT, "Uniwersalny", 0, 1, "Brak", "MĹ‚ody naukowiec"))

                self.players.append(player)

            self.setup_players_ui()
            self.prepare_round()

            # OdĹ›wieĹĽ zakĹ‚adkÄ™ projektĂłw po zaĹ‚adowaniu danych
            self.setup_projects_tab()

            self.next_phase_btn['state'] = 'normal'
            self.next_round_btn['state'] = 'normal'
            self.log_message("Gra skonfigurowana - 3 graczy")

        except Exception as e:
            messagebox.showerror("BĹ‚Ä…d", f"BĹ‚Ä…d podczas konfiguracji gry: {e}")
            print(f"SzczegĂłĹ‚y bĹ‚Ä™du: {e}")

    def setup_players_ui(self):
        """Tworzy interfejs graczy"""
        # WyczyĹ›Ä‡ poprzedni UI
        for widget in self.players_frame.winfo_children():
            widget.destroy()

        for i, player in enumerate(self.players):
            # PodĹ›wietl aktywnego gracza
            relief = 'solid' if i == self.current_player_idx else 'flat'

            player_frame = ttk.LabelFrame(self.players_frame, text=f"{player.name} ({player.color})", relief=relief)
            player_frame.pack(fill='x', padx=5, pady=5)

            # Instytut
            if player.institute:
                inst_label = ttk.Label(player_frame, text=f"đźŹ›ď¸Ź {player.institute.name[:15]}...",
                                     font=('Arial', 8, 'bold'))
                inst_label.pack(anchor='w', padx=5)

            # Zasoby
            resources_frame = ttk.Frame(player_frame)
            resources_frame.pack(fill='x', padx=5, pady=2)

            ttk.Label(resources_frame, text=f"đź’°{player.credits//1000}K").pack(side='left')
            ttk.Label(resources_frame, text=f"â­{player.prestige_points}PZ").pack(side='left', padx=(5, 0))
            ttk.Label(resources_frame, text=f"đź”¬{player.research_points}PB").pack(side='left', padx=(5, 0))
            ttk.Label(resources_frame, text=f"đź“Š{player.reputation}Rep").pack(side='left', padx=(5, 0))

            # Personel i badania
            status_frame = ttk.Frame(player_frame)
            status_frame.pack(fill='x', padx=5, pady=2)

            scientists_count = len(player.scientists)
            scientists_btn = ttk.Button(status_frame, text=f"đź‘¨â€Ťđź”¬{scientists_count}",
                                       command=lambda p=player: self.show_employed_scientists(p))
            scientists_btn.pack(side='left')

            active_research = len(player.active_research)
            completed_research = len(player.completed_research)
            ttk.Label(status_frame, text=f"đź§Ş{active_research}/{completed_research}").pack(side='left', padx=(5, 0))

            hand_size = len(player.hand_cards)
            ttk.Label(status_frame, text=f"đźŹ{hand_size}").pack(side='left', padx=(5, 0))

            # Grant i akcje
            if player.current_grant:
                grant_label = ttk.Label(player_frame, text=f"đź“‹ {player.current_grant.name[:12]}...",
                                      font=('Arial', 8))
                grant_label.pack(anchor='w', padx=5)

            used_actions = len([card for card in player.action_cards if card.is_used])
            available_actions = len(player.action_cards) - used_actions
            actions_label = ttk.Label(player_frame, text=f"âšˇ {available_actions}/{len(player.action_cards)}",
                                    font=('Arial', 8))
            actions_label.pack(anchor='w', padx=5)

    def prepare_round(self):
        """Przygotowuje nowÄ… rundÄ™"""
        # Resetuj karty akcji graczy
        for player in self.players:
            for card in player.action_cards:
                card.is_used = False
            player.has_passed = False
            # Reset rundowych punktĂłw aktywnoĹ›ci (do subwencji)
            try:
                player.round_activity_points = 0
            except Exception:
                pass

        # Przygotuj granty na rundÄ™
        available_grant_count = min(6, len(self.game_data.grants))
        self.available_grants = random.sample(self.game_data.grants, available_grant_count)

        # Przygotuj czasopisma
        available_journal_count = min(4, len(self.game_data.journals))
        self.available_journals = random.sample(self.game_data.journals, available_journal_count)

        # Przygotuj naukowcĂłw na rynek
        available_scientist_count = min(4, len(self.game_data.scientists))
        self.available_scientists = random.sample(self.game_data.scientists, available_scientist_count)

        self.current_phase = GamePhase.GRANTY
        self.current_player_idx = 0
        self.current_action_card = None
        self.remaining_action_points = 0
        self.update_ui()
        self.log_message(f"RozpoczÄ™to rundÄ™ {self.current_round}")

    def next_phase(self):
        """Przechodzi do nastÄ™pnej fazy gry"""
        if self.current_phase == GamePhase.GRANTY:
            self.current_phase = GamePhase.AKCJE
            self.pass_btn['state'] = 'normal'
            self.log_message("PrzejĹ›cie do fazy akcji")

        elif self.current_phase == GamePhase.AKCJE:
            self.current_phase = GamePhase.PORZADKOWA
            self.pass_btn['state'] = 'disabled'
            self.end_action_btn['state'] = 'disabled'
            self.log_message("PrzejĹ›cie do fazy porzÄ…dkowej")

        elif self.current_phase == GamePhase.PORZADKOWA:
            self.end_round()

        self.update_ui()

    def player_pass(self):
        """Gracz pasuje w fazie akcji"""
        if self.current_phase == GamePhase.AKCJE:
            current_player = self.players[self.current_player_idx]
            current_player.has_passed = True

            # Bonus za pasowanie zaleĹĽny od liczby kart na rÄ™ku
            hand_size = len(current_player.hand_cards)
            pass_bonus = {5: 0, 4: 1000, 3: 3000, 2: 5000, 1: 8000}.get(hand_size, 0)
            current_player.credits += pass_bonus

            self.log_message(f"{current_player.name} pasuje (bonus: {pass_bonus//1000}K)")

            # ZakoĹ„cz aktualnÄ… akcjÄ™
            self.current_action_card = None
            self.remaining_action_points = 0

            # SprawdĹş czy wszyscy spasowali
            if all(p.has_passed for p in self.players):
                self.current_phase = GamePhase.PORZADKOWA
                self.pass_btn['state'] = 'disabled'
                self.end_action_btn['state'] = 'disabled'
                self.log_message("Wszyscy gracze spasowali - przejĹ›cie do fazy porzÄ…dkowej")
            else:
                self.next_player()

            self.update_ui()

    def end_current_action(self):
        """KoĹ„czy aktualnÄ… akcjÄ™"""
        if self.current_action_card:
            self.log_message(f"ZakoĹ„czono akcjÄ™ {self.current_action_card.action_type.value}")
            self.current_action_card = None
            self.remaining_action_points = 0
            self.next_player()
            self.update_ui()

    def next_player(self):
        """Przechodzi do nastÄ™pnego gracza"""
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        # JeĹ›li wszyscy spasowali, pomiĹ„
        attempts = 0
        while self.players[self.current_player_idx].has_passed and attempts < len(self.players):
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            attempts += 1

    def end_round(self):
        """KoĹ„czy rundÄ™ i przechodzi do nastÄ™pnej"""
        # ZapĹ‚aÄ‡ pensje
        for player in self.players:
            self.pay_salaries(player)

        # SprawdĹş cele grantĂłw
        for player in self.players:
            self.check_grant_completion(player)

        # SprawdĹş warunki koĹ„ca gry
        if self.check_end_game():
            return

        # Rozliczenie subwencji rzÄ…dowej (6 punktĂłw aktywnoĹ›ci w tej rundzie â†’ 10K)
        try:
            for player in self.players:
                cg = player.current_grant
                if cg and not getattr(cg, 'is_completed', False) and 'subwencja' in (cg.name or '').lower():
                    rap = getattr(player, 'round_activity_points', 0)
                    if rap >= 6:
                        cg.is_completed = True
                        player.credits += 10000
                        self.log_message(f"{player.name} zrealizowaĹ‚ subwencjÄ™: +10K")
        except Exception:
            pass

        # Auto-ukoĹ„czenie Wielkich ProjektĂłw (jeĹ›li speĹ‚niono progi PB/K)
        try:
            import re
            for project in self.game_data.large_projects:
                if project.is_completed or not project.director:
                    continue
                # Wymagania: PB i K
                req_txt = project.requirements or ''
                m_pb = re.search(r"(\d+)\s*PB", req_txt, flags=re.I)
                pb_req = int(m_pb.group(1)) if m_pb else 0
                m_k = re.search(r"(\d+)\s*K", req_txt, flags=re.I)
                k_req = (int(m_k.group(1)) * 1000) if m_k else 0
                if project.contributed_pb >= pb_req and project.contributed_credits >= k_req:
                    # Nagrody (kierownik i czĹ‚onkowie): sumujemy PZ i jednorazowe K
                    def parse_reward(txt):
                        pz = 0; kredyty = 0
                        m = re.search(r"(\d+)\s*PZ", txt or '', flags=re.I)
                        if m: pz = int(m.group(1))
                        for x in re.findall(r"(\d+)\s*K(?!\s*/\s*rund)", txt or '', flags=re.I):
                            kredyty += int(x) * 1000
                        return pz, kredyty
                    pz_dir, k_dir = parse_reward(project.director_reward)
                    project.director.prestige_points += pz_dir
                    project.director.credits += k_dir
                    pz_mem, k_mem = parse_reward(project.member_reward)
                    for member in getattr(project, 'members', []):
                        if member is project.director:
                            continue
                        member.prestige_points += pz_mem
                        member.credits += k_mem
                    project.is_completed = True
                    self.log_message(f"Ukonczono projekt: {project.name}. Kierownik +{pz_dir} PZ, +{k_dir//1000}K; czlonkowie +{pz_mem} PZ, +{k_mem//1000}K")
        except Exception:
            pass

        self.current_round += 1
        self.prepare_round()

    def pay_salaries(self, player: Player):
        """PĹ‚aci pensje dla gracza"""
        total_salary = 0

        for scientist in player.scientists:
            if scientist.type != ScientistType.DOKTORANT:
                eff_salary = scientist.salary if scientist.salary >= 100 else scientist.salary * 1000
                total_salary += eff_salary

        # Dodaj karÄ™ za przeciÄ…ĹĽenie (wiÄ™cej niĹĽ 3 naukowcĂłw, nie liczÄ…c doktorantĂłw)
        non_doctoral_count = len([s for s in player.scientists
                                if s.type != ScientistType.DOKTORANT])
        if non_doctoral_count > 3:
            overload_penalty = (non_doctoral_count - 3) * 1000
            total_salary += overload_penalty
            self.log_message(f"{player.name}: kara przeciÄ…ĹĽenia {overload_penalty//1000}K")

        # SprawdĹş czy moĹĽe zapĹ‚aciÄ‡
        # Korekta total_salary (konwersja 2/3 â†’ 2K/3K, kara przeciÄ…ĹĽenia)
        try:
            _total = 0
            for s in player.scientists:
                if s.type != ScientistType.DOKTORANT:
                    _sal = s.salary if s.salary >= 100 else s.salary * 1000
                    _total += _sal
            _count = len(player.scientists)
            if _count > 3:
                _total += _count * 1000
            total_salary = _total
        except Exception:
            pass

        if player.credits >= total_salary:
            player.credits -= total_salary
            # PrzywrĂłÄ‡ aktywnoĹ›Ä‡ pĹ‚atnych naukowcĂłw
            try:
                for s in player.scientists:
                    if s.type != ScientistType.DOKTORANT:
                        s.is_paid = True
            except Exception:
                pass
            self.log_message(f"{player.name} zapĹ‚aciĹ‚ {total_salary//1000}K pensji")
        else:
            # Nie moĹĽe zapĹ‚aciÄ‡ - kara reputacji tylko za pierwszÄ… niewypĹ‚atÄ™
            unpaid_count = len([s for s in player.scientists if not s.is_paid])
            if unpaid_count == 0:  # Pierwsza niewypĹ‚ata
                player.reputation = max(0, player.reputation - 1)
                self.log_message(f"{player.name}: niewypĹ‚ata pensji, -1 Reputacja")

            # Oznacz naukowcĂłw jako niewypĹ‚aconych
            for scientist in player.scientists:
                if scientist.type != ScientistType.DOKTORANT:
                    scientist.is_paid = False

    def meets_grant_requirements(self, player: Player, grant: GrantCard) -> bool:
        """Heurystyczna walidacja wymagaĹ„ grantu z pola tekstowego."""
        req = (grant.requirements or '').lower()
        if not req or 'brak wymag' in req:
            return True

        # Reputacja X+
        if 'reputacja' in req:
            import re
            m = re.search(r'reputacja\s*(\d+)', req)
            if m and player.reputation < int(m.group(1)):
                return False

        # Min. 1 doktor/profesor/doktorant
        if 'min. 1 doktorant' in req:
            if not any(s.type == ScientistType.DOKTORANT for s in player.scientists):
                return False
        if 'min. 1 doktor' in req and 'doktorant' not in req:
            if not any(s.type == ScientistType.DOKTOR for s in player.scientists):
                return False
        if 'min. 1 profesor' in req:
            if not any(s.type == ScientistType.PROFESOR for s in player.scientists):
                return False

        # Naukowiec w dziedzinie (fizyk/biolog/chemik)
        if 'naukowiec fizyk' in req and not any('fiz' in s.field.lower() for s in player.scientists):
            return False
        if 'naukowiec biolog' in req and not any('bio' in s.field.lower() for s in player.scientists):
            return False
        if 'naukowiec chemik' in req and not any('chem' in s.field.lower() for s in player.scientists):
            return False

        # Min. 2 naukowcĂłw
        if 'min. 2 naukowc' in req:
            if len(player.scientists) < 2:
                return False

        # Naukowcy z 2 rĂłĹĽnych dziedzin
        if '2 rĂłĹĽnych dziedzin' in req or '2 roznych dziedzin' in req:
            fields = set(s.field for s in player.scientists)
            if len(fields) < 2:
                return False

        # Min. 1 konsorcjum
        if 'min. 1 konsorcjum' in req or 'min. 1 konsorcja' in req:
            in_any = False
            for p in self.game_data.large_projects:
                if p.director == player or player in getattr(p, 'members', []):
                    in_any = True
                    break
            if not in_any:
                return False

        return True

    def check_grant_completion(self, player: Player):
        """Sprawdza czy gracz ukoĹ„czyĹ‚ cel grantu"""
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
            # SprawdĹş czy zaĹ‚oĹĽyĹ‚ konsorcjum
            for project in self.game_data.large_projects:
                if project.director == player:
                    completed = True
                    break

        elif "aktywnoĹ›ci" in goal:
            # Punkty aktywnoĹ›ci: zatrudnienie (2p), publikacja (3p), ukoĹ„czenie badania (4p), konsorcjum (5p)
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
            # Daj nagrodÄ™
            reward = player.current_grant.reward
            credits = self.game_data.safe_int_parse(reward.replace('K', ''), 0) * 1000
            if credits > 0:
                player.credits += credits
                self.log_message(f"{player.name} ukoĹ„czyĹ‚ grant: +{credits//1000}K")

    def check_end_game(self) -> bool:
        """Sprawdza warunki koĹ„ca gry"""
        # SprawdĹş rĂłĹĽne warunki koĹ„ca gry
        for player in self.players:
            # Warunek 1: 35 PZ
            if player.prestige_points >= 35:
                self.end_game(f"{player.name} osiÄ…gnÄ…Ĺ‚ 35 PZ!")
                return True

            # Warunek 2: 6 ukoĹ„czonych badaĹ„
            if len(player.completed_research) >= 6:
                self.end_game(f"{player.name} ukoĹ„czyĹ‚ 6 badaĹ„!")
                return True

        # Warunek 3: 3 Wielkie Projekty ukoĹ„czone
        completed_projects = len([p for p in self.game_data.large_projects if p.is_completed])
        if completed_projects >= 3:
            self.end_game("UkoĹ„czono 3 Wielkie Projekty!")
            return True

        return False

    def end_game(self, reason: str):
        """KoĹ„czy grÄ™"""
        self.game_ended = True
        self.log_message(f"KONIEC GRY: {reason}")

        # PokaĹĽ wyniki koĹ„cowe
        results = []
        for player in self.players:
            total_score = player.prestige_points
            results.append((player.name, total_score, player.prestige_points, len(player.completed_research), player.publications))

        results.sort(key=lambda x: x[1], reverse=True)

        result_text = "WYNIKI KOĹCOWE:\n\n"
        for i, (name, score, pz, research, pubs) in enumerate(results, 1):
            result_text += f"{i}. {name}: {score} PZ ({research} badaĹ„, {pubs} publikacji)\n"

        messagebox.showinfo("Koniec gry", result_text)

    def update_ui(self):
        """Aktualizuje interfejs uĹĽytkownika"""
        self.round_label.config(text=f"Runda: {self.current_round}")
        self.phase_label.config(text=f"Faza: {self.current_phase.value}")

        if self.current_action_card:
            self.action_points_label.config(text=f"PA: {self.remaining_action_points}/{self.current_action_card.action_points}")
        else:
            self.action_points_label.config(text="PA: 0/0")

        if self.players:
            current_player = self.players[self.current_player_idx]
            self.current_player_label.config(text=f"Gracz: {current_player.name}")

        # Ustaw stan przyciskĂłw
        if self.current_action_card and self.remaining_action_points > 0:
            self.end_action_btn['state'] = 'normal'
        else:
            self.end_action_btn['state'] = 'disabled'

        self.setup_players_ui()
        self.setup_game_area()
        self.setup_research_area()
        self.update_markets()
        self.setup_achievements_tab()  # OdĹ›wieĹĽ zakĹ‚adkÄ™ osiÄ…gniÄ™Ä‡
        self.update_notifications()  # OdĹ›wieĹĽ powiadomienia

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
        """Konfiguruje gĹ‚Ăłwny obszar gry w zaleĹĽnoĹ›ci od fazy"""
        # WyczyĹ›Ä‡ poprzedni UI
        for widget in self.game_tab.winfo_children():
            widget.destroy()

        if self.current_phase == GamePhase.GRANTY:
            self.setup_grants_phase()
        elif self.current_phase == GamePhase.AKCJE:
            self.setup_actions_phase()
        elif self.current_phase == GamePhase.PORZADKOWA:
            self.setup_cleanup_phase()

    def setup_grants_phase(self):
        """Konfiguruje interfejs fazy grantĂłw"""
        ttk.Label(self.game_tab, text="đźŽŻ DostÄ™pne Granty", font=('Arial', 14, 'bold')).pack(pady=10)

        # Scroll frame dla grantĂłw
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

            ttk.Label(grant_frame, text=f"đź“‹ Wymagania: {grant.requirements}").pack(anchor='w', padx=5)
            ttk.Label(grant_frame, text=f"đźŽŻ Cel: {grant.goal}").pack(anchor='w', padx=5)
            ttk.Label(grant_frame, text=f"đź’° Nagroda: {grant.reward}").pack(anchor='w', padx=5)

            # SprawdĹş czy gracze sÄ… zainicjalizowani
            can_take = True
            if self.players and self.current_player_idx < len(self.players):
                current_player = self.players[self.current_player_idx]
                can_take = current_player.current_grant is None

            take_btn = ttk.Button(grant_frame, text="WeĹş grant",
                                 command=lambda g=grant: self.take_grant(g),
                                 state='normal' if can_take else 'disabled')
            take_btn.pack(anchor='e', padx=5, pady=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Przycisk subwencji rzÄ…dowej, jeĹ›li brak grantĂłw speĹ‚niajÄ…cych wymagania
        if self.players and self.current_player_idx < len(self.players):
            current_player = self.players[self.current_player_idx]
            eligible = [g for g in self.available_grants if self.meets_grant_requirements(current_player, g)]
            if current_player.current_grant is None and len(eligible) == 0:
                sub_btn = ttk.Button(self.game_tab, text="WeĹş subwencjÄ™ rzÄ…dowÄ… (cel: 6 AP, nagroda 10K)", command=self.take_subvention)
                sub_btn.pack(pady=8)

    def setup_actions_phase(self):
        """Konfiguruje interfejs fazy akcji"""
        current_player = self.players[self.current_player_idx]
        # CERN: refund 1 PA przy akcjach konsorcyjnych w ramach FINANSUJ
        try:
            if self.current_action_card and self.current_action_card.action_type == ActionType.FINANSUJ:
                inst = (current_player.institute.name if current_player.institute else '').lower()
                if 'cern' in inst:
                    # Deprecated: refund moved to effective-cost handling
                    self.remaining_action_points += 0
        except Exception:
            pass

        if current_player.has_passed:
            ttk.Label(self.game_tab, text=f"{current_player.name} spasowaĹ‚",
                     font=('Arial', 14, 'bold')).pack(pady=20)
            return

        ttk.Label(self.game_tab, text="âšˇ KARTY AKCJI", font=('Arial', 14, 'bold')).pack(pady=10)

        # JeĹ›li gracz ma aktywnÄ… kartÄ™ akcji, pokaĹĽ menu akcji
        if self.current_action_card:
            self.show_action_menu()
        else:
            # PokaĹĽ dostÄ™pne karty akcji
            cards_frame = tk.Frame(self.game_tab)
            cards_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # UtwĂłrz siatkÄ™ 2x3 dla kart
            row = 0
            col = 0
            for card in current_player.action_cards:
                card_widget = ActionCardWidget(cards_frame, card,
                                             on_play_callback=self.play_action_card)
                card_widget.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

                col += 1
                if col >= 3:  # 3 karty na rzÄ…d
                    col = 0
                    row += 1

            # Skonfiguruj elastycznoĹ›Ä‡ siatki
            for i in range(3):
                cards_frame.columnconfigure(i, weight=1)
            for i in range(2):
                cards_frame.rowconfigure(i, weight=1)

    def show_action_menu(self):
        """Pokazuje menu akcji dla aktywnej karty"""
        current_player = self.players[self.current_player_idx]

        # NagĹ‚Ăłwek aktywnej karty
        header_frame = tk.Frame(self.game_tab, bg='lightgreen', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(header_frame, text=f"AKTYWNA KARTA: {self.current_action_card.action_type.value}",
                font=('Arial', 12, 'bold'), bg='lightgreen').pack(pady=5)
        tk.Label(header_frame, text=f"PozostaĹ‚e PA: {self.remaining_action_points}",
                font=('Arial', 10, 'bold'), bg='lightgreen').pack()

        # Menu akcji
        menu_frame = tk.Frame(self.game_tab)
        menu_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Akcje dodatkowe
        ttk.Label(menu_frame, text="DostÄ™pne akcje:", font=('Arial', 11, 'bold')).pack(anchor='w')

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

        # UsuĹ„ stare elementy menu akcji
        for widget in self.game_tab.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_children():
                # SprawdĹş czy to nagĹ‚Ăłwek lub menu akcji
                first_child = widget.winfo_children()[0]
                if isinstance(first_child, tk.Label):
                    text = first_child.cget('text')
                    if 'AKTYWNA KARTA' in str(text) or 'DostÄ™pne akcje' in str(text):
                        widget.destroy()

        # PokaĹĽ zaktualizowane menu
        self.show_action_menu()

    def play_action_card(self, action_card: ActionCard):
        """Gracz zagrywa kartÄ™ akcji"""
        if action_card.is_used:
            messagebox.showwarning("Uwaga", "Ta karta zostaĹ‚a juĹĽ uĹĽyta w tej rundzie!")
            return

        current_player = self.players[self.current_player_idx]

        # Oznacz kartÄ™ jako uĹĽytÄ…
        action_card.is_used = True
        self.current_action_card = action_card
        self.remaining_action_points = action_card.action_points

        # Wykonaj akcjÄ™ podstawowÄ…
        self.execute_basic_action(action_card)

        self.log_message(f"{current_player.name} zagraĹ‚ kartÄ™: {action_card.action_type.value}")
        self.update_ui()

    def execute_basic_action(self, action_card: ActionCard):
        """Wykonuje akcjÄ™ podstawowÄ… karty"""
        current_player = self.players[self.current_player_idx]

        if action_card.action_type == ActionType.PROWADZ_BADANIA:
            doktoranci = [s for s in current_player.scientists if s.type == ScientistType.DOKTORANT]
            if doktoranci and doktoranci[0].is_paid and current_player.active_research:
                self.add_hex_to_research(current_player, 1)
                self.log_message(f"Aktywowano doktoranta (+1 heks)")
            elif doktoranci and doktoranci[0].is_paid:
                self.log_message(f"Doktorant gotowy - rozpocznij badanie aby go aktywowaÄ‡")
            else:
                self.log_message(f"Brak aktywnego doktoranta")

        elif action_card.action_type == ActionType.ZATRUDNIJ:
            current_player.credits += 1000
            self.log_message(f"Otrzymano 1K")

        elif action_card.action_type == ActionType.PUBLIKUJ:
            # Akcja podstawowa: moĹĽliwoĹ›Ä‡ publikacji w czasopiĹ›mie z rynku
            # PokaĹĽ okno wyboru czasopisma
            self.show_journal_selection_for_publish()
            self.log_message(f"MoĹĽesz opublikowaÄ‡ w dostÄ™pnych czasopismach (akcja podstawowa)")

        elif action_card.action_type == ActionType.FINANSUJ:
            current_player.credits += 2000
            self.log_message(f"Otrzymano 2K")

        elif action_card.action_type == ActionType.ZARZADZAJ:
            current_player.credits += 2000
            self.log_message(f"Otrzymano 2K")

    def execute_additional_action(self, action_desc: str, cost: int):
        # CERN: -1 PA dla akcji konsorcjum w ramach FINANSUJ
        current_player = self.players[self.current_player_idx]
        effective_cost = cost
        try:
            is_consortium_action = 'konsorcj' in (action_desc or '').lower()
            is_finansuj = bool(self.current_action_card and self.current_action_card.action_type == ActionType.FINANSUJ)
            inst_name = (current_player.institute.name if current_player.institute else '').lower()
            if is_consortium_action and is_finansuj and 'cern' in inst_name:
                effective_cost = max(0, cost - 1)
        except Exception:
            effective_cost = cost
        """Wykonuje akcjÄ™ dodatkowÄ…"""
        if self.remaining_action_points < effective_cost:
            messagebox.showwarning("Uwaga", "Brak wystarczajÄ…cych punktĂłw akcji!")
            return

        current_player = self.players[self.current_player_idx]
        self.remaining_action_points -= effective_cost

        # Parsuj akcjÄ™ i wykonaj
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
        elif "weĹş 3k" in action_desc.lower():
            current_player.credits += 3000
            self.log_message(f"Otrzymano 3K")
        elif "konsultacje" in action_desc.lower():
            self.commercial_consulting()
        elif "wpĹ‚aÄ‡ do konsorcjum" in action_desc.lower():
            self.contribute_to_consortium()
        elif "zaĹ‚ĂłĹĽ konsorcjum" in action_desc.lower():
            self.start_consortium()
        elif "kredyt awaryjny" in action_desc.lower():
            current_player.credits += 5000
            current_player.reputation = max(0, current_player.reputation - 1)
            self.log_message(f"Kredyt awaryjny (+5K, -1 Rep)")
        elif "odĹ›wieĹĽ rynek" in action_desc.lower():
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
        """Inicjuje tryb ukĹ‚adania heksĂłw dla gracza"""
        if not player.active_research:
            messagebox.showinfo("Info", "Brak aktywnych badaĹ„. Najpierw rozpocznij badanie.")
            return

        if player.hex_tokens < hex_count:
            messagebox.showwarning("Uwaga", "Brak wystarczajÄ…cej liczby heksĂłw!")
            return

        # ZnajdĹş pierwsze aktywne badanie
        research = player.active_research[0]

        # WprowadĹş tryb ukĹ‚adania heksĂłw
        self.pending_hex_placements = hex_count
        self.hex_placement_mode = True
        self.current_research_for_hex = research

        self.log_message(f"UkĹ‚adaj {hex_count} heks(Ăłw) na mapie badania '{research.name}'. Kliknij na dozwolone pola.")
        self.update_ui()

        # Auto-expand odpowiedni widget badania
        self.auto_expand_research_widget(research)

    def on_hex_clicked(self, position, research: ResearchCard):
        """ObsĹ‚uguje klikniÄ™cie na heks podczas ukĹ‚adania"""
        if not self.hex_placement_mode or research != self.current_research_for_hex:
            return

        current_player = self.players[self.current_player_idx]

        # SprawdĹş czy moĹĽna poĹ‚oĹĽyÄ‡ heks na tej pozycji
        if research.hex_research_map.can_place_hex(position, research.player_path):
            # UmieĹ›Ä‡ heks
            result = research.hex_research_map.place_hex(position, current_player.color, research.player_path)

            if result['success']:
                # UsuĹ„ heks z puli gracza
                current_player.hex_tokens -= 1
                self.pending_hex_placements -= 1

                # Aktualizuj postÄ™p badania
                research.hexes_placed = len(research.player_path)

                self.log_message(f"PoĹ‚oĹĽono heks na pozycji ({position.q},{position.r})")

                # SprawdĹş bonusy
                if result['bonus']:
                    self.apply_hex_bonus(current_player, result['bonus'])
                    self.log_message(f"Bonus z heksa: {result['bonus']}")

                # SprawdĹş ukoĹ„czenie badania
                if result['completed']:
                    self.log_message(f"Badanie '{research.name}' zostaĹ‚o ukoĹ„czone!")
                    self.complete_research(current_player, research)
                    self.hex_placement_mode = False
                    self.pending_hex_placements = 0
                    self.current_research_for_hex = None
                    self.auto_collapse_all_research_widgets()
                    self.update_ui()
                    return

                # SprawdĹş czy pozostaĹ‚y jeszcze heksy do poĹ‚oĹĽenia
                if self.pending_hex_placements <= 0:
                    self.hex_placement_mode = False
                    self.current_research_for_hex = None
                    self.auto_collapse_all_research_widgets()
                    self.log_message("Wszystkie heksy zostaĹ‚y poĹ‚oĹĽone.")

                self.update_ui()
            else:
                self.log_message("Nie moĹĽna poĹ‚oĹĽyÄ‡ heksa w tym miejscu!")
        else:
            self.log_message("Nie moĹĽna poĹ‚oĹĽyÄ‡ heksa w tym miejscu! Heks musi przylegaÄ‡ do juĹĽ poĹ‚oĹĽonych.")

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
        """KoĹ„czy badanie"""
        research.is_completed = True
        player.active_research.remove(research)
        player.completed_research.append(research)

        # Reset hex map for this player
        if research.hex_research_map:
            research.hex_research_map.reset_player_progress(player.color)

        # Clear player path
        research.player_path = []

        # Odzyskaj heksy - gracz zawsze wraca do 20 heksĂłw
        player.hex_tokens = 20

        # Daj nagrodÄ™ podstawowÄ…
        self.apply_research_reward(player, research.basic_reward)

        # Bonusy instytutĂłw po ukoĹ„czeniu badania
        try:
            inst_name = (player.institute.name if player.institute else '').lower()
            if 'max planck' in inst_name:
                player.research_points += 1  # +1 PB za kaĹĽde ukoĹ„czone badanie
            if 'cambridge' in inst_name:
                player.credits += 2000       # +2K za badanie
        except Exception:
            pass

        # ZwiÄ™ksz punkty aktywnoĹ›ci
        player.activity_points += 4
        try:
            player.round_activity_points += 4
        except Exception:
            pass

        self.log_message(f"UkoĹ„czono badanie: {research.name}")

    def apply_research_reward(self, player: Player, reward: str):
        """Aplikuje nagrodÄ™ za ukoĹ„czone badanie"""
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
        """UĹĽywa naukowca do badaĹ„"""
        current_player = self.players[self.current_player_idx]
        scientists = [s for s in current_player.scientists
                     if s.type == scientist_type and s.is_paid]

        if scientists:
            # Bonusy instytutĂłw: MIT/Stanford +1 heks przy badaniach fizycznych
            extra_hex = 0
            try:
                inst_name = (current_player.institute.name if current_player.institute else '').lower()
                is_mit_or_stanford = ('mit' in inst_name) or ('stanford' in inst_name)
                # JeĹ›li aktywne badanie dotyczy fizyki, dodaj +1 heks
                if is_mit_or_stanford and current_player.active_research:
                    active = current_player.active_research[0]
                    if 'fiz' in (active.field or '').lower():
                        extra_hex = 1
            except Exception:
                pass
            self.add_hex_to_research(current_player, hexes + extra_hex)
            self.log_message(f"Aktywowano {scientist_type.value} (+{hexes} heks)")
        else:
            messagebox.showwarning("Uwaga", f"Brak dostÄ™pnego {scientist_type.value}!")

    def hire_scientist(self, scientist_type: ScientistType):
        """Zatrudnia naukowca"""
        current_player = self.players[self.current_player_idx]

        # SprawdĹş czy moĹĽe sobie pozwoliÄ‡
        cost = {
            ScientistType.DOKTORANT: 0,
            ScientistType.DOKTOR: 2000,
            ScientistType.PROFESOR: 3000
        }.get(scientist_type, 0)

        if current_player.credits >= cost:
            # StwĂłrz nowego naukowca
            if scientist_type == ScientistType.DOKTORANT:
                new_scientist = Scientist(f"Doktorant {len(current_player.scientists)+1}",
                                        ScientistType.DOKTORANT, "Uniwersalny", 0, 1, "Brak", "MĹ‚ody naukowiec")
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
            messagebox.showwarning("Uwaga", "Brak wystarczajÄ…cych Ĺ›rodkĂłw!")

    def start_new_research(self):
        """Rozpoczyna nowe badanie"""
        current_player = self.players[self.current_player_idx]
        if current_player.hand_cards:
            # WeĹş pierwszÄ… kartÄ™ z rÄ™ki
            card = current_player.hand_cards[0]
            current_player.hand_cards.remove(card)
            current_player.active_research.append(card)
            card.is_active = True
            self.log_message(f"RozpoczÄ™to badanie: {card.name}")

    def commercial_consulting(self):
        """Konsultacje komercyjne"""
        current_player = self.players[self.current_player_idx]
        professors = [s for s in current_player.scientists if s.type == ScientistType.PROFESOR and s.is_paid]

        if professors:
            current_player.credits += 4000
            self.log_message(f"Konsultacje komercyjne (+4K)")
        else:
            messagebox.showwarning("Uwaga", "Brak dostÄ™pnego profesora!")

    def contribute_to_consortium(self):
        """WpĹ‚aca do konsorcjum lub skĹ‚ada wniosek o doĹ‚Ä…czenie"""
        current_player = self.players[self.current_player_idx]
        available_consortiums = [p for p in self.game_data.large_projects if p.director and not p.is_completed]

        if not available_consortiums:
            messagebox.showinfo("Info", "Brak dostÄ™pnych konsorcjĂłw")
            return

        # SprawdĹş czy gracz jest kierownikiem ktĂłregoĹ› konsorcjum
        player_consortiums = [p for p in available_consortiums if p.director == current_player]
        other_consortiums = [p for p in available_consortiums if p.director != current_player]

        if player_consortiums and other_consortiums:
            # Gracz ma wĹ‚asne konsorcja i sÄ… teĹĽ inne - daj wybĂłr
            self.show_consortium_contribution_choice(player_consortiums, other_consortiums)
        elif player_consortiums:
            # Gracz ma tylko wĹ‚asne konsorcja
            self.show_consortium_selection_for_contribution(player_consortiums, is_director=True)
        else:
            # Gracz nie ma wĹ‚asnych konsorcjĂłw - moĹĽe tylko skĹ‚adaÄ‡ wnioski
            self.show_consortium_selection_for_join(other_consortiums)

    def show_consortium_contribution_choice(self, player_consortiums, other_consortiums):
        """Pokazuje wybĂłr miÄ™dzy wpĹ‚acaniem do wĹ‚asnych konsorcjĂłw a skĹ‚adaniem wnioskĂłw do innych"""
        popup = tk.Toplevel(self.root)
        popup.title("WybĂłr akcji")
        popup.geometry("400x300")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='lightblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text="WYBIERZ AKCJÄ", font=('Arial', 16, 'bold'), bg='lightblue').pack(pady=5)

        # Opcje
        options_frame = tk.Frame(popup)
        options_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # WpĹ‚aÄ‡ do wĹ‚asnego konsorcjum
        own_btn = tk.Button(options_frame, text="đź’° WpĹ‚aÄ‡ do mojego konsorcjum",
                           command=lambda: [popup.destroy(), self.show_consortium_selection_for_contribution(player_consortiums, is_director=True)],
                           bg='lightgreen', font=('Arial', 12, 'bold'), height=2)
        own_btn.pack(fill='x', pady=10)

        # ZĹ‚ĂłĹĽ wniosek do innego konsorcjum
        other_btn = tk.Button(options_frame, text="đź“ť ZĹ‚ĂłĹĽ wniosek o doĹ‚Ä…czenie do innego konsorcjum",
                             command=lambda: [popup.destroy(), self.show_consortium_selection_for_join(other_consortiums)],
                             bg='lightyellow', font=('Arial', 12, 'bold'), height=2)
        other_btn.pack(fill='x', pady=10)

        # Anuluj
        cancel_btn = tk.Button(options_frame, text="Anuluj", command=popup.destroy,
                              bg='lightgray', font=('Arial', 10))
        cancel_btn.pack(pady=10)

    def show_consortium_selection_for_contribution(self, consortiums, is_director=False):
        """Pokazuje interfejs wyboru konsorcjum do wpĹ‚acania zasobĂłw"""
        popup = tk.Toplevel(self.root)
        popup.title("WpĹ‚aÄ‡ do konsorcjum")
        popup.geometry("600x500")

        # NagĹ‚Ăłwek
        header_color = 'gold' if is_director else 'lightgreen'
        header_text = "đź’° WPĹAÄ† DO KONSORCJUM" if is_director else "đź“ť DOĹÄ„CZ DO KONSORCJUM"
        header_frame = tk.Frame(popup, bg=header_color, relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text=header_text, font=('Arial', 16, 'bold'), bg=header_color).pack(pady=5)

        if is_director:
            tk.Label(header_frame, text="Jako kierownik moĹĽesz wpĹ‚acaÄ‡ bezpoĹ›rednio", font=('Arial', 10), bg=header_color).pack()
        else:
            tk.Label(header_frame, text="ZĹ‚ĂłĹĽ wniosek o doĹ‚Ä…czenie", font=('Arial', 10), bg=header_color).pack()

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

        # Lista konsorcjĂłw
        for project in consortiums:
            project_frame = tk.Frame(scrollable_frame, bg='lightcyan', relief='raised', borderwidth=2)
            project_frame.pack(fill='x', padx=5, pady=5)

            # Nazwa i kierownik
            header_frame = tk.Frame(project_frame, bg='lightcyan')
            header_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(header_frame, text=project.name, font=('Arial', 12, 'bold'), bg='lightcyan').pack(side='left')
            if is_director:
                tk.Label(header_frame, text="đź‘‘ TWOJE KONSORCJUM", font=('Arial', 10), bg='lightcyan', fg='darkblue').pack(side='right')
            else:
                tk.Label(header_frame, text=f"đź‘‘ Kierownik: {project.director.name}", font=('Arial', 10), bg='lightcyan').pack(side='right')

            # PostÄ™p
            progress_frame = tk.Frame(project_frame, bg='lightcyan')
            progress_frame.pack(fill='x', padx=5, pady=2)
            progress_text = f"PostÄ™p: {project.contributed_pb} PB / {project.contributed_credits//1000}K zebrane"
            tk.Label(progress_frame, text=progress_text, font=('Arial', 9), bg='lightcyan').pack(anchor='w')

            # Przyciski wpĹ‚acania
            buttons_frame = tk.Frame(project_frame, bg='lightcyan')
            buttons_frame.pack(fill='x', padx=5, pady=5)

            if is_director:
                # Kierownik moĹĽe wpĹ‚acaÄ‡ bezpoĹ›rednio
                pb_btn = tk.Button(buttons_frame, text="WpĹ‚aÄ‡ 1 PB",
                                  command=lambda p=project: self.contribute_resources_to_project(p, "pb", 1, popup),
                                  bg='lightblue', font=('Arial', 9))
                pb_btn.pack(side='left', padx=2)

                credits_btn = tk.Button(buttons_frame, text="WpĹ‚aÄ‡ 3K",
                                       command=lambda p=project: self.contribute_resources_to_project(p, "credits", 3000, popup),
                                       bg='lightblue', font=('Arial', 9))
                credits_btn.pack(side='left', padx=2)
                # Zakoncz projekt (jesli spelniono wymagania)
                try:
                    can_finish = self.can_complete_project(project)
                except Exception:
                    can_finish = False
                finish_btn = tk.Button(buttons_frame, text="Zakocz projekt",
                                       command=lambda p=project: self.complete_project(p),
                                       bg=('gold' if can_finish else 'lightgray'), font=('Arial', 9, 'bold'))
                if not can_finish:
                    finish_btn.config(state='disabled')
                finish_btn.pack(side='right', padx=4)
            else:
                # Nie-kierownik skĹ‚ada wniosek
                join_btn = tk.Button(buttons_frame, text="ZĹ‚ĂłĹĽ wniosek o doĹ‚Ä…czenie",
                                    command=lambda p=project: self.request_consortium_membership(p, popup),
                                    bg='lightgreen', font=('Arial', 9))
                join_btn.pack(side='left', padx=2)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk anulowania
        tk.Button(popup, text="Anuluj", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def contribute_resources_to_project(self, project, resource_type, amount, popup):
        """Kierownik wpĹ‚aca zasoby bezpoĹ›rednio do swojego konsorcjum"""
        current_player = self.players[self.current_player_idx]

        if resource_type == "pb":
            if current_player.research_points >= amount:
                current_player.research_points -= amount
                project.contributed_pb += amount
                self.log_message(f"{current_player.name} wpĹ‚aciĹ‚ {amount} PB do konsorcjum: {project.name}")
            else:
                messagebox.showwarning("Uwaga", f"Brak wystarczajÄ…cych punktĂłw badawczych! Potrzebujesz {amount} PB")
                return
        elif resource_type == "credits":
            if current_player.credits >= amount:
                current_player.credits -= amount
                project.contributed_credits += amount
                self.log_message(f"{current_player.name} wpĹ‚aciĹ‚ {amount//1000}K do konsorcjum: {project.name}")
            else:
                messagebox.showwarning("Uwaga", f"Brak wystarczajÄ…cych Ĺ›rodkĂłw! Potrzebujesz {amount//1000}K")
                return

        popup.destroy()
        self.update_ui()

    # ===== Wielkie Projekty: parsowanie wymagan i nagrod, ukonczenie =====
    def parse_requirements_numbers(self, requirements_text):
        import re
        txt = requirements_text or ''
        pb_req = 0
        m = re.search(r"(\d+)\s*PB", txt, flags=re.I)
        if m:
            pb_req = int(m.group(1))
        k_req = 0
        m = re.search(r"(\d+)\s*K", txt, flags=re.I)
        if m:
            k_req = int(m.group(1)) * 1000
        comp_req = 0
        m = re.search(r"(\d+)\s*uko\w*czone badania", txt, flags=re.I)
        if m:
            comp_req = int(m.group(1))
        needs_prof = ('profesor' in txt.lower())
        return pb_req, k_req, comp_req, needs_prof

    def parse_reward_numbers(self, reward_text):
        import re
        txt = reward_text or ''
        pz = 0
        kredyty = 0
        m = re.search(r"(\d+)\s*PZ", txt, flags=re.I)
        if m:
            pz = int(m.group(1))
        for m in re.findall(r"(\d+)\s*K(?!\s*/\s*rund)", txt, flags=re.I):
            kredyty += int(m) * 1000
        return pz, kredyty

    def can_complete_project(self, project):
        if project.is_completed or not project.director:
            return False
        pb_req, k_req, comp_req, needs_prof = self.parse_requirements_numbers(project.requirements)
        if project.contributed_pb < pb_req:
            return False
        if project.contributed_credits < k_req:
            return False
        director = project.director
        if comp_req and len(director.completed_research) < comp_req:
            return False
        if needs_prof and not any(s.type == ScientistType.PROFESOR for s in director.scientists):
            return False
        return True

    def complete_project(self, project):
        if project.is_completed:
            return
        if not self.can_complete_project(project):
            messagebox.showwarning("Uwaga", "Nie spelniono wszystkich wymagan projektu")
            return
        director = project.director
        pz_dir, k_dir = self.parse_reward_numbers(project.director_reward)
        director.prestige_points += pz_dir
        director.credits += k_dir
        pz_mem, k_mem = self.parse_reward_numbers(project.member_reward)
        for member in project.members:
            if member is director:
                continue
            member.prestige_points += pz_mem
            member.credits += k_mem
        project.is_completed = True
        self.log_message(f"Ukonczono projekt: {project.name}. Kierownik +{pz_dir} PZ, +{k_dir//1000}K; czlonkowie +{pz_mem} PZ, +{k_mem//1000}K")
        self.update_ui()

    def show_consortium_selection_for_join(self, available_consortiums):
        """Pokazuje interfejs wyboru konsorcjum do zĹ‚oĹĽenia wniosku o czĹ‚onkostwo"""
        popup = tk.Toplevel(self.root)
        popup.title("DoĹ‚Ä…cz do Konsorcjum")
        popup.geometry("600x500")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='lightgreen', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text="đź¤ť DOĹÄ„CZ DO KONSORCJUM", font=('Arial', 16, 'bold'), bg='lightgreen').pack(pady=5)
        tk.Label(header_frame, text="Wybierz konsorcjum i zĹ‚ĂłĹĽ wniosek o doĹ‚Ä…czenie", font=('Arial', 10), bg='lightgreen').pack()

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

        # Lista konsorcjĂłw
        for project in available_consortiums:
            project_frame = tk.Frame(scrollable_frame, bg='lightcyan', relief='raised', borderwidth=2)
            project_frame.pack(fill='x', padx=5, pady=5)

            # Nazwa i kierownik
            header_frame = tk.Frame(project_frame, bg='lightcyan')
            header_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(header_frame, text=project.name, font=('Arial', 12, 'bold'), bg='lightcyan').pack(side='left')
            tk.Label(header_frame, text=f"đź‘‘ Kierownik: {project.director.name}",
                    font=('Arial', 10), bg='lightcyan').pack(side='right')

            # Opis
            tk.Label(project_frame, text=project.description, font=('Arial', 9),
                    bg='lightcyan', wraplength=500).pack(anchor='w', padx=5, pady=2)

            # PostÄ™p
            progress_frame = tk.Frame(project_frame, bg='lightcyan')
            progress_frame.pack(fill='x', padx=5, pady=2)
            progress_text = f"PostÄ™p: {project.contributed_pb} PB / {project.contributed_credits//1000}K zebrane"
            tk.Label(progress_frame, text=progress_text, font=('Arial', 9), bg='lightcyan').pack(anchor='w')

            # CzĹ‚onkowie
            if project.members:
                members_text = "CzĹ‚onkowie: " + ", ".join([member.name for member in project.members])
                tk.Label(project_frame, text=members_text, font=('Arial', 8),
                        bg='lightcyan', wraplength=500).pack(anchor='w', padx=5, pady=2)

            # Nagroda czĹ‚onka
            reward_frame = tk.Frame(project_frame, bg='lightcyan')
            reward_frame.pack(fill='x', padx=5, pady=2)
            tk.Label(reward_frame, text=f"đźŽ Nagroda czĹ‚onka: {project.member_reward}",
                    font=('Arial', 9, 'bold'), bg='lightcyan').pack(anchor='w')

            # Przycisk skĹ‚adania wniosku
            join_btn = ttk.Button(project_frame, text="ZĹ‚ĂłĹĽ wniosek o doĹ‚Ä…czenie",
                                 command=lambda p=project: self.request_consortium_membership(p, popup))
            join_btn.pack(pady=5)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk anulowania
        tk.Button(popup, text="Anuluj", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def request_consortium_membership(self, project, popup):
        """SkĹ‚ada wniosek o czĹ‚onkostwo w konsorcjum"""
        current_player = self.players[self.current_player_idx]

        # SprawdĹş czy gracz juĹĽ jest czĹ‚onkiem lub juĹĽ zĹ‚oĹĽyĹ‚ wniosek
        if current_player in project.members:
            messagebox.showinfo("Info", "JesteĹ› juĹĽ czĹ‚onkiem tego konsorcjum!")
            return

        if current_player in project.pending_members:
            messagebox.showinfo("Info", "JuĹĽ zĹ‚oĹĽyĹ‚eĹ› wniosek o doĹ‚Ä…czenie do tego konsorcjum!")
            return

        # Dodaj gracza do listy oczekujÄ…cych
        project.pending_members.append(current_player)

        self.log_message(f"{current_player.name} zĹ‚oĹĽyĹ‚ wniosek o doĹ‚Ä…czenie do konsorcjum: {project.name}")

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

        messagebox.showinfo("Sukces", f"ZĹ‚oĹĽono wniosek o doĹ‚Ä…czenie do konsorcjum '{project.name}'. Kierownik zostanie powiadomiony.")

        popup.destroy()
        self.update_ui()

    def approve_consortium_membership(self, project, applicant):
        """Kierownik akceptuje wniosek o czĹ‚onkostwo"""
        if applicant in project.pending_members:
            project.pending_members.remove(applicant)
            project.members.append(applicant)

            # UsuĹ„ powiadomienie
            if hasattr(self, 'consortium_notifications'):
                self.consortium_notifications = [
                    notif for notif in self.consortium_notifications
                    if not (notif.get('type') == 'membership_request' and
                           notif.get('project') == project and
                           notif.get('applicant') == applicant)
                ]

            self.log_message(f"{project.director.name} zaakceptowaĹ‚ {applicant.name} do konsorcjum: {project.name}")
            self.update_ui()
            return True
        return False

    def reject_consortium_membership(self, project, applicant):
        """Kierownik odrzuca wniosek o czĹ‚onkostwo"""
        if applicant in project.pending_members:
            project.pending_members.remove(applicant)

            # UsuĹ„ powiadomienie
            if hasattr(self, 'consortium_notifications'):
                self.consortium_notifications = [
                    notif for notif in self.consortium_notifications
                    if not (notif.get('type') == 'membership_request' and
                           notif.get('project') == project and
                           notif.get('applicant') == applicant)
                ]

            self.log_message(f"{project.director.name} odrzuciĹ‚ wniosek {applicant.name} o czĹ‚onkostwo w konsorcjum: {project.name}")
            self.update_ui()
            return True
        return False

    def show_consortium_management_panel(self):
        """Pokazuje panel zarzÄ…dzania konsorcjami dla kierownikĂłw"""
        current_player = self.players[self.current_player_idx]

        # ZnajdĹş konsorcja kierowane przez obecnego gracza
        managed_projects = [p for p in self.game_data.large_projects if p.director == current_player]

        if not managed_projects:
            messagebox.showinfo("Info", "Nie kierujesz ĹĽadnym konsorcjum")
            return

        popup = tk.Toplevel(self.root)
        popup.title("ZarzÄ…dzanie Konsorcjami")
        popup.geometry("700x600")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='gold', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text="đź‘‘ ZARZÄ„DZANIE KONSORCJAMI", font=('Arial', 16, 'bold'), bg='gold').pack(pady=5)
        tk.Label(header_frame, text="ZarzÄ…dzaj swoimi konsorcjami i wnioskami o czĹ‚onkostwo", font=('Arial', 10), bg='gold').pack()

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

        # Lista zarzÄ…dzanych konsorcjĂłw
        for project in managed_projects:
            project_frame = tk.Frame(scrollable_frame, bg='lightyellow', relief='raised', borderwidth=3)
            project_frame.pack(fill='x', padx=5, pady=5)

            # Nazwa i status
            header_frame = tk.Frame(project_frame, bg='lightyellow')
            header_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(header_frame, text=f"đź‘‘ {project.name}", font=('Arial', 14, 'bold'), bg='lightyellow').pack(side='left')
            status_text = "âś… UKOĹCZONY" if project.is_completed else "đź”¨ W REALIZACJI"
            tk.Label(header_frame, text=status_text, font=('Arial', 10), bg='lightyellow').pack(side='right')

            # PostÄ™p
            progress_frame = tk.Frame(project_frame, bg='lightyellow')
            progress_frame.pack(fill='x', padx=5, pady=2)
            progress_text = f"Zebrane zasoby: {project.contributed_pb} PB / {project.contributed_credits//1000}K"
            tk.Label(progress_frame, text=progress_text, font=('Arial', 10), bg='lightyellow').pack(anchor='w')

            # CzĹ‚onkowie
            if project.members:
                members_frame = tk.Frame(project_frame, bg='lightyellow')
                members_frame.pack(fill='x', padx=5, pady=2)
                members_text = "CzĹ‚onkowie: " + ", ".join([member.name for member in project.members])
                tk.Label(members_frame, text=members_text, font=('Arial', 9), bg='lightyellow').pack(anchor='w')

            # OczekujÄ…ce wnioski
            if project.pending_members:
                pending_frame = tk.LabelFrame(project_frame, text="âŹł OczekujÄ…ce wnioski o czĹ‚onkostwo", bg='lightyellow')
                pending_frame.pack(fill='x', padx=5, pady=5)

                for applicant in project.pending_members:
                    applicant_frame = tk.Frame(pending_frame, bg='lightcyan', relief='groove', borderwidth=1)
                    applicant_frame.pack(fill='x', padx=2, pady=2)

                    # Nazwa gracza
                    tk.Label(applicant_frame, text=f"đź‘¤ {applicant.name}", font=('Arial', 10, 'bold'), bg='lightcyan').pack(side='left', padx=5)

                    # Przyciski akceptacji/odrzucenia
                    button_frame = tk.Frame(applicant_frame, bg='lightcyan')
                    button_frame.pack(side='right', padx=5)

                    accept_btn = tk.Button(button_frame, text="âś… Akceptuj",
                                         command=lambda p=project, a=applicant: [self.approve_consortium_membership(p, a), popup.destroy(), self.show_consortium_management_panel()],
                                         bg='lightgreen', font=('Arial', 8))
                    accept_btn.pack(side='left', padx=2)

                    reject_btn = tk.Button(button_frame, text="âťŚ OdrzuÄ‡",
                                         command=lambda p=project, a=applicant: [self.reject_consortium_membership(p, a), popup.destroy(), self.show_consortium_management_panel()],
                                         bg='lightcoral', font=('Arial', 8))
                    reject_btn.pack(side='left', padx=2)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk zamkniÄ™cia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def show_independent_consortium_join(self):
        """Pokazuje interfejs doĹ‚Ä…czania do konsorcjĂłw niezaleĹĽnie od kart akcji"""
        current_player = self.players[self.current_player_idx]
        available_consortiums = [p for p in self.game_data.large_projects
                               if p.director and not p.is_completed and p.director != current_player]

        if not available_consortiums:
            messagebox.showinfo("Info", "Brak dostÄ™pnych konsorcjĂłw do doĹ‚Ä…czenia")
            return

        popup = tk.Toplevel(self.root)
        popup.title("DoĹ‚Ä…cz do Konsorcjum")
        popup.geometry("700x600")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='lightgreen', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text="đź¤ť DOĹÄ„CZ DO KONSORCJUM", font=('Arial', 16, 'bold'), bg='lightgreen').pack(pady=5)
        tk.Label(header_frame, text="ZĹ‚ĂłĹĽ wniosek o doĹ‚Ä…czenie do wybranego konsorcjum", font=('Arial', 10), bg='lightgreen').pack()
        tk.Label(header_frame, text="(NiezaleĹĽne od kart akcji - moĹĽliwe w dowolnym momencie)",
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

        # Lista dostÄ™pnych konsorcjĂłw
        for project in available_consortiums:
            project_frame = tk.Frame(scrollable_frame, bg='lightcyan', relief='raised', borderwidth=2)
            project_frame.pack(fill='x', padx=5, pady=5)

            # NagĹ‚Ăłwek projektu
            header_frame = tk.Frame(project_frame, bg='steelblue')
            header_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(header_frame, text=project.name, font=('Arial', 12, 'bold'),
                    bg='steelblue', fg='white').pack(side='left')
            tk.Label(header_frame, text=f"đź‘‘ Kierownik: {project.director.name}",
                    font=('Arial', 10), bg='steelblue', fg='lightgray').pack(side='right')

            # Opis projektu
            if project.description:
                desc_frame = tk.Frame(project_frame, bg='lightcyan')
                desc_frame.pack(fill='x', padx=5, pady=2)
                tk.Label(desc_frame, text=project.description, font=('Arial', 9),
                        bg='lightcyan', wraplength=600, justify='left').pack(anchor='w')

            # PostÄ™p projektu
            progress_frame = tk.Frame(project_frame, bg='lightcyan')
            progress_frame.pack(fill='x', padx=5, pady=2)
            progress_text = f"đź“Š PostÄ™p: {project.contributed_pb} PB / {project.contributed_credits//1000}K zebrane"
            tk.Label(progress_frame, text=progress_text, font=('Arial', 9), bg='lightcyan').pack(anchor='w')

            # Aktualni czĹ‚onkowie
            if project.members:
                members_frame = tk.Frame(project_frame, bg='lightcyan')
                members_frame.pack(fill='x', padx=5, pady=2)
                members_text = "đź‘Ą CzĹ‚onkowie: " + ", ".join([m.name for m in project.members])
                tk.Label(members_frame, text=members_text, font=('Arial', 9),
                        bg='lightcyan', fg='darkgreen').pack(anchor='w')

            # OczekujÄ…cy na akceptacjÄ™
            if hasattr(project, 'pending_members') and project.pending_members:
                pending_frame = tk.Frame(project_frame, bg='lightcyan')
                pending_frame.pack(fill='x', padx=5, pady=2)
                pending_text = "âŹł OczekujÄ… na akceptacjÄ™: " + ", ".join([m.name for m in project.pending_members])
                tk.Label(pending_frame, text=pending_text, font=('Arial', 9),
                        bg='lightcyan', fg='orange').pack(anchor='w')

            # Nagroda dla czĹ‚onkĂłw
            reward_frame = tk.Frame(project_frame, bg='lightcyan')
            reward_frame.pack(fill='x', padx=5, pady=2)
            tk.Label(reward_frame, text=f"đźŽ Nagroda czĹ‚onka: {project.member_reward}",
                    font=('Arial', 9, 'bold'), bg='lightcyan', fg='darkblue').pack(anchor='w')

            # SprawdĹş status gracza wzglÄ™dem tego projektu
            action_frame = tk.Frame(project_frame, bg='lightcyan')
            action_frame.pack(fill='x', padx=5, pady=5)

            if current_player in project.members:
                tk.Label(action_frame, text="âś… JesteĹ› juĹĽ czĹ‚onkiem tego konsorcjum",
                        font=('Arial', 10, 'bold'), bg='lightcyan', fg='green').pack()
            elif current_player in project.pending_members:
                tk.Label(action_frame, text="âŹł TwĂłj wniosek oczekuje na akceptacjÄ™",
                        font=('Arial', 10, 'bold'), bg='lightcyan', fg='orange').pack()
            else:
                join_btn = tk.Button(action_frame, text="đź“ť ZĹ‚ĂłĹĽ wniosek o doĹ‚Ä…czenie",
                                   command=lambda p=project: self.request_consortium_membership_independent(p, popup),
                                   bg='lightgreen', font=('Arial', 10, 'bold'))
                join_btn.pack()

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk zamkniÄ™cia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def request_consortium_membership_independent(self, project, popup):
        """SkĹ‚ada wniosek o czĹ‚onkostwo niezaleĹĽnie od kart akcji"""
        current_player = self.players[self.current_player_idx]

        # SprawdĹş czy gracz juĹĽ jest czĹ‚onkiem lub juĹĽ zĹ‚oĹĽyĹ‚ wniosek
        if current_player in project.members:
            messagebox.showinfo("Info", "JesteĹ› juĹĽ czĹ‚onkiem tego konsorcjum!")
            return

        if current_player in project.pending_members:
            messagebox.showinfo("Info", "JuĹĽ zĹ‚oĹĽyĹ‚eĹ› wniosek o doĹ‚Ä…czenie do tego konsorcjum!")
            return

        # Dodaj gracza do listy oczekujÄ…cych
        project.pending_members.append(current_player)

        self.log_message(f"{current_player.name} zĹ‚oĹĽyĹ‚ wniosek o doĹ‚Ä…czenie do konsorcjum: {project.name} (niezaleĹĽnie)")

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

        messagebox.showinfo("Sukces", f"ZĹ‚oĹĽono wniosek o doĹ‚Ä…czenie do konsorcjum '{project.name}'. Kierownik zostanie powiadomiony.")

        popup.destroy()
        self.update_ui()

    def start_consortium(self):
        """ZakĹ‚ada konsorcjum"""
        current_player = self.players[self.current_player_idx]

        # SprawdĹş czy gracz ma kartÄ™ konsorcjum w rÄ™ce
        consortium_cards = [card for card in current_player.hand_cards
                           if hasattr(card, 'card_type') and card.card_type == "KONSORCJUM"]
        if not consortium_cards:
            messagebox.showwarning("Uwaga", "Musisz mieÄ‡ KartÄ™ Konsorcjum w rÄ™ce, aby zaĹ‚oĹĽyÄ‡ konsorcjum!")
            return

        available_projects = [p for p in self.game_data.large_projects if not p.director]
        if not available_projects:
            messagebox.showinfo("Info", "Brak dostÄ™pnych Wielkich ProjektĂłw do zaĹ‚oĹĽenia konsorcjum")
            return

        # PokaĹĽ interfejs wyboru projektu
        self.show_project_selection_for_consortium(available_projects, consortium_cards[0])

    def show_project_selection_for_consortium(self, available_projects, consortium_card):
        """Pokazuje interfejs wyboru projektu do zaĹ‚oĹĽenia konsorcjum"""
        popup = tk.Toplevel(self.root)
        popup.title("ZaĹ‚ĂłĹĽ Konsorcjum")
        popup.geometry("600x500")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='gold', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text="đź¤ť ZAĹĂ“Ĺ» KONSORCJUM", font=('Arial', 16, 'bold'), bg='gold').pack(pady=5)
        tk.Label(header_frame, text="Wybierz Wielki Projekt do objÄ™cia kierownictwem", font=('Arial', 10), bg='gold').pack()

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

        # Lista projektĂłw
        for project in available_projects:
            project_frame = tk.Frame(scrollable_frame, bg='lightgray', relief='raised', borderwidth=2)
            project_frame.pack(fill='x', padx=5, pady=5)

            # Nazwa i koszt
            name_frame = tk.Frame(project_frame, bg='lightgray')
            name_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(name_frame, text=project.name, font=('Arial', 12, 'bold'), bg='lightgray').pack(side='left')
            tk.Label(name_frame, text=f"đź’° {project.cost_pb} PB | {project.cost_credits}K",
                    font=('Arial', 10), bg='lightgray').pack(side='right')

            # Opis
            tk.Label(project_frame, text=project.description, font=('Arial', 9),
                    bg='lightgray', wraplength=500).pack(anchor='w', padx=5, pady=2)

            # Nagroda kierownika
            reward_frame = tk.Frame(project_frame, bg='lightgray')
            reward_frame.pack(fill='x', padx=5, pady=2)
            tk.Label(reward_frame, text=f"đź‘‘ Nagroda kierownika: {project.director_reward}",
                    font=('Arial', 9, 'bold'), bg='lightgray').pack(anchor='w')

            # Przycisk zaĹ‚oĹĽenia
            found_btn = ttk.Button(project_frame, text="ZostaĹ„ kierownikiem tego projektu",
                                 command=lambda p=project: self.found_consortium_for_project(p, consortium_card, popup))
            found_btn.pack(pady=5)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk anulowania
        tk.Button(popup, text="Anuluj", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def found_consortium_for_project(self, project, consortium_card, popup):
        """ZaĹ‚oĹĽyÄ‡ konsorcjum dla wybranego projektu"""
        current_player = self.players[self.current_player_idx]

        # UsuĹ„ kartÄ™ konsorcjum z rÄ™ki
        if consortium_card in current_player.hand_cards:
            current_player.hand_cards.remove(consortium_card)

        # Ustaw kierownika i dodaj do czĹ‚onkĂłw
        project.director = current_player
        project.members.append(current_player)

        # ZwiÄ™ksz punkty aktywnoĹ›ci
        current_player.activity_points += 5
        try:
            current_player.round_activity_points += 5
        except Exception:
            pass

        self.log_message(f"{current_player.name} zaĹ‚oĹĽyĹ‚ konsorcjum: {project.name} (uĹĽyto KartÄ™ Konsorcjum)")

        popup.destroy()
        self.update_ui()

    def refresh_market(self):
        """OdĹ›wieĹĽa rynek"""
        available_journal_count = min(4, len(self.game_data.journals))
        self.available_journals = random.sample(self.game_data.journals, available_journal_count)

        available_scientist_count = min(4, len(self.game_data.scientists))
        self.available_scientists = random.sample(self.game_data.scientists, available_scientist_count)

        self.log_message("OdĹ›wieĹĽono rynek czasopism i naukowcĂłw")

    def setup_cleanup_phase(self):
        """Konfiguruje interfejs fazy porzÄ…dkowej"""
        ttk.Label(self.game_tab, text="đź”§ Faza PorzÄ…dkowa", font=('Arial', 14, 'bold')).pack(pady=20)

        cleanup_info = """
        Faza porzÄ…dkowa:
        1. âś… WypĹ‚ata pensji
        2. âś… Sprawdzenie celĂłw grantĂłw
        3. âś… OdĹ›wieĹĽenie rynkĂłw
        4. âś… Odzyskanie kart akcji
        5. âś… Sprawdzenie koĹ„ca gry
        """

        ttk.Label(self.game_tab, text=cleanup_info, justify='left', font=('Arial', 10)).pack(pady=20)

        # PokaĹĽ wyniki rundy
        results_frame = ttk.LabelFrame(self.game_tab, text="đź“Š Wyniki rundy")
        results_frame.pack(fill='x', padx=20, pady=10)

        for player in self.players:
            player_result = f"{player.name}: {player.prestige_points} PZ, {player.credits//1000}K, {len(player.completed_research)} badaĹ„"
            ttk.Label(results_frame, text=player_result).pack(anchor='w', padx=10, pady=2)

    def setup_research_area(self):
        """Konfiguruje obszar badaĹ„"""
        # WyczyĹ›Ä‡ poprzedni UI
        for widget in self.research_frame.winfo_children():
            widget.destroy()

        if self.current_phase != GamePhase.AKCJE:
            return

        current_player = self.players[self.current_player_idx]

        # Tryb selekcji badania do rozpoczÄ™cia
        if self.research_selection_mode:
            ttk.Label(self.research_frame, text="đź“‹ WYBIERZ BADANIE DO ROZPOCZÄCIA",
                     font=('Arial', 11, 'bold'), foreground='red').pack(pady=5)

            selection_frame = ttk.LabelFrame(self.research_frame, text="đźŹ Kliknij kartÄ™ aby podejrzeÄ‡")
            selection_frame.pack(fill='x', padx=5, pady=5)

            # Filtruj tylko karty badaĹ„ z rÄ™ki
            research_cards_in_hand = [card for card in current_player.hand_cards if isinstance(card, ResearchCard)]

            for card in research_cards_in_hand:
                card_frame = tk.Frame(selection_frame, relief='groove', borderwidth=2, padx=5, pady=5)
                card_frame.pack(fill='x', padx=2, pady=2)

                # Nazwa i podstawowe info
                title_label = tk.Label(card_frame, text=f"{card.name} ({card.field})",
                                     font=('Arial', 10, 'bold'))
                title_label.pack(anchor='w')

                # Przycisk podglÄ…du
                preview_btn = tk.Button(card_frame, text="PodglÄ…d karty",
                                      command=lambda c=card: self.preview_research_card(c),
                                      bg='lightblue')
                preview_btn.pack(side='left', padx=(0, 5))

                # Przycisk wyboru (aktywny tylko jeĹ›li karta jest wybrana)
                select_color = 'lightgreen' if card == self.selected_research_for_start else 'lightgray'
                select_btn = tk.Button(card_frame, text="Wybierz tÄ™ kartÄ™",
                                     command=lambda c=card: self.select_research_for_start(c),
                                     bg=select_color)
                select_btn.pack(side='left', padx=(0, 5))

            # Przyciski akcji
            action_frame = tk.Frame(self.research_frame)
            action_frame.pack(fill='x', padx=5, pady=10)

            if self.selected_research_for_start:
                confirm_btn = tk.Button(action_frame, text="ZATWIERDĹą WYBĂ“R",
                                      command=self.confirm_research_start,
                                      bg='green', fg='white', font=('Arial', 10, 'bold'))
                confirm_btn.pack(side='left', padx=(0, 5))

            cancel_btn = tk.Button(action_frame, text="ANULUJ",
                                 command=self.cancel_research_selection,
                                 bg='red', fg='white')
            cancel_btn.pack(side='left')

        else:
            # Normalny tryb - karty na rÄ™ku (tylko podglÄ…d)
            hand_frame = ttk.LabelFrame(self.research_frame, text="đźŹ Karty na rÄ™ku (tylko podglÄ…d)")
            hand_frame.pack(fill='x', padx=5, pady=5)

            for card in current_player.hand_cards:
                # StwĂłrz ramkÄ™ dla kaĹĽdej karty
                card_container = tk.Frame(hand_frame)
                card_container.pack(fill='x', padx=2, pady=1)

                # OkreĹ›l typ karty i odpowiedni tekst
                if hasattr(card, 'field'):  # ResearchCard
                    card_text = f"{card.name} ({card.field})"
                    preview_command = lambda c=card: self.preview_research_card(c)
                    is_intrigue = False
                    is_opportunity = False
                elif hasattr(card, 'card_type'):
                    if card.card_type == "KONSORCJUM":
                        card_text = f"đź¤ť {card.name}"
                        preview_command = lambda c=card: self.preview_consortium_card(c)
                        is_intrigue = False
                        is_opportunity = False
                    elif card.card_type == "INTRYGA":
                        card_text = f"đźŽ­ {card.name}"
                        preview_command = lambda c=card: self.preview_intrigue_card(c)
                        is_intrigue = True
                        is_opportunity = False
                    elif card.card_type == "OKAZJA":
                        card_text = f"âś¨ {card.name}"
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
                    # Dla kart intryg: podglÄ…d + czerwony przycisk uĹĽycia
                    preview_btn = ttk.Button(card_container, text=card_text,
                                           command=preview_command,
                                           width=25)
                    preview_btn.pack(side='left', fill='x', expand=True)

                    use_btn = tk.Button(card_container, text="UĹ»YJ",
                                      command=lambda c=card: self.use_intrigue_card(c),
                                      bg='red', fg='white', font=('Arial', 8, 'bold'),
                                      width=6)
                    use_btn.pack(side='right', padx=(2, 0))
                elif is_opportunity:
                    # Dla kart okazji: podglÄ…d + zielony przycisk uĹĽycia
                    preview_btn = ttk.Button(card_container, text=card_text,
                                           command=preview_command,
                                           width=25)
                    preview_btn.pack(side='left', fill='x', expand=True)

                    use_btn = tk.Button(card_container, text="UĹ»YJ",
                                      command=lambda c=card: self.use_opportunity_card(c),
                                      bg='green', fg='white', font=('Arial', 8, 'bold'),
                                      width=6)
                    use_btn.pack(side='right', padx=(2, 0))
                else:
                    # Dla innych kart: tylko podglÄ…d
                    card_btn = ttk.Button(card_container, text=card_text,
                                         command=preview_command)
                    card_btn.pack(fill='x')

        # Aktywne badania z zwijalnymi panelami
        if current_player.active_research:
            active_frame = ttk.LabelFrame(self.research_frame, text="đź§Ş Aktywne badania")
            active_frame.pack(fill='both', expand=True, padx=5, pady=5)

            # Przechowuj referencje do widgetĂłw badaĹ„
            if not hasattr(self, 'research_widgets'):
                self.research_widgets = []

            # WyczyĹ›Ä‡ poprzednie widgety
            for widget in self.research_widgets:
                widget.destroy()
            self.research_widgets.clear()

            for research in current_player.active_research:
                # StwĂłrz zwijany widget badania
                research_widget = CollapsibleResearchWidget(
                    active_frame,
                    research,
                    self  # przekaĹĽ gĹ‚Ăłwny UI
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

            self.log_message(f"RozpoczÄ™to badanie: {card.name}")
            self.update_ui()

    def collapse_siblings(self, current_widget):
        """Zwija wszystkie inne widgety badaĹ„ (accordion behavior)"""
        if hasattr(self, 'research_widgets'):
            for widget in self.research_widgets:
                if widget != current_widget and widget.is_expanded:
                    widget.collapse()

    def auto_expand_research_widget(self, research):
        """Auto-rozwijanie widgetu badania przy rozpoczÄ™ciu hex placement"""
        if hasattr(self, 'research_widgets'):
            for widget in self.research_widgets:
                if widget.research == research:
                    widget.expand()
                    break

    def auto_collapse_all_research_widgets(self):
        """Auto-zwijanie wszystkich widgetĂłw po zakoĹ„czeniu hex placement"""
        if hasattr(self, 'research_widgets'):
            for widget in self.research_widgets:
                if widget.is_expanded:
                    widget.collapse()

    def take_grant(self, grant: GrantCard):
        """Gracz bierze grant"""
        current_player = self.players[self.current_player_idx]

        if current_player.current_grant is None:
            # Walidacja wymagaĹ„ grantu
            try:
                if not self.meets_grant_requirements(current_player, grant):
                    messagebox.showwarning("Uwaga", "Nie speĹ‚niasz wymagaĹ„ tego grantu")
                    return
            except Exception:
                pass
            current_player.current_grant = grant
            self.available_grants.remove(grant)
            self.log_message(f"WziÄ™to grant: {grant.name}")

            # PrzejdĹş do nastÄ™pnego gracza
            self.next_player()
            self.update_ui()
        else:
            messagebox.showwarning("Uwaga", "Masz juĹĽ grant w tej rundzie!")

    def take_subvention(self):
        """Przydziela subwencjÄ™ rzÄ…dowÄ… graczowi (cel: 6 AP w tej rundzie, nagroda: 10K)."""
        current_player = self.players[self.current_player_idx]
        if current_player.current_grant is not None:
            messagebox.showwarning("Uwaga", "Masz juĹĽ grant w tej rundzie!")
            return
        sub = GrantCard(
            name="Subwencja RzÄ…dowa",
            requirements="Brak wymagaĹ„",
            goal="6 punktĂłw aktywnoĹ›ci w rundzie",
            reward="10K",
            round_bonus="",
            description="Wsparcie paĹ„stwowe, gdy brak dostÄ™pnych grantĂłw"
        )
        current_player.current_grant = sub
        self.log_message(f"Przydzielono subwencjÄ™ rzÄ…dowÄ… graczowi {current_player.name}")
        self.update_ui()

    def enter_research_selection_mode(self):
        """WĹ‚Ä…cza tryb selekcji badania do rozpoczÄ™cia"""
        current_player = self.players[self.current_player_idx]

        if not current_player.hand_cards:
            messagebox.showinfo("Info", "Brak kart badaĹ„ na rÄ™ku!")
            return

        self.research_selection_mode = True
        self.selected_research_for_start = None
        self.log_message(f"{current_player.name} wybiera badanie do rozpoczÄ™cia")
        self.update_ui()

    def select_research_for_start(self, card: ResearchCard):
        """Wybiera kartÄ™ badania do rozpoczÄ™cia"""
        self.selected_research_for_start = card
        self.log_message(f"Wybrano kartÄ™: {card.name}")
        self.update_ui()

    def preview_research_card(self, card: ResearchCard):
        """Pokazuje podglÄ…d karty badania"""
        popup = tk.Toplevel(self.root)
        popup.title(f"PodglÄ…d: {card.name}")
        popup.geometry("600x700")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='lightblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=card.name, font=('Arial', 14, 'bold'), bg='lightblue').pack(pady=5)
        tk.Label(header_frame, text=f"Dziedzina: {card.field}", font=('Arial', 10), bg='lightblue').pack()

        # Informacje o badaniu
        info_frame = tk.LabelFrame(popup, text="Informacje o badaniu")
        info_frame.pack(fill='both', expand=True, padx=5, pady=5)

        tk.Label(info_frame, text=f"DĹ‚ugoĹ›Ä‡ badania: {card.max_hexes} heksĂłw",
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

        # Wizualizacja heksĂłw
        hex_frame = tk.LabelFrame(popup, text="Mapa heksagonalna")
        hex_frame.pack(fill='both', expand=True, padx=5, pady=5)

        if card.hex_research_map:
            # UĹĽyj prawdziwej mapy heksagonalnej
            hex_widget = HexMapWidget(hex_frame, card.hex_research_map)
            hex_widget.pack(fill='both', expand=True, padx=5, pady=5)
        else:
            # Fallback - prosta wizualizacja
            hex_display = tk.Frame(hex_frame)
            hex_display.pack(pady=5)

            for i in range(card.max_hexes):
                color = 'green' if i == 0 else ('red' if i == card.max_hexes - 1 else 'lightgray')
                hex_label = tk.Label(hex_display, text='â¬˘', font=('Arial', 20), fg=color)
                hex_label.pack(side='left', padx=2)

        # Przycisk zamkniÄ™cia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def preview_scientist(self, scientist):
        """Pokazuje podglÄ…d karty naukowca"""
        popup = tk.Toplevel(self.root)
        popup.title(f"PodglÄ…d: {scientist.name}")
        popup.geometry("350x400")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='lightgreen', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=scientist.name, font=('Arial', 14, 'bold'), bg='lightgreen').pack(pady=5)
        tk.Label(header_frame, text=f"Typ: {scientist.type.value}", font=('Arial', 10), bg='lightgreen').pack()

        # Informacje o naukowcu
        info_frame = tk.LabelFrame(popup, text="Informacje o naukowcu")
        info_frame.pack(fill='both', expand=True, padx=5, pady=5)

        tk.Label(info_frame, text=f"đź”¬ Dziedzina: {scientist.field}",
                font=('Arial', 10, 'bold')).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"đź’° Pensja: {scientist.salary}K/rundÄ™",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"â¬˘ Bonus heksĂłw: {scientist.hex_bonus} heks/akcja",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        # Specjalny bonus with word wrapping
        bonus_frame = tk.Frame(info_frame)
        bonus_frame.pack(fill='x', padx=5, pady=2)

        tk.Label(bonus_frame, text="â­ Specjalny bonus:",
                font=('Arial', 10, 'bold')).pack(anchor='w')

        bonus_text = tk.Text(bonus_frame, height=3, wrap=tk.WORD, font=('Arial', 10),
                           bg=info_frame.cget('bg'), relief='flat', cursor='arrow')
        bonus_text.insert('1.0', scientist.special_bonus)
        bonus_text.config(state='disabled')
        bonus_text.pack(fill='x', pady=(2, 0))

        # Opis
        desc_frame = tk.LabelFrame(popup, text="Opis")
        desc_frame.pack(fill='x', padx=5, pady=5)

        desc_text = tk.Text(desc_frame, height=4, wrap='word')
        desc_text.pack(fill='x', padx=5, pady=5)
        desc_text.insert(1.0, scientist.description)
        desc_text.config(state='disabled')

        # Przycisk zamkniÄ™cia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def preview_journal(self, journal):
        """Pokazuje podglÄ…d karty czasopisma"""
        popup = tk.Toplevel(self.root)
        popup.title(f"PodglÄ…d: {journal.name}")
        popup.geometry("350x400")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='lightyellow', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=journal.name, font=('Arial', 14, 'bold'), bg='lightyellow').pack(pady=5)
        tk.Label(header_frame, text=f"Impact Factor: {journal.impact_factor}", font=('Arial', 10), bg='lightyellow').pack()

        # Informacje o czasopiĹ›mie
        info_frame = tk.LabelFrame(popup, text="Informacje o czasopiĹ›mie")
        info_frame.pack(fill='both', expand=True, padx=5, pady=5)

        tk.Label(info_frame, text=f"đź“Š Impact Factor: {journal.impact_factor}",
                font=('Arial', 10, 'bold')).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"đź’Ž Koszt publikacji: {journal.pb_cost} PB",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"đźŹ† Nagroda PZ: {journal.pz_reward} PZ",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        tk.Label(info_frame, text=f"đź“‹ Wymagania: {journal.requirements}",
                font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)

        # Specjalny bonus with word wrapping
        journal_bonus_frame = tk.Frame(info_frame)
        journal_bonus_frame.pack(fill='x', padx=5, pady=2)

        tk.Label(journal_bonus_frame, text="â­ Specjalny bonus:",
                font=('Arial', 10, 'bold')).pack(anchor='w')

        journal_bonus_text = tk.Text(journal_bonus_frame, height=3, wrap=tk.WORD, font=('Arial', 10),
                           bg=info_frame.cget('bg'), relief='flat', cursor='arrow')
        journal_bonus_text.insert('1.0', journal.special_bonus)
        journal_bonus_text.config(state='disabled')
        journal_bonus_text.pack(fill='x', pady=(2, 0))

        # Opis
        desc_frame = tk.LabelFrame(popup, text="Opis")
        desc_frame.pack(fill='x', padx=5, pady=5)

        desc_text = tk.Text(desc_frame, height=4, wrap='word')
        desc_text.pack(fill='x', padx=5, pady=5)
        desc_text.insert(1.0, journal.description)
        desc_text.config(state='disabled')

        # Przycisk zamkniÄ™cia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def hire_scientist_direct(self, scientist):
        """Zatrudnia konkretnego naukowca bezpoĹ›rednio"""
        if not self.players:
            messagebox.showwarning("BĹ‚Ä…d", "Brak graczy!")
            return

        current_player = self.players[self.current_player_idx]

        # SprawdĹş koszty
        eff_salary = scientist.salary if scientist.salary >= 100 else scientist.salary * 1000
        hire_cost = eff_salary * 2
        if current_player.credits < hire_cost:
            messagebox.showwarning("BĹ‚Ä…d", f"Brak Ĺ›rodkĂłw! Koszt: {hire_cost}K")
            return

        # Zatrudnij
        current_player.credits -= hire_cost
        current_player.scientists.append(scientist)

        # UsuĹ„ z rynku
        self.available_scientists.remove(scientist)

        self.log_message(f"Zatrudniono: {scientist.name} za {hire_cost//1000}K")
        self.update_markets()
        self.update_ui()

    def publish_in_journal_direct(self, journal):
        """Publikuje w konkretnym czasopiĹ›mie bezpoĹ›rednio"""
        if not self.players:
            messagebox.showwarning("BĹ‚Ä…d", "Brak graczy!")
            return

        current_player = self.players[self.current_player_idx]

        # SprawdĹş koszty
        if current_player.research_points < journal.pb_cost:
            messagebox.showwarning("BĹ‚Ä…d", f"Brak punktĂłw badaĹ„! Koszt: {journal.pb_cost} PB")
            return

        # SprawdĹş wymagania reputacji (parsuj z requirements)
        rep_required = 0
        if "Reputacja" in journal.requirements:
            try:
                rep_text = journal.requirements.split("Reputacja")[1].strip()
                rep_required = int(rep_text.split("+")[0].strip())
            except:
                rep_required = 0

        if current_player.reputation < rep_required:
            messagebox.showwarning("BĹ‚Ä…d", f"NiewystarczajÄ…ca reputacja! Wymagana: {rep_required}")
            return

        # Dodatkowe progi reputacji vs nagroda PZ (globalne)
        try:
            rep = current_player.reputation
            if rep <= 1 and journal.pz_reward >= 4:
                messagebox.showwarning("Uwaga", "Reputacja zbyt niska na publikacjÄ™ o tej wartoĹ›ci PZ")
                return
            if rep == 2 and journal.pz_reward >= 6:
                messagebox.showwarning("Uwaga", "Reputacja zbyt niska na publikacjÄ™ o tej wartoĹ›ci PZ")
                return
        except Exception:
            pass

        # Publikuj
        current_player.research_points -= journal.pb_cost
        pz_gain = journal.pz_reward
        try:
            # Cambridge: wszystkie publikacje +1 PZ
            if current_player.institute and 'cambridge' in current_player.institute.name.lower():
                pz_gain += 1
        except Exception:
            pass
        current_player.prestige_points += pz_gain
        current_player.publications += 1
        current_player.activity_points += 3  # Punkt aktywnoĹ›ci za publikacjÄ™
        try:
            current_player.round_activity_points += 3
        except Exception:
            pass

        # Harvard: publikacja IF 6+ â†’ +1 reputacja
        try:
            if current_player.institute and 'harvard' in current_player.institute.name.lower() and journal.impact_factor >= 6:
                current_player.reputation = min(5, current_player.reputation + 1)
        except Exception:
            pass
        try:
            current_player.round_activity_points += 3
        except Exception:
            pass
        try:
            current_player.round_activity_points += 3
        except Exception:
            pass

        # Dodaj do historii publikacji
        import copy
        current_player.publication_history.append(copy.deepcopy(journal))

        self.log_message(f"Opublikowano w {journal.name} za {journal.pb_cost} PB, +{pz_gain} PZ")
        self.update_ui()

    def hire_scientist_from_market(self, scientist):
        """Zatrudnia naukowca z rynku podczas akcji ZATRUDNIJ PERSONEL"""
        if not (hasattr(self, 'current_action_card') and self.current_action_card and
                self.current_action_card.action_type == ActionType.ZATRUDNIJ):
            messagebox.showwarning("BĹ‚Ä…d", "Musisz najpierw zagraÄ‡ kartÄ™ ZATRUDNIJ PERSONEL!")
            return

        current_player = self.players[self.current_player_idx]

        # SprawdĹş koszty w punktach akcji
        pa_cost = 2 if scientist.type == ScientistType.DOKTOR else 3 if scientist.type == ScientistType.PROFESOR else 1
        if self.remaining_action_points < pa_cost:
            messagebox.showwarning("BĹ‚Ä…d", f"Brak punktĂłw akcji! Wymagane: {pa_cost} PA")
            return

        # SprawdĹş koszty finansowe (koszt zatrudnienia = 2x pensja)
        eff_salary = scientist.salary if scientist.salary >= 100 else scientist.salary * 1000
        hire_cost = eff_salary * 2
        if current_player.credits < hire_cost:
            messagebox.showwarning("BĹ‚Ä…d", f"Brak Ĺ›rodkĂłw! Koszt: {hire_cost}K")
            return

        # Zatrudnij
        current_player.credits -= hire_cost
        current_player.scientists.append(scientist)
        self.remaining_action_points -= pa_cost

        # UsuĹ„ z rynku
        self.available_scientists.remove(scientist)

        # Dodaj punkty aktywnoĹ›ci
        current_player.activity_points += 2
        try:
            current_player.round_activity_points += 2
        except Exception:
            pass
        try:
            current_player.round_activity_points += 2
        except Exception:
            pass
        try:
            current_player.round_activity_points += 2
        except Exception:
            pass

        self.log_message(f"Zatrudniono {scientist.name} za {hire_cost//1000}K (-{pa_cost} PA)")
        self.update_markets()
        self.update_ui()
        self.update_action_menu()

    def publish_in_journal_from_market(self, journal):
        """Publikuje w czasopiĹ›mie z rynku podczas akcji PUBLIKUJ"""
        if not (hasattr(self, 'current_action_card') and self.current_action_card and
                self.current_action_card.action_type == ActionType.PUBLIKUJ):
            messagebox.showwarning("BĹ‚Ä…d", "Musisz najpierw zagraÄ‡ kartÄ™ PUBLIKUJ!")
            return

        current_player = self.players[self.current_player_idx]

        # SprawdĹş koszty
        if current_player.research_points < journal.pb_cost:
            messagebox.showwarning("BĹ‚Ä…d", f"Brak punktĂłw badaĹ„! Koszt: {journal.pb_cost} PB")
            return

        # SprawdĹş wymagania reputacji
        rep_required = 0
        if "Reputacja" in journal.requirements:
            try:
                rep_text = journal.requirements.split("Reputacja")[1].strip()
                rep_required = int(rep_text.split("+")[0].strip())
            except:
                rep_required = 0

        if current_player.reputation < rep_required:
            messagebox.showwarning("BĹ‚Ä…d", f"NiewystarczajÄ…ca reputacja! Wymagana: {rep_required}")
            return

        # Dodatkowe progi reputacji vs PZ
        try:
            rep = current_player.reputation
            if rep <= 1 and journal.pz_reward >= 4:
                messagebox.showwarning("Uwaga", "Reputacja zbyt niska na publikacjÄ™ o tej wartoĹ›ci PZ")
                return
            if rep == 2 and journal.pz_reward >= 6:
                messagebox.showwarning("Uwaga", "Reputacja zbyt niska na publikacjÄ™ o tej wartoĹ›ci PZ")
                return
        except Exception:
            pass

        # Publikuj (akcja podstawowa - nie kosztuje PA)
        current_player.research_points -= journal.pb_cost
        pz_gain = journal.pz_reward
        try:
            if current_player.institute and 'cambridge' in current_player.institute.name.lower():
                pz_gain += 1
        except Exception:
            pass
        current_player.prestige_points += pz_gain
        current_player.publications += 1
        current_player.activity_points += 3
        try:
            current_player.round_activity_points += 3
        except Exception:
            pass

        # Harvard bonus: IF 6+ â†’ +1 reputacja
        try:
            if current_player.institute and 'harvard' in current_player.institute.name.lower() and journal.impact_factor >= 6:
                current_player.reputation = min(5, current_player.reputation + 1)
        except Exception:
            pass

        # Dodaj do historii publikacji
        import copy
        current_player.publication_history.append(copy.deepcopy(journal))

        self.log_message(f"Opublikowano w {journal.name} za {journal.pb_cost} PB â†’ +{pz_gain} PZ")
        self.update_ui()

    def show_journal_selection_for_publish(self):
        """Pokazuje okno wyboru czasopisma dla akcji podstawowej PUBLIKUJ"""
        if not self.available_journals:
            messagebox.showinfo("Info", "Brak dostÄ™pnych czasopism na rynku")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Wybierz czasopismo do publikacji")
        popup.geometry("500x600")

        # NagĹ‚Ăłwek
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

            # SzczegĂłĹ‚y
            details_frame = tk.Frame(journal_frame, bg='lightyellow')
            details_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(details_frame, text=f"đź’° {journal.pb_cost} PB", font=('Arial', 10), bg='lightyellow').pack(side='left')
            tk.Label(details_frame, text=f"â­ +{journal.pz_reward} PZ", font=('Arial', 10), bg='lightyellow').pack(side='left', padx=(10,0))

            # Wymagania
            if journal.requirements != "Brak wymagaĹ„":
                req_frame = tk.Frame(journal_frame, bg='lightyellow')
                req_frame.pack(fill='x', padx=5, pady=2)
                tk.Label(req_frame, text=f"đź“‹ {journal.requirements}", font=('Arial', 9), bg='lightyellow').pack()

            # Bonus specjalny
            if journal.special_bonus != "Brak":
                bonus_frame = tk.Frame(journal_frame, bg='lightyellow')
                bonus_frame.pack(fill='x', padx=5, pady=2)
                tk.Label(bonus_frame, text=f"đźŽ {journal.special_bonus}", font=('Arial', 9), bg='lightyellow').pack()

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
        # Filtruj dostÄ™pnych naukowcĂłw wedĹ‚ug typu
        available_scientists = [s for s in self.available_scientists if s.type == scientist_type]

        if not available_scientists:
            messagebox.showinfo("Info", f"Brak dostÄ™pnych naukowcĂłw typu {scientist_type.value} na rynku")
            return

        popup = tk.Toplevel(self.root)
        popup.title(f"Wybierz {scientist_type.value}")
        popup.geometry("400x500")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='lightsteelblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=f"Wybierz {scientist_type.value} do zatrudnienia",
                font=('Arial', 14, 'bold'), bg='lightsteelblue').pack(pady=5)
        tk.Label(header_frame, text=f"Koszt: {pa_cost} PA",
                font=('Arial', 10), bg='lightsteelblue').pack()

        # Scrollable frame dla naukowcĂłw
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

            # SzczegĂłĹ‚y
            details_frame = tk.Frame(scientist_frame, bg='lightblue')
            details_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(details_frame, text=f"đź’° {scientist.salary * 2}K (koszt)", font=('Arial', 10), bg='lightblue').pack(side='left')
            tk.Label(details_frame, text=f"â¬˘ {scientist.hex_bonus} heks", font=('Arial', 10), bg='lightblue').pack(side='left', padx=(10,0))

            # Bonus
            if scientist.special_bonus != "Brak":
                bonus_frame = tk.Frame(scientist_frame, bg='lightblue')
                bonus_frame.pack(fill='x', padx=5, pady=2)
                tk.Label(bonus_frame, text=f"â­ {scientist.special_bonus}", font=('Arial', 9), bg='lightblue').pack()

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

        # SprawdĹş koszty finansowe
        eff_salary = scientist.salary if scientist.salary >= 100 else scientist.salary * 1000
        hire_cost = eff_salary * 2
        if current_player.credits < hire_cost:
            messagebox.showwarning("BĹ‚Ä…d", f"Brak Ĺ›rodkĂłw! Koszt: {hire_cost}K")
            return

        # Zatrudnij (PA zostaĹ‚o juĹĽ odejmowane w execute_additional_action)
        current_player.credits -= hire_cost
        current_player.scientists.append(scientist)

        # UsuĹ„ z rynku
        self.available_scientists.remove(scientist)

        # Dodaj punkty aktywnoĹ›ci
        current_player.activity_points += 2

        self.log_message(f"Zatrudniono {scientist.name} za {hire_cost//1000}K")
        self.update_markets()
        self.update_ui()
        self.update_action_menu()

    def show_employed_scientists(self, player):
        """Pokazuje okno z zatrudnionymi naukowcami gracza"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Zatrudnieni naukowcy - {player.name}")
        popup.geometry("500x600")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='lightcyan', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=f"ZespĂłĹ‚ {player.name}", font=('Arial', 14, 'bold'), bg='lightcyan').pack(pady=5)
        tk.Label(header_frame, text=f"Zatrudnionych: {len(player.scientists)}", font=('Arial', 10), bg='lightcyan').pack()

        # Scrollable frame dla naukowcĂłw
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

                tk.Label(info_frame, text=f"đź”¬ {scientist.field}", font=('Arial', 10), bg='lightblue').pack(side='left')
                tk.Label(info_frame, text=f"đź’° {scientist.salary}K/rundÄ™", font=('Arial', 10), bg='lightblue').pack(side='left', padx=(10,0))
                tk.Label(info_frame, text=f"â¬˘ {scientist.hex_bonus} heks", font=('Arial', 10), bg='lightblue').pack(side='left', padx=(10,0))

                # Trzecia linia - bonus i status
                bonus_frame = tk.Frame(scientist_frame, bg='lightblue')
                bonus_frame.pack(fill='x', padx=5, pady=2)

                tk.Label(bonus_frame, text=f"â­ {scientist.special_bonus}", font=('Arial', 9), bg='lightblue').pack(side='left')

                # Status opĹ‚acenia
                status = "âś… OpĹ‚acony" if scientist.is_paid else "âťŚ NieopĹ‚acony"
                status_color = 'green' if scientist.is_paid else 'red'
                tk.Label(bonus_frame, text=status, font=('Arial', 9, 'bold'), fg=status_color, bg='lightblue').pack(side='right')

                # Przycisk podglÄ…du szczegĂłĹ‚owego
                preview_btn = ttk.Button(scientist_frame, text="đź‘ď¸Ź SzczegĂłĹ‚y",
                                       command=lambda s=scientist: self.preview_scientist(s))
                preview_btn.pack(pady=5)

        else:
            tk.Label(scrollable_frame, text="Brak zatrudnionych naukowcĂłw",
                    font=('Arial', 12), fg='gray').pack(pady=50)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Przycisk zamkniÄ™cia
        tk.Button(popup, text="Zamknij", command=popup.destroy,
                 font=('Arial', 10), bg='lightgray').pack(pady=10)

    def confirm_research_start(self):
        """Zatwierdza rozpoczÄ™cie wybranego badania"""
        if not self.selected_research_for_start:
            messagebox.showwarning("Uwaga", "Nie wybrano karty badania!")
            return

        current_player = self.players[self.current_player_idx]
        card = self.selected_research_for_start

        # Rozpocznij badanie
        current_player.hand_cards.remove(card)
        current_player.active_research.append(card)
        card.is_active = True

        self.log_message(f"RozpoczÄ™to badanie: {card.name}")

        # WyjdĹş z trybu selekcji
        self.research_selection_mode = False
        self.selected_research_for_start = None

        self.update_ui()

    def cancel_research_selection(self):
        """Anuluje selekcjÄ™ badania"""
        self.research_selection_mode = False
        self.selected_research_for_start = None

        # ZwrĂłÄ‡ punkt akcji
        self.remaining_action_points += 1

        self.log_message("Anulowano wybĂłr badania")
        self.update_ui()

    def select_scenario(self):
        """Pozwala graczowi wybraÄ‡ scenariusz gry"""
        scenario_popup = tk.Toplevel(self.root)
        scenario_popup.title("WybĂłr Scenariusza")
        scenario_popup.geometry("800x600")
        scenario_popup.grab_set()  # Modal dialog

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(scenario_popup, bg='darkblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text="đźŽ­ WYBĂ“R SCENARIUSZA GRY",
                font=('Arial', 18, 'bold'), bg='darkblue', fg='white').pack(pady=10)

        tk.Label(header_frame, text="Wybierz scenariusz, ktĂłry okreĹ›li warunki tej rozgrywki",
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

            # NagĹ‚Ăłwek scenariusza
            header = tk.Frame(scenario_frame, bg='steelblue')
            header.pack(fill='x', padx=5, pady=5)

            tk.Label(header, text=scenario.name, font=('Arial', 14, 'bold'),
                    bg='steelblue', fg='white').pack(pady=5)

            # Element fabularny
            story_frame = tk.Frame(scenario_frame, bg='lightblue')
            story_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(story_frame, text="đź“– FABUĹA:", font=('Arial', 10, 'bold'),
                    bg='lightblue').pack(anchor='w')
            tk.Label(story_frame, text=scenario.story_element, font=('Arial', 10),
                    bg='lightblue', wraplength=700, justify='left').pack(anchor='w', padx=20)

            # Modyfikatory globalne
            mods_frame = tk.Frame(scenario_frame, bg='lightblue')
            mods_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(mods_frame, text="âš™ď¸Ź MODYFIKATORY:", font=('Arial', 10, 'bold'),
                    bg='lightblue').pack(anchor='w')
            tk.Label(mods_frame, text=scenario.global_modifiers, font=('Arial', 10),
                    bg='lightblue', wraplength=700, justify='left').pack(anchor='w', padx=20)

            # Informacje o grze
            info_frame = tk.Frame(scenario_frame, bg='lightblue')
            info_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(info_frame, text="đźŽŻ WARUNKI GRY:", font=('Arial', 10, 'bold'),
                    bg='lightblue').pack(anchor='w')
            tk.Label(info_frame, text=f"Maksymalnie rund: {scenario.max_rounds}",
                    font=('Arial', 10), bg='lightblue').pack(anchor='w', padx=20)
            tk.Label(info_frame, text=f"ZwyciÄ™stwo: {scenario.victory_conditions}",
                    font=('Arial', 10), bg='lightblue').pack(anchor='w', padx=20)
            tk.Label(info_frame, text=f"Kryzysy: {scenario.crisis_count} kart w rundach {scenario.crisis_rounds}",
                    font=('Arial', 10), bg='lightblue').pack(anchor='w', padx=20)

            # Przycisk wyboru
            select_btn = ttk.Button(scenario_frame, text="WYBIERZ TEN SCENARIUSZ",
                                  command=lambda s=scenario: [selected_scenario.__setitem__(0, s), scenario_popup.destroy()])
            select_btn.pack(pady=10)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Czekaj na wybĂłr scenariusza
        scenario_popup.wait_window()

        if selected_scenario[0]:
            self.current_scenario = selected_scenario[0]
            self.prepare_crisis_deck()
            self.log_message(f"Wybrano scenariusz: {self.current_scenario.name}")
        else:
            # JeĹ›li nie wybrano, uĹĽyj pierwszego scenariusza
            self.current_scenario = self.game_data.scenarios[0]
            self.prepare_crisis_deck()
            self.log_message(f"UĹĽyto domyĹ›lnego scenariusza: {self.current_scenario.name}")

        # Aktualizuj wyĹ›wietlanie scenariusza
        self.update_scenario_display()
        self.update_round_display()
        self.update_crisis_display()

    def prepare_crisis_deck(self):
        """Przygotowuje taliÄ™ kryzysĂłw na podstawie wybranego scenariusza"""
        if not self.current_scenario:
            return

        # Wybierz losowe kryzysy z dostÄ™pnej puli
        available_crises = self.game_data.crisis_cards.copy()
        random.shuffle(available_crises)

        # Dobierz odpowiedniÄ… liczbÄ™ kryzysĂłw
        self.crisis_deck = available_crises[:self.current_scenario.crisis_count]

        self.log_message(f"Przygotowano {len(self.crisis_deck)} kryzysĂłw na rundy {self.current_scenario.crisis_rounds}")

    def check_for_crisis(self):
        """Sprawdza czy w aktualnej rundzie powinien zostaÄ‡ odkryty kryzys"""
        if not self.current_scenario or not self.crisis_deck:
            return

        # SprawdĹş czy aktualna runda jest w liĹ›cie rund kryzysowych
        if self.game_data.current_round in self.current_scenario.crisis_rounds:
            # ZnajdĹş indeks rundy w liĹ›cie
            crisis_index = self.current_scenario.crisis_rounds.index(self.game_data.current_round)

            # SprawdĹş czy mamy jeszcze kryzysy do odkrycia
            if crisis_index < len(self.crisis_deck):
                crisis = self.crisis_deck[crisis_index]
                self.reveal_crisis(crisis)

    def reveal_crisis(self, crisis: CrisisCard):
        """Odkrywa i aktywuje kryzys"""
        self.game_data.revealed_crises.append(crisis)

        # PokaĹĽ informacjÄ™ o kryzysie
        messagebox.showinfo(
            f"KRYZYS - Runda {self.game_data.current_round}",
            f"đźš¨ {crisis.name}\n\n{crisis.description}\n\nEfekt: {crisis.effect}\n\nEfekt jest aktywny natychmiast!"
        )

        # Zastosuj efekt kryzysu
        self.apply_crisis_effect(crisis)

        # Aktualizuj interfejs
        self.update_crisis_display()
        self.log_message(f"KRYZYS AKTYWOWANY: {crisis.name}")

    def apply_crisis_effect(self, crisis: CrisisCard):
        """Stosuje efekt kryzysu do wszystkich graczy"""
        # Tutaj moĹĽna dodaÄ‡ konkretnÄ… logikÄ™ dla rĂłĹĽnych typĂłw kryzysĂłw
        # Na razie tylko logujemy efekt
        self.log_message(f"Efekt kryzysu: {crisis.effect}")

        # PrzykĹ‚ady moĹĽliwych efektĂłw (do rozwiniÄ™cia w przyszĹ‚oĹ›ci):
        if "pensje" in crisis.effect.lower():
            self.log_message("đź’° Wszystkie pensje kosztujÄ… wiÄ™cej w tej rundzie")
        elif "badania" in crisis.effect.lower():
            self.log_message("đź”¬ Badania sÄ… trudniejsze w tej rundzie")
        elif "reputacja" in crisis.effect.lower():
            self.log_message("â­ WpĹ‚yw na reputacjÄ™ wszystkich graczy")

    def advance_round(self):
        """Rozpoczyna nowÄ… rundÄ™ i sprawdza kryzysy"""
        self.game_data.current_round += 1
        self.log_message(f"\nđź•’ RUNDA {self.game_data.current_round}")

        # SprawdĹş czy koĹ„czymy grÄ™
        if self.current_scenario and self.game_data.current_round > self.current_scenario.max_rounds:
            self.end_game()
            return

        # SprawdĹş kryzysy na poczÄ…tek rundy
        self.check_for_crisis()

        # Aktualizuj interfejs
        self.update_round_display()

    def update_round_display(self):
        """Aktualizuje wyĹ›wietlanie informacji o rundzie"""
        round_info = f"Runda: {self.game_data.current_round}"
        if self.current_scenario:
            round_info += f"/{self.current_scenario.max_rounds}"

        self.round_label.config(text=round_info)

    def update_crisis_display(self):
        """Aktualizuje wyĹ›wietlanie aktywnych kryzysĂłw"""
        if not self.game_data.revealed_crises:
            self.active_crisis_text.config(text="Brak", foreground='green')
        else:
            crisis_names = [crisis.name for crisis in self.game_data.revealed_crises]
            crisis_text = ", ".join(crisis_names)
            self.active_crisis_text.config(text=crisis_text, foreground='red')

    def update_scenario_display(self):
        """Aktualizuje wyĹ›wietlanie informacji o scenariuszu"""
        if self.current_scenario:
            scenario_text = f"Scenariusz: {self.current_scenario.name}"
            self.scenario_label.config(text=scenario_text)
        else:
            self.scenario_label.config(text="Scenariusz: Brak")

    def end_game(self):
        """KoĹ„czy grÄ™ i podsumowuje wyniki"""
        messagebox.showinfo(
            "Koniec gry",
            f"Gra zakoĹ„czona po {self.current_scenario.max_rounds} rundach!\n\n"
            f"Scenariusz: {self.current_scenario.name}\n"
            f"Warunki zwyciÄ™stwa: {self.current_scenario.victory_conditions}"
        )

    def hire_scientist(self, scientist_type: ScientistType):
        """Zatrudnia naukowca bezpoĹ›rednio (np. doktoranta)"""
        current_player = self.players[self.current_player_idx]

        # UtwĂłrz nowego naukowca odpowiedniego typu
        if scientist_type == ScientistType.DOKTORANT:
            new_scientist = Scientist("Doktorant", ScientistType.DOKTORANT, "Uniwersalny", 0, 1, "Brak", "MĹ‚ody naukowiec")
            hire_cost = 0  # Doktorant nie kosztuje pieniÄ™dzy
        elif scientist_type == ScientistType.DOKTOR:
            new_scientist = Scientist("Dr Nowy", ScientistType.DOKTOR, "Uniwersalny", 2000, 2, "Brak", "Nowo zatrudniony doktor")
            hire_cost = 4000  # 2x pensja
        elif scientist_type == ScientistType.PROFESOR:
            new_scientist = Scientist("Prof. Nowy", ScientistType.PROFESOR, "Uniwersalny", 3000, 3, "Brak", "Nowo zatrudniony profesor")
            hire_cost = 6000  # 2x pensja
        else:
            messagebox.showwarning("BĹ‚Ä…d", f"Nieznany typ naukowca: {scientist_type}")
            return

        # SprawdĹş koszty finansowe
        if current_player.credits < hire_cost:
            messagebox.showwarning("BĹ‚Ä…d", f"Brak Ĺ›rodkĂłw! Koszt: {hire_cost//1000}K")
            return

        # Zatrudnij
        current_player.credits -= hire_cost
        current_player.scientists.append(new_scientist)

        # Dodaj punkty aktywnoĹ›ci
        current_player.activity_points += 2

        if hire_cost > 0:
            self.log_message(f"Zatrudniono {new_scientist.name} za {hire_cost//1000}K")
        else:
            self.log_message(f"Zatrudniono {new_scientist.name} (bez kosztĂłw)")

        self.update_ui()
        self.update_action_menu()

    def preview_research_card(self, card):
        """Pokazuje podglÄ…d karty badania"""
        popup = tk.Toplevel(self.root)
        popup.title(f"PodglÄ…d: {card.name}")
        popup.geometry("600x700")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='lightblue', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=card.name, font=('Arial', 16, 'bold'), bg='lightblue').pack(pady=5)
        tk.Label(header_frame, text=f"Dziedzina: {card.field}", font=('Arial', 12), bg='lightblue').pack()

        # SzczegĂłĹ‚y
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

        # Mapa heksagonalna (jeĹ›li istnieje)
        if card.hex_research_map:
            map_frame = tk.LabelFrame(details_frame, text="Mapa badania")
            map_frame.pack(fill='both', expand=True, pady=10)
            hex_widget = HexMapWidget(map_frame, card.hex_research_map)
            hex_widget.pack(fill='both', expand=True)

        # Przycisk zamkniÄ™cia
        tk.Button(popup, text="Zamknij", command=popup.destroy, font=('Arial', 10)).pack(pady=10)

    def preview_consortium_card(self, card):
        """Pokazuje podglÄ…d karty konsorcjum"""
        popup = tk.Toplevel(self.root)
        popup.title(f"PodglÄ…d: {card.name}")
        popup.geometry("400x300")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='gold', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text="đź¤ť KARTA KONSORCJUM", font=('Arial', 16, 'bold'), bg='gold').pack(pady=5)

        # SzczegĂłĹ‚y
        details_frame = tk.Frame(popup)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)

        tk.Label(details_frame, text="Ta karta umoĹĽliwia zostanie kierownikiem konsorcjum.",
                font=('Arial', 12), wraplength=350, justify='center').pack(pady=20)

        tk.Label(details_frame, text="â€˘ Pozwala zostaÄ‡ kierownikiem konsorcjum", font=('Arial', 10)).pack(anchor='w', pady=2)
        tk.Label(details_frame, text="â€˘ UmoĹĽliwia zaĹ‚oĹĽenie nowego konsorcjum", font=('Arial', 10)).pack(anchor='w', pady=2)
        tk.Label(details_frame, text="â€˘ Do doĹ‚Ä…czenia do istniejÄ…cego konsorcjum nie jest potrzebna", font=('Arial', 10)).pack(anchor='w', pady=2)

        # Przycisk zamkniÄ™cia
        tk.Button(popup, text="Zamknij", command=popup.destroy, font=('Arial', 10)).pack(pady=10)

    def preview_intrigue_card(self, card):
        """Pokazuje podglÄ…d karty intryg"""
        popup = tk.Toplevel(self.root)
        popup.title(f"PodglÄ…d: {card.name}")
        popup.geometry("450x350")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='darkred', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=f"đźŽ­ {card.name}", font=('Arial', 16, 'bold'), bg='darkred', fg='white').pack(pady=5)

        # SzczegĂłĹ‚y
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

        # Przycisk zamkniÄ™cia
        tk.Button(popup, text="Zamknij", command=popup.destroy, font=('Arial', 10)).pack(pady=10)

    def preview_opportunity_card(self, card):
        """Pokazuje podglÄ…d karty okazji"""
        popup = tk.Toplevel(self.root)
        popup.title(f"PodglÄ…d: {card.name}")
        popup.geometry("450x350")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='green', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=f"âś¨ {card.name}", font=('Arial', 16, 'bold'), bg='green', fg='white').pack(pady=5)

        # SzczegĂłĹ‚y
        details_frame = tk.Frame(popup)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Typ bonusu
        bonus_types = {
            "credits": "Kredyty",
            "research_points": "Punkty badaĹ„",
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

        # Przycisk zamkniÄ™cia
        tk.Button(popup, text="Zamknij", command=popup.destroy, font=('Arial', 10)).pack(pady=10)

    def preview_generic_card(self, card):
        """Pokazuje podglÄ…d karty ogĂłlnej"""
        popup = tk.Toplevel(self.root)
        popup.title(f"PodglÄ…d: {card.name}")
        popup.geometry("400x300")

        # NagĹ‚Ăłwek
        header_frame = tk.Frame(popup, bg='lightgray', relief='raised', borderwidth=2)
        header_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(header_frame, text=card.name, font=('Arial', 16, 'bold'), bg='lightgray').pack(pady=5)

        # SzczegĂłĹ‚y
        details_frame = tk.Frame(popup)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # WyĹ›wietl wszystkie dostÄ™pne atrybuty
        for attr_name in dir(card):
            if not attr_name.startswith('_') and hasattr(card, attr_name):
                attr_value = getattr(card, attr_name)
                if not callable(attr_value):
                    tk.Label(details_frame, text=f"{attr_name}: {attr_value}",
                            font=('Arial', 10)).pack(anchor='w', pady=2)

        # Przycisk zamkniÄ™cia
        tk.Button(popup, text="Zamknij", command=popup.destroy, font=('Arial', 10)).pack(pady=10)

    def use_intrigue_card(self, card: IntrigueCard):
        """UĹĽywa kartÄ™ intrygi - wybiera cel i wykonuje efekt"""
        current_player = self.players[self.current_player_idx]

        # SprawdĹş czy karta wymaga wyboru celu
        if card.target == "opponent" or any(effect.target_type == "opponent" for effect in card.effects):
            self.select_target_for_intrigue(card)
        elif card.target == "all" or any(effect.target_type in ["all_players", "all_opponents"] for effect in card.effects):
            self.confirm_intrigue_usage(card, None)  # Brak konkretnego celu
        else:  # self
            self.confirm_intrigue_usage(card, current_player)

    def select_target_for_intrigue(self, card: IntrigueCard):
        """Pozwala wybraÄ‡ gracza jako cel karty intrygi"""
        current_player = self.players[self.current_player_idx]

        # Popup do wyboru celu
        target_popup = tk.Toplevel(self.root)
        target_popup.title("Wybierz cel")
        target_popup.geometry("400x300")
        target_popup.grab_set()

        # NagĹ‚Ăłwek
        tk.Label(target_popup, text=f"Karta: {card.name}",
                font=('Arial', 14, 'bold')).pack(pady=10)
        tk.Label(target_popup, text="Wybierz gracza docelowego:",
                font=('Arial', 12)).pack(pady=5)

        # Lista dostÄ™pnych celĂłw (przeciwnicy)
        for player in self.players:
            if player != current_player:  # Nie moĹĽna wybraÄ‡ siebie jako celu
                player_frame = tk.Frame(target_popup, relief='groove', borderwidth=2)
                player_frame.pack(fill='x', padx=20, pady=5)

                # Informacje o graczu
                info_text = f"{player.name} ({player.color})"
                if player.institute:
                    info_text += f" - {player.institute.name}"
                info_text += f"\nđź’°{player.credits//1000}K â­{player.prestige_points}PZ đź”¬{player.research_points}PB"

                tk.Label(player_frame, text=info_text, font=('Arial', 10)).pack(pady=5)

                # Przycisk wyboru
                select_btn = tk.Button(player_frame, text="WYBIERZ TEGO GRACZA",
                                     command=lambda p=player: [target_popup.destroy(), self.confirm_intrigue_usage(card, p)],
                                     bg='red', fg='white')
                select_btn.pack(pady=5)

        # Przycisk anulowania
        tk.Button(target_popup, text="Anuluj", command=target_popup.destroy).pack(pady=20)

    def confirm_intrigue_usage(self, card: IntrigueCard, target_player):
        """Potwierdza uĹĽycie karty intrygi i wykonuje efekt"""
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
            f"Czy na pewno chcesz uĹĽyÄ‡ kartÄ™ '{card.name}' {target_text}?\n\n"
            f"Efekt: {card.effect}",
            icon='question'
        )

        if confirm:
            self.execute_intrigue_effects(card, target_player)
            # UsuĹ„ kartÄ™ z rÄ™ki gracza
            current_player.hand_cards.remove(card)
            self.log_message(f"{current_player.name} uĹĽyĹ‚ karty intrygi: {card.name}")
            self.update_ui()

    def execute_intrigue_effects(self, card: IntrigueCard, target_player):
        """Wykonuje wszystkie efekty karty intrygi"""
        current_player = self.players[self.current_player_idx]

        for effect in card.effects:
            # OkreĹ›l listÄ™ graczy docelowych
            targets = []
            if effect.target_type == "opponent" and target_player:
                targets = [target_player]
            elif effect.target_type == "all_opponents":
                targets = [p for p in self.players if p != current_player]
            elif effect.target_type == "all_players":
                targets = self.players
            elif effect.target_type == "self":
                targets = [current_player]

            # Wykonaj efekt na kaĹĽdym celu
            for target in targets:
                self.apply_intrigue_effect(effect, target, current_player)

    def use_opportunity_card(self, card: OpportunityCard):
        """UĹĽywa kartÄ™ okazji - sprawdza warunki i wykonuje efekt na graczu"""
        current_player = self.players[self.current_player_idx]

        # SprawdĹş warunki karty
        if not self.check_opportunity_conditions(card, current_player):
            messagebox.showwarning("Warunki niezpeĹ‚nione",
                                 f"Nie speĹ‚niasz warunkĂłw karty '{card.name}'.\n"
                                 f"Wymagania: {card.requirements}")
            return

        # Popup potwierdzenia
        confirm = messagebox.askyesno(
            "Potwierdzenie",
            f"Czy na pewno chcesz uĹĽyÄ‡ kartÄ™ '{card.name}'?\n\n"
            f"Efekt: {card.bonus_value} {card.bonus_type}\n"
            f"Opis: {card.description}",
            icon='question'
        )

        if confirm:
            self.execute_opportunity_effects(card, current_player)
            # UsuĹ„ kartÄ™ z rÄ™ki gracza
            current_player.hand_cards.remove(card)
            self.log_message(f"{current_player.name} uĹĽyĹ‚ karty okazji: {card.name}")
            self.update_ui()

    def check_opportunity_conditions(self, card: OpportunityCard, player) -> bool:
        """Sprawdza czy gracz speĹ‚nia warunki uĹĽycia karty okazji"""
        condition = card.requirements.lower()

        if condition == "brak":
            return True
        elif "min. 1 publikacja" in condition:
            return player.publications >= 1
        elif "aktywne badanie" in condition:
            return len(player.active_research) > 0
        elif "reputacja 3+" in condition:
            return player.reputation >= 3
        elif "ukoĹ„czone badanie" in condition:
            return len(player.completed_research) > 0
        elif "min. 1 profesor" in condition:
            return any(scientist.type == ScientistType.PROFESOR for scientist in player.scientists)
        elif "badanie chemiczne lub fizyczne" in condition:
            return any(research.field in ["Chemia", "Fizyka"] for research in player.active_research + player.completed_research)
        else:
            return True  # DomyĹ›lnie pozwĂłl

    def execute_opportunity_effects(self, card: OpportunityCard, target_player):
        """Wykonuje wszystkie efekty karty okazji"""
        for effect in card.effects:
            self.apply_opportunity_effect(effect, target_player)

    def apply_opportunity_effect(self, effect: OpportunityEffect, target_player):
        """Stosuje pojedynczy efekt okazji na graczu"""
        # Stanford: podwaja zyski z kart okazji
        try:
            cp = self.players[self.current_player_idx]
            stanford_mult = 2 if (cp and cp.institute and 'stanford' in cp.institute.name.lower()) else 1
        except Exception:
            stanford_mult = 1
        if effect.operation == "add":
            if effect.parameter == "credits":
                target_player.credits += (effect.value * stanford_mult)
                self.log_message(f"{target_player.name} zyskuje {effect.value//1000}K")
            elif effect.parameter == "research_points":
                target_player.research_points += (effect.value * stanford_mult)
                self.log_message(f"{target_player.name} zyskuje {effect.value} PB")
            elif effect.parameter == "reputation":
                try:
                    target_player.reputation = max(0, min(5, target_player.reputation + (effect.value * stanford_mult)))
                except Exception:
                    target_player.reputation += (effect.value * stanford_mult)
                self.log_message(f"{target_player.name} zyskuje {effect.value} reputacji")
            elif effect.parameter == "hex_tokens":
                target_player.hex_tokens += effect.value
                self.log_message(f"{target_player.name} zyskuje {effect.value} heksĂłw")
            elif effect.parameter == "action_points":
                try:
                    self.remaining_action_points += (effect.value * stanford_mult)
                except Exception:
                    pass
                self.log_message(f"{target_player.name} zyskuje {effect.value} punktĂłw akcji")
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
                    f"RÄ™ka gracza {target_player.name}",
                    f"Karty w rÄ™ce:\n" + "\n".join(card_names) if card_names else "Brak kart w rÄ™ce"
                )

        # TODO: DodaÄ‡ obsĹ‚ugÄ™ pozostaĹ‚ych operacji (block, copy, itp.)

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
            self.main_notebook.add(self.developer_tab, text="đź”§ Developer")
            self.setup_developer_tab()
            self.log_message("đź”§ Developer mode ENABLED")
        else:
            # Disable developer mode
            self.dev_mode_label.pack_forget()
            # Remove developer tab
            try:
                self.main_notebook.forget(self.developer_tab)
            except:
                pass  # Tab might not be added yet
            self.log_message("đź”§ Developer mode DISABLED")

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
                               text="âš ď¸Ź DEVELOPER MODE - FOR TESTING ONLY âš ď¸Ź",
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
            self.log_message(f"đź”§ DEV: Set {player.name} {attr_name} to {new_value}")

            # Update main UI
            self.update_ui()

        except (ValueError, IndexError):
            self.log_message(f"đź”§ DEV ERROR: Invalid value for {attr_name}")

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

                self.log_message(f"đź”§ DEV: Added {card_name} to {player.name}'s hand")
                self.update_ui()
            else:
                self.log_message(f"đź”§ DEV ERROR: Card {card_name} not found")

        except (ValueError, IndexError) as e:
            self.log_message(f"đź”§ DEV ERROR: {e}")

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
                    self.log_message(f"đź”§ DEV: Removed {card_name} from {player.name}'s hand")
                    self.update_ui()
                    return

            self.log_message(f"đź”§ DEV ERROR: {card_name} not found in {player.name}'s hand")

        except (ValueError, IndexError) as e:
            self.log_message(f"đź”§ DEV ERROR: {e}")

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

            self.log_message(f"đź”§ DEV: Changed current player from {old_player} to {new_player}")
            self.update_ui()

        except (ValueError, IndexError) as e:
            self.log_message(f"đź”§ DEV ERROR: {e}")

    def dev_next_player(self):
        """Advance to next player"""
        old_player = self.players[self.current_player_idx].name
        self.next_player()
        new_player = self.players[self.current_player_idx].name
        self.log_message(f"đź”§ DEV: Advanced from {old_player} to {new_player}")

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

            self.log_message(f"đź”§ DEV: Set phase to {phase_name}")
            self.update_ui()

        except Exception as e:
            self.log_message(f"đź”§ DEV ERROR: {e}")

    def dev_next_phase(self):
        """Advance to next phase"""
        old_phase = self.current_phase.value
        self.next_phase()
        new_phase = self.current_phase.value
        self.log_message(f"đź”§ DEV: Advanced from {old_phase} to {new_phase}")

    def dev_set_round(self):
        """Set the current round"""
        try:
            new_round = int(self.dev_round_var.get())
            if new_round < 1:
                new_round = 1

            old_round = self.current_round
            self.current_round = new_round
            self.log_message(f"đź”§ DEV: Set round from {old_round} to {new_round}")
            self.update_ui()

        except ValueError:
            self.log_message("đź”§ DEV ERROR: Invalid round number")

    def dev_next_round(self):
        """Advance to next round"""
        old_round = self.current_round
        self.advance_round()
        self.log_message(f"đź”§ DEV: Advanced from round {old_round} to {self.current_round}")

    def dev_set_action_points(self):
        """Set remaining action points"""
        try:
            new_ap = int(self.dev_ap_var.get())
            if new_ap < 0:
                new_ap = 0

            old_ap = self.remaining_action_points
            self.remaining_action_points = new_ap
            self.log_message(f"đź”§ DEV: Set action points from {old_ap} to {new_ap}")
            self.update_ui()

        except ValueError:
            self.log_message("đź”§ DEV ERROR: Invalid action points value")

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
            self.log_message(f"đź”§ DEV: Hired {scientist_type} for {player.name}")
            self.update_ui()

        except (ValueError, IndexError) as e:
            self.log_message(f"đź”§ DEV ERROR: {e}")

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

                self.log_message(f"đź”§ DEV: Added {added} hexes to {research.name} for {player.name}")

                # Check if research is complete
                if research.hexes_placed >= research.max_hexes:
                    self.complete_research(player, research)

                self.update_ui()
            else:
                self.log_message(f"đź”§ DEV ERROR: {player.name} has no active research")

        except (ValueError, IndexError) as e:
            self.log_message(f"đź”§ DEV ERROR: {e}")

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
                self.log_message(f"đź”§ DEV: Completed research {research.name} for {player.name}")
                self.update_ui()
            else:
                self.log_message(f"đź”§ DEV ERROR: {player.name} has no active research")

        except (ValueError, IndexError) as e:
            self.log_message(f"đź”§ DEV ERROR: {e}")

    def update_notifications(self):
        """Aktualizuje panel powiadomieĹ„"""
        current_player = self.players[self.current_player_idx] if self.players else None

        if not current_player:
            return

        # SprawdĹş czy obecny gracz ma jakieĹ› powiadomienia jako kierownik
        player_notifications = []

        if hasattr(self, 'consortium_notifications'):
            player_notifications = [
                notif for notif in self.consortium_notifications
                if notif.get('director') == current_player
            ]

        # JeĹ›li sÄ… powiadomienia, pokaĹĽ panel
        if player_notifications:
            # PokaĹĽ panel powiadomieĹ„
            self.notifications_frame.pack(fill='x', pady=(0, 10), after=self.info_frame)

            # WyczyĹ›Ä‡ poprzednie powiadomienia
            for widget in self.notifications_frame.winfo_children():
                widget.destroy()

            # NagĹ‚Ăłwek
            header_frame = tk.Frame(self.notifications_frame, bg='orange', relief='raised', borderwidth=2)
            header_frame.pack(fill='x', padx=5, pady=2)

            tk.Label(header_frame, text=f"đź”” POWIADOMIENIA DLA {current_player.name}",
                    font=('Arial', 12, 'bold'), bg='orange', fg='white').pack(pady=3)

            # Lista powiadomieĹ„
            for notif in player_notifications:
                if notif.get('type') == 'membership_request':
                    project = notif.get('project')
                    applicant = notif.get('applicant')

                    notif_frame = tk.Frame(self.notifications_frame, bg='lightyellow', relief='groove', borderwidth=2)
                    notif_frame.pack(fill='x', padx=5, pady=2)

                    # Tekst powiadomienia
                    info_frame = tk.Frame(notif_frame, bg='lightyellow')
                    info_frame.pack(fill='x', padx=5, pady=3)

                    tk.Label(info_frame, text=f"đź‘¤ {applicant.name} chce doĹ‚Ä…czyÄ‡ do konsorcjum:",
                            font=('Arial', 10, 'bold'), bg='lightyellow').pack(anchor='w')
                    tk.Label(info_frame, text=f"đźŹ›ď¸Ź {project.name}",
                            font=('Arial', 10), bg='lightyellow').pack(anchor='w', padx=20)

                    # Przyciski akcji
                    button_frame = tk.Frame(notif_frame, bg='lightyellow')
                    button_frame.pack(fill='x', padx=5, pady=3)

                    accept_btn = tk.Button(button_frame, text="âś… Akceptuj",
                                         command=lambda p=project, a=applicant: self.approve_consortium_membership(p, a),
                                         bg='lightgreen', font=('Arial', 9, 'bold'))
                    accept_btn.pack(side='left', padx=2)

                    reject_btn = tk.Button(button_frame, text="âťŚ OdrzuÄ‡",
                                         command=lambda p=project, a=applicant: self.reject_consortium_membership(p, a),
                                         bg='lightcoral', font=('Arial', 9, 'bold'))
                    reject_btn.pack(side='left', padx=2)

                    # Przycisk zarzÄ…dzania
                    manage_btn = tk.Button(button_frame, text="đź‘‘ ZarzÄ…dzaj konsorcjami",
                                         command=self.show_consortium_management_panel,
                                         bg='gold', font=('Arial', 9, 'bold'))
                    manage_btn.pack(side='right', padx=2)

        else:
            # Ukryj panel jeĹ›li brak powiadomieĹ„
            self.notifications_frame.pack_forget()

    # Metody komunikacji sieciowej
    def send_action_to_network(self, action_type, action_data):
        """WysyĹ‚a akcjÄ™ gracza do sieci"""
        if self.is_network_game and not self.is_host:
            if self.game_client:
                self.game_client.send_action(action_type, action_data)
        elif self.is_network_game and self.is_host:
            if self.game_server:
                # Host rozgĹ‚asza akcjÄ™ do wszystkich klientĂłw
                message = NetworkMessage(
                    type=MessageType.PLAYER_ACTION,
                    data={'action_type': action_type, 'action_data': action_data}
                )
                self.game_server._broadcast_message(message)

    def handle_network_action(self, message):
        """ObsĹ‚uguje akcjÄ™ od innego gracza przez sieÄ‡"""
        action_type = message.data.get('action_type')
        action_data = message.data.get('action_data')

        # TODO: ZaimplementowaÄ‡ obsĹ‚ugÄ™ rĂłĹĽnych typĂłw akcji
        if action_type == 'play_card':
            self.handle_network_play_card(action_data)
        elif action_type == 'hex_placement':
            self.handle_network_hex_placement(action_data)
        elif action_type == 'research_start':
            self.handle_network_research_start(action_data)

        # OdĹ›wieĹĽ UI
        self.update_ui()

    def handle_network_play_card(self, action_data):
        """ObsĹ‚uguje zagranie karty przez innego gracza"""
        # TODO: ImplementowaÄ‡
        pass

    def handle_network_hex_placement(self, action_data):
        """ObsĹ‚uguje umieszczenie heksa przez innego gracza"""
        # TODO: ImplementowaÄ‡
        pass

    def handle_network_research_start(self, action_data):
        """ObsĹ‚uguje rozpoczÄ™cie badania przez innego gracza"""
        # TODO: ImplementowaÄ‡
        pass

    def broadcast_game_state(self):
        """RozgĹ‚asza aktualny stan gry (tylko host)"""
        if self.is_network_game and self.is_host and self.game_server:
            # Zostanie wywoĹ‚ane przez serwer automatycznie
            pass

    def cleanup_network(self):
        """CzyĹ›ci poĹ‚Ä…czenia sieciowe"""
        if self.game_server:
            self.game_server.stop()
        if self.game_client:
            self.game_client.disconnect()

    def run(self):
        """Uruchamia grÄ™"""
        try:
            self.root.mainloop()
        finally:
            # WyczyĹ›Ä‡ poĹ‚Ä…czenia sieciowe przy zamykaniu
            self.cleanup_network()

class CollapsibleResearchWidget(tk.Frame):
    """Widget dla zwijanych/rozwijanych paneli badaĹ„"""

    def __init__(self, parent, research, game_instance, **kwargs):
        super().__init__(parent, **kwargs)

        self.research = research
        self.game = game_instance
        self.is_expanded = False
        self.hex_widget = None

        # Konfiguracja stylu - zmodernizowany
        self.configure(relief='flat', borderwidth=1, bg=ModernTheme.SURFACE,
                      highlightbackground=ModernTheme.BORDER_LIGHT)

        # Tworzenie struktury
        self.create_header()
        self.create_content_frame()

        # Inicjalny stan - zwiniÄ™te
        self.content_frame.pack_forget()

    def create_header(self):
        """Tworzy zawsze widoczny nagĹ‚Ăłwek"""
        self.header_frame = tk.Frame(self, bg=ModernTheme.PRIMARY_LIGHT, relief='flat', borderwidth=1)
        self.header_frame.pack(fill='x', padx=ModernTheme.SPACING_XS, pady=ModernTheme.SPACING_XS)

        # Lewy panel - przycisk expand i nazwa
        left_panel = tk.Frame(self.header_frame, bg=ModernTheme.PRIMARY_LIGHT)
        left_panel.pack(side='left', fill='x', expand=True)

        # Przycisk expand/collapse - zmodernizowany
        self.toggle_btn = tk.Button(left_panel, text="â–¶",
                                   command=self.toggle_expanded,
                                   bg=ModernTheme.PRIMARY,
                                   fg=ModernTheme.TEXT_ON_PRIMARY,
                                   font=('Segoe UI', ModernTheme.FONT_SIZE_SMALL, 'bold'),
                                   relief='flat', width=3, bd=0)
        self.toggle_btn.pack(side='left', padx=(ModernTheme.SPACING_SM, ModernTheme.SPACING_XS), pady=ModernTheme.SPACING_XS)

        # Nazwa i dziedzina - ulepszona typografia
        name_frame = tk.Frame(left_panel, bg=ModernTheme.PRIMARY_LIGHT)
        name_frame.pack(side='left', fill='x', expand=True, padx=(ModernTheme.SPACING_SM, 0))

        tk.Label(name_frame, text=f"đź”¬ {self.research.name}",
                font=('Segoe UI', ModernTheme.FONT_SIZE_MEDIUM, 'bold'),
                bg=ModernTheme.PRIMARY_LIGHT, fg=ModernTheme.TEXT_PRIMARY).pack(anchor='w')
        tk.Label(name_frame, text=f"đź“š {self.research.field}",
                font=('Segoe UI', ModernTheme.FONT_SIZE_SMALL),
                bg=ModernTheme.PRIMARY_LIGHT, fg=ModernTheme.TEXT_SECONDARY).pack(anchor='w')

        # Prawy panel - postÄ™p i status
        right_panel = tk.Frame(self.header_frame, bg=ModernTheme.PRIMARY_LIGHT)
        right_panel.pack(side='right', padx=ModernTheme.SPACING_SM)

        # Progress info - lepsze kolory
        progress_text = f"{self.get_progress()}/{self.research.max_hexes}"
        self.progress_label = tk.Label(right_panel, text=progress_text,
                                     font=('Segoe UI', ModernTheme.FONT_SIZE_NORMAL, 'bold'),
                                     bg=ModernTheme.PRIMARY_LIGHT, fg=ModernTheme.SUCCESS)
        self.progress_label.pack(side='right', padx=ModernTheme.SPACING_SM)

        # Status indicator - zmodernizowany
        self.status_label = tk.Label(right_panel, text="",
                                   font=('Segoe UI', ModernTheme.FONT_SIZE_SMALL, 'bold'),
                                   bg=ModernTheme.PRIMARY_LIGHT, fg=ModernTheme.WARNING)
        self.status_label.pack(side='right', padx=ModernTheme.SPACING_SM)

        self.update_header_status()

    def create_content_frame(self):
        """Tworzy rozwijany content frame"""
        self.content_frame = tk.Frame(self, bg='lightblue')

        # Informacje o nagrodach
        rewards_frame = tk.Frame(self.content_frame, bg='lightblue')
        rewards_frame.pack(fill='x', padx=5, pady=2)

        tk.Label(rewards_frame, text=f"đźŹ† Podstawowa: {self.research.basic_reward}",
                font=('Arial', 9), bg='lightblue', fg='darkgreen').pack(side='left')
        if self.research.bonus_reward and self.research.bonus_reward != "Brak":
            tk.Label(rewards_frame, text=f"â­ Bonusowa: {self.research.bonus_reward}",
                    font=('Arial', 9), bg='lightblue', fg='orange').pack(side='right')

        # SzczegĂłĹ‚owy status
        self.detail_status_frame = tk.Frame(self.content_frame, bg='lightblue')
        self.detail_status_frame.pack(fill='x', padx=5, pady=2)

        # Container dla mapy heksagonalnej
        self.hex_container = tk.Frame(self.content_frame, bg='lightblue')
        self.hex_container.pack(fill='both', expand=True, padx=5, pady=5)

    def toggle_expanded(self):
        """PrzeĹ‚Ä…cza stan rozwiniÄ™cia"""
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
            self.toggle_btn.config(text="â–Ľ")
            self.content_frame.pack(fill='both', expand=True, padx=2, pady=(0, 2))

            # StwĂłrz/odĹ›wieĹĽ mapÄ™ heksagonalnÄ…
            self.create_hex_widget()

            # Aktualizuj szczegĂłĹ‚owy status
            self.update_detail_status()

            # Auto-scroll do tego panelu jeĹ›li potrzeba
            self.bring_to_top()

    def collapse(self):
        """Zwija panel"""
        if self.is_expanded:
            self.is_expanded = False
            self.toggle_btn.config(text="â–¶")
            self.content_frame.pack_forget()

            # UsuĹ„ hex widget aby zwolniÄ‡ pamiÄ™Ä‡
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
        # UsuĹ„ poprzedni widget jeĹ›li istnieje
        for widget in self.hex_container.winfo_children():
            widget.destroy()

        if self.research.hex_research_map:
            self.hex_widget = HexMapWidget(self.hex_container, self.research.hex_research_map)

            # Ustawienia callback
            self.hex_widget.on_hex_click_callback = lambda pos: self.game.on_hex_clicked(pos, self.research)

            # OdtwĂłrz postÄ™p gracza
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
            # Fallback dla badaĹ„ bez map heksowych
            fallback_label = tk.Label(self.hex_container,
                                    text="Mapa heksagonalna niedostÄ™pna",
                                    bg='lightblue', fg='gray')
            fallback_label.pack(expand=True)

    def update_header_status(self):
        """Aktualizuje status w nagĹ‚Ăłwku"""
        # Progress
        progress_text = f"{self.get_progress()}/{self.research.max_hexes}"
        self.progress_label.config(text=progress_text)

        # Status indicator
        if (hasattr(self.game, 'hex_placement_mode') and
            self.game.hex_placement_mode and
            self.research == getattr(self.game, 'current_research_for_hex', None)):
            self.status_label.config(text="đźŽŻ AKTYWNE", fg='red')
        else:
            self.status_label.config(text="", fg='yellow')

    def update_detail_status(self):
        """Aktualizuje szczegĂłĹ‚owy status w rozwiniÄ™tym panelu"""
        # WyczyĹ›Ä‡ poprzedni status
        for widget in self.detail_status_frame.winfo_children():
            widget.destroy()

        if (hasattr(self.game, 'hex_placement_mode') and
            self.game.hex_placement_mode and
            self.research == getattr(self.game, 'current_research_for_hex', None)):

            pending = getattr(self.game, 'pending_hex_placements', 0)
            status_text = f"đźŽŻ UĹĂ“Ĺ» {pending} HEKS(Ă“W) - Kliknij na mapÄ™!"
            status_label = tk.Label(self.detail_status_frame, text=status_text,
                                  font=('Arial', 10, 'bold'), bg='yellow', fg='red')
            status_label.pack(pady=2)

    def get_progress(self):
        """Zwraca aktualny postÄ™p badania"""
        if hasattr(self.research, 'player_path'):
            return len(self.research.player_path)
        return getattr(self.research, 'hexes_placed', 0)

    def bring_to_top(self):
        """Przewija do tego panelu jeĹ›li jest poza ekranem"""
        # To moĹĽna zaimplementowaÄ‡ pĂłĹşniej dla auto-scroll
        pass

    def auto_expand_if_active(self):
        """Auto-rozwija jeĹ›li to badanie jest aktywne"""
        if (hasattr(self.game, 'hex_placement_mode') and
            self.game.hex_placement_mode and
            self.research == getattr(self.game, 'current_research_for_hex', None)):
            self.expand()

    def refresh(self):
        """OdĹ›wieĹĽa caĹ‚y widget"""
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
        print(f"BĹ‚Ä…d uruchomienia gry: {e}")
        import traceback
        traceback.print_exc()


