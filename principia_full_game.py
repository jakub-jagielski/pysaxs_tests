#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRINCIPIA - Pełna implementacja gry planszowej
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import os

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

# Klasy danych (rozszerzone)
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
    is_active: bool = True

@dataclass
class ResearchCard:
    name: str
    field: str
    hex_map: str
    basic_reward: str
    bonus_reward: str
    description: str
    hex_research_map: Optional[HexResearchMap] = None
    player_path: List[HexPosition] = field(default_factory=list)
    is_completed: bool = False
    is_active: bool = False

    def __post_init__(self):
        if self.hex_research_map is None:
            self.hex_research_map = HexResearchMap(self.hex_map)

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
    progress_points: int = 0

@dataclass
class InstituteCard:
    name: str
    starting_resources: str
    starting_reputation: int
    specialization_bonus: str
    special_ability: str
    description: str

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
    hand_cards: List[ResearchCard] = field(default_factory=list)
    current_grant: Optional[GrantCard] = None
    hex_tokens: int = 20
    action_cards: List[ActionType] = field(default_factory=lambda: list(ActionType))
    publications: int = 0
    activity_points: int = 0  # Punkty aktywności dla grantów

class GameData:
    """Klasa do zarządzania danymi gry wczytanymi z CSV"""
    def __init__(self):
        self.scientists = []
        self.research_cards = []
        self.journals = []
        self.grants = []
        self.institutes = []
        self.scenarios = []

    def load_data(self):
        """Wczytuje wszystkie dane z plików CSV"""
        try:
            # Wczytaj naukowców
            if os.path.exists('karty_naukowcy.csv'):
                with open('karty_naukowcy.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        scientist_type = ScientistType.DOKTOR if row['Typ'] == 'Doktor' else ScientistType.PROFESOR
                        salary = int(row['Pensja'].replace('K', '')) * 1000
                        self.scientists.append(Scientist(
                            name=row['Imię i Nazwisko'],
                            type=scientist_type,
                            field=row['Dziedzina'],
                            salary=salary,
                            hex_bonus=int(row['Bonus Heksów']),
                            special_bonus=row['Specjalny Bonus'],
                            description=row['Opis']
                        ))

            # Wczytaj karty badań
            if os.path.exists('karty_badan.csv'):
                with open('karty_badan.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.research_cards.append(ResearchCard(
                            name=row['Nazwa'],
                            field=row['Dziedzina'],
                            hex_map=row['Mapa_Heksagonalna'],
                            basic_reward=row['Nagroda_Podstawowa'],
                            bonus_reward=row['Nagroda_Dodatkowa'],
                            description=row['Opis']
                        ))

            # Wczytaj czasopisma
            if os.path.exists('karty_czasopisma.csv'):
                with open('karty_czasopisma.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.journals.append(JournalCard(
                            name=row['Nazwa'],
                            impact_factor=int(row['Impact_Factor']),
                            pb_cost=int(row['Koszt_PB']),
                            requirements=row['Wymagania'],
                            pz_reward=int(row['Nagroda_PZ']),
                            special_bonus=row['Specjalny_Bonus'],
                            description=row['Opis']
                        ))

            # Wczytaj granty
            if os.path.exists('karty_granty.csv'):
                with open('karty_granty.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.grants.append(GrantCard(
                            name=row['Nazwa'],
                            requirements=row['Wymagania'],
                            goal=row['Cel'],
                            reward=row['Nagroda'],
                            round_bonus=row['Runda_Bonus'],
                            description=row['Opis']
                        ))

            # Wczytaj instytuty
            if os.path.exists('karty_instytuty.csv'):
                with open('karty_instytuty.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.institutes.append(InstituteCard(
                            name=row['Nazwa'],
                            starting_resources=row['Zasoby_Startowe'],
                            starting_reputation=int(row['Reputacja_Start']),
                            specialization_bonus=row['Specjalizacja_Bonus'],
                            special_ability=row['Specjalna_Zdolność'],
                            description=row['Opis']
                        ))

            return True

        except Exception as e:
            print(f"Błąd podczas wczytywania danych: {e}")
            # Stwórz przykładowe dane
            self.create_sample_data()
            return False

    def create_sample_data(self):
        """Tworzy przykładowe dane gdy nie można wczytać z plików"""
        # Przykładowi naukowcy
        self.scientists = [
            Scientist("Dr Sarah Chen", ScientistType.DOKTOR, "Fizyka", 2000, 2, "+1 PB przy publikacji", "Pionierka algorytmów"),
            Scientist("Prof. Lisa Wang", ScientistType.PROFESOR, "Fizyka", 3000, 3, "+2K za badanie", "Autorytet w fizyce"),
            Scientist("Dr Klaus Weber", ScientistType.DOKTOR, "Chemia", 2000, 2, "+1 heks", "Ekspert chemii"),
        ]

        # Przykładowe badania
        self.research_cards = [
            ResearchCard("Bozon Higgsa", "Fizyka", "START(0,0)->[(1,0)->(2,0)->(3,0)END | (1,1)->(2,1)BONUS(+2PB)]", "4 PB, 2 PZ", "Publikacja Nature", "Poszukiwanie cząstki boga"),
            ResearchCard("Kwantowa Kryptografia", "Fizyka", "START(0,0)->[(1,0)->(2,0)END | (0,1)BONUS(+1PZ)]", "2 PB, 3 PZ", "Granty rządowe", "Niezniszczalny system szyfrowania"),
            ResearchCard("Superprzewodnik", "Fizyka", "START(0,0)->[(1,0)->(2,0)END | (0,1)->(1,1)BONUS(+1PZ)]", "2 PB, 2 PZ", "+3K za badania", "Materiał zero rezystancji"),
        ]

        # Przykładowe granty
        self.grants = [
            GrantCard("Grant Startup", "Brak wymagań", "10 punktów aktywności", "8K", "+2K/rundę", "Podstawowe finansowanie"),
            GrantCard("Grant Fizyczny", "Min. 1 fizyk", "Ukończ badanie fizyczne", "14K", "+2K/rundę", "Finansowanie fizyki"),
            GrantCard("Grant Prestiżowy", "Reputacja 4+", "Publikacja Nature", "18K", "+2K/rundę", "Elitarne finansowanie"),
        ]

        # Przykładowe instytuty
        self.institutes = [
            InstituteCard("MIT", "8K, 2 PZ", 3, "+1 heks fizyka", "4 naukowców bez kary", "Wiodąca uczelnia techniczna"),
            InstituteCard("Harvard", "10K, 1 PZ", 3, "+1 Rep za IF 6+", "5 naukowców bez kary", "Najstarsza uczelnia"),
            InstituteCard("Max Planck", "7K, 3 PZ", 3, "+1 PB za badanie", "Limit ręki +2", "Niemiecki instytut badań"),
        ]

