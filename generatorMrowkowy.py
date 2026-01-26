#!/usr/bin/env python3
import networkx as nx
import sys
import random
import numpy as np

# Domyślny limit generacji (iteracji kolonii)
DEFAULT_LIMIT = 10000

def get_eigen_cost(adj_matrix):
    """
    Funkcja kosztu: suma odchyleń wartości własnych od liczb całkowitych.
    0.0 oznacza graf całkowity.
    """
    try:
        eigenvalues = np.linalg.eigvalsh(adj_matrix)
        cost = sum(abs(ev - round(ev)) for ev in eigenvalues)
        return cost
    except np.linalg.LinAlgError:
        return float('inf')

def select_edges_probabilistically(n, k, pheromones):
    """
    Mrówka buduje graf wybierając k krawędzi na podstawie poziomu feromonów.
    """
    # Indeksy górnego trójkąta macierzy (wszystkie możliwe pary wierzchołków)
    rows, cols = np.triu_indices(n, k=1)
    
    # Pobieramy wartości feromonów dla tych par
    probs = pheromones[rows, cols]
    
    # Normalizacja prawdopodobieństw
    prob_sum = probs.sum()
    if prob_sum == 0:
        probs = np.ones_like(probs) / len(probs)
    else:
        probs = probs / prob_sum
    
    # Wybór indeksów krawędzi (weighted random sampling bez zwracania)
    selected_indices = np.random.choice(len(rows), size=k, replace=False, p=probs)
    
    # Budowa macierzy sąsiedztwa
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
        
        arg3 = sys.argv[3] if len(sys.argv) > 3 else str(DEFAULT_LIMIT)
        
        # Obsługa seeda/limitu
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
        sys.stderr.write("Błąd argumentów.\n")
        sys.exit(1)

    # --- PARAMETRY ACO ---
    ants_per_gen = 20       # Liczba mrówek w jednej iteracji
    evaporation_rate = 0.1  # Szybkość parowania feromonu
    
    # Inicjalizacja feromonów (startujemy z 1.0)
    pheromones = np.ones((n, n))
    
    best_global_cost = float('inf')
    
    generation = 0
    no_improvement_counter = 0
    
    while generation < limit:
        
        # 1. Konstrukcja rozwiązań przez mrówki
        solutions = []
        for _ in range(ants_per_gen):
            adj = select_edges_probabilistically(n, k, pheromones)
            cost = get_eigen_cost(adj)
            solutions.append((adj, cost))
            
            # Sprawdzenie sukcesu (Graf Całkowity)
            if cost < 1e-7:
                G_out = nx.from_numpy_array(adj)
                output = nx.to_graph6_string(G_out, header=False)
                sys.stdout.write(output + '\n')
                sys.stdout.flush()
                
                # Restart po znalezieniu
                pheromones = np.ones((n, n))
                best_global_cost = float('inf')

        # 2. Sortowanie mrówek (elitaryzm)
        solutions.sort(key=lambda x: x[1])
        best_ant_adj, best_ant_cost = solutions[0]
        
        # Aktualizacja najlepszego wyniku
        if best_ant_cost < best_global_cost:
            best_global_cost = best_ant_cost
            no_improvement_counter = 0
        else:
            no_improvement_counter += 1

        # 3. Aktualizacja feromonów
        # a) Parowanie
        pheromones *= (1.0 - evaporation_rate)
        
        # b) Wzmacnianie (3 najlepsze mrówki zostawiają ślad)
        top_ants = solutions[:3]
        for adj, cost in top_ants:
            deposit = 1.0 / (cost + 0.5) 
            pheromones += (adj * deposit) * 0.1 

        pheromones = np.clip(pheromones, 0.01, 100.0)

        # 4. Restart przy stagnacji
        if no_improvement_counter > 150:
            pheromones = np.ones((n, n))
            no_improvement_counter = 0
        
        generation += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        sys.stderr.close()