#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRINCIPIA - Gra Planszowa w Pythonie
Implementacja gry o konkurencji instytutów naukowych
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import json
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math

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
    field: str  # Fizyka, Biologia, Chemia
    salary: int
    hex_bonus: int
    special_bonus: str
    description: str
    is_paid: bool = True

@dataclass
class ResearchCard:
    name: str
    field: str
    hex_map: str  # Mapa heksagonalna w formacie tekstowym
    basic_reward: str
    bonus_reward: str
    description: str
    hexes_placed: List[Tuple[int, int]] = field(default_factory=list)
    is_completed: bool = False

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
class Player:
    name: str
    color: str
    institute: Optional[InstituteCard] = None
    credits: int = 0
    prestige_points: int = 0
    research_points: int = 0
    reputation: int = 3
    scientists: List[Scientist] = field(default_factory=list)
    research_cards: List[ResearchCard] = field(default_factory=list)
    completed_research: List[ResearchCard] = field(default_factory=list)
    hand_cards: List[ResearchCard] = field(default_factory=list)
    current_grant: Optional[GrantCard] = None
    hex_tokens: int = 20
    action_cards: List[ActionType] = field(default_factory=lambda: list(ActionType))
    publications: int = 0

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
            with open('karty_naukowcy.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    scientist_type = ScientistType.DOKTOR if row['Typ'] == 'Doktor' else ScientistType.PROFESOR
                    self.scientists.append(Scientist(
                        name=row['Imię i Nazwisko'],
                        type=scientist_type,
                        field=row['Dziedzina'],
                        salary=int(row['Pensja'].replace('K', '000')),
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

        except FileNotFoundError as e:
            messagebox.showerror("Błąd", f"Nie można wczytać pliku: {e}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas wczytywania danych: {e}")

class HexMapParser:
    """Klasa do parsowania i wyświetlania map heksagonalnych"""

    @staticmethod
    def parse_hex_map(hex_string: str) -> Dict:
        """Parsuje string mapy heksagonalnej do struktury danych"""
        # Przykład: "START(0,0)->[(1,0)->(2,0)->(3,0)END | (1,1)->(2,1)BONUS(+2PB)]"

        hex_map = {
            'start': (0, 0),
            'end': None,
            'path': [],
            'bonuses': []
        }

        try:
            # Znajdź pozycję startu
            if 'START(' in hex_string:
                start_part = hex_string.split('START(')[1].split(')')[0]
                start_coords = start_part.split(',')
                hex_map['start'] = (int(start_coords[0]), int(start_coords[1]))

            # Znajdź wszystkie pozycje END
            if 'END' in hex_string:
                # Znajdź pozycję przed END
                parts = hex_string.split('END')[0]
                # Wyciągnij ostatnią pozycję przed END
                coords = parts.split('->')[-1].replace('(', '').replace(')', '').split(',')
                if len(coords) == 2:
                    hex_map['end'] = (int(coords[0]), int(coords[1]))

            # Znajdź wszystkie bonusy
            if 'BONUS(' in hex_string:
                bonus_parts = hex_string.split('BONUS(')
                for i, part in enumerate(bonus_parts[1:], 1):
                    bonus_value = part.split(')')[0]
                    # Znajdź pozycję bonusu (przed BONUS)
                    prev_part = bonus_parts[i-1]
                    coords_match = prev_part.split('->')[-1].replace('(', '').replace(')', '').split(',')
                    if len(coords_match) == 2:
                        try:
                            bonus_pos = (int(coords_match[0]), int(coords_match[1]))
                            hex_map['bonuses'].append({
                                'position': bonus_pos,
                                'reward': bonus_value
                            })
                        except ValueError:
                            continue

        except Exception as e:
            print(f"Błąd parsowania mapy heksagonalnej: {e}")

        return hex_map

class PrincipiaGame:
    """Główna klasa gry Principia"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PRINCIPIA - Gra Planszowa")
        self.root.geometry("1400x900")

        self.game_data = GameData()
        self.players = []
        self.current_player_idx = 0
        self.current_round = 1
        self.current_phase = GamePhase.GRANTY
        self.available_grants = []
        self.available_journals = []
        self.game_ended = False

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

        # Kontener główny
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)

        # Panel graczy (lewa strona)
        self.players_frame = ttk.LabelFrame(content_frame, text="Gracze")
        self.players_frame.pack(side='left', fill='y', padx=(0, 10))

        # Panel głównej gry (środek)
        self.game_frame = ttk.LabelFrame(content_frame, text="Główny panel gry")
        self.game_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Panel kontroli (prawa strona)
        self.control_frame = ttk.LabelFrame(content_frame, text="Kontrola")
        self.control_frame.pack(side='right', fill='y')

        # Setup button
        setup_btn = ttk.Button(self.control_frame, text="Setup Gry", command=self.setup_game)
        setup_btn.pack(padx=10, pady=10)

        # Przycisk następnej fazy
        self.next_phase_btn = ttk.Button(self.control_frame, text="Następna faza",
                                        command=self.next_phase, state='disabled')
        self.next_phase_btn.pack(padx=10, pady=5)

        # Log gry
        log_frame = ttk.LabelFrame(self.control_frame, text="Log gry")
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=30, height=20)
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
                    player.institute = random.choice(self.game_data.institutes[:3])  # Weź pierwsze 3

                    # Parsuj zasoby startowe
                    resources = player.institute.starting_resources.split(', ')
                    for resource in resources:
                        if 'K' in resource:
                            player.credits = int(resource.replace('K', '000'))
                        elif 'PZ' in resource:
                            player.prestige_points = int(resource.replace(' PZ', ''))

                    player.reputation = player.institute.starting_reputation

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
            player_frame = ttk.LabelFrame(self.players_frame, text=f"{player.name} ({player.color})")
            player_frame.pack(fill='x', padx=5, pady=5)

            # Instytut
            if player.institute:
                ttk.Label(player_frame, text=f"Instytut: {player.institute.name}",
                         font=('Arial', 9, 'bold')).pack(anchor='w', padx=5)

            # Zasoby
            resources_frame = ttk.Frame(player_frame)
            resources_frame.pack(fill='x', padx=5, pady=2)

            ttk.Label(resources_frame, text=f"Kredyty: {player.credits}").pack(side='left')
            ttk.Label(resources_frame, text=f"PZ: {player.prestige_points}").pack(side='left', padx=(10, 0))
            ttk.Label(resources_frame, text=f"Rep: {player.reputation}").pack(side='left', padx=(10, 0))

            # Naukowcy
            scientists_label = ttk.Label(player_frame, text=f"Naukowcy: {len(player.scientists)}")
            scientists_label.pack(anchor='w', padx=5)

            # Badania
            research_label = ttk.Label(player_frame, text=f"Badania: {len(player.completed_research)}")
            research_label.pack(anchor='w', padx=5)

    def prepare_round(self):
        """Przygotowuje nową rundę"""
        # Przygotuj granty na rundę
        self.available_grants = random.sample(self.game_data.grants, min(6, len(self.game_data.grants)))

        # Przygotuj czasopisma
        self.available_journals = random.sample(self.game_data.journals, min(4, len(self.game_data.journals)))

        self.current_phase = GamePhase.GRANTY
        self.update_ui()
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
            total_salary = sum(s.salary for s in player.scientists if s.is_paid)
            # Dodaj karę za przeciążenie (więcej niż 3 naukowców)
            scientist_count = len([s for s in player.scientists if s.type != ScientistType.DOKTORANT])
            if scientist_count > 3:
                overload_penalty = (scientist_count - 3) * 1000
                total_salary += overload_penalty

            player.credits = max(0, player.credits - total_salary)
            self.log_message(f"{player.name} zapłacił {total_salary} pensji")

        # Sprawdź cele grantów
        for player in self.players:
            if player.current_grant and not player.current_grant.is_completed:
                # Tutaj sprawdzenie celów grantu (uproszczone)
                # W pełnej implementacji byłoby to bardziej złożone
                pass

        self.current_round += 1
        self.prepare_round()

    def update_ui(self):
        """Aktualizuje interfejs użytkownika"""
        self.round_label.config(text=f"Runda: {self.current_round}")
        self.phase_label.config(text=f"Faza: {self.current_phase.value}")

        if self.players:
            current_player = self.players[self.current_player_idx]
            self.current_player_label.config(text=f"Gracz: {current_player.name}")

        self.setup_players_ui()
        self.setup_game_area()

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

        grants_list_frame = ttk.Frame(self.game_frame)
        grants_list_frame.pack(fill='both', expand=True, padx=10)

        for i, grant in enumerate(self.available_grants):
            grant_frame = ttk.LabelFrame(grants_list_frame, text=grant.name)
            grant_frame.pack(fill='x', pady=5)

            ttk.Label(grant_frame, text=f"Wymagania: {grant.requirements}").pack(anchor='w', padx=5)
            ttk.Label(grant_frame, text=f"Cel: {grant.goal}").pack(anchor='w', padx=5)
            ttk.Label(grant_frame, text=f"Nagroda: {grant.reward}").pack(anchor='w', padx=5)

            take_btn = ttk.Button(grant_frame, text="Weź grant",
                                 command=lambda g=grant: self.take_grant(g))
            take_btn.pack(anchor='e', padx=5, pady=5)

    def setup_actions_phase(self):
        """Konfiguruje interfejs fazy akcji"""
        ttk.Label(self.game_frame, text="Karty Akcji", font=('Arial', 14, 'bold')).pack(pady=10)

        actions_frame = ttk.Frame(self.game_frame)
        actions_frame.pack(fill='both', expand=True, padx=10)

        current_player = self.players[self.current_player_idx]

        for action in ActionType:
            action_frame = ttk.LabelFrame(actions_frame, text=action.value)
            action_frame.pack(fill='x', pady=5)

            # Opis akcji
            action_desc = self.get_action_description(action)
            ttk.Label(action_frame, text=action_desc, wraplength=400).pack(anchor='w', padx=5, pady=2)

            play_btn = ttk.Button(action_frame, text="Zagraj kartę",
                                 command=lambda a=action: self.play_action(a))
            play_btn.pack(anchor='e', padx=5, pady=5)

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

    def get_action_description(self, action: ActionType) -> str:
        """Zwraca opis akcji"""
        descriptions = {
            ActionType.PROWADZ_BADANIA: "🔹 Aktywuj doktoranta (+1 heks) | ⚡ Aktywuj doktora (+2 heks, 2PA) | ⚡ Aktywuj profesora (+3 heks, 2PA) | ⚡ Rozpocznij badanie (1PA)",
            ActionType.ZATRUDNIJ: "🔹 Weź 1K | ⚡ Zatrudnij doktora (2PA) | ⚡ Zatrudnij profesora (3PA) | ⚡ Zatrudnij doktoranta (1PA)",
            ActionType.PUBLIKUJ: "🔹 Opublikuj artykuł | ⚡ Weź 3K (1PA) | ⚡ Kup kartę (1PA) | ⚡ Konsultacje (1PA)",
            ActionType.FINANSUJ: "🔹 Weź 2K | ⚡ Wpłać do konsorcjum (1PA) | ⚡ Załóż konsorcjum (1PA) | ⚡ Kredyt awaryjny (2PA)",
            ActionType.ZARZADZAJ: "🔹 Weź 2K | ⚡ Odśwież rynek (2PA) | ⚡ Kampania PR (1PA) | ⚡ Poprawa wizerunku (1PA)"
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
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            self.update_ui()
        else:
            messagebox.showwarning("Uwaga", "Masz już grant w tej rundzie!")

    def play_action(self, action: ActionType):
        """Gracz gra kartę akcji"""
        current_player = self.players[self.current_player_idx]

        # Wykonaj akcję podstawową
        if action == ActionType.PROWADZ_BADANIA:
            # Aktywuj doktoranta (jeśli jest)
            doktoranci = [s for s in current_player.scientists if s.type == ScientistType.DOKTORANT]
            if doktoranci:
                current_player.research_points += 1
                self.log_message(f"{current_player.name} aktywował doktoranta (+1 heks)")
            else:
                self.log_message(f"{current_player.name} nie ma doktoranta do aktywacji")

        elif action == ActionType.ZATRUDNIJ:
            current_player.credits += 1000
            self.log_message(f"{current_player.name} otrzymał 1K")

        elif action == ActionType.PUBLIKUJ:
            current_player.publications += 1
            current_player.prestige_points += 2  # Przykładowa nagroda
            self.log_message(f"{current_player.name} opublikował artykuł")

        elif action == ActionType.FINANSUJ:
            current_player.credits += 2000
            self.log_message(f"{current_player.name} otrzymał 2K")

        elif action == ActionType.ZARZADZAJ:
            current_player.credits += 2000
            self.log_message(f"{current_player.name} otrzymał 2K")

        # Przejdź do następnego gracza
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        self.update_ui()

    def run(self):
        """Uruchamia grę"""
        self.root.mainloop()

if __name__ == "__main__":
    game = PrincipiaGame()
    game.run()