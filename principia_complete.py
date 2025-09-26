#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRINCIPIA - Kompletna implementacja gry planszowej
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

# Importuj system heksagonalny
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

# Klasy danych
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

@dataclass
class InstituteCard:
    name: str
    starting_resources: str
    starting_reputation: int
    specialization_bonus: str
    special_ability: str
    description: str

@dataclass
class LargeProject:
    name: str
    requirements: str
    director_reward: str
    member_reward: str
    description: str
    contributed_pb: int = 0
    contributed_credits: int = 0
    director: Optional['Player'] = None
    members: List['Player'] = field(default_factory=list)
    is_completed: bool = False

@dataclass
class Player:
    name: str
    color: str
    institute: Optional[InstituteCard] = None
    credits: int = 0
    prestige_points: int = 0
    research_points: int = 0  # PB - Punkty Badań
    reputation: int = 3
    scientists: List[Scientist] = field(default_factory=list)
    active_research: List[ResearchCard] = field(default_factory=list)
    completed_research: List[ResearchCard] = field(default_factory=list)
    hand_cards: List[ResearchCard] = field(default_factory=list)
    current_grant: Optional[GrantCard] = None
    hex_tokens: int = 20
    available_actions: List[ActionType] = field(default_factory=lambda: list(ActionType))
    used_actions: List[ActionType] = field(default_factory=list)
    publications: int = 0
    has_passed: bool = False