class PrincipiaFullGame:
    """Pełna implementacja gry Principia"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PRINCIPIA - Gra Planszowa (Pełna Wersja)")
        self.root.geometry("1600x1000")

        self.game_data = GameData()
        self.players = []
        self.current_player_idx = 0
        self.current_round = 1
        self.current_phase = GamePhase.GRANTY
        self.available_grants = []
        self.available_journals = []
        self.available_scientists = []
        self.game_ended = False
        self.selected_research = None

        self.setup_ui()

    def setup_ui(self):
        """Tworzy rozszerzony interfejs użytkownika"""
        # Główny kontener
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Panel informacji o grze (góra)
        self.info_frame = ttk.LabelFrame(main_frame, text="Informacje o grze")
        self.info_frame.pack(fill='x', pady=(0, 5))

        info_row = ttk.Frame(self.info_frame)
        info_row.pack(fill='x', padx=10, pady=5)

        self.round_label = ttk.Label(info_row, text="Runda: 1", font=('Arial', 12, 'bold'))
        self.round_label.pack(side='left')

        self.phase_label = ttk.Label(info_row, text="Faza: Grantów", font=('Arial', 12, 'bold'))
        self.phase_label.pack(side='left', padx=(20, 0))

        self.current_player_label = ttk.Label(info_row, text="Gracz: -", font=('Arial', 12, 'bold'))
        self.current_player_label.pack(side='left', padx=(20, 0))

        # Kontener główny (środek)
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

        # Zakładka badań
        self.research_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.research_tab, text="Badania")

        # Zakładka rynków
        self.markets_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.markets_tab, text="Rynki")

        # Panel kontroli (prawa strona)
        self.control_frame = ttk.LabelFrame(content_frame, text="Kontrola")
        self.control_frame.pack(side='right', fill='y')

        self.setup_control_panel()
        self.setup_research_tab()
        self.setup_markets_tab()

    def setup_control_panel(self):
        """Konfiguruje panel kontroli"""
        # Przyciski główne
        setup_btn = ttk.Button(self.control_frame, text="Nowa Gra", command=self.setup_game)
        setup_btn.pack(padx=10, pady=5, fill='x')

        self.next_phase_btn = ttk.Button(self.control_frame, text="Następna faza",
                                        command=self.next_phase, state='disabled')
        self.next_phase_btn.pack(padx=10, pady=5, fill='x')

        # Separacja
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill='x', padx=10, pady=10)

        # Akcje szybkie
        ttk.Label(self.control_frame, text="Szybkie akcje:", font=('Arial', 10, 'bold')).pack(padx=10, anchor='w')

        add_credits_btn = ttk.Button(self.control_frame, text="Dodaj 5K kredytów",
                                    command=lambda: self.modify_current_player('credits', 5000))
        add_credits_btn.pack(padx=10, pady=2, fill='x')

        add_pz_btn = ttk.Button(self.control_frame, text="Dodaj 3 PZ",
                               command=lambda: self.modify_current_player('prestige_points', 3))
        add_pz_btn.pack(padx=10, pady=2, fill='x')

        hire_scientist_btn = ttk.Button(self.control_frame, text="Zatrudnij naukowca",
                                       command=self.hire_random_scientist)
        hire_scientist_btn.pack(padx=10, pady=2, fill='x')

        # Separacja
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill='x', padx=10, pady=10)

        # Log gry
        log_frame = ttk.LabelFrame(self.control_frame, text="Log gry")
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=25, height=15)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)

    def setup_research_tab(self):
        """Konfiguruje zakładkę badań"""
        # Główny kontener
        research_main = ttk.Frame(self.research_tab)
        research_main.pack(fill='both', expand=True, padx=5, pady=5)

        # Panel wyboru badań (góra)
        select_frame = ttk.LabelFrame(research_main, text="Wybierz badanie")
        select_frame.pack(fill='x', pady=(0, 5))

        self.research_listbox = tk.Listbox(select_frame, height=3)
        self.research_listbox.pack(fill='x', padx=5, pady=5)
        self.research_listbox.bind('<<ListboxSelect>>', self.on_research_select)

        # Panel mapy heksagonalnej (środek)
        self.hex_map_frame = ttk.LabelFrame(research_main, text="Mapa badania")
        self.hex_map_frame.pack(fill='both', expand=True, pady=(0, 5))

        # Panel informacji o badaniu (dół)
        self.research_info_frame = ttk.LabelFrame(research_main, text="Informacje o badaniu")
        self.research_info_frame.pack(fill='x')

        self.research_info_text = tk.Text(self.research_info_frame, height=4, wrap='word')
        self.research_info_text.pack(fill='x', padx=5, pady=5)

        # Przyciski akcji
        research_buttons = ttk.Frame(self.research_info_frame)
        research_buttons.pack(fill='x', padx=5, pady=5)

        self.start_research_btn = ttk.Button(research_buttons, text="Rozpocznij badanie",
                                           command=self.start_research)
        self.start_research_btn.pack(side='left', padx=(0, 5))

        self.place_hex_btn = ttk.Button(research_buttons, text="Połóż heks",
                                       command=self.place_hex, state='disabled')
        self.place_hex_btn.pack(side='left', padx=5)

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

        self.scientists_listbox = tk.Listbox(scientists_frame)
        self.scientists_listbox.pack(fill='both', expand=True, padx=5, pady=5)

        hire_btn = ttk.Button(scientists_frame, text="Zatrudnij", command=self.hire_selected_scientist)
        hire_btn.pack(pady=5)

        # Rynek czasopism
        journals_frame = ttk.LabelFrame(right_markets, text="Dostępne czasopisma")
        journals_frame.pack(fill='both', expand=True, pady=(0, 5))

        self.journals_listbox = tk.Listbox(journals_frame)
        self.journals_listbox.pack(fill='both', expand=True, padx=5, pady=5)

        publish_btn = ttk.Button(journals_frame, text="Publikuj", command=self.publish_article)
        publish_btn.pack(pady=5)

        # Dostępne granty
        grants_frame = ttk.LabelFrame(right_markets, text="Dostępne granty")
        grants_frame.pack(fill='both', expand=True)

        self.grants_listbox = tk.Listbox(grants_frame)
        self.grants_listbox.pack(fill='both', expand=True, padx=5, pady=5)

        take_grant_btn = ttk.Button(grants_frame, text="Weź grant", command=self.take_selected_grant)
        take_grant_btn.pack(pady=5)

    def log_message(self, message: str):
        """Dodaje wiadomość do logu gry"""
        self.log_text.insert(tk.END, f"[R{self.current_round}] {message}\n")
        self.log_text.see(tk.END)

    def setup_game(self):
        """Konfiguruje nową grę"""
        try:
            self.game_data.load_data()
            self.log_message("Wczytano dane gry")

            # Stwórz trzech graczy
            colors = ['red', 'blue', 'green']
            player_names = ['Gracz 1', 'Gracz 2', 'Gracz 3']

            self.players = []
            for i in range(3):
                player = Player(
                    name=player_names[i],
                    color=colors[i]
                )

                # Przypisz instytut
                if self.game_data.institutes:
                    player.institute = self.game_data.institutes[i % len(self.game_data.institutes)]

                    # Parsuj zasoby startowe
                    resources = player.institute.starting_resources.split(', ')
                    for resource in resources:
                        if 'K' in resource:
                            player.credits = int(resource.replace('K', '')) * 1000
                        elif 'PZ' in resource:
                            player.prestige_points = int(resource.replace(' PZ', ''))

                    player.reputation = player.institute.starting_reputation

                # Daj startowe karty badań
                if self.game_data.research_cards:
                    player.hand_cards = random.sample(self.game_data.research_cards, min(3, len(self.game_data.research_cards)))

                self.players.append(player)

            # Przygotuj rynki
            self.available_scientists = random.sample(self.game_data.scientists, min(4, len(self.game_data.scientists)))
            self.available_journals = random.sample(self.game_data.journals, min(4, len(self.game_data.journals)))

            self.setup_players_ui()
            self.update_research_list()
            self.update_markets()
            self.prepare_round()
            self.next_phase_btn['state'] = 'normal'
            self.log_message("Gra skonfigurowana - 3 graczy")

        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas konfiguracji gry: {e}")

    def setup_players_ui(self):
        """Tworzy interfejs graczy"""
        # Wyczyść poprzedni UI
        for widget in self.players_frame.winfo_children():
            widget.destroy()

        for i, player in enumerate(self.players):
            # Frame gracza z kolorem
            player_frame = ttk.LabelFrame(self.players_frame, text=f"{player.name}")
            player_frame.pack(fill='x', padx=5, pady=5)

            # Wskaźnik aktywnego gracza
            if i == self.current_player_idx:
                indicator = ttk.Label(player_frame, text=">>> AKTYWNY <<<",
                                    foreground=player.color, font=('Arial', 10, 'bold'))
                indicator.pack(pady=2)

            # Instytut
            if player.institute:
                ttk.Label(player_frame, text=f"{player.institute.name}",
                         font=('Arial', 9, 'bold')).pack(anchor='w', padx=5)

            # Zasoby w siatce
            resources_frame = ttk.Frame(player_frame)
            resources_frame.pack(fill='x', padx=5, pady=2)

            ttk.Label(resources_frame, text=f"💰 {player.credits}").grid(row=0, column=0, sticky='w')
            ttk.Label(resources_frame, text=f"⭐ {player.prestige_points}").grid(row=0, column=1, sticky='w', padx=(10, 0))
            ttk.Label(resources_frame, text=f"📊 {player.reputation}").grid(row=1, column=0, sticky='w')
            ttk.Label(resources_frame, text=f"🔬 {player.research_points}").grid(row=1, column=1, sticky='w', padx=(10, 0))

            # Zespół
            team_frame = ttk.Frame(player_frame)
            team_frame.pack(fill='x', padx=5, pady=2)

            ttk.Label(team_frame, text=f"👥 Zespół: {len(player.scientists)}").pack(anchor='w')

            # Lista naukowców
            if player.scientists:
                scientists_text = ", ".join([f"{s.name} ({s.type.value})" for s in player.scientists[:2]])
                if len(player.scientists) > 2:
                    scientists_text += f" i {len(player.scientists) - 2} innych"
                ttk.Label(team_frame, text=scientists_text, font=('Arial', 8)).pack(anchor='w')

            # Badania
            research_frame = ttk.Frame(player_frame)
            research_frame.pack(fill='x', padx=5, pady=2)

            ttk.Label(research_frame, text=f"🧪 Aktywne: {len(player.active_research)}").pack(anchor='w')
            ttk.Label(research_frame, text=f"✅ Ukończone: {len(player.completed_research)}").pack(anchor='w')

            # Grant
            if player.current_grant:
                grant_frame = ttk.Frame(player_frame)
                grant_frame.pack(fill='x', padx=5, pady=2)
                ttk.Label(grant_frame, text=f"💼 {player.current_grant.name}",
                         font=('Arial', 8, 'italic')).pack(anchor='w')

    def prepare_round(self):
        """Przygotowuje nową rundę"""
        # Przygotuj granty na rundę
        self.available_grants = random.sample(self.game_data.grants, min(6, len(self.game_data.grants)))

        self.current_phase = GamePhase.GRANTY
        self.update_ui()
        self.update_markets()
        self.log_message(f"Rozpoczęto rundę {self.current_round}")

    def next_phase(self):
        """Przechodzi do następnej fazy gry"""
        if self.current_phase == GamePhase.GRANTY:
            self.current_phase = GamePhase.AKCJE
            self.log_message("Przejście do fazy akcji")

        elif self.current_phase == GamePhase.AKCJE:
            self.current_phase = GamePhase.PORZADKOWA
            self.log_message("Przejście do fazy porządkowej")

        elif self.current_phase == GamePhase.PORZADKOWA:
            self.end_round()

        self.update_ui()

    def end_round(self):
        """Kończy rundę i przechodzi do następnej"""
        # Zapłać pensje
        for player in self.players:
            total_salary = 0
            scientist_count = len([s for s in player.scientists if s.type != ScientistType.DOKTORANT])

            for scientist in player.scientists:
                if scientist.is_paid:
                    total_salary += scientist.salary

            # Dodaj karę za przeciążenie (więcej niż 3 naukowców)
            if scientist_count > 3:
                overload_penalty = (scientist_count - 3) * 1000
                total_salary += overload_penalty
                self.log_message(f"{player.name} ma karę przeciążenia: {overload_penalty}")

            if player.credits >= total_salary:
                player.credits -= total_salary
                self.log_message(f"{player.name} zapłacił {total_salary} pensji")
            else:
                player.reputation = max(0, player.reputation - 1)
                self.log_message(f"{player.name} nie zapłacił pensji! Reputacja -1")

        # Sprawdź cele grantów
        self.check_grant_objectives()

        # Odśwież rynki
        self.refresh_markets()

        # Przygotuj następną rundę
        self.current_round += 1
        self.current_player_idx = 0
        self.prepare_round()

    def check_grant_objectives(self):
        """Sprawdza cele grantów graczy"""
        for player in self.players:
            if player.current_grant and not player.current_grant.is_completed:
                goal = player.current_grant.goal.lower()

                # Sprawdź różne typy celów
                if "punktów aktywności" in goal:
                    required_points = int(goal.split()[0])
                    if player.activity_points >= required_points:
                        self.complete_grant(player)

                elif "publikacje" in goal or "publikacji" in goal:
                    required_pubs = int(goal.split()[0])
                    if player.publications >= required_pubs:
                        self.complete_grant(player)

                elif "badanie" in goal:
                    if len(player.completed_research) > 0:
                        self.complete_grant(player)

        # Reset punktów aktywności
        for player in self.players:
            player.activity_points = 0

    def complete_grant(self, player: Player):
        """Kończy grant gracza"""
        if player.current_grant:
            # Daj nagrodę
            reward = player.current_grant.reward
            if 'K' in reward:
                credits = int(reward.replace('K', '')) * 1000
                player.credits += credits
                self.log_message(f"{player.name} ukończył grant i otrzymał {credits} kredytów!")

            player.current_grant.is_completed = True
            player.current_grant = None

    def refresh_markets(self):
        """Odświeża rynki"""
        # Usuń pierwszego naukowca, dodaj nowego
        if self.available_scientists and self.game_data.scientists:
            self.available_scientists.pop(0)
            available_pool = [s for s in self.game_data.scientists if s not in self.available_scientists]
            if available_pool:
                self.available_scientists.append(random.choice(available_pool))

        # Podobnie z czasopismami
        if self.available_journals and self.game_data.journals:
            self.available_journals.pop(0)
            available_pool = [j for j in self.game_data.journals if j not in self.available_journals]
            if available_pool:
                self.available_journals.append(random.choice(available_pool))

        self.update_markets()

    def update_ui(self):
        """Aktualizuje interfejs użytkownika"""
        self.round_label.config(text=f"Runda: {self.current_round}")
        self.phase_label.config(text=f"Faza: {self.current_phase.value}")

        if self.players:
            current_player = self.players[self.current_player_idx]
            self.current_player_label.config(text=f"Gracz: {current_player.name}")

        self.setup_players_ui()
        self.update_research_list()

    def update_research_list(self):
        """Aktualizuje listę badań"""
        self.research_listbox.delete(0, tk.END)

        if self.players:
            current_player = self.players[self.current_player_idx]

            # Dodaj karty z ręki
            for card in current_player.hand_cards:
                self.research_listbox.insert(tk.END, f"[RĘKA] {card.name} ({card.field})")

            # Dodaj aktywne badania
            for card in current_player.active_research:
                status = "UKOŃCZONE" if card.is_completed else f"AKTYWNE {len(card.player_path)} heksów"
                self.research_listbox.insert(tk.END, f"[{status}] {card.name}")

    def update_markets(self):
        """Aktualizuje rynki"""
        # Naukowcy
        self.scientists_listbox.delete(0, tk.END)
        for scientist in self.available_scientists:
            salary_text = f"{scientist.salary//1000}K"
            self.scientists_listbox.insert(tk.END, f"{scientist.name} ({scientist.type.value}) - {salary_text}")

        # Czasopisma
        self.journals_listbox.delete(0, tk.END)
        for journal in self.available_journals:
            self.journals_listbox.insert(tk.END, f"{journal.name} (IF: {journal.impact_factor}, {journal.pz_reward} PZ)")

        # Granty
        self.grants_listbox.delete(0, tk.END)
        for grant in self.available_grants:
            self.grants_listbox.insert(tk.END, f"{grant.name} - {grant.reward}")

    def on_research_select(self, event):
        """Obsługuje wybór badania z listy"""
        selection = self.research_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        current_player = self.players[self.current_player_idx]

        # Znajdź wybrane badanie
        all_research = current_player.hand_cards + current_player.active_research
        if idx < len(all_research):
            self.selected_research = all_research[idx]
            self.display_research_info()

    def display_research_info(self):
        """Wyświetla informacje o wybranym badaniu"""
        if not self.selected_research:
            return

        self.research_info_text.delete(1.0, tk.END)
        info = f"Nazwa: {self.selected_research.name}\n"
        info += f"Dziedzina: {self.selected_research.field}\n"
        info += f"Nagroda: {self.selected_research.basic_reward}\n"
        info += f"Bonus: {self.selected_research.bonus_reward}\n"
        info += f"Opis: {self.selected_research.description}"

        self.research_info_text.insert(1.0, info)

        # Aktualizuj mapę heksagonalną
        self.update_hex_map()

        # Aktualizuj przyciski
        if self.selected_research.is_active:
            self.start_research_btn['state'] = 'disabled'
            self.place_hex_btn['state'] = 'normal'
        else:
            self.start_research_btn['state'] = 'normal'
            self.place_hex_btn['state'] = 'disabled'

    def update_hex_map(self):
        """Aktualizuje mapę heksagonalną"""
        # Wyczyść poprzednią mapę
        for widget in self.hex_map_frame.winfo_children():
            widget.destroy()

        if not self.selected_research or not self.selected_research.hex_research_map:
            return

        # Stwórz widget mapy
        self.hex_map_widget = HexMapWidget(self.hex_map_frame, self.selected_research.hex_research_map)
        self.hex_map_widget.pack(fill='both', expand=True, padx=5, pady=5)

        # Ustaw callback
        self.hex_map_widget.on_hex_click_callback = self.on_hex_click

        # Podświetl istniejącą ścieżkę gracza
        current_player = self.players[self.current_player_idx]
        for pos in self.selected_research.player_path:
            self.hex_map_widget.highlight_hex(pos, current_player.color)

    def on_hex_click(self, position: HexPosition):
        """Obsługuje kliknięcie na heks"""
        if not self.selected_research or not self.selected_research.is_active:
            return

        current_player = self.players[self.current_player_idx]

        # Spróbuj położyć heks
        result = self.selected_research.hex_research_map.place_hex(
            position, current_player.color, self.selected_research.player_path
        )

        if result['success']:
            self.log_message(f"{current_player.name} położył heks na ({position.q}, {position.r})")

            # Sprawdź bonus
            if result['bonus']:
                self.apply_hex_bonus(current_player, result['bonus'])

            # Sprawdź ukończenie
            if result['completed']:
                self.complete_research(current_player, self.selected_research)

            # Aktualizuj wyświetlanie
            self.hex_map_widget.update_display()
            self.update_hex_map()
            self.setup_players_ui()

        else:
            messagebox.showwarning("Uwaga", "Nie można położyć heksu w tym miejscu!")

    def apply_hex_bonus(self, player: Player, bonus: str):
        """Aplikuje bonus z heksu"""
        if 'PB' in bonus:
            pb_amount = int(bonus.replace('+', '').replace('PB', ''))
            player.research_points += pb_amount
            self.log_message(f"{player.name} otrzymał bonus {bonus}")
        elif 'PZ' in bonus:
            pz_amount = int(bonus.replace('+', '').replace('PZ', ''))
            player.prestige_points += pz_amount
            self.log_message(f"{player.name} otrzymał bonus {bonus}")
        elif 'K' in bonus:
            credits = int(bonus.replace('+', '').replace('K', '')) * 1000
            player.credits += credits
            self.log_message(f"{player.name} otrzymał bonus {bonus}")

    def start_research(self):
        """Rozpoczyna badanie"""
        if not self.selected_research:
            return

        current_player = self.players[self.current_player_idx]

        # Przenieś z ręki do aktywnych badań
        if self.selected_research in current_player.hand_cards:
            current_player.hand_cards.remove(self.selected_research)
            current_player.active_research.append(self.selected_research)
            self.selected_research.is_active = True
            self.selected_research.player_path = []

            self.log_message(f"{current_player.name} rozpoczął badanie: {self.selected_research.name}")
            current_player.activity_points += 4  # Ukończenie badania = 4 punkty aktywności

            self.update_research_list()
            self.display_research_info()

    def place_hex(self):
        """Umieszcza heks na mapie (automatycznie)"""
        if not self.selected_research or not self.selected_research.is_active:
            return

        current_player = self.players[self.current_player_idx]

        # Znajdź następną możliwą pozycję
        hex_map = self.selected_research.hex_research_map

        # Jeśli to pierwszy heks, połóż na start
        if not self.selected_research.player_path:
            if hex_map.start_position:
                self.on_hex_click(hex_map.start_position)
            return

        # W przeciwnym razie znajdź sąsiednią pozycję
        last_pos = self.selected_research.player_path[-1]
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

        for dq, dr in directions:
            new_pos = HexPosition(last_pos.q + dq, last_pos.r + dr)
            if hex_map.can_place_hex(new_pos, self.selected_research.player_path):
                self.on_hex_click(new_pos)
                break

    def complete_research(self, player: Player, research: ResearchCard):
        """Kończy badanie"""
        research.is_completed = True
        player.active_research.remove(research)
        player.completed_research.append(research)

        # Daj nagrody
        if 'PB' in research.basic_reward:
            pb_match = research.basic_reward.split('PB')[0].strip().split()[-1]
            try:
                pb_amount = int(pb_match)
                player.research_points += pb_amount
            except ValueError:
                pass

        if 'PZ' in research.basic_reward:
            pz_parts = research.basic_reward.split('PZ')
            if len(pz_parts) > 1:
                try:
                    pz_amount = int(pz_parts[0].strip().split()[-1])
                    player.prestige_points += pz_amount
                except ValueError:
                    pass

        # Reset mapy badania
        research.hex_research_map.reset_player_progress(player.color)
        research.player_path = []

        # Zwróć heksy
        player.hex_tokens = 20

        self.log_message(f"{player.name} ukończył badanie: {research.name}!")
        player.activity_points += 4  # Ukończenie badania = 4 punkty aktywności

    def modify_current_player(self, attribute: str, amount: int):
        """Modyfikuje atrybut aktualnego gracza"""
        if not self.players:
            return

        current_player = self.players[self.current_player_idx]
        current_value = getattr(current_player, attribute)
        setattr(current_player, attribute, current_value + amount)

        self.log_message(f"{current_player.name}: {attribute} +{amount}")
        self.setup_players_ui()

    def hire_random_scientist(self):
        """Zatrudnia losowego naukowca"""
        if not self.available_scientists or not self.players:
            return

        current_player = self.players[self.current_player_idx]
        scientist = random.choice(self.available_scientists)

        if current_player.credits >= scientist.salary * 2:  # Sprawdź czy stać na pensję
            current_player.scientists.append(scientist)
            current_player.credits -= scientist.salary * 2  # Koszt zatrudnienia
            self.available_scientists.remove(scientist)

            self.log_message(f"{current_player.name} zatrudnił {scientist.name}")
            current_player.activity_points += 2  # Zatrudnienie = 2 punkty aktywności

            self.setup_players_ui()
            self.update_markets()
        else:
            messagebox.showwarning("Uwaga", "Nie stać Cię na tego naukowca!")

    def hire_selected_scientist(self):
        """Zatrudnia wybranego naukowca"""
        selection = self.scientists_listbox.curselection()
        if not selection or not self.players:
            return

        idx = selection[0]
        scientist = self.available_scientists[idx]
        current_player = self.players[self.current_player_idx]

        if current_player.credits >= scientist.salary * 2:
            current_player.scientists.append(scientist)
            current_player.credits -= scientist.salary * 2
            self.available_scientists.remove(scientist)

            self.log_message(f"{current_player.name} zatrudnił {scientist.name}")
            current_player.activity_points += 2

            self.setup_players_ui()
            self.update_markets()
        else:
            messagebox.showwarning("Uwaga", "Nie stać Cię na tego naukowca!")

    def publish_article(self):
        """Publikuje artykuł"""
        selection = self.journals_listbox.curselection()
        if not selection or not self.players:
            return

        idx = selection[0]
        journal = self.available_journals[idx]
        current_player = self.players[self.current_player_idx]

        if current_player.research_points >= journal.pb_cost:
            current_player.research_points -= journal.pb_cost
            current_player.prestige_points += journal.pz_reward
            current_player.publications += 1

            self.log_message(f"{current_player.name} opublikował w {journal.name} za {journal.pz_reward} PZ")
            current_player.activity_points += 3  # Publikacja = 3 punkty aktywności

            self.setup_players_ui()
        else:
            messagebox.showwarning("Uwaga", "Nie masz wystarczająco punktów badań!")

    def take_selected_grant(self):
        """Bierze wybrany grant"""
        selection = self.grants_listbox.curselection()
        if not selection or not self.players:
            return

        idx = selection[0]
        grant = self.available_grants[idx]
        current_player = self.players[self.current_player_idx]

        if current_player.current_grant is None:
            current_player.current_grant = grant
            self.available_grants.remove(grant)

            self.log_message(f"{current_player.name} wziął grant: {grant.name}")

            self.setup_players_ui()
            self.update_markets()
        else:
            messagebox.showwarning("Uwaga", "Masz już grant w tej rundzie!")

    def run(self):
        """Uruchamia grę"""
        self.log_message("Witaj w grze PRINCIPIA!")
        self.log_message("Kliknij 'Nowa Gra' aby rozpocząć.")
        self.root.mainloop()

if __name__ == "__main__":
    game = PrincipiaFullGame()
    game.run()