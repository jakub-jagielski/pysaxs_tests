#!/usr/bin/env python3

# Test nowego formatu map heksagonalnych
# Format: START(0,0) -> główna ścieżka do END + opcjonalne ślepe zaułki z bonusami

test_maps = [
    # Proste badanie - ścieżka prosta + ślepy zaułek z bonusem
    "START(0,0)->(1,0)->(2,0)END + BRANCH(0,1)->BONUS(+1PB)",
    
    # Złożone badanie - główna ścieżka + 2 ślepe zaułki
    "START(0,0)->(1,0)->(2,0)->(3,0)END + BRANCH(1,1)->BONUS(+1PZ) + BRANCH(2,1)->BONUS(+2PB)",
    
    # Format dla Metamorfozy Kontrolowanej - jak powinno być
    "START(0,0)->(1,0)->(2,0)END + BRANCH(0,1)->(1,1)->BONUS(+1PZ)"
]

def parse_new_hex_format(hex_string):
    """Parsuje nowy format z jednym END i ślepymi zaułkami"""
    all_hexes = {}
    connections = []
    
    # Podziel na główną ścieżkę i branże
    parts = hex_string.split(' + ')
    main_path = parts[0]
    branches = parts[1:] if len(parts) > 1 else []
    
    print(f"Główna ścieżka: {main_path}")
    print(f"Ślepe zaułki: {branches}")
    
    # Parsuj główną ścieżkę
    import re
    
    # Znajdź wszystkie współrzędne w głównej ścieżce
    coords = re.findall(r'\((\d+),(\d+)\)', main_path)
    
    for i, (x, y) in enumerate(coords):
        x, y = int(x), int(y)
        
        if i == 0:
            hex_type = 'start'
        elif 'END' in main_path and i == len(coords) - 1:
            hex_type = 'end'
        else:
            hex_type = 'normal'
            
        all_hexes[(x, y)] = {'type': hex_type, 'bonus': None}
        
        # Dodaj połączenie z poprzednim
        if i > 0:
            prev_x, prev_y = int(coords[i-1][0]), int(coords[i-1][1])
            connections.append(((prev_x, prev_y), (x, y)))
    
    # Parsuj ślepe zaułki
    for branch in branches:
        branch = branch.strip()
        if branch.startswith('BRANCH'):
            # Znajdź współrzędne w branży
            branch_coords = re.findall(r'\((\d+),(\d+)\)', branch)
            bonus_match = re.search(r'BONUS\(([^)]+)\)', branch)
            bonus = bonus_match.group(1) if bonus_match else None
            
            # Połącz punkty w branży
            for i, (x, y) in enumerate(branch_coords):
                x, y = int(x), int(y)
                
                # Ostatni punkt w branży to bonus
                if i == len(branch_coords) - 1 and bonus:
                    hex_type = 'bonus'
                else:
                    hex_type = 'normal'
                
                all_hexes[(x, y)] = {
                    'type': hex_type, 
                    'bonus': bonus if hex_type == 'bonus' else None
                }
                
                # Dodaj połączenie
                if i > 0:
                    prev_x, prev_y = int(branch_coords[i-1][0]), int(branch_coords[i-1][1])
                    connections.append(((prev_x, prev_y), (x, y)))
    
    return all_hexes, connections

# Test
for i, test_map in enumerate(test_maps):
    print(f"\n=== TEST {i+1} ===")
    print(f"Mapa: {test_map}")
    hexes, connections = parse_new_hex_format(test_map)
    print(f"Heksy: {hexes}")
    print(f"Połączenia: {connections}")