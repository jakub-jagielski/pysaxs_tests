#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System heksagonalnych badań dla gry Principia
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

@dataclass
class HexPosition:
    q: int  # Współrzędna q w systemie heksagonalnym
    r: int  # Współrzędna r w systemie heksagonalnym

    def __eq__(self, other):
        return isinstance(other, HexPosition) and self.q == other.q and self.r == other.r

    def __hash__(self):
        return hash((self.q, self.r))

@dataclass
class HexTile:
    position: HexPosition
    tile_type: str  # 'start', 'end', 'bonus', 'normal'
    bonus_reward: Optional[str] = None
    is_occupied: bool = False
    player_color: Optional[str] = None

class HexResearchMap:
    """Klasa reprezentująca mapę heksagonalną badania"""

    def __init__(self, map_string: str):
        self.tiles: Dict[HexPosition, HexTile] = {}
        self.start_position: Optional[HexPosition] = None
        self.end_position: Optional[HexPosition] = None
        self.bonus_tiles: List[HexTile] = []
        self.player_path: List[HexPosition] = []

        self.parse_map_string(map_string)

    def parse_map_string(self, map_string: str):
        """Parsuje string mapy do struktury heksagonalnej"""
        try:
            # Przykład: "START(0,0)->[(1,0)->(2,0)->(3,0)END | (1,1)->(2,1)BONUS(+2PB)]"

            # Znajdź start
            if 'START(' in map_string:
                start_part = map_string.split('START(')[1].split(')')[0]
                q, r = map(int, start_part.split(','))
                self.start_position = HexPosition(q, r)
                self.tiles[self.start_position] = HexTile(self.start_position, 'start')

            # Znajdź wszystkie pozycje w nawiasach
            positions = []
            i = 0
            while i < len(map_string):
                if map_string[i] == '(':
                    j = i + 1
                    while j < len(map_string) and map_string[j] != ')':
                        j += 1
                    if j < len(map_string):
                        coord_str = map_string[i+1:j]
                        if ',' in coord_str:
                            try:
                                q, r = map(int, coord_str.split(','))
                                positions.append(HexPosition(q, r))
                            except ValueError:
                                pass
                    i = j + 1
                else:
                    i += 1

            # Dodaj wszystkie pozycje jako zwykłe tiles
            for pos in positions:
                if pos not in self.tiles:
                    self.tiles[pos] = HexTile(pos, 'normal')

            # Znajdź end
            if 'END' in map_string:
                # Znajdź pozycję przed END
                parts = map_string.split('END')
                if len(parts) > 0:
                    before_end = parts[0]
                    # Znajdź ostatnią pozycję
                    last_pos_match = None
                    for pos in reversed(positions):
                        if f"({pos.q},{pos.r})" in before_end:
                            last_pos_match = pos
                            break

                    if last_pos_match:
                        self.end_position = last_pos_match
                        if last_pos_match in self.tiles:
                            self.tiles[last_pos_match].tile_type = 'end'

            # Znajdź bonusy
            if 'BONUS(' in map_string:
                bonus_parts = map_string.split('BONUS(')
                for i in range(1, len(bonus_parts)):
                    bonus_value = bonus_parts[i].split(')')[0]
                    # Znajdź pozycję bonusu - szukaj wstecz
                    before_bonus = bonus_parts[i-1]
                    bonus_pos = None
                    for pos in reversed(positions):
                        if f"({pos.q},{pos.r})" in before_bonus:
                            bonus_pos = pos
                            break

                    if bonus_pos and bonus_pos in self.tiles:
                        self.tiles[bonus_pos].tile_type = 'bonus'
                        self.tiles[bonus_pos].bonus_reward = bonus_value
                        self.bonus_tiles.append(self.tiles[bonus_pos])

        except Exception as e:
            print(f"Błąd parsowania mapy: {e}")
            # Stwórz prostą mapę fallback
            self.create_simple_fallback_map()

    def create_simple_fallback_map(self):
        """Tworzy prostą mapę w przypadku błędu parsowania"""
        self.start_position = HexPosition(0, 0)
        self.end_position = HexPosition(2, 0)

        self.tiles = {
            HexPosition(0, 0): HexTile(HexPosition(0, 0), 'start'),
            HexPosition(1, 0): HexTile(HexPosition(1, 0), 'normal'),
            HexPosition(2, 0): HexTile(HexPosition(2, 0), 'end'),
            HexPosition(1, 1): HexTile(HexPosition(1, 1), 'bonus', '+1PB')
        }
        self.bonus_tiles = [self.tiles[HexPosition(1, 1)]]

    def can_place_hex(self, position: HexPosition, player_path: List[HexPosition]) -> bool:
        """Sprawdza czy można położyć heks na danej pozycji"""
        if position not in self.tiles:
            return False

        if self.tiles[position].is_occupied:
            return False

        # Pierwszy heks musi być na start
        if not player_path:
            return position == self.start_position

        # Kolejne heksy muszą przylegać do już położonych
        return self.is_adjacent_to_path(position, player_path)

    def is_adjacent_to_path(self, position: HexPosition, player_path: List[HexPosition]) -> bool:
        """Sprawdza czy pozycja przylega do ścieżki gracza"""
        for path_pos in player_path:
            if self.are_adjacent(position, path_pos):
                return True
        return False

    def are_adjacent(self, pos1: HexPosition, pos2: HexPosition) -> bool:
        """Sprawdza czy dwie pozycje są sąsiednie w siatce heksagonalnej"""
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]

        for dq, dr in directions:
            if pos1.q + dq == pos2.q and pos1.r + dr == pos2.r:
                return True
        return False

    def place_hex(self, position: HexPosition, player_color: str, player_path: List[HexPosition]) -> Dict:
        """Umieszcza heks gracza na mapie"""
        result = {'success': False, 'bonus': None, 'completed': False}

        if self.can_place_hex(position, player_path):
            self.tiles[position].is_occupied = True
            self.tiles[position].player_color = player_color
            player_path.append(position)
            result['success'] = True

            # Sprawdź bonus
            if self.tiles[position].tile_type == 'bonus':
                result['bonus'] = self.tiles[position].bonus_reward

            # Sprawdź ukończenie
            if position == self.end_position:
                result['completed'] = True

        return result

    def is_completed(self, player_path: List[HexPosition]) -> bool:
        """Sprawdza czy badanie zostało ukończone"""
        return self.end_position in player_path

    def reset_player_progress(self, player_color: str):
        """Resetuje postęp gracza (po ukończeniu badania)"""
        for tile in self.tiles.values():
            if tile.player_color == player_color:
                tile.is_occupied = False
                tile.player_color = None

