#!/usr/bin/env python3
import networkx as nx
import sys
import random
import numpy as np

# Limit generacji (iteracji kolonii)
DEFAULT_LIMIT = 5000

def get_integrality_energy(adj_matrix):
    """
    Funkcja celu z KARĄ ZA NIESPÓJNOŚĆ.
    """
    try:
        # 1. Sprawdzenie spójności
        # Tworzymy tymczasowy graf NetworkX
        G_temp = nx.from_numpy_array(adj_matrix)
        
        if not nx.is_connected(G_temp):
            return 1000.0  # <--- OGROMNA KARA. Mrówki będą uciekać od takich grafów.

        # 2. Obliczenie energii tylko jeśli graf jest spójny
        eigenvalues = np.linalg.eigvalsh(adj_matrix)
        energy = sum(abs(ev - round(ev)) for ev in eigenvalues)
        return energy

    except np.linalg.LinAlgError:
        return float('inf')

def select_edges_probabilistically(n, k, pheromones):
    """
    Mrówka buduje graf wybierając k krawędzi na podstawie poziomu feromonów.
    """
    # Indeksy górnego trójkąta (wszystkie możliwe pary)
    rows, cols = np.triu_indices(n, k=1)
    
    # Pobieramy feromony dla par
    probs = pheromones[rows, cols]
    
    # Normalizacja
    prob_sum = probs.sum()
    if prob_sum == 0:
        probs = np.ones_like(probs) / len(probs)
    else:
        probs = probs / prob_sum
    
    # Losowanie bez zwracania (Weighted Random Sampling)
    selected_indices = np.random.choice(len(rows), size=k, replace=False, p=probs)
    
    # Budowa macierzy
    adj = np.zeros((n, n), dtype=int)
    adj[rows[selected_indices], cols[selected_indices]] = 1
    
    # Symetryzacja
    adj = adj + adj.T
    return adj

def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Użycie: python3 generatorMrowkowy.py <n> <k> [limit/seed]\n")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        k = int(sys.argv[2])
        
        # --- ZMIANA: Pobieranie ID Paczki ---
        arg3 = sys.argv[3] if len(sys.argv) > 3 else str(DEFAULT_LIMIT)
        package_id = arg3
        
        if '/' in arg3:
            parts = arg3.split('/')
            seed_val = int(parts[0]) + int(parts[1])
            random.seed(seed_val)
            np.random.seed(seed_val)
            limit = DEFAULT_LIMIT
        else:
            limit = int(arg3)
            random.seed()
            np.random.seed(None)
            
    except ValueError:
        return

    # --- PARAMETRY ACO ---
    ants_per_gen = 25       # Liczba mrówek w pokoleniu
    evaporation_rate = 0.1  # Parowanie
    
    # Inicjalizacja feromonów (macierz NxN)
    pheromones = np.ones((n, n))
    
    best_global_energy = float('inf')
    
    generation = 0
    no_improvement_counter = 0
    
    while generation < limit:
        
        # 1. Konstrukcja rozwiązań
        solutions = []
        for _ in range(ants_per_gen):
            adj = select_edges_probabilistically(n, k, pheromones)
            energy = get_integrality_energy(adj)
            solutions.append((adj, energy))
            
            # --- SUKCES (Energia ~ 0) ---
            if energy < 1e-7:
                G_out = nx.from_numpy_array(adj)
                # Fix dla NetworkX 3.0+
                output = nx.to_graph6_bytes(G_out, header=False).decode('ascii').strip()
                sys.stdout.write(output + '\n')
                sys.stdout.flush()
                
                # Reset po sukcesie
                pheromones = np.ones((n, n))
                best_global_energy = float('inf')

            # --- BLISKIE ROZWIĄZANIE (Logowanie do stderr) ---
            elif energy < 0.9:
                G_out = nx.from_numpy_array(adj)
                g6 = nx.to_graph6_bytes(G_out, header=False).decode('ascii').strip()
                sys.stderr.write(f"PACZKA {package_id} ENERGY {energy:.5f} {g6}\n")
                sys.stderr.flush()

        # 2. Sortowanie mrówek (Najlepsze na początku)
        solutions.sort(key=lambda x: x[1])
        best_ant_adj, best_ant_energy = solutions[0]
        
        # Aktualizacja globalnego najlepszego wyniku
        if best_ant_energy < best_global_energy:
            best_global_energy = best_ant_energy
            no_improvement_counter = 0
        else:
            no_improvement_counter += 1

        # 3. Aktualizacja feromonów
        # a) Parowanie
        pheromones *= (1.0 - evaporation_rate)
        
        # b) Wzmacnianie (Tylko 3 najlepsze mrówki zostawiają ślad)
        top_ants = solutions[:3]
        for adj, energy in top_ants:
            # Im mniejsza energia, tym silniejszy ślad
            deposit = 1.0 / (energy + 0.5) 
            # Wzmacniamy krawędzie występujące w dobrych grafach
            pheromones += (adj * deposit) * 0.2 

        # Ograniczenie feromonów (żeby nie wybuchły do nieskończoności)
        pheromones = np.clip(pheromones, 0.01, 50.0)

        # 4. Restart przy stagnacji (gdy feromony zbiegną się do złego minimum)
        if no_improvement_counter > 200:
            pheromones = np.ones((n, n))
            no_improvement_counter = 0
            best_global_energy = float('inf')
        
        generation += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        sys.stderr.close()