class GameData:
    """Klasa do zarządzania danymi gry wczytanymi z CSV"""
    def __init__(self):
        self.scientists = []
        self.research_cards = []
        self.journals = []
        self.grants = []
        self.institutes = []
        self.large_projects = []

    def load_data(self):
        """Wczytuje wszystkie dane z plików CSV"""
        try:
            # Wczytaj naukowców
            with open('karty_naukowcy.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    scientist_type = ScientistType.DOKTOR if row['Typ'] == 'Doktor' else ScientistType.PROFESOR
                    salary_str = row['Pensja'].replace('K', '').replace(' ', '')
                    self.scientists.append(Scientist(
                        name=row['Imię i Nazwisko'],
                        type=scientist_type,
                        field=row['Dziedzina'],
                        salary=int(salary_str) * 1000,
                        hex_bonus=int(row['Bonus Heksów']),
                        special_bonus=row['Specjalny Bonus'],
                        description=row['Opis']
                    ))

            # Wczytaj karty badań
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

            # Stwórz przykładowe Wielkie Projekty
            self.large_projects = [
                LargeProject(
                    name="FUZJA JĄDROWA",
                    requirements="22 PB + 20K + 2 ukończone badania fizyczne",
                    director_reward="+10 PZ + wszystkie akcje kosztują -1 PA przez resztę gry",
                    member_reward="+4 PZ każdy",
                    description="Reaktor fuzji jądrowej - przełom energetyczny"
                ),
                LargeProject(
                    name="SUPERPRZEWODNIK",
                    requirements="18 PB + 25K + 2 ukończone badania fizyczne",
                    director_reward="+8 PZ + karta Superprzewodnik (stały bonus)",
                    member_reward="+3 PZ każdy",
                    description="Materiał o zerowej rezystancji w temperaturze pokojowej"
                ),
                LargeProject(
                    name="TERAPIA GENOWA",
                    requirements="15 PB + 30K + 1 profesor + 1 ukończone badanie biologiczne",
                    director_reward="+6 PZ + karta Terapia genowa (+2 PZ za artykuły biologiczne)",
                    member_reward="+2 PZ + 5K każdy",
                    description="Uniwersalna terapia genowa przeciwko nowotworom"
                ),
                LargeProject(
                    name="EKSPLORACJA MARSA",
                    requirements="20 PB + 35K + 3 ukończone badania (dowolne)",
                    director_reward="+7 PZ + dostęp do ekskluzywnego Mars Journal",
                    member_reward="+3 PZ + 1 dodatkowa karta na rundę",
                    description="Pierwsza stała baza na Marsie"
                ),
                LargeProject(
                    name="NANOMATERIAŁY",
                    requirements="16 PB + 15K + 2 ukończone badania chemiczne + 1 ukończone badanie fizyczne",
                    director_reward="+5 PZ + wszystkie granty chemiczne dają +3K",
                    member_reward="+2 PZ + ochrona przed 1 kartą kryzysu",
                    description="Rewolucyjne nanomateriały o programowalnych właściwościach"
                )
            ]

        except FileNotFoundError as e:
            messagebox.showerror("Błąd", f"Nie można wczytać pliku: {e}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas wczytywania danych: {e}")

class PrincipiaGame:
    """Główna klasa gry Principia"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PRINCIPIA - Gra Planszowa")
        self.root.geometry("1600x1000")

        self.game_data = GameData()
        self.players = []
        self.current_player_idx = 0
        self.current_round = 1
        self.current_phase = GamePhase.GRANTY
        self.available_grants = []
        self.available_journals = []
        self.game_ended = False

        # Aktualna aktywność
        self.selected_research = None
        self.action_points = 0

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

        self.action_points_label = ttk.Label(info_row, text="PA: 0", font=('Arial', 12, 'bold'))
        self.action_points_label.pack(side='left', padx=(20, 0))

        # Kontener główny - trzech kolumn
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)

        # Panel graczy (lewa strona)
        self.players_frame = ttk.LabelFrame(content_frame, text="Gracze")
        self.players_frame.pack(side='left', fill='y', padx=(0, 5))

        # Panel głównej gry (środek)
        self.game_frame = ttk.LabelFrame(content_frame, text="Główny panel gry")
        self.game_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

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

        # Log gry
        log_frame = ttk.LabelFrame(self.control_frame, text="Log gry")
        log_frame.pack(side='right', fill='both', expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=50, height=6)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)

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
                # Przypisz losowy instytut
                if self.game_data.institutes:
                    player.institute = random.choice(self.game_data.institutes[:3])

                    # Parsuj zasoby startowe
                    resources = player.institute.starting_resources.split(', ')
                    for resource in resources:
                        if 'K' in resource:
                            player.credits = int(resource.replace('K', '').replace(' ', '')) * 1000
                        elif 'PZ' in resource:
                            player.prestige_points = int(resource.replace(' PZ', '').replace(' ', ''))

                    player.reputation = player.institute.starting_reputation

                # Daj startowe karty badań (maksymalnie 5)
                if self.game_data.research_cards:
                    player.hand_cards = random.sample(self.game_data.research_cards,
                                                    min(5, len(self.game_data.research_cards)))

                self.players.append(player)

            self.setup_players_ui()
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
            # Podświetl aktywnego gracza
            bg_color = 'lightblue' if i == self.current_player_idx else None

            player_frame = ttk.LabelFrame(self.players_frame, text=f"{player.name} ({player.color})")
            player_frame.pack(fill='x', padx=5, pady=5)

            if bg_color:
                player_frame.configure(style="Highlight.TLabelFrame")

            # Instytut
            if player.institute:
                inst_label = ttk.Label(player_frame, text=f"Instytut: {player.institute.name[:20]}...",
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
            ttk.Label(status_frame, text=f"👨‍🔬{scientists_count}").pack(side='left')

            active_research = len(player.active_research)
            completed_research = len(player.completed_research)
            ttk.Label(status_frame, text=f"🧪{active_research}/{completed_research}").pack(side='left', padx=(5, 0))

            hand_size = len(player.hand_cards)
            ttk.Label(status_frame, text=f"🃏{hand_size}").pack(side='left', padx=(5, 0))

            # Grant i akcje
            if player.current_grant:
                grant_label = ttk.Label(player_frame, text=f"Grant: {player.current_grant.name[:15]}...",
                                      font=('Arial', 8))
                grant_label.pack(anchor='w', padx=5)

            used_actions = len(player.used_actions)
            available_actions = len(player.available_actions) - used_actions
            actions_label = ttk.Label(player_frame, text=f"Akcje: {available_actions}/{len(player.available_actions)}",
                                    font=('Arial', 8))
            actions_label.pack(anchor='w', padx=5)

    def prepare_round(self):
        """Przygotowuje nową rundę"""
        # Resetuj akcje graczy
        for player in self.players:
            player.available_actions = list(ActionType)
            player.used_actions = []
            player.has_passed = False

        # Przygotuj granty na rundę
        self.available_grants = random.sample(self.game_data.grants,
                                            min(6, len(self.game_data.grants)))

        # Przygotuj czasopisma
        self.available_journals = random.sample(self.game_data.journals,
                                              min(4, len(self.game_data.journals)))

        self.current_phase = GamePhase.GRANTY
        self.current_player_idx = 0
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

            # Sprawdź czy wszyscy spasowali
            if all(p.has_passed for p in self.players):
                self.current_phase = GamePhase.PORZADKOWA
                self.pass_btn['state'] = 'disabled'
                self.log_message("Wszyscy gracze spasowali - przejście do fazy porządkowej")
            else:
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

        # Odśwież rynki (dodaj nowe karty)
        self.refresh_markets()

        self.current_round += 1
        self.prepare_round()

    def pay_salaries(self, player: Player):
        """Płaci pensje dla gracza"""
        total_salary = 0
        unpaid_scientists = []

        for scientist in player.scientists:
            if scientist.is_paid:
                total_salary += scientist.salary
            else:
                unpaid_scientists.append(scientist)

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
            # Nie może zapłacić wszystkich - kara reputacji
            if not unpaid_scientists:  # Pierwsza niewypłata
                player.reputation = max(0, player.reputation - 1)
                self.log_message(f"{player.name}: niewypłata pensji, -1 Reputacja")

            # Oznacz naukowców jako niewypłaconych
            for scientist in player.scientists:
                scientist.is_paid = False

    def check_grant_completion(self, player: Player):
        """Sprawdza czy gracz ukończył cel grantu"""
        if not player.current_grant or player.current_grant.is_completed:
            return

        # Uproszczone sprawdzenie celów grantów
        # W pełnej implementacji byłoby to bardziej szczegółowe
        goal = player.current_grant.goal.lower()

        completed = False
        if "publikacj" in goal:
            required_pubs = 2  # Domyślnie 2 publikacje
            if player.publications >= required_pubs:
                completed = True

        elif "badanie" in goal:
            if len(player.completed_research) >= 1:
                completed = True

        elif "konsorcjum" in goal:
            # Sprawdź czy założył konsorcjum (uproszczone)
            completed = False

        if completed:
            player.current_grant.is_completed = True
            # Daj nagrodę
            reward = player.current_grant.reward
            if 'K' in reward:
                credits = int(reward.split('K')[0]) * 1000
                player.credits += credits
                self.log_message(f"{player.name} ukończył grant: +{credits//1000}K")

    def refresh_markets(self):
        """Odświeża rynki kart"""
        # Usuń stare karty i dobierz nowe (uproszczone)
        self.available_journals = random.sample(self.game_data.journals,
                                              min(4, len(self.game_data.journals)))

    def update_ui(self):
        """Aktualizuje interfejs użytkownika"""
        self.round_label.config(text=f"Runda: {self.current_round}")
        self.phase_label.config(text=f"Faza: {self.current_phase.value}")
        self.action_points_label.config(text=f"PA: {self.action_points}")

        if self.players:
            current_player = self.players[self.current_player_idx]
            self.current_player_label.config(text=f"Gracz: {current_player.name}")

        self.setup_players_ui()
        self.setup_game_area()
        self.setup_research_area()

    def setup_game_area(self):
        """Konfiguruje główny obszar gry w zależności od fazy"""
        # Wyczyść poprzedni UI
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        if self.current_phase == GamePhase.GRANTY:
            self.setup_grants_phase()
        elif self.current_phase == GamePhase.AKCJE:
            self.setup_actions_phase()
        elif self.current_phase == GamePhase.PORZADKOWA:
            self.setup_cleanup_phase()

    def setup_grants_phase(self):
        """Konfiguruje interfejs fazy grantów"""
        ttk.Label(self.game_frame, text="Dostępne Granty", font=('Arial', 14, 'bold')).pack(pady=10)

        # Scroll frame dla grantów
        canvas = tk.Canvas(self.game_frame)
        scrollbar = ttk.Scrollbar(self.game_frame, orient="vertical", command=canvas.yview)
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

            ttk.Label(grant_frame, text=f"Wymagania: {grant.requirements}").pack(anchor='w', padx=5)
            ttk.Label(grant_frame, text=f"Cel: {grant.goal}").pack(anchor='w', padx=5)
            ttk.Label(grant_frame, text=f"Nagroda: {grant.reward}").pack(anchor='w', padx=5)

            take_btn = ttk.Button(grant_frame, text="Weź grant",
                                 command=lambda g=grant: self.take_grant(g))
            take_btn.pack(anchor='e', padx=5, pady=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_actions_phase(self):
        """Konfiguruje interfejs fazy akcji"""
        ttk.Label(self.game_frame, text="Karty Akcji", font=('Arial', 14, 'bold')).pack(pady=10)

        current_player = self.players[self.current_player_idx]

        # Pokaż dostępne akcje
        for action in ActionType:
            if action in current_player.used_actions:
                continue  # Pomiń już użyte akcje

            action_frame = ttk.LabelFrame(self.game_frame, text=action.value)
            action_frame.pack(fill='x', padx=10, pady=5)

            # Opis akcji
            action_desc = self.get_action_description(action)
            ttk.Label(action_frame, text=action_desc, wraplength=600).pack(anchor='w', padx=5, pady=2)

            play_btn = ttk.Button(action_frame, text="Zagraj kartę",
                                 command=lambda a=action: self.play_action(a))
            play_btn.pack(anchor='e', padx=5, pady=5)

        # Wielkie Projekty
        projects_frame = ttk.LabelFrame(self.game_frame, text="Wielkie Projekty")
        projects_frame.pack(fill='x', padx=10, pady=10)

        for project in self.game_data.large_projects:
            if project.is_completed:
                continue

            proj_frame = ttk.Frame(projects_frame)
            proj_frame.pack(fill='x', padx=5, pady=2)

            ttk.Label(proj_frame, text=f"{project.name}: {project.requirements}",
                     font=('Arial', 10, 'bold')).pack(side='left')

            if project.director:
                ttk.Label(proj_frame, text=f"Kierownik: {project.director.name}").pack(side='left', padx=(10, 0))

            join_btn = ttk.Button(proj_frame, text="Dołącz/Załóż",
                                 command=lambda p=project: self.join_project(p))
            join_btn.pack(side='right')

    def setup_cleanup_phase(self):
        """Konfiguruje interfejs fazy porządkowej"""
        ttk.Label(self.game_frame, text="Faza Porządkowa", font=('Arial', 14, 'bold')).pack(pady=20)

        cleanup_info = """
        Faza porządkowa:
        1. Wypłata pensji
        2. Sprawdzenie celów grantów
        3. Odświeżenie rynków
        4. Odzyskanie kart akcji
        5. Sprawdzenie końca gry
        """

        ttk.Label(self.game_frame, text=cleanup_info, justify='left').pack(pady=20)

        # Pokaż wyniki rundy
        results_frame = ttk.LabelFrame(self.game_frame, text="Wyniki rundy")
        results_frame.pack(fill='x', padx=20, pady=10)

        for player in self.players:
            player_result = f"{player.name}: {player.prestige_points} PZ, {player.credits//1000}K"
            ttk.Label(results_frame, text=player_result).pack(anchor='w', padx=10, pady=2)

    def setup_research_area(self):
        """Konfiguruje obszar badań"""
        # Wyczyść poprzedni UI
        for widget in self.research_frame.winfo_children():
            widget.destroy()

        if self.current_phase != GamePhase.AKCJE:
            return

        current_player = self.players[self.current_player_idx]

        # Karty na ręku
        hand_frame = ttk.LabelFrame(self.research_frame, text="Karty na ręku")
        hand_frame.pack(fill='x', padx=5, pady=5)

        for card in current_player.hand_cards:
            card_btn = ttk.Button(hand_frame, text=card.name,
                                 command=lambda c=card: self.start_research(c))
            card_btn.pack(fill='x', padx=2, pady=1)

        # Aktywne badania
        if current_player.active_research:
            active_frame = ttk.LabelFrame(self.research_frame, text="Aktywne badania")
            active_frame.pack(fill='both', expand=True, padx=5, pady=5)

            for research in current_player.active_research:
                research_frame = ttk.Frame(active_frame)
                research_frame.pack(fill='x', padx=2, pady=2)

                ttk.Label(research_frame, text=research.name, font=('Arial', 10, 'bold')).pack(anchor='w')

                # Hex map widget
                if research.hex_research_map:
                    hex_widget = HexMapWidget(research_frame, research.hex_research_map,
                                            width=300, height=200)
                    hex_widget.pack(fill='both', expand=True)

                    def on_hex_click(pos, res=research):
                        self.place_hex_on_research(res, pos)

                    hex_widget.on_hex_click_callback = on_hex_click

    def get_action_description(self, action: ActionType) -> str:
        """Zwraca opis akcji"""
        descriptions = {
            ActionType.PROWADZ_BADANIA: "🔹 Aktywuj doktoranta (+1 heks) | ⚡ Aktywuj doktora (+2 heks, 2PA) | ⚡ Aktywuj profesora (+3 heks, 2PA) | ⚡ Rozpocznij badanie (1PA)",
            ActionType.ZATRUDNIJ: "🔹 Weź 1K | ⚡ Zatrudnij doktora (2PA) | ⚡ Zatrudnij profesora (3PA) | ⚡ Zatrudnij doktoranta (1PA) | ⚡ Kup kartę badań (1PA)",
            ActionType.PUBLIKUJ: "🔹 Opublikuj artykuł | ⚡ Weź 3K (1PA) | ⚡ Kup kartę możliwości (1PA) | ⚡ Konsultacje komercyjne (1PA)",
            ActionType.FINANSUJ: "🔹 Weź 2K | ⚡ Wpłać do konsorcjum (1PA za zasób) | ⚡ Załóż konsorcjum (1PA) | ⚡ Kredyt awaryjny +5K, -1 Rep (2PA)",
            ActionType.ZARZADZAJ: "🔹 Weź 2K | ⚡ Odśwież rynek (2PA) | ⚡ Kampania PR: 4K → +1 Rep (1PA) | ⚡ Poprawa wizerunku: 2PB → +1 Rep (1PA)"
        }
        return descriptions.get(action, "Brak opisu")

    def take_grant(self, grant: GrantCard):
        """Gracz bierze grant"""
        current_player = self.players[self.current_player_idx]

        if current_player.current_grant is None:
            current_player.current_grant = grant
            self.available_grants.remove(grant)
            self.log_message(f"{current_player.name} wziął grant: {grant.name}")

            # Przejdź do następnego gracza
            self.next_player()
            self.update_ui()
        else:
            messagebox.showwarning("Uwaga", "Masz już grant w tej rundzie!")

    def play_action(self, action: ActionType):
        """Gracz gra kartę akcji"""
        current_player = self.players[self.current_player_idx]

        if action in current_player.used_actions:
            messagebox.showwarning("Uwaga", "Ta karta akcji została już użyta w tej rundzie!")
            return

        # Oznacz akcję jako użytą
        current_player.used_actions.append(action)

        # Daj punkty akcji
        action_points = {
            ActionType.PROWADZ_BADANIA: 3,
            ActionType.ZATRUDNIJ: 3,
            ActionType.PUBLIKUJ: 2,
            ActionType.FINANSUJ: 3,
            ActionType.ZARZADZAJ: 2
        }.get(action, 3)

        self.action_points = action_points

        # Wykonaj akcję podstawową
        if action == ActionType.PROWADZ_BADANIA:
            # Aktywuj doktoranta (jeśli jest)
            doktoranci = [s for s in current_player.scientists if s.type == ScientistType.DOKTORANT]
            if doktoranci and doktoranci[0].is_paid:
                self.add_hex_to_research(current_player, 1)
                self.log_message(f"{current_player.name} aktywował doktoranta (+1 heks)")
            else:
                self.log_message(f"{current_player.name} nie ma aktywnego doktoranta")

        elif action == ActionType.ZATRUDNIJ:
            current_player.credits += 1000
            self.log_message(f"{current_player.name} otrzymał 1K")

        elif action == ActionType.PUBLIKUJ:
            if current_player.research_points >= 2:  # Przykładowy koszt publikacji
                current_player.research_points -= 2
                current_player.publications += 1
                current_player.prestige_points += 2
                self.log_message(f"{current_player.name} opublikował artykuł (+2 PZ)")
            else:
                self.log_message(f"{current_player.name} nie ma wystarczająco PB do publikacji")

        elif action == ActionType.FINANSUJ:
            current_player.credits += 2000
            self.log_message(f"{current_player.name} otrzymał 2K")

        elif action == ActionType.ZARZADZAJ:
            current_player.credits += 2000
            self.log_message(f"{current_player.name} otrzymał 2K")

        self.setup_action_menu(action)
        self.update_ui()

    def setup_action_menu(self, action: ActionType):
        """Pokazuje menu dodatkowych akcji"""
        if self.action_points <= 0:
            self.next_player()
            return

        # Stwórz popup z dodatkowymi akcjami
        popup = tk.Toplevel(self.root)
        popup.title(f"Dodatkowe akcje - {action.value}")
        popup.geometry("400x300")

        ttk.Label(popup, text=f"Punkty akcji: {self.action_points}", font=('Arial', 12, 'bold')).pack(pady=10)

        current_player = self.players[self.current_player_idx]

        if action == ActionType.PROWADZ_BADANIA:
            self.create_research_actions(popup, current_player)
        elif action == ActionType.ZATRUDNIJ:
            self.create_hiring_actions(popup, current_player)
        elif action == ActionType.PUBLIKUJ:
            self.create_publishing_actions(popup, current_player)
        elif action == ActionType.FINANSUJ:
            self.create_funding_actions(popup, current_player)
        elif action == ActionType.ZARZADZAJ:
            self.create_management_actions(popup, current_player)

        ttk.Button(popup, text="Zakończ", command=lambda: self.finish_action(popup)).pack(pady=10)

    def create_research_actions(self, popup, player):
        """Tworzy akcje badawcze"""
        ttk.Label(popup, text="Akcje badawcze:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10)

        # Aktywuj doktora
        doctors = [s for s in player.scientists if s.type == ScientistType.DOKTOR and s.is_paid]
        if doctors and self.action_points >= 2:
            btn = ttk.Button(popup, text="Aktywuj doktora (+2 heks, 2PA)",
                           command=lambda: self.use_scientist(ScientistType.DOKTOR, 2, 2))
            btn.pack(fill='x', padx=10, pady=2)

        # Aktywuj profesora
        professors = [s for s in player.scientists if s.type == ScientistType.PROFESOR and s.is_paid]
        if professors and self.action_points >= 2:
            btn = ttk.Button(popup, text="Aktywuj profesora (+3 heks, 2PA)",
                           command=lambda: self.use_scientist(ScientistType.PROFESOR, 3, 2))
            btn.pack(fill='x', padx=10, pady=2)

        # Rozpocznij badanie
        if player.hand_cards and self.action_points >= 1:
            btn = ttk.Button(popup, text="Rozpocznij nowe badanie (1PA)",
                           command=lambda: self.start_new_research(1))
            btn.pack(fill='x', padx=10, pady=2)

    def create_hiring_actions(self, popup, player):
        """Tworzy akcje zatrudniania"""
        ttk.Label(popup, text="Akcje zatrudniania:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10)

        if self.action_points >= 2:
            btn = ttk.Button(popup, text="Zatrudnij doktora (2PA)",
                           command=lambda: self.hire_scientist(ScientistType.DOKTOR, 2))
            btn.pack(fill='x', padx=10, pady=2)

        if self.action_points >= 3:
            btn = ttk.Button(popup, text="Zatrudnij profesora (3PA)",
                           command=lambda: self.hire_scientist(ScientistType.PROFESOR, 3))
            btn.pack(fill='x', padx=10, pady=2)

        if self.action_points >= 1:
            btn = ttk.Button(popup, text="Zatrudnij doktoranta (1PA)",
                           command=lambda: self.hire_scientist(ScientistType.DOKTORANT, 1))
            btn.pack(fill='x', padx=10, pady=2)

    def create_publishing_actions(self, popup, player):
        """Tworzy akcje publikowania"""
        ttk.Label(popup, text="Akcje publikowania:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10)

        if self.action_points >= 1:
            btn = ttk.Button(popup, text="Weź 3K (1PA)",
                           command=lambda: self.take_credits(3000, 1))
            btn.pack(fill='x', padx=10, pady=2)

            btn2 = ttk.Button(popup, text="Kup kartę możliwości (1PA)",
                            command=lambda: self.buy_opportunity_card(1))
            btn2.pack(fill='x', padx=10, pady=2)

            # Konsultacje komercyjne
            professors = [s for s in player.scientists if s.type == ScientistType.PROFESOR and s.is_paid]
            if professors:
                btn3 = ttk.Button(popup, text="Konsultacje komercyjne (+4K, 1PA)",
                                command=lambda: self.commercial_consulting(1))
                btn3.pack(fill='x', padx=10, pady=2)

    def create_funding_actions(self, popup, player):
        """Tworzy akcje finansowania"""
        ttk.Label(popup, text="Akcje finansowania:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10)

        if self.action_points >= 1:
            btn = ttk.Button(popup, text="Wpłać do konsorcjum (1PA za zasób)",
                           command=lambda: self.contribute_to_consortium(1))
            btn.pack(fill='x', padx=10, pady=2)

            btn2 = ttk.Button(popup, text="Załóż konsorcjum (1PA)",
                            command=lambda: self.start_consortium(1))
            btn2.pack(fill='x', padx=10, pady=2)

        if self.action_points >= 2:
            btn3 = ttk.Button(popup, text="Kredyt awaryjny (+5K, -1 Rep, 2PA)",
                            command=lambda: self.emergency_credit(2))
            btn3.pack(fill='x', padx=10, pady=2)

    def create_management_actions(self, popup, player):
        """Tworzy akcje zarządzania"""
        ttk.Label(popup, text="Akcje zarządzania:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10)

        if self.action_points >= 2:
            btn = ttk.Button(popup, text="Odśwież rynek (2PA)",
                           command=lambda: self.refresh_market(2))
            btn.pack(fill='x', padx=10, pady=2)

        if self.action_points >= 1 and player.credits >= 4000:
            btn2 = ttk.Button(popup, text="Kampania PR (4K → +1 Rep, 1PA)",
                            command=lambda: self.pr_campaign(1))
            btn2.pack(fill='x', padx=10, pady=2)

        if self.action_points >= 1 and player.research_points >= 2:
            btn3 = ttk.Button(popup, text="Poprawa wizerunku (2PB → +1 Rep, 1PA)",
                            command=lambda: self.improve_reputation(1))
            btn3.pack(fill='x', padx=10, pady=2)

    def use_scientist(self, scientist_type: ScientistType, hexes: int, cost: int):
        """Używa naukowca do badań"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]
            scientists = [s for s in current_player.scientists
                         if s.type == scientist_type and s.is_paid]

            if scientists:
                self.action_points -= cost
                self.add_hex_to_research(current_player, hexes)
                self.log_message(f"{current_player.name} aktywował {scientist_type.value} (+{hexes} heks)")
                self.update_ui()

    def add_hex_to_research(self, player: Player, hex_count: int):
        """Dodaje heksy do aktywnych badań gracza"""
        if not player.active_research:
            messagebox.showinfo("Info", "Brak aktywnych badań. Najpierw rozpocznij badanie.")
            return

        # Dla uproszczenia, dodaj heksy do pierwszego aktywnego badania
        research = player.active_research[0]
        player.hex_tokens = max(0, player.hex_tokens - hex_count)

        # W rzeczywistej implementacji gracz wybierałby które heksy położyć
        # Tutaj symulujemy automatyczne układanie
        for _ in range(hex_count):
            if research.hex_research_map and research.hex_research_map.start_position:
                # Znajduje następną możliwą pozycję
                next_pos = self.find_next_hex_position(research)
                if next_pos:
                    result = research.hex_research_map.place_hex(next_pos, player.color, research.player_path)
                    if result['success']:
                        if result['bonus']:
                            self.apply_hex_bonus(player, result['bonus'])
                        if result['completed']:
                            self.complete_research(player, research)
                            break

    def find_next_hex_position(self, research: ResearchCard) -> Optional[HexPosition]:
        """Znajduje następną możliwą pozycję dla heksa"""
        if not research.player_path and research.hex_research_map.start_position:
            return research.hex_research_map.start_position

        # Znajdź pierwszą dostępną pozycję sąsiadującą ze ścieżką
        for pos in research.hex_research_map.tiles.keys():
            if research.hex_research_map.can_place_hex(pos, research.player_path):
                return pos
        return None

    def apply_hex_bonus(self, player: Player, bonus: str):
        """Aplikuje bonus z heksa"""
        if "+1PB" in bonus:
            player.research_points += 1
        elif "+2PB" in bonus:
            player.research_points += 2
        elif "+1PZ" in bonus:
            player.prestige_points += 1
        elif "+2PZ" in bonus:
            player.prestige_points += 2
        elif "+1K" in bonus:
            player.credits += 1000
        elif "+2K" in bonus:
            player.credits += 2000

        self.log_message(f"{player.name} otrzymał bonus: {bonus}")

    def complete_research(self, player: Player, research: ResearchCard):
        """Kończy badanie"""
        research.is_completed = True
        player.active_research.remove(research)
        player.completed_research.append(research)

        # Odzyskaj heksy
        player.hex_tokens = 20

        # Daj nagrodę podstawową
        self.apply_research_reward(player, research.basic_reward)

        self.log_message(f"{player.name} ukończył badanie: {research.name}")

    def apply_research_reward(self, player: Player, reward: str):
        """Aplikuje nagrodę za ukończone badanie"""
        parts = reward.split(', ')
        for part in parts:
            if 'PB' in part:
                pb = int(part.split(' ')[0])
                player.research_points += pb
            elif 'PZ' in part:
                pz = int(part.split(' ')[0])
                player.prestige_points += pz

    def start_new_research(self, cost: int):
        """Rozpoczyna nowe badanie"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]
            if current_player.hand_cards:
                # Pokaż wybór kart
                self.show_card_selection(current_player, cost)

    def show_card_selection(self, player: Player, cost: int):
        """Pokazuje wybór kart do rozpoczęcia badania"""
        popup = tk.Toplevel(self.root)
        popup.title("Wybierz kartę badania")
        popup.geometry("400x300")

        ttk.Label(popup, text="Wybierz kartę do rozpoczęcia badania:",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        for card in player.hand_cards:
            btn = ttk.Button(popup, text=f"{card.name} ({card.field})",
                           command=lambda c=card: self.start_research_card(c, cost, popup))
            btn.pack(fill='x', padx=10, pady=2)

    def start_research_card(self, card: ResearchCard, cost: int, popup):
        """Rozpoczyna badanie wybranej karty"""
        current_player = self.players[self.current_player_idx]

        self.action_points -= cost
        current_player.hand_cards.remove(card)
        current_player.active_research.append(card)
        card.is_active = True

        self.log_message(f"{current_player.name} rozpoczął badanie: {card.name}")
        popup.destroy()
        self.update_ui()

    def start_research(self, card: ResearchCard):
        """Rozpoczyna badanie z panelu kart"""
        current_player = self.players[self.current_player_idx]
        if card in current_player.hand_cards:
            current_player.hand_cards.remove(card)
            current_player.active_research.append(card)
            card.is_active = True
            self.log_message(f"{current_player.name} rozpoczął badanie: {card.name}")
            self.update_ui()

    def place_hex_on_research(self, research: ResearchCard, position: HexPosition):
        """Umieszcza heks na badaniu w wybranej pozycji"""
        current_player = self.players[self.current_player_idx]

        if current_player.hex_tokens <= 0:
            messagebox.showwarning("Uwaga", "Brak dostępnych heksów!")
            return

        if research.hex_research_map.can_place_hex(position, research.player_path):
            result = research.hex_research_map.place_hex(position, current_player.color, research.player_path)

            if result['success']:
                current_player.hex_tokens -= 1

                if result['bonus']:
                    self.apply_hex_bonus(current_player, result['bonus'])

                if result['completed']:
                    self.complete_research(current_player, research)

                self.update_ui()
        else:
            messagebox.showwarning("Uwaga", "Nie można położyć heksa w tym miejscu!")

    def hire_scientist(self, scientist_type: ScientistType, cost: int):
        """Zatrudnia naukowca"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]

            # Znajdź dostępnego naukowca
            available = [s for s in self.game_data.scientists
                        if s.type == scientist_type and s not in current_player.scientists]

            if available:
                scientist = random.choice(available)
                current_player.scientists.append(scientist)
                self.action_points -= cost
                self.log_message(f"{current_player.name} zatrudnił: {scientist.name}")
                self.update_ui()

    def take_credits(self, amount: int, cost: int):
        """Bierze kredyty"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]
            current_player.credits += amount
            self.action_points -= cost
            self.log_message(f"{current_player.name} otrzymał {amount//1000}K")
            self.update_ui()

    def buy_opportunity_card(self, cost: int):
        """Kupuje kartę możliwości"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]
            current_player.research_points += 1  # Symulacja karty możliwości
            self.action_points -= cost
            self.log_message(f"{current_player.name} kupił kartę możliwości (+1 PB)")
            self.update_ui()

    def commercial_consulting(self, cost: int):
        """Konsultacje komercyjne"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]
            professors = [s for s in current_player.scientists if s.type == ScientistType.PROFESOR and s.is_paid]

            if professors:
                current_player.credits += 4000
                self.action_points -= cost
                self.log_message(f"{current_player.name} wykonał konsultacje komercyjne (+4K)")
                self.update_ui()

    def contribute_to_consortium(self, cost: int):
        """Wpłaca do konsorcjum"""
        if self.action_points >= cost:
            # Pokaż dostępne konsorcja
            self.show_consortium_selection(cost)

    def show_consortium_selection(self, cost: int):
        """Pokazuje wybór konsorcjów"""
        popup = tk.Toplevel(self.root)
        popup.title("Wybierz konsorcjum")
        popup.geometry("500x400")

        ttk.Label(popup, text="Wybierz konsorcjum do wsparcia:",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        for project in self.game_data.large_projects:
            if project.director:  # Projekt ma kierownika
                frame = ttk.Frame(popup)
                frame.pack(fill='x', padx=10, pady=5)

                ttk.Label(frame, text=f"{project.name} - Kierownik: {project.director.name}").pack(side='left')

                btn_pb = ttk.Button(frame, text="Wpłać 1 PB",
                                   command=lambda p=project: self.contribute_pb_to_project(p, cost, popup))
                btn_pb.pack(side='right', padx=(5, 0))

                btn_credits = ttk.Button(frame, text="Wpłać 3K",
                                       command=lambda p=project: self.contribute_credits_to_project(p, cost, popup))
                btn_credits.pack(side='right')

    def contribute_pb_to_project(self, project: LargeProject, cost: int, popup):
        """Wpłaca PB do projektu"""
        current_player = self.players[self.current_player_idx]

        if current_player.research_points >= 1:
            current_player.research_points -= 1
            project.contributed_pb += 1
            self.action_points -= cost

            if current_player not in project.members:
                project.members.append(current_player)

            self.log_message(f"{current_player.name} wpłacił 1 PB do {project.name}")
            popup.destroy()
            self.update_ui()

    def contribute_credits_to_project(self, project: LargeProject, cost: int, popup):
        """Wpłaca kredyty do projektu"""
        current_player = self.players[self.current_player_idx]

        if current_player.credits >= 3000:
            current_player.credits -= 3000
            project.contributed_credits += 3000
            self.action_points -= cost

            if current_player not in project.members:
                project.members.append(current_player)

            self.log_message(f"{current_player.name} wpłacił 3K do {project.name}")
            popup.destroy()
            self.update_ui()

    def start_consortium(self, cost: int):
        """Zakłada konsorcjum"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]

            # Pokaż dostępne projekty
            available_projects = [p for p in self.game_data.large_projects if not p.director]

            if available_projects:
                self.show_project_selection(available_projects, cost)

    def show_project_selection(self, projects: List[LargeProject], cost: int):
        """Pokazuje wybór projektów do założenia"""
        popup = tk.Toplevel(self.root)
        popup.title("Załóż konsorcjum")
        popup.geometry("500x400")

        ttk.Label(popup, text="Wybierz projekt do kierowania:",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        for project in projects:
            frame = ttk.Frame(popup)
            frame.pack(fill='x', padx=10, pady=5)

            ttk.Label(frame, text=f"{project.name}: {project.requirements}").pack(side='left')

            btn = ttk.Button(frame, text="Załóż",
                           command=lambda p=project: self.found_consortium(p, cost, popup))
            btn.pack(side='right')

    def found_consortium(self, project: LargeProject, cost: int, popup):
        """Zakłada konsorcjum"""
        current_player = self.players[self.current_player_idx]

        project.director = current_player
        project.members.append(current_player)
        self.action_points -= cost

        self.log_message(f"{current_player.name} założył konsorcjum: {project.name}")
        popup.destroy()
        self.update_ui()

    def emergency_credit(self, cost: int):
        """Kredyt awaryjny"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]
            current_player.credits += 5000
            current_player.reputation = max(0, current_player.reputation - 1)
            self.action_points -= cost
            self.log_message(f"{current_player.name} wziął kredyt awaryjny (+5K, -1 Rep)")
            self.update_ui()

    def refresh_market(self, cost: int):
        """Odświeża rynek"""
        if self.action_points >= cost:
            self.refresh_markets()
            self.action_points -= cost
            self.log_message("Rynek został odświeżony")
            self.update_ui()

    def pr_campaign(self, cost: int):
        """Kampania PR"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]
            if current_player.credits >= 4000:
                current_player.credits -= 4000
                current_player.reputation = min(5, current_player.reputation + 1)
                self.action_points -= cost
                self.log_message(f"{current_player.name} przeprowadził kampanię PR (+1 Rep)")
                self.update_ui()

    def improve_reputation(self, cost: int):
        """Poprawa wizerunku"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]
            if current_player.research_points >= 2:
                current_player.research_points -= 2
                current_player.reputation = min(5, current_player.reputation + 1)
                self.action_points -= cost
                self.log_message(f"{current_player.name} poprawił wizerunek (+1 Rep)")
                self.update_ui()

    def join_project(self, project: LargeProject):
        """Dołącza do projektu lub zakłada go"""
        current_player = self.players[self.current_player_idx]

        if not project.director:
            # Załóż projekt
            project.director = current_player
            project.members.append(current_player)
            self.log_message(f"{current_player.name} założył konsorcjum: {project.name}")
        elif current_player not in project.members:
            # Dołącz do projektu
            project.members.append(current_player)
            self.log_message(f"{current_player.name} dołączył do konsorcjum: {project.name}")

        self.update_ui()

    def finish_action(self, popup):
        """Kończy akcję i przechodzi do następnego gracza"""
        popup.destroy()
        self.action_points = 0
        self.next_player()
        self.update_ui()

    def run(self):
        """Uruchamia grę"""
        self.root.mainloop()

if __name__ == "__main__":
    game = PrincipiaGame()
    game.run()