class HexMapWidget(tk.Frame):
    """Widget do wyświetlania i interakcji z mapą heksagonalną - responsive i skalowany"""

    def __init__(self, parent, research_map: HexResearchMap, **kwargs):
        super().__init__(parent, **kwargs)

        self.research_map = research_map
        self.base_hex_size = 30
        self.hex_size = 30
        self.scale_factor = 1.0

        # Offset do panning
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.last_pan_x = 0
        self.last_pan_y = 0
        self.is_panning = False

        # Tworzenie głównego kontenera z scrollbarami
        self.create_responsive_layout()

        self.hex_widgets = {}  # position -> canvas item id
        self.selected_position = None
        self.on_hex_click_callback = None

        self.draw_map()
        self.setup_bindings()

    def create_responsive_layout(self):
        """Tworzy responsive layout z przewijaniem i kontrolkami"""
        # Frame dla kontrolek zoom
        self.controls_frame = tk.Frame(self, bg='lightgray', height=35)
        self.controls_frame.pack(fill='x', side='top')
        self.controls_frame.pack_propagate(False)

        # Kontrolki zoom
        tk.Button(self.controls_frame, text="🔍+", command=self.zoom_in,
                 font=('Arial', 10, 'bold'), width=4).pack(side='left', padx=2, pady=2)
        tk.Button(self.controls_frame, text="🔍-", command=self.zoom_out,
                 font=('Arial', 10, 'bold'), width=4).pack(side='left', padx=2, pady=2)
        tk.Button(self.controls_frame, text="📐", command=self.fit_to_window,
                 font=('Arial', 10, 'bold'), width=4).pack(side='left', padx=2, pady=2)
        tk.Button(self.controls_frame, text="🔄", command=self.reset_view,
                 font=('Arial', 10, 'bold'), width=4).pack(side='left', padx=2, pady=2)

        # Label ze skalą
        self.scale_label = tk.Label(self.controls_frame, text="100%",
                                   font=('Arial', 8), bg='lightgray')
        self.scale_label.pack(side='right', padx=5, pady=5)

        # Container dla canvas z scrollbarami
        self.canvas_container = tk.Frame(self)
        self.canvas_container.pack(fill='both', expand=True)

        # Canvas z scrollbarami
        self.canvas = tk.Canvas(self.canvas_container, bg='white')

        # Scrollbary
        self.h_scrollbar = tk.Scrollbar(self.canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scrollbar = tk.Scrollbar(self.canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)

        # Konfiguracja scrollowania
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)

        # Grid layout dla canvas i scrollbary
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')

        # Konfiguracja grid weights
        self.canvas_container.grid_rowconfigure(0, weight=1)
        self.canvas_container.grid_columnconfigure(0, weight=1)

        # Ustaw minimalny rozmiar canvas
        self.canvas.configure(width=300, height=200)

    def setup_bindings(self):
        """Konfiguruje event bindings dla interakcji"""
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Button-2>', self.start_pan)  # Środkowy przycisk myszy
        self.canvas.bind('<B2-Motion>', self.do_pan)     # Przeciąganie środkowym przyciskiem
        self.canvas.bind('<ButtonRelease-2>', self.end_pan)
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)  # Windows
        self.canvas.bind('<Button-4>', self.on_mouse_wheel)    # Linux
        self.canvas.bind('<Button-5>', self.on_mouse_wheel)    # Linux

        # Bind dla resizing
        self.canvas.bind('<Configure>', self.on_canvas_configure)

    def zoom_in(self):
        """Powiększa mapę"""
        if self.scale_factor < 3.0:  # Maksymalny zoom
            self.scale_factor *= 1.2
            self.hex_size = self.base_hex_size * self.scale_factor
            self.update_scale_label()
            self.draw_map()
            self.update_scroll_region()

    def zoom_out(self):
        """Pomniejsza mapę"""
        if self.scale_factor > 0.3:  # Minimalny zoom
            self.scale_factor /= 1.2
            self.hex_size = self.base_hex_size * self.scale_factor
            self.update_scale_label()
            self.draw_map()
            self.update_scroll_region()

    def fit_to_window(self):
        """Dopasowuje mapę do okna"""
        # Oblicz zakres mapy
        if not self.research_map.tiles:
            return

        min_q = min(pos.q for pos in self.research_map.tiles.keys())
        max_q = max(pos.q for pos in self.research_map.tiles.keys())
        min_r = min(pos.r for pos in self.research_map.tiles.keys())
        max_r = max(pos.r for pos in self.research_map.tiles.keys())

        # Oblicz rozmiar potrzebny dla mapy
        map_width = (max_q - min_q + 1) * self.base_hex_size * 1.5
        map_height = (max_r - min_r + 1) * self.base_hex_size * math.sqrt(3)

        # Pobierz rozmiar canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width > 1 and canvas_height > 1:  # Upewnij się że canvas jest już wyrenderowany
            # Oblicz scale factor aby zmieścić mapę
            scale_x = (canvas_width - 40) / map_width  # 40px marginesu
            scale_y = (canvas_height - 40) / map_height
            self.scale_factor = min(scale_x, scale_y, 3.0)  # Nie więcej niż 3x
            self.scale_factor = max(self.scale_factor, 0.3)  # Nie mniej niż 0.3x

            self.hex_size = self.base_hex_size * self.scale_factor
            self.update_scale_label()
            self.draw_map()
            self.update_scroll_region()

            # Wycentruj mapę
            self.center_map()

    def reset_view(self):
        """Resetuje widok do domyślnych ustawień"""
        self.scale_factor = 1.0
        self.hex_size = self.base_hex_size
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.update_scale_label()
        self.draw_map()
        self.update_scroll_region()

    def update_scale_label(self):
        """Aktualizuje label ze skalą"""
        self.scale_label.config(text=f"{int(self.scale_factor * 100)}%")

    def start_pan(self, event):
        """Rozpoczyna panning"""
        self.is_panning = True
        self.last_pan_x = event.x
        self.last_pan_y = event.y

    def do_pan(self, event):
        """Wykonuje panning"""
        if self.is_panning:
            dx = event.x - self.last_pan_x
            dy = event.y - self.last_pan_y

            self.canvas.scan_dragto(event.x, event.y, gain=1)

            self.last_pan_x = event.x
            self.last_pan_y = event.y

    def end_pan(self, event):
        """Kończy panning"""
        self.is_panning = False

    def on_mouse_wheel(self, event):
        """Obsługuje zoom przez mouse wheel"""
        if event.delta > 0 or event.num == 4:  # Scroll up
            self.zoom_in()
        elif event.delta < 0 or event.num == 5:  # Scroll down
            self.zoom_out()

    def on_canvas_configure(self, event):
        """Obsługuje zmianę rozmiaru canvas"""
        self.update_scroll_region()

    def update_scroll_region(self):
        """Aktualizuje obszar przewijania"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def center_map(self):
        """Centruje mapę w canvas"""
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox('all')
        if bbox:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Oblicz offset do wycentrowania
            map_width = bbox[2] - bbox[0]
            map_height = bbox[3] - bbox[1]

            x_offset = (canvas_width - map_width) / 2
            y_offset = (canvas_height - map_height) / 2

            if x_offset > 0 or y_offset > 0:
                self.canvas.scan_mark(0, 0)
                self.canvas.scan_dragto(int(x_offset), int(y_offset), gain=1)

    def hex_to_pixel(self, position: HexPosition) -> Tuple[float, float]:
        """Konwertuje współrzędne heksagonalne na piksele"""
        size = self.hex_size
        x = size * 3/2 * position.q
        y = size * math.sqrt(3) * (position.r + position.q/2)

        # Przesunięcie do środka canvas (responsywne)
        x += 200 * self.scale_factor + self.pan_offset_x
        y += 150 * self.scale_factor + self.pan_offset_y

        return x, y

    def pixel_to_hex(self, x: float, y: float) -> HexPosition:
        """Konwertuje piksele na współrzędne heksagonalne (przybliżone)"""
        # Przesunięcie z powrotem (responsywne)
        x -= 200 * self.scale_factor + self.pan_offset_x
        y -= 150 * self.scale_factor + self.pan_offset_y

        size = self.hex_size
        q = (2/3 * x) / size
        r = (-1/3 * x + math.sqrt(3)/3 * y) / size

        return HexPosition(round(q), round(r))

    def draw_hexagon(self, center_x: float, center_y: float, size: float, fill_color: str, outline_color: str = 'black', outline_width: int = 2) -> int:
        """Rysuje heksagon i zwraca ID elementu canvas"""
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            x = center_x + size * math.cos(angle)
            y = center_y + size * math.sin(angle)
            points.extend([x, y])

        return self.canvas.create_polygon(points, fill=fill_color, outline=outline_color, width=outline_width)

    def draw_map(self):
        """Rysuje całą mapę heksagonalną"""
        self.canvas.delete('all')
        self.hex_widgets.clear()

        for position, tile in self.research_map.tiles.items():
            x, y = self.hex_to_pixel(position)

            # Wybierz kolor na podstawie typu
            if tile.tile_type == 'start':
                color = 'lightgreen'
            elif tile.tile_type == 'end':
                color = 'lightcoral'
            elif tile.tile_type == 'bonus':
                color = 'gold'
            elif tile.is_occupied:
                color = tile.player_color
            else:
                color = 'lightgray'

            # Dodaj ramkę dla zajętych heksów
            outline_color = 'black'
            outline_width = max(1, int(2 * self.scale_factor))  # Skaluj grubość ramki
            if tile.is_occupied:
                outline_color = 'darkgreen'  # Zielona ramka dla położonych heksów
                outline_width = max(2, int(4 * self.scale_factor))

            hex_id = self.draw_hexagon(x, y, self.hex_size, color, outline_color, outline_width)
            self.hex_widgets[position] = hex_id

            # Dodaj tekst (skalowany)
            text = ''
            if tile.tile_type == 'start':
                text = 'START'
            elif tile.tile_type == 'end':
                text = 'END'
            elif tile.tile_type == 'bonus':
                text = tile.bonus_reward or 'BONUS'

            if text:
                font_size = max(6, int(8 * self.scale_factor))
                self.canvas.create_text(x, y, text=text, font=('Arial', font_size, 'bold'))

            # Dodaj współrzędne (opcjonalnie, skalowane)
            coord_font_size = max(4, int(6 * self.scale_factor))
            coord_offset = max(10, int(15 * self.scale_factor))
            self.canvas.create_text(x, y + coord_offset, text=f'({position.q},{position.r})',
                                  font=('Arial', coord_font_size), fill='darkgray')

        # Aktualizuj obszar przewijania po narysowaniu
        self.after_idle(self.update_scroll_region)

    def on_canvas_click(self, event):
        """Obsługuje kliknięcie na canvas"""
        clicked_position = self.pixel_to_hex(event.x, event.y)

        # Znajdź najbliższą prawdziwą pozycję
        closest_position = None
        min_distance = float('inf')

        for position in self.research_map.tiles.keys():
            distance = abs(position.q - clicked_position.q) + abs(position.r - clicked_position.r)
            if distance < min_distance:
                min_distance = distance
                closest_position = position

        if closest_position and min_distance <= 1:  # Tolerancja kliknięcia
            self.selected_position = closest_position
            if self.on_hex_click_callback:
                self.on_hex_click_callback(closest_position)

    def highlight_hex(self, position: HexPosition, color: str = 'yellow'):
        """Podświetla wybrany heks"""
        if position in self.hex_widgets:
            self.canvas.itemconfig(self.hex_widgets[position], outline=color, width=3)

    def clear_highlights(self):
        """Usuwa wszystkie podświetlenia"""
        for hex_id in self.hex_widgets.values():
            self.canvas.itemconfig(hex_id, outline='black', width=2)

    def update_display(self):
        """Aktualizuje wyświetlanie mapy"""
        self.draw_map()
        # Auto-fit gdy po raz pierwszy ładuje się mapa
        if self.scale_factor == 1.0:
            self.after(100, self.fit_to_window)  # Delay dla pełnego renderowania

# Test widget
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test mapy heksagonalnej")

    # Stwórz przykładową mapę
    map_string = "START(0,0)->[(1,0)->(2,0)->(3,0)END | (1,1)->(2,1)BONUS(+2PB)]"
    research_map = HexResearchMap(map_string)

    # Stwórz widget
    hex_widget = HexMapWidget(root, research_map)
    hex_widget.pack(fill='both', expand=True)

    def on_hex_click(position):
        print(f"Kliknięto heks: ({position.q}, {position.r})")
        hex_widget.clear_highlights()
        hex_widget.highlight_hex(position)

    hex_widget.on_hex_click_callback = on_hex_click

    root.mainloop()