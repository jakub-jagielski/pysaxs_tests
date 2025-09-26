#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator kart dla gry Principia
Tworzy obrazy PNG kart na podstawie plików CSV
"""

import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
from pathlib import Path
import math
import re

# Wymiary kart (w pikselach, 300 DPI)
CARD_WIDTH_STANDARD = 750  # 2.5 inch * 300 DPI
CARD_HEIGHT_STANDARD = 1050  # 3.5 inch * 300 DPI
CARD_WIDTH_INSTITUTE = 1050  # 3.5 inch * 300 DPI (poziomo)
CARD_HEIGHT_INSTITUTE = 750  # 2.5 inch * 300 DPI (poziomo)

# Kolory
COLOR_BACKGROUND = (240, 240, 240)
COLOR_TEXT = (20, 20, 20)
COLOR_HEADER = (60, 90, 150)
COLOR_BORDER = (100, 100, 100)

# Dziedziny naukowe - kolory tematyczne
DOMAIN_COLORS = {
    'Fizyka': (70, 130, 220),
    'Biologia': (80, 170, 80),
    'Chemia': (220, 120, 50)
}

def setup_fonts():
    """Konfiguruje fonty - używa domyślnych jeśli nie ma dostępu do specjalnych"""
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_header = ImageFont.truetype("arial.ttf", 28)
        font_text = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 20)
        font_tiny = ImageFont.truetype("arial.ttf", 16)
    except:
        # Fallback na domyślny font
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_tiny = ImageFont.load_default()
    
    return font_title, font_header, font_text, font_small, font_tiny

def create_card_background(width, height, domain=None):
    """Tworzy tło karty z ramką"""
    img = Image.new('RGB', (width, height), COLOR_BACKGROUND)
    draw = ImageDraw.Draw(img)
    
    # Ramka zewnętrzna
    draw.rectangle([0, 0, width-1, height-1], outline=COLOR_BORDER, width=8)
    
    # Kolorowy pasek dziedziny (jeśli podana)
    if domain and domain in DOMAIN_COLORS:
        color = DOMAIN_COLORS[domain]
        draw.rectangle([10, 10, width-10, 60], fill=color)
    
    return img, draw

def wrap_text(text, font, max_width):
    """Łamie tekst do określonej szerokości"""
    lines = []
    words = text.split(' ')
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        if bbox[2] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def generate_scientists_cards():
    """Generuje karty naukowców"""
    print("Generowanie kart naukowców...")
    df = pd.read_csv('karty_naukowcy.csv')
    font_title, font_header, font_text, font_small, font_tiny = setup_fonts()
    
    os.makedirs('cards/naukowcy', exist_ok=True)
    
    for idx, row in df.iterrows():
        img, draw = create_card_background(CARD_WIDTH_STANDARD, CARD_HEIGHT_STANDARD, row['Dziedzina'])
        
        y = 80
        
        # Typ i dziedzina
        draw.text((20, 20), f"{row['Typ']} - {row['Dziedzina']}", fill=(255, 255, 255), font=font_small)
        
        # Imię i nazwisko
        name_lines = wrap_text(row['Imię i Nazwisko'], font_header, CARD_WIDTH_STANDARD - 40)
        for line in name_lines:
            draw.text((20, y), line, fill=COLOR_HEADER, font=font_header)
            y += 35
        
        y += 20
        
        # Pensja i bonus heksów
        draw.text((20, y), f"Pensja: {row['Pensja']}/rundę", fill=COLOR_TEXT, font=font_text)
        y += 30
        draw.text((20, y), f"Wydajność: {row['Bonus Heksów']} heksów", fill=COLOR_TEXT, font=font_text)
        y += 40
        
        # Specjalny bonus
        if pd.notna(row['Specjalny Bonus']) and row['Specjalny Bonus'].strip():
            draw.text((20, y), "SPECJALNY BONUS:", fill=COLOR_HEADER, font=font_small)
            y += 25
            bonus_lines = wrap_text(row['Specjalny Bonus'], font_small, CARD_WIDTH_STANDARD - 40)
            for line in bonus_lines:
                draw.text((20, y), line, fill=COLOR_TEXT, font=font_small)
                y += 25
            y += 20
        
        # Opis
        draw.text((20, y), "BIOGRAFIA:", fill=COLOR_HEADER, font=font_small)
        y += 25
        desc_lines = wrap_text(row['Opis'], font_small, CARD_WIDTH_STANDARD - 40)
        for line in desc_lines:
            if y < CARD_HEIGHT_STANDARD - 30:
                draw.text((20, y), line, fill=COLOR_TEXT, font=font_small)
                y += 22
        
        # Zapisz kartę
        filename = f"naukowiec_{idx+1:02d}_{row['Imię i Nazwisko'].replace(' ', '_').replace('.', '')}.png"
        img.save(f'cards/naukowcy/{filename}')
    
    print(f"Wygenerowano {len(df)} kart naukowców")

def parse_hex_map(hex_string):
    """
    Parsuje string mapy heksagonalnej - NOWA LOGIKA:
    - Tylko PIERWSZA ścieżka prowadzi do END
    - Pozostałe ścieżki z bonusami to ślepe zaułki
    Format: START(0,0)->[(1,0)->(2,0)END | (0,1)->(1,1)BONUS(+1PB)->(2,1)->(2,0)END]
    """
    all_hexes = {}
    connections = []
    
    # Znajdź start
    start_match = re.search(r'START\((\d+),(\d+)\)', hex_string)
    if not start_match:
        return [], []
    
    start_x, start_y = int(start_match.group(1)), int(start_match.group(2))
    all_hexes[(start_x, start_y)] = {'type': 'start', 'bonus': None}
    
    # Znajdź wszystkie ścieżki w nawiasach kwadratowych
    paths_match = re.search(r'\[\s*(.+)\s*\]', hex_string)
    if not paths_match:
        return [], []
    
    # Podziel na poszczególne ścieżki (oddzielone |)
    paths_text = paths_match.group(1)
    individual_paths = re.split(r'\s*\|\s*', paths_text)
    
    # NOWA LOGIKA: pierwsza ścieżka = główna (z END), reszta = ślepe zaułki
    for path_index, path in enumerate(individual_paths):
        is_main_path = (path_index == 0)  # Tylko pierwsza ścieżka prowadzi do END
        
        # Znajdź wszystkie węzły w ścieżce
        coords = re.findall(r'\((\d+),(\d+)\)', path)
        bonuses = re.findall(r'BONUS\(([^)]+)\)', path)
        bonus_idx = 0
        
        path_coords = [(start_x, start_y)]  # Zaczynamy od start
        
        for i, (x, y) in enumerate(coords):
            x, y = int(x), int(y)
            path_coords.append((x, y))
            
            # Określ typ heksa
            hex_type = 'normal'
            bonus = None
            
            # Sprawdź czy to jest heks z bonusem
            coord_pos = path.find(f'({x},{y})')
            if coord_pos != -1 and 'BONUS' in path[coord_pos:coord_pos+20]:
                hex_type = 'bonus'
                if bonus_idx < len(bonuses):
                    bonus = bonuses[bonus_idx]
                    bonus_idx += 1
            
            # NOWA LOGIKA: END tylko w pierwszej ścieżce
            if is_main_path:
                end_pattern = f'\\({x},{y}\\)(?:BONUS\\([^)]+\\))?END'
                if re.search(end_pattern, path):
                    hex_type = 'end'
            
            # Nie nadpisuj już istniejących heksów (np. START)
            if (x, y) not in all_hexes:
                all_hexes[(x, y)] = {'type': hex_type, 'bonus': bonus}
        
        # Dodaj połączenia w tej ścieżce - ALE nie dla ścieżek bonusowych prowadzących do END
        for i in range(len(path_coords) - 1):
            from_coord = path_coords[i]
            to_coord = path_coords[i + 1]
            
            # Sprawdź czy to próba połączenia ślepego zaułka z END
            if not is_main_path and to_coord in all_hexes and all_hexes[to_coord]['type'] == 'end':
                # NIE dodawaj połączenia ślepego zaułka z END
                continue
                
            connection = (from_coord, to_coord)
            if connection not in connections:
                connections.append(connection)
    
    # Konwertuj do listy z dodatkową informacją o pozycji
    hex_list = []
    for (x, y), data in all_hexes.items():
        hex_list.append({
            'x': x, 'y': y, 
            'type': data['type'], 
            'bonus': data['bonus']
        })
    
    return hex_list, connections

def draw_hex_map(draw, hexes, connections, start_x, start_y, hex_size=40):
    """Rysuje rozgałęzioną mapę heksagonalną na karcie"""
    
    if not hexes:
        return start_y + 80
    
    # Znajdź wymiary mapy
    min_x = min(h['x'] for h in hexes)
    max_x = max(h['x'] for h in hexes)
    min_y = min(h['y'] for h in hexes)
    max_y = max(h['y'] for h in hexes)
    
    # Większe wymiary mapy
    map_width = (max_x - min_x + 1) * hex_size * 2.0
    map_height = (max_y - min_y + 1) * hex_size * 2.0
    
    # Kolory dla różnych typów heksów
    colors = {
        'start': (100, 200, 100),   # Jasno zielony
        'end': (220, 80, 80),       # Czerwony  
        'bonus': (255, 220, 100),   # Żółty
        'normal': (245, 245, 245)   # Biały
    }
    
    font_small = ImageFont.load_default()
    
    # Funkcja do rysowania prawdziwego heksagonu
    def draw_hexagon(draw, center_x, center_y, size, fill_color, outline_color=(40, 40, 40)):
        """Rysuje prawdziwy heksagon"""
        import math
        points = []
        for i in range(6):
            angle = math.pi * i / 3  # 60 stopni w radianach
            x = center_x + size * math.cos(angle)
            y = center_y + size * math.sin(angle)
            points.append((x, y))
        draw.polygon(points, fill=fill_color, outline=outline_color, width=2)
        return points
    
    # Funkcja do obliczania pozycji heksa (prostokątna siatka)
    def get_hex_position(hex_x, hex_y):
        pos_x = start_x + 50 + (hex_x - min_x) * hex_size * 1.8
        pos_y = start_y + 20 + (hex_y - min_y) * hex_size * 1.6
        return pos_x, pos_y
    
    # Najpierw rysuj wszystkie połączenia
    for (from_coord, to_coord) in connections:
        from_x, from_y = get_hex_position(from_coord[0], from_coord[1])
        to_x, to_y = get_hex_position(to_coord[0], to_coord[1])
        
        # Rysuj linię połączenia - grubszą i jaśniejszą
        draw.line([from_x, from_y, to_x, to_y], 
                 fill=(80, 80, 80), width=4)
    
    # Teraz rysuj heksy (żeby były nad liniami)
    hex_positions = {}
    for hex_data in hexes:
        pos_x, pos_y = get_hex_position(hex_data['x'], hex_data['y'])
        hex_positions[(hex_data['x'], hex_data['y'])] = (pos_x, pos_y)
        
        # Rysuj prawdziwy heksagon
        color = colors.get(hex_data['type'], colors['normal'])
        draw_hexagon(draw, pos_x, pos_y, hex_size//2, color)
        
        # Dodaj symbol w centrum
        symbol = ''
        if hex_data['type'] == 'start':
            symbol = 'START'
        elif hex_data['type'] == 'end':
            symbol = 'META'
        elif hex_data['type'] == 'bonus':
            # Użyj tekstu bonusu zamiast gwiazdki
            symbol = hex_data['bonus'] if hex_data['bonus'] else '+BONUS'
        else:
            symbol = ''  # Puste pole nie potrzebuje symbolu
        
        # Narysuj symbol - większy i bardziej czytelny
        if symbol:
            bbox = draw.textbbox((0, 0), symbol, font=font_small)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Czarny tekst na wszystkich polach
            draw.text((pos_x - text_width//2, pos_y - text_height//2), 
                     symbol, fill=(0, 0, 0), font=font_small)
    
    # Legenda na dole mapy
    legend_y = start_y + map_height + 15
    draw.text((start_x, legend_y), "⭐ = Pole bonusowe", 
             fill=COLOR_TEXT, font=font_small)
    
    return legend_y + 25

def generate_research_cards():
    """Generuje karty badań z wizualizacją map heksagonalnych"""
    print("Generowanie kart badań...")
    df = pd.read_csv('karty_badan.csv')
    font_title, font_header, font_text, font_small, font_tiny = setup_fonts()
    
    os.makedirs('cards/badania', exist_ok=True)
    
    for idx, row in df.iterrows():
        img, draw = create_card_background(CARD_WIDTH_STANDARD, CARD_HEIGHT_STANDARD, row['Dziedzina'])
        
        y = 80
        
        # Dziedzina
        draw.text((20, 20), row['Dziedzina'], fill=(255, 255, 255), font=font_small)
        
        # Nazwa badania
        name_lines = wrap_text(row['Nazwa'], font_header, CARD_WIDTH_STANDARD - 40)
        for line in name_lines:
            draw.text((20, y), line, fill=COLOR_HEADER, font=font_header)
            y += 35
        
        y += 10
        
        # Najpierw nagrody w górnej części
        draw.text((20, y), f"NAGRODA: {row['Nagroda_Podstawowa']}", fill=COLOR_TEXT, font=font_small)
        y += 25
        
        if pd.notna(row['Nagroda_Dodatkowa']) and row['Nagroda_Dodatkowa'].strip():
            draw.text((20, y), "BONUS:", fill=COLOR_HEADER, font=font_small)
            y += 20
            bonus_lines = wrap_text(row['Nagroda_Dodatkowa'], font_small, CARD_WIDTH_STANDARD - 40)
            for line in bonus_lines[:3]:  # Maksymalnie 3 linie bonusu
                draw.text((20, y), line, fill=COLOR_TEXT, font=font_small)
                y += 18
        
        y += 20
        
        # Mapa heksagonalna NA DOLE karty - większa i bardziej widoczna
        map_start_y = CARD_HEIGHT_STANDARD - 250  # Zacznij 250px od dołu
        draw.text((20, map_start_y - 25), "MAPA BADANIA:", fill=COLOR_HEADER, font=font_small)
        
        try:
            hexes, connections = parse_hex_map(row['Mapa_Heksagonalna'])
            if hexes:
                # JESZCZE WIĘKSZE heksagony dla lepszej widoczności
                draw_hex_map(draw, hexes, connections, 30, map_start_y, hex_size=70)
            else:
                draw.text((20, map_start_y), "Prosta ścieżka badawcza", fill=COLOR_TEXT, font=font_small)
        except Exception as e:
            # Fallback - pokaż informację o błędzie
            draw.text((20, map_start_y), f"Mapa niedostępna: {str(e)[:50]}", fill=(150, 150, 150), font=font_small)
        
        filename = f"badanie_{idx+1:02d}_{row['Nazwa'].replace(' ', '_').replace('/', '_')[:20]}.png"
        img.save(f'cards/badania/{filename}')
    
    print(f"Wygenerowano {len(df)} kart badań z rozgałęzionymi mapami heksagonalnymi")

def generate_consortium_cards():
    """Generuje karty konsorcjów"""
    print("Generowanie kart konsorcjów...")
    df = pd.read_csv('karty_konsorcja.csv')
    font_title, font_header, font_text, font_small, font_tiny = setup_fonts()
    
    os.makedirs('cards/konsorcja', exist_ok=True)
    
    for idx, row in df.iterrows():
        img, draw = create_card_background(CARD_WIDTH_STANDARD, CARD_HEIGHT_STANDARD)
        
        # Specjalne tło dla konsorcjów
        draw.rectangle([10, 10, CARD_WIDTH_STANDARD-10, 60], fill=(120, 80, 140))
        draw.text((20, 20), "KONSORCJUM NAUKOWE", fill=(255, 255, 255), font=font_small)
        
        y = 80
        
        # Główny opis
        desc_lines = wrap_text(row['Opis'], font_text, CARD_WIDTH_STANDARD - 40)
        for line in desc_lines:
            if y < CARD_HEIGHT_STANDARD - 200:
                draw.text((20, y), line, fill=COLOR_TEXT, font=font_text)
                y += 28
        
        y += 40
        
        # Cytat
        if pd.notna(row['Cytat']) and row['Cytat'].strip():
            draw.rectangle([15, y-10, CARD_WIDTH_STANDARD-15, y+100], fill=(250, 250, 250), outline=COLOR_BORDER)
            y += 10
            
            quote_lines = wrap_text(row['Cytat'], font_small, CARD_WIDTH_STANDARD - 50)
            for line in quote_lines:
                if y < CARD_HEIGHT_STANDARD - 30:
                    draw.text((25, y), line, fill=COLOR_HEADER, font=font_small)
                    y += 22
        
        filename = f"konsorcjum_{idx+1:02d}.png"
        img.save(f'cards/konsorcja/{filename}')
    
    print(f"Wygenerowano {len(df)} kart konsorcjów")

def generate_intrigue_cards():
    """Generuje karty intryg"""
    print("Generowanie kart intryg...")
    df = pd.read_csv('karty_intrygi.csv')
    font_title, font_header, font_text, font_small, font_tiny = setup_fonts()
    
    os.makedirs('cards/intrygi', exist_ok=True)
    
    for idx, row in df.iterrows():
        img, draw = create_card_background(CARD_WIDTH_STANDARD, CARD_HEIGHT_STANDARD)
        
        # Ciemne tło dla intryg
        draw.rectangle([10, 10, CARD_WIDTH_STANDARD-10, 60], fill=(140, 40, 40))
        draw.text((20, 20), "INTRYGA", fill=(255, 255, 255), font=font_small)
        
        y = 80
        
        # Nazwa
        name_lines = wrap_text(row['Nazwa'], font_header, CARD_WIDTH_STANDARD - 40)
        for line in name_lines:
            draw.text((20, y), line, fill=COLOR_HEADER, font=font_header)
            y += 35
        
        y += 20
        
        # Efekt
        draw.text((20, y), "EFEKT:", fill=COLOR_HEADER, font=font_text)
        y += 30
        effect_lines = wrap_text(row['Efekt'], font_text, CARD_WIDTH_STANDARD - 40)
        for line in effect_lines:
            draw.text((20, y), line, fill=COLOR_TEXT, font=font_text)
            y += 28
        
        y += 30
        
        # Opis
        draw.text((20, y), "OPIS:", fill=COLOR_HEADER, font=font_small)
        y += 25
        desc_lines = wrap_text(row['Opis'], font_small, CARD_WIDTH_STANDARD - 40)
        for line in desc_lines:
            if y < CARD_HEIGHT_STANDARD - 30:
                draw.text((20, y), line, fill=COLOR_TEXT, font=font_small)
                y += 22
        
        filename = f"intryga_{idx+1:02d}_{row['Nazwa'].replace(' ', '_')[:15]}.png"
        img.save(f'cards/intrygi/{filename}')
    
    print(f"Wygenerowano {len(df)} kart intryg")

def generate_opportunity_cards():
    """Generuje karty okazji"""
    print("Generowanie kart okazji...")
    df = pd.read_csv('karty_okazje.csv')
    font_title, font_header, font_text, font_small, font_tiny = setup_fonts()
    
    os.makedirs('cards/okazje', exist_ok=True)
    
    for idx, row in df.iterrows():
        img, draw = create_card_background(CARD_WIDTH_STANDARD, CARD_HEIGHT_STANDARD)
        
        # Jasne, pozytywne tło
        draw.rectangle([10, 10, CARD_WIDTH_STANDARD-10, 60], fill=(40, 140, 40))
        draw.text((20, 20), "OKAZJA", fill=(255, 255, 255), font=font_small)
        
        y = 80
        
        # Nazwa
        name_lines = wrap_text(row['Nazwa'], font_header, CARD_WIDTH_STANDARD - 40)
        for line in name_lines:
            draw.text((20, y), line, fill=COLOR_HEADER, font=font_header)
            y += 35
        
        y += 20
        
        # Efekt
        draw.text((20, y), "EFEKT:", fill=COLOR_HEADER, font=font_text)
        y += 30
        effect_lines = wrap_text(row['Efekt'], font_text, CARD_WIDTH_STANDARD - 40)
        for line in effect_lines:
            draw.text((20, y), line, fill=COLOR_TEXT, font=font_text)
            y += 28
        
        y += 30
        
        # Opis
        draw.text((20, y), "OPIS:", fill=COLOR_HEADER, font=font_small)
        y += 25
        desc_lines = wrap_text(row['Opis'], font_small, CARD_WIDTH_STANDARD - 40)
        for line in desc_lines:
            if y < CARD_HEIGHT_STANDARD - 30:
                draw.text((20, y), line, fill=COLOR_TEXT, font=font_small)
                y += 22
        
        filename = f"okazja_{idx+1:02d}_{row['Nazwa'].replace(' ', '_')[:15]}.png"
        img.save(f'cards/okazje/{filename}')
    
    print(f"Wygenerowano {len(df)} kart okazji")

def generate_institute_cards():
    """Generuje karty instytutów (poziome, większe)"""
    print("Generowanie kart instytutów...")
    df = pd.read_csv('karty_instytuty.csv')
    font_title, font_header, font_text, font_small, font_tiny = setup_fonts()
    
    os.makedirs('cards/instytuty', exist_ok=True)
    
    for idx, row in df.iterrows():
        # Większe, poziome karty dla instytutów
        img, draw = create_card_background(CARD_WIDTH_INSTITUTE, CARD_HEIGHT_INSTITUTE)
        
        # Eleganckie tło dla instytutów
        draw.rectangle([10, 10, CARD_WIDTH_INSTITUTE-10, 80], fill=(50, 70, 120))
        
        y = 100
        
        # Nazwa instytutu
        name_lines = wrap_text(row['Nazwa'], font_title, CARD_WIDTH_INSTITUTE - 40)
        for line in name_lines:
            draw.text((20, 20), line, fill=(255, 255, 255), font=font_title)
        
        # Zasoby startowe
        draw.text((20, y), f"START: {row['Zasoby_Startowe']}", fill=COLOR_HEADER, font=font_text)
        y += 35
        draw.text((20, y), f"REPUTACJA: {row['Reputacja_Start']}", fill=COLOR_HEADER, font=font_text)
        y += 50
        
        # Specjalizacja
        draw.text((20, y), "SPECJALIZACJA:", fill=COLOR_HEADER, font=font_text)
        y += 30
        spec_lines = wrap_text(row['Specjalizacja_Bonus'], font_text, CARD_WIDTH_INSTITUTE - 40)
        for line in spec_lines:
            draw.text((20, y), line, fill=COLOR_TEXT, font=font_text)
            y += 28
        
        y += 30
        
        # Specjalna zdolność
        draw.text((20, y), "SPECJALNA ZDOLNOŚĆ:", fill=COLOR_HEADER, font=font_text)
        y += 30
        ability_lines = wrap_text(row['Specjalna_Zdolność'], font_text, CARD_WIDTH_INSTITUTE - 40)
        for line in ability_lines:
            if y < CARD_HEIGHT_INSTITUTE - 100:
                draw.text((20, y), line, fill=COLOR_TEXT, font=font_text)
                y += 28
        
        # Opis na prawej stronie
        right_x = CARD_WIDTH_INSTITUTE // 2 + 20
        draw.text((right_x, 100), "O INSTYTUCIE:", fill=COLOR_HEADER, font=font_small)
        desc_y = 130
        desc_lines = wrap_text(row['Opis'], font_small, CARD_WIDTH_INSTITUTE // 2 - 40)
        for line in desc_lines:
            if desc_y < CARD_HEIGHT_INSTITUTE - 30:
                draw.text((right_x, desc_y), line, fill=COLOR_TEXT, font=font_small)
                desc_y += 22
        
        filename = f"instytut_{idx+1:02d}_{row['Nazwa'].split('(')[0].strip().replace(' ', '_')}.png"
        img.save(f'cards/instytuty/{filename}')
    
    print(f"Wygenerowano {len(df)} kart instytutów")

def generate_remaining_cards():
    """Generuje pozostałe typy kart (granty, czasopisma, etc.)"""
    
    # Granty
    print("Generowanie kart grantów...")
    df = pd.read_csv('karty_granty.csv')
    font_title, font_header, font_text, font_small, font_tiny = setup_fonts()
    
    os.makedirs('cards/granty', exist_ok=True)
    
    for idx, row in df.iterrows():
        img, draw = create_card_background(CARD_WIDTH_STANDARD, CARD_HEIGHT_STANDARD)
        
        draw.rectangle([10, 10, CARD_WIDTH_STANDARD-10, 60], fill=(180, 140, 60))
        draw.text((20, 20), "GRANT", fill=(255, 255, 255), font=font_small)
        
        y = 80
        
        # Nazwa
        name_lines = wrap_text(row['Nazwa'], font_header, CARD_WIDTH_STANDARD - 40)
        for line in name_lines:
            draw.text((20, y), line, fill=COLOR_HEADER, font=font_header)
            y += 35
        
        y += 20
        
        # Wymagania
        if pd.notna(row['Wymagania']) and row['Wymagania'].strip() != 'Brak wymagań':
            draw.text((20, y), "WYMAGANIA:", fill=COLOR_HEADER, font=font_text)
            y += 25
            req_lines = wrap_text(row['Wymagania'], font_small, CARD_WIDTH_STANDARD - 40)
            for line in req_lines:
                draw.text((20, y), line, fill=COLOR_TEXT, font=font_small)
                y += 22
            y += 20
        
        # Cel
        draw.text((20, y), "CEL:", fill=COLOR_HEADER, font=font_text)
        y += 25
        goal_lines = wrap_text(row['Cel'], font_text, CARD_WIDTH_STANDARD - 40)
        for line in goal_lines:
            draw.text((20, y), line, fill=COLOR_TEXT, font=font_text)
            y += 28
        
        y += 20
        
        # Nagroda
        total_reward = f"{row['Nagroda']} (+{row['Runda_Bonus']}/rundę)"
        draw.text((20, y), f"NAGRODA: {total_reward}", fill=COLOR_HEADER, font=font_text)
        
        filename = f"grant_{idx+1:02d}_{row['Nazwa'].replace(' ', '_')[:15]}.png"
        img.save(f'cards/granty/{filename}')
    
    print(f"Wygenerowano {len(df)} kart grantów")
    
    # Czasopisma
    print("Generowanie kart czasopism...")
    df = pd.read_csv('karty_czasopisma.csv')
    os.makedirs('cards/czasopisma', exist_ok=True)
    
    for idx, row in df.iterrows():
        img, draw = create_card_background(CARD_WIDTH_STANDARD, CARD_HEIGHT_STANDARD)
        
        # Kolor zależny od Impact Factor
        if row['Impact_Factor'] >= 8:
            color = (150, 50, 50)  # Czerwony dla top-tier
        elif row['Impact_Factor'] >= 5:
            color = (50, 120, 180)  # Niebieski dla mid-tier
        else:
            color = (100, 100, 100)  # Szary dla pozostałych
            
        draw.rectangle([10, 10, CARD_WIDTH_STANDARD-10, 60], fill=color)
        draw.text((20, 20), f"CZASOPISMO (IF: {row['Impact_Factor']})", fill=(255, 255, 255), font=font_small)
        
        y = 80
        
        # Nazwa
        name_lines = wrap_text(row['Nazwa'], font_header, CARD_WIDTH_STANDARD - 40)
        for line in name_lines:
            draw.text((20, y), line, fill=COLOR_HEADER, font=font_header)
            y += 35
        
        y += 20
        
        # Wymagania
        if pd.notna(row['Wymagania']) and row['Wymagania'].strip() != 'Brak wymagań':
            draw.text((20, y), "WYMAGANIA:", fill=COLOR_HEADER, font=font_text)
            y += 25
            req_lines = wrap_text(row['Wymagania'], font_small, CARD_WIDTH_STANDARD - 40)
            for line in req_lines:
                draw.text((20, y), line, fill=COLOR_TEXT, font=font_small)
                y += 22
            y += 20
        
        # Koszt PB
        if pd.notna(row['Koszt_PB']) and str(row['Koszt_PB']).strip():
            draw.text((20, y), f"KOSZT: {row['Koszt_PB']} PB", fill=(180, 60, 60), font=font_text)
            y += 30
        
        # Nagroda PZ
        draw.text((20, y), f"NAGRODA: {row['Nagroda_PZ']} PZ", fill=COLOR_HEADER, font=font_text)
        y += 40
        
        # Specjalny bonus
        if pd.notna(row['Specjalny_Bonus']) and row['Specjalny_Bonus'].strip():
            draw.text((20, y), "BONUS:", fill=COLOR_HEADER, font=font_small)
            y += 25
            bonus_lines = wrap_text(row['Specjalny_Bonus'], font_small, CARD_WIDTH_STANDARD - 40)
            for line in bonus_lines:
                if y < CARD_HEIGHT_STANDARD - 30:
                    draw.text((20, y), line, fill=COLOR_TEXT, font=font_small)
                    y += 22
        
        filename = f"czasopismo_{idx+1:02d}_{row['Nazwa'].replace(' ', '_')[:15]}.png"
        img.save(f'cards/czasopisma/{filename}')
    
    print(f"Wygenerowano {len(df)} kart czasopism")

def main():
    """Główna funkcja generująca wszystkie karty"""
    print("=== GENERATOR KART PRINCIPIA ===")
    print("Tworzenie folderów...")
    
    os.makedirs('cards', exist_ok=True)
    
    try:
        generate_scientists_cards()
        generate_research_cards()
        generate_consortium_cards()
        generate_intrigue_cards()
        generate_opportunity_cards()
        generate_institute_cards()
        generate_remaining_cards()
        
        print("\n=== GENEROWANIE ZAKOŃCZONE ===")
        print("Wszystkie karty zostały wygenerowane w folderze 'cards/'")
        print("Struktura folderów:")
        print("├── cards/")
        print("    ├── naukowcy/")
        print("    ├── badania/")
        print("    ├── konsorcja/")
        print("    ├── intrygi/")
        print("    ├── okazje/")
        print("    ├── instytuty/")
        print("    ├── granty/")
        print("    └── czasopisma/")
        
    except Exception as e:
        print(f"Błąd podczas generowania: {e}")
        print("Sprawdź czy wszystkie pliki CSV istnieją w katalogu.")

if __name__ == "__main__":
    main()