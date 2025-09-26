#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re

def fix_hex_map_format(hex_string):
    """
    Naprawia format mapy heksagonalnej:
    - Bonusy powinny być na końcu ślepych zaułków
    - Usuwa niepotrzebne pola po bonusie
    """
    
    # Znajdź start
    start_match = re.search(r'START\((\d+),(\d+)\)', hex_string)
    if not start_match:
        return hex_string
    
    # Znajdź wszystkie ścieżki
    paths_match = re.search(r'\[\s*(.+)\s*\]', hex_string)
    if not paths_match:
        return hex_string
    
    paths_text = paths_match.group(1)
    individual_paths = re.split(r'\s*\|\s*', paths_text)
    
    fixed_paths = []
    
    for i, path in enumerate(individual_paths):
        if i == 0:
            # Pierwsza ścieżka (główna) - pozostaw jak jest
            fixed_paths.append(path.strip())
        else:
            # Ścieżki bonusowe - usuń wszystko po BONUS
            # Format: (0,1)->(1,1)BONUS(+1PZ)->(2,1)->(2,0)END
            # Powinno być: (0,1)->(1,1)BONUS(+1PZ)
            
            # Znajdź pozycję BONUS
            bonus_match = re.search(r'BONUS\([^)]+\)', path)
            if bonus_match:
                # Obetnij wszystko po bonusie
                bonus_end = bonus_match.end()
                fixed_path = path[:bonus_end]
                fixed_paths.append(fixed_path.strip())
            else:
                # Jeśli nie ma bonusu, zostaw jak jest
                fixed_paths.append(path.strip())
    
    # Złóż z powrotem
    start_part = f"START({start_match.group(1)},{start_match.group(2)})"
    fixed_format = f"{start_part}->[{' | '.join(fixed_paths)}]"
    
    return fixed_format

def main():
    # Wczytaj CSV
    df = pd.read_csv('karty_badan.csv')
    
    print(f"Naprawiam {len(df)} map heksagonalnych...")
    
    fixed_count = 0
    for idx, row in df.iterrows():
        old_map = row['Mapa_Heksagonalna']
        new_map = fix_hex_map_format(old_map)
        
        if old_map != new_map:
            df.at[idx, 'Mapa_Heksagonalna'] = new_map
            fixed_count += 1
            print(f"Naprawiono kartę: {row['Nazwa']}")
            print(f"  Przed: {old_map}")
            print(f"  Po: {new_map}")
            print()
    
    # Zapisz z powrotem
    df.to_csv('karty_badan.csv', index=False)
    print(f"✅ Naprawiono {fixed_count} map heksagonalnych")
    print("Zapisano do karty_badan.csv")

if __name__ == "__main__":
    main()