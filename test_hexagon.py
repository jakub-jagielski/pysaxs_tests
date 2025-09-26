#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import math

def draw_hexagon(draw, center_x, center_y, size, fill_color, outline_color=(40, 40, 40)):
    """Rysuje prawdziwy heksagon"""
    points = []
    for i in range(6):
        angle = math.pi * i / 3  # 60 stopni w radianach
        x = center_x + size * math.cos(angle)
        y = center_y + size * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=fill_color, outline=outline_color, width=2)
    return points

def create_test_hex_map():
    """Tworzy testową mapę heksagonalną jak w przykładzie"""
    
    # Utwórz obraz
    img = Image.new('RGB', (400, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    # Kolory
    colors = {
        'start': (100, 200, 100),   # Jasno zielony
        'end': (220, 80, 80),       # Czerwony  
        'bonus': (255, 220, 100),   # Żółty
        'normal': (245, 245, 245)   # Biały
    }
    
    hex_size = 30
    
    # Pozycje heksów (jak w przykładzie)
    # START w lewym dolnym rogu
    start_x, start_y = 100, 200
    
    # Normalne pola
    normal1_x, normal1_y = 150, 150
    normal2_x, normal2_y = 200, 150
    normal3_x, normal3_y = 200, 100
    
    # Bonus (żółty) w prawym górnym rogu
    bonus_x, bonus_y = 250, 100
    
    # META (czerwony) w lewym górnym rogu  
    end_x, end_y = 100, 100
    
    # Rysuj połączenia
    connections = [
        ((start_x, start_y), (normal1_x, normal1_y)),
        ((normal1_x, normal1_y), (normal2_x, normal2_y)),
        ((normal2_x, normal2_y), (normal3_x, normal3_y)),
        ((normal3_x, normal3_y), (bonus_x, bonus_y)),
        ((normal3_x, normal3_y), (end_x, end_y)),
        ((normal1_x, normal1_y), (end_x, end_y))
    ]
    
    for (from_pos, to_pos) in connections:
        draw.line([from_pos[0], from_pos[1], to_pos[0], to_pos[1]], 
                 fill=(80, 80, 80), width=3)
    
    # Rysuj heksagony
    hexes = [
        (start_x, start_y, 'start', 'START'),
        (normal1_x, normal1_y, 'normal', ''),
        (normal2_x, normal2_y, 'normal', ''),
        (normal3_x, normal3_y, 'normal', ''),
        (bonus_x, bonus_y, 'bonus', '+1PB'),
        (end_x, end_y, 'end', 'META')
    ]
    
    for x, y, hex_type, text in hexes:
        color = colors[hex_type]
        draw_hexagon(draw, x, y, hex_size, color)
        
        if text:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text((x - text_width//2, y - text_height//2), 
                     text, fill=(0, 0, 0), font=font)
    
    # Zapisz obraz
    img.save('test_hexagon.png')
    print("Zapisano test_hexagon.png")

if __name__ == "__main__":
    create_test_hex_map()