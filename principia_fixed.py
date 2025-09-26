#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRINCIPIA - Naprawiona implementacja gry planszowej
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

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
    hexes_placed: int = 0
    max_hexes: int = 5  # Domyślnie 5 heksów do ukończenia
    is_completed: bool = False
    is_active: bool = False

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

    def safe_int_parse(self, value: str, default: int = 0) -> int:
        """Bezpiecznie parsuje int z możliwością podania domyślnej wartości"""
        try:
            if isinstance(value, str):
                # Usuń wszystkie nie-cyfry oprócz pierwszej liczby
                clean_value = ''.join(c for c in value if c.isdigit())
                return int(clean_value) if clean_value else default
            return int(value)
        except (ValueError, TypeError):
            return default

    def load_data(self):
        """Wczytuje wszystkie dane z plików CSV"""
        try:
            # Wczytaj naukowców
            try:
                with open('karty_naukowcy.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        scientist_type = ScientistType.DOKTOR if row['Typ'] == 'Doktor' else ScientistType.PROFESOR
                        salary = self.safe_int_parse(row['Pensja'].replace('K', '').replace(' ', '')) * 1000
                        self.scientists.append(Scientist(
                            name=row['Imię i Nazwisko'],
                            type=scientist_type,
                            field=row['Dziedzina'],
                            salary=salary,
                            hex_bonus=self.safe_int_parse(row['Bonus Heksów'], 2),
                            special_bonus=row['Specjalny Bonus'],
                            description=row['Opis']
                        ))
            except FileNotFoundError:
                # Stwórz przykładowych naukowców
                self.scientists = [
                    Scientist("Dr Jan Kowalski", ScientistType.DOKTOR, "Fizyka", 2000, 2, "+1PB przy publikacji", "Fizyk teoretyczny"),
                    Scientist("Prof. Anna Nowak", ScientistType.PROFESOR, "Fizyka", 3000, 3, "+2K za badanie", "Ekspert w fizyce kwantowej"),
                    Scientist("Dr Maria Wiśniewska", ScientistType.DOKTOR, "Biologia", 2000, 2, "+1PB przy publikacji", "Biolog molekularny"),
                    Scientist("Prof. Piotr Zieliński", ScientistType.PROFESOR, "Chemia", 3000, 3, "+1 heks przy badaniach", "Chemik organiczny")
                ]

            # Wczytaj karty badań
            try:
                with open('karty_badan.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.research_cards.append(ResearchCard(
                            name=row['Nazwa'],
                            field=row['Dziedzina'],
                            hex_map=row['Mapa_Heksagonalna'],
                            basic_reward=row['Nagroda_Podstawowa'],
                            bonus_reward=row['Nagroda_Dodatkowa'],
                            description=row['Opis'],
                            max_hexes=random.randint(3, 8)  # Losowa długość badania
                        ))
            except FileNotFoundError:
                # Stwórz przykładowe badania
                self.research_cards = [
                    ResearchCard("Bozon Higgsa", "Fizyka", "simple", "4 PB, 2 PZ", "Publikacja w Nature", "Poszukiwanie cząstki Boga", max_hexes=6),
                    ResearchCard("Algorytm Deep Learning", "Fizyka", "simple", "3 PB, 2 PZ", "+1K za publikację", "Sztuczna inteligencja", max_hexes=4),
                    ResearchCard("Synteza Organiczna", "Chemia", "simple", "2 PB, 3 PZ", "Dostęp do grantów", "Nowe związki chemiczne", max_hexes=5),
                    ResearchCard("Terapia Genowa", "Biologia", "simple", "5 PB, 4 PZ", "10K natychmiast", "Leczenie genów", max_hexes=7)
                ]

            # Wczytaj czasopisma
            try:
                with open('karty_czasopisma.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.journals.append(JournalCard(
                            name=row['Nazwa'],
                            impact_factor=self.safe_int_parse(row['Impact_Factor'], 5),
                            pb_cost=self.safe_int_parse(row['Koszt_PB'], 10),
                            requirements=row['Wymagania'],
                            pz_reward=self.safe_int_parse(row['Nagroda_PZ'], 3),
                            special_bonus=row['Specjalny_Bonus'],
                            description=row['Opis']
                        ))
            except FileNotFoundError:
                # Stwórz przykładowe czasopisma
                self.journals = [
                    JournalCard("Nature", 10, 15, "Reputacja 4+", 5, "Prestiż międzynarodowy", "Najlepsze czasopismo świata"),
                    JournalCard("Science", 9, 14, "Reputacja 4+", 5, "Dostęp do konferencji", "Amerykański odpowiednik Nature"),
                    JournalCard("Physical Review", 8, 12, "1 badanie fizyczne", 4, "Współpraca fizyczna", "Czasopismo fizyczne"),
                    JournalCard("Local Journal", 3, 5, "Brak", 2, "Brak", "Lokalne czasopismo")
                ]

            # Wczytaj granty
            try:
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
            except FileNotFoundError:
                # Stwórz przykładowe granty
                self.grants = [
                    GrantCard("Grant Startup", "Brak wymagań", "10 punktów aktywności", "8K", "+2K/rundę", "Grant dla początkujących"),
                    GrantCard("Grant Badawczy", "Min. 1 doktor", "2 publikacje", "12K", "+2K/rundę", "Standardowy grant badawczy"),
                    GrantCard("Grant Fizyczny", "Spec. Fizyka", "1 badanie fizyczne", "14K", "+2K/rundę", "Grant dla fizyków"),
                    GrantCard("Grant Prestiżowy", "Reputacja 4+", "Publikacja w Nature", "18K", "+2K/rundę", "Elitarny grant"),
                    GrantCard("Grant Współpracy", "Brak", "Załóż konsorcjum", "15K", "+2K/rundę", "Grant na współpracę"),
                    GrantCard("Grant Kryzysowy", "Brak", "Utrzymaj pensje", "10K", "+2K/rundę", "Grant awaryjny")
                ]

            # Wczytaj instytuty
            try:
                with open('karty_instytuty.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.institutes.append(InstituteCard(
                            name=row['Nazwa'],
                            starting_resources=row['Zasoby_Startowe'],
                            starting_reputation=self.safe_int_parse(row['Reputacja_Start'], 3),
                            specialization_bonus=row['Specjalizacja_Bonus'],
                            special_ability=row['Specjalna_Zdolność'],
                            description=row['Opis']
                        ))
            except FileNotFoundError:
                # Stwórz przykładowe instytuty
                self.institutes = [
                    InstituteCard("MIT", "8K, 2 PZ", 3, "+1 heks przy fizyce", "4. naukowiec bez kary", "Czołowa uczelnia techniczna"),
                    InstituteCard("CERN", "6K, 4 PZ", 3, "Konsorcja -1 PA", "Granty konsorcjów zawsze dostępne", "Największe lab fizyki"),
                    InstituteCard("Max Planck", "7K, 3 PZ", 3, "+1 PB za badanie", "Limit ręki +2", "Niemiecki instytut badawczy")
                ]

            # Stwórz Wielkie Projekty
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
            # Kontynuuj z przykładowymi danymi

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

                # Daj startowe karty badań (maksymalnie 5)
                if self.game_data.research_cards:
                    available_cards = self.game_data.research_cards.copy()
                    start_cards = min(5, len(available_cards))
                    player.hand_cards = random.sample(available_cards, start_cards)

                # Daj startowego doktoranta
                player.scientists.append(Scientist("Doktorant", ScientistType.DOKTORANT, "Uniwersalny", 0, 1, "Brak", "Młody naukowiec"))

                self.players.append(player)

            self.setup_players_ui()
            self.prepare_round()
            self.next_phase_btn['state'] = 'normal'
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
            ttk.Label(status_frame, text=f"👨‍🔬{scientists_count}").pack(side='left')

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

            used_actions = len(player.used_actions)
            available_actions = len(player.available_actions) - used_actions
            actions_label = ttk.Label(player_frame, text=f"⚡ {available_actions}/{len(player.available_actions)}",
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
        available_grant_count = min(6, len(self.game_data.grants))
        self.available_grants = random.sample(self.game_data.grants, available_grant_count)

        # Przygotuj czasopisma
        available_journal_count = min(4, len(self.game_data.journals))
        self.available_journals = random.sample(self.game_data.journals, available_journal_count)

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
        ttk.Label(self.game_frame, text="🎯 Dostępne Granty", font=('Arial', 14, 'bold')).pack(pady=10)

        # Scroll frame dla grantów
        canvas = tk.Canvas(self.game_frame, height=400)
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

            ttk.Label(grant_frame, text=f"📋 Wymagania: {grant.requirements}").pack(anchor='w', padx=5)
            ttk.Label(grant_frame, text=f"🎯 Cel: {grant.goal}").pack(anchor='w', padx=5)
            ttk.Label(grant_frame, text=f"💰 Nagroda: {grant.reward}").pack(anchor='w', padx=5)

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
            ttk.Label(self.game_frame, text=f"{current_player.name} spasował",
                     font=('Arial', 14, 'bold')).pack(pady=20)
            return

        ttk.Label(self.game_frame, text="⚡ Karty Akcji", font=('Arial', 14, 'bold')).pack(pady=10)

        # Pokaż dostępne akcje
        actions_frame = ttk.Frame(self.game_frame)
        actions_frame.pack(fill='both', expand=True, padx=10)

        for action in ActionType:
            if action in current_player.used_actions:
                continue  # Pomiń już użyte akcje

            action_frame = ttk.LabelFrame(actions_frame, text=action.value)
            action_frame.pack(fill='x', pady=5)

            # Opis akcji
            action_desc = self.get_action_description(action)
            ttk.Label(action_frame, text=action_desc, wraplength=600).pack(anchor='w', padx=5, pady=2)

            play_btn = ttk.Button(action_frame, text="Zagraj kartę",
                                 command=lambda a=action: self.play_action(a))
            play_btn.pack(anchor='e', padx=5, pady=5)

        # Wielkie Projekty
        projects_frame = ttk.LabelFrame(self.game_frame, text="🚀 Wielkie Projekty")
        projects_frame.pack(fill='x', padx=10, pady=10)

        for project in self.game_data.large_projects:
            if project.is_completed:
                continue

            proj_frame = ttk.Frame(projects_frame)
            proj_frame.pack(fill='x', padx=5, pady=2)

            status_text = f"{project.name}: {project.requirements}"
            if project.director:
                status_text += f" | Kierownik: {project.director.name}"
            if project.members:
                status_text += f" | Członków: {len(project.members)}"

            ttk.Label(proj_frame, text=status_text, font=('Arial', 9)).pack(side='left')

            join_btn = ttk.Button(proj_frame, text="Dołącz/Załóż",
                                 command=lambda p=project: self.join_project(p))
            join_btn.pack(side='right')

    def setup_cleanup_phase(self):
        """Konfiguruje interfejs fazy porządkowej"""
        ttk.Label(self.game_frame, text="🔧 Faza Porządkowa", font=('Arial', 14, 'bold')).pack(pady=20)

        cleanup_info = """
        Faza porządkowa:
        1. ✅ Wypłata pensji
        2. ✅ Sprawdzenie celów grantów
        3. ✅ Odświeżenie rynków
        4. ✅ Odzyskanie kart akcji
        5. ✅ Sprawdzenie końca gry
        """

        ttk.Label(self.game_frame, text=cleanup_info, justify='left', font=('Arial', 10)).pack(pady=20)

        # Pokaż wyniki rundy
        results_frame = ttk.LabelFrame(self.game_frame, text="📊 Wyniki rundy")
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

        # Karty na ręku
        hand_frame = ttk.LabelFrame(self.research_frame, text="🃏 Karty na ręku")
        hand_frame.pack(fill='x', padx=5, pady=5)

        for card in current_player.hand_cards:
            card_btn = ttk.Button(hand_frame, text=f"{card.name} ({card.field})",
                                 command=lambda c=card: self.start_research(c))
            card_btn.pack(fill='x', padx=2, pady=1)

        # Aktywne badania
        if current_player.active_research:
            active_frame = ttk.LabelFrame(self.research_frame, text="🧪 Aktywne badania")
            active_frame.pack(fill='both', expand=True, padx=5, pady=5)

            for research in current_player.active_research:
                hex_widget = SimpleHexWidget(active_frame, research)
                hex_widget.pack(fill='x', padx=2, pady=5)

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
            if current_player.research_points >= 2:
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
        popup.geometry("500x400")

        ttk.Label(popup, text=f"Punkty akcji: {self.action_points}", font=('Arial', 12, 'bold')).pack(pady=10)

        current_player = self.players[self.current_player_idx]

        # Stwórz canvas z scrollbarem
        canvas = tk.Canvas(popup)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        if action == ActionType.PROWADZ_BADANIA:
            self.create_research_actions(scrollable_frame, current_player)
        elif action == ActionType.ZATRUDNIJ:
            self.create_hiring_actions(scrollable_frame, current_player)
        elif action == ActionType.PUBLIKUJ:
            self.create_publishing_actions(scrollable_frame, current_player)
        elif action == ActionType.FINANSUJ:
            self.create_funding_actions(scrollable_frame, current_player)
        elif action == ActionType.ZARZADZAJ:
            self.create_management_actions(scrollable_frame, current_player)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(popup, text="Zakończ", command=lambda: self.finish_action(popup)).pack(pady=10)

    def create_research_actions(self, parent, player):
        """Tworzy akcje badawcze"""
        ttk.Label(parent, text="🔬 Akcje badawcze:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)

        # Aktywuj doktora
        doctors = [s for s in player.scientists if s.type == ScientistType.DOKTOR and s.is_paid]
        if doctors and self.action_points >= 2:
            btn = ttk.Button(parent, text="Aktywuj doktora (+2 heks, 2PA)",
                           command=lambda: self.use_scientist(ScientistType.DOKTOR, 2, 2))
            btn.pack(fill='x', padx=10, pady=2)

        # Aktywuj profesora
        professors = [s for s in player.scientists if s.type == ScientistType.PROFESOR and s.is_paid]
        if professors and self.action_points >= 2:
            btn = ttk.Button(parent, text="Aktywuj profesora (+3 heks, 2PA)",
                           command=lambda: self.use_scientist(ScientistType.PROFESOR, 3, 2))
            btn.pack(fill='x', padx=10, pady=2)

        # Rozpocznij badanie
        if player.hand_cards and self.action_points >= 1:
            btn = ttk.Button(parent, text="Rozpocznij nowe badanie (1PA)",
                           command=lambda: self.start_new_research(1))
            btn.pack(fill='x', padx=10, pady=2)

    def create_hiring_actions(self, parent, player):
        """Tworzy akcje zatrudniania"""
        ttk.Label(parent, text="👨‍🔬 Akcje zatrudniania:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)

        if self.action_points >= 2 and player.credits >= 2000:
            btn = ttk.Button(parent, text="Zatrudnij doktora (2PA, pensja 2K/rundę)",
                           command=lambda: self.hire_scientist(ScientistType.DOKTOR, 2))
            btn.pack(fill='x', padx=10, pady=2)

        if self.action_points >= 3 and player.credits >= 3000:
            btn = ttk.Button(parent, text="Zatrudnij profesora (3PA, pensja 3K/rundę)",
                           command=lambda: self.hire_scientist(ScientistType.PROFESOR, 3))
            btn.pack(fill='x', padx=10, pady=2)

        if self.action_points >= 1:
            btn = ttk.Button(parent, text="Zatrudnij doktoranta (1PA, bez pensji)",
                           command=lambda: self.hire_scientist(ScientistType.DOKTORANT, 1))
            btn.pack(fill='x', padx=10, pady=2)

        if self.action_points >= 1 and player.research_points >= 2:
            btn = ttk.Button(parent, text="Kup kartę badań (1PA, 2PB)",
                           command=lambda: self.buy_research_card(1))
            btn.pack(fill='x', padx=10, pady=2)

    def create_publishing_actions(self, parent, player):
        """Tworzy akcje publikowania"""
        ttk.Label(parent, text="📄 Akcje publikowania:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)

        if self.action_points >= 1:
            btn = ttk.Button(parent, text="Weź 3K (1PA)",
                           command=lambda: self.take_credits(3000, 1))
            btn.pack(fill='x', padx=10, pady=2)

            btn2 = ttk.Button(parent, text="Kup kartę możliwości (+1PB, 1PA)",
                            command=lambda: self.buy_opportunity_card(1))
            btn2.pack(fill='x', padx=10, pady=2)

        # Konsultacje komercyjne
        professors = [s for s in player.scientists if s.type == ScientistType.PROFESOR and s.is_paid]
        if professors and self.action_points >= 1:
            btn3 = ttk.Button(parent, text="Konsultacje komercyjne (+4K, 1PA)",
                            command=lambda: self.commercial_consulting(1))
            btn3.pack(fill='x', padx=10, pady=2)

        # Publikuj w czasopiśmie
        if self.action_points >= 1:
            for journal in self.available_journals:
                if player.research_points >= journal.pb_cost:
                    btn_pub = ttk.Button(parent, text=f"Publikuj w {journal.name} ({journal.pb_cost}PB → {journal.pz_reward}PZ, 1PA)",
                                       command=lambda j=journal: self.publish_in_journal(j, 1))
                    btn_pub.pack(fill='x', padx=10, pady=2)

    def create_funding_actions(self, parent, player):
        """Tworzy akcje finansowania"""
        ttk.Label(parent, text="💰 Akcje finansowania:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)

        if self.action_points >= 1:
            btn = ttk.Button(parent, text="Wpłać do konsorcjum (1PA za zasób)",
                           command=lambda: self.contribute_to_consortium(1))
            btn.pack(fill='x', padx=10, pady=2)

            btn2 = ttk.Button(parent, text="Załóż konsorcjum (1PA)",
                            command=lambda: self.start_consortium(1))
            btn2.pack(fill='x', padx=10, pady=2)

        if self.action_points >= 2:
            btn3 = ttk.Button(parent, text="Kredyt awaryjny (+5K, -1 Rep, 2PA)",
                            command=lambda: self.emergency_credit(2))
            btn3.pack(fill='x', padx=10, pady=2)

    def create_management_actions(self, parent, player):
        """Tworzy akcje zarządzania"""
        ttk.Label(parent, text="🏢 Akcje zarządzania:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)

        if self.action_points >= 2:
            btn = ttk.Button(parent, text="Odśwież rynek (2PA)",
                           command=lambda: self.refresh_market(2))
            btn.pack(fill='x', padx=10, pady=2)

        if self.action_points >= 1 and player.credits >= 4000:
            btn2 = ttk.Button(parent, text="Kampania PR (4K → +1 Rep, 1PA)",
                            command=lambda: self.pr_campaign(1))
            btn2.pack(fill='x', padx=10, pady=2)

        if self.action_points >= 1 and player.research_points >= 2:
            btn3 = ttk.Button(parent, text="Poprawa wizerunku (2PB → +1 Rep, 1PA)",
                            command=lambda: self.improve_reputation(1))
            btn3.pack(fill='x', padx=10, pady=2)

    def add_hex_to_research(self, player: Player, hex_count: int):
        """Dodaje heksy do aktywnych badań gracza"""
        if not player.active_research:
            messagebox.showinfo("Info", "Brak aktywnych badań. Najpierw rozpocznij badanie.")
            return

        # Dla uproszczenia, dodaj heksy do pierwszego aktywnego badania
        research = player.active_research[0]

        if player.hex_tokens >= hex_count:
            player.hex_tokens -= hex_count
            research.hexes_placed += hex_count

            # Sprawdź czy badanie zostało ukończone
            if research.hexes_placed >= research.max_hexes:
                self.complete_research(player, research)

            self.log_message(f"{player.name} dodał {hex_count} heks do {research.name}")
        else:
            messagebox.showwarning("Uwaga", "Brak wystarczającej liczby heksów!")

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
            part = part.strip()
            if 'PB' in part:
                pb = self.game_data.safe_int_parse(part.split(' ')[0], 0)
                player.research_points += pb
            elif 'PZ' in part:
                pz = self.game_data.safe_int_parse(part.split(' ')[0], 0)
                player.prestige_points += pz

    def start_research(self, card: ResearchCard):
        """Rozpoczyna badanie z panelu kart"""
        current_player = self.players[self.current_player_idx]
        if card in current_player.hand_cards:
            current_player.hand_cards.remove(card)
            current_player.active_research.append(card)
            card.is_active = True
            self.log_message(f"{current_player.name} rozpoczął badanie: {card.name}")
            self.update_ui()

    def start_new_research(self, cost: int):
        """Rozpoczyna nowe badanie za punkty akcji"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]
            if current_player.hand_cards:
                # Weź pierwszą kartę z ręki
                card = current_player.hand_cards[0]
                self.start_research(card)
                self.action_points -= cost

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

    def hire_scientist(self, scientist_type: ScientistType, cost: int):
        """Zatrudnia naukowca"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]

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
            self.action_points -= cost
            self.log_message(f"{current_player.name} zatrudnił: {new_scientist.name}")
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
            current_player.research_points += 1
            self.action_points -= cost
            self.log_message(f"{current_player.name} kupił kartę możliwości (+1 PB)")
            self.update_ui()

    def buy_research_card(self, cost: int):
        """Kupuje kartę badań"""
        if self.action_points >= cost and self.players[self.current_player_idx].research_points >= 2:
            current_player = self.players[self.current_player_idx]
            current_player.research_points -= 2

            # Dodaj losową kartę badań
            if self.game_data.research_cards:
                available_cards = [c for c in self.game_data.research_cards if c not in current_player.hand_cards]
                if available_cards:
                    new_card = random.choice(available_cards)
                    # Stwórz kopię karty
                    card_copy = ResearchCard(
                        name=new_card.name,
                        field=new_card.field,
                        hex_map=new_card.hex_map,
                        basic_reward=new_card.basic_reward,
                        bonus_reward=new_card.bonus_reward,
                        description=new_card.description,
                        max_hexes=new_card.max_hexes
                    )
                    current_player.hand_cards.append(card_copy)

            self.action_points -= cost
            self.log_message(f"{current_player.name} kupił kartę badań")
            self.update_ui()

    def publish_in_journal(self, journal: JournalCard, cost: int):
        """Publikuje w czasopiśmie"""
        if self.action_points >= cost:
            current_player = self.players[self.current_player_idx]
            if current_player.research_points >= journal.pb_cost:
                current_player.research_points -= journal.pb_cost
                current_player.prestige_points += journal.pz_reward
                current_player.publications += 1
                self.action_points -= cost

                # Bonus za prestiżowe czasopisma
                if journal.impact_factor >= 8:
                    current_player.reputation = min(5, current_player.reputation + 1)
                    self.log_message(f"{current_player.name} opublikował w {journal.name} (+{journal.pz_reward} PZ, +1 Rep)")
                else:
                    self.log_message(f"{current_player.name} opublikował w {journal.name} (+{journal.pz_reward} PZ)")

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
            # Znajdź konsorcja do wsparcia
            available_consortiums = [p for p in self.game_data.large_projects if p.director and not p.is_completed]

            if available_consortiums:
                self.show_consortium_selection(available_consortiums, cost)

    def show_consortium_selection(self, projects: List[LargeProject], cost: int):
        """Pokazuje wybór konsorcjów"""
        popup = tk.Toplevel(self.root)
        popup.title("Wybierz konsorcjum")
        popup.geometry("600x400")

        ttk.Label(popup, text="Wybierz konsorcjum do wsparcia:", font=('Arial', 12, 'bold')).pack(pady=10)

        for project in projects:
            frame = ttk.Frame(popup)
            frame.pack(fill='x', padx=10, pady=5)

            ttk.Label(frame, text=f"{project.name} - Kierownik: {project.director.name}").pack(side='left')

            current_player = self.players[self.current_player_idx]

            if current_player.research_points >= 1:
                btn_pb = ttk.Button(frame, text="Wpłać 1 PB",
                                   command=lambda p=project: self.contribute_pb_to_project(p, cost, popup))
                btn_pb.pack(side='right', padx=(5, 0))

            if current_player.credits >= 3000:
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

            # Znajdź dostępne projekty
            available_projects = [p for p in self.game_data.large_projects if not p.director]

            if available_projects:
                self.show_project_selection(available_projects, cost)

    def show_project_selection(self, projects: List[LargeProject], cost: int):
        """Pokazuje wybór projektów do założenia"""
        popup = tk.Toplevel(self.root)
        popup.title("Załóż konsorcjum")
        popup.geometry("600x400")

        ttk.Label(popup, text="Wybierz projekt do kierowania:", font=('Arial', 12, 'bold')).pack(pady=10)

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
            # Odśwież czasopisma
            available_journal_count = min(4, len(self.game_data.journals))
            self.available_journals = random.sample(self.game_data.journals, available_journal_count)

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
    try:
        game = PrincipiaGame()
        game.run()
    except Exception as e:
        print(f"Błąd uruchomienia gry: {e}")
        import traceback
        traceback.print_exc()