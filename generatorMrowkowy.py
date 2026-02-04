#!/usr/bin/env python3
import networkx as nx
import sys
import random
import numpy as np

# Limit generacji (iteracji kolonii)
DEFAULT_LIMIT = 5000

def get_integrality_energy(adj_matrix):
    """
    Oblicza energię rozwiązania z uwzględnieniem kary za brak spójności.
    E(G) = suma odległości wartości własnych od liczb całkowitych.
    """
    try:
        # Weryfikacja spójności grafu
        G_temp = nx.from_numpy_array(adj_matrix)
        
        if not nx.is_connected(G_temp):
            # Wysoka kara wymuszająca poszukiwanie grafów spójnych
            return 1000.0

        # Obliczenie widma i energii dla grafu spójnego
        eigenvalues = np.linalg.eigvalsh(adj_matrix)
        energy = sum(abs(ev - round(ev)) for ev in eigenvalues)
        return energy

    except np.linalg.LinAlgError:
        return float('inf')

def select_edges_probabilistically(n, k, pheromones):
    """
    Konstrukcja stochastyczna grafu na podstawie macierzy feromonowej.
    Wybór k krawędzi metodą Weighted Random Sampling.
    """
    rows, cols = np.triu_indices(n, k=1)
    
    # Pobranie poziomu feromonów dla każdej potencjalnej krawędzi
    probs = pheromones[rows, cols]
    
    # Normalizacja prawdopodobieństwa
    prob_sum = probs.sum()
    if prob_sum == 0:
        probs = np.ones_like(probs) / len(probs)
    else:
        probs = probs / prob_sum
    
    # Losowanie indeksów krawędzi bez zwracania
    selected_indices = np.random.choice(len(rows), size=k, replace=False, p=probs)
    
    # Konstrukcja macierzy sąsiedztwa
    adj = np.zeros((n, n), dtype=int)
    adj[rows[selected_indices], cols[selected_indices]] = 1
    
    # Symetryzacja macierzy (graf nieskierowany)
    adj = adj + adj.T
    return adj

def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Użycie: python3 generatorMrowkowy.py <n> <k> [limit/seed]\n")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        k = int(sys.argv[2])
        
        # Obsługa argumentu seed/limit (format: ID/TOTAL lub INT)
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

    # Parametry algorytmu ACO
    ants_per_gen = 25       # Rozmiar populacji
    evaporation_rate = 0.1  # Współczynnik parowania śladu
    
    # Inicjalizacja macierzy feromonów
    pheromones = np.ones((n, n))
    
    best_global_energy = float('inf')
    
    generation = 0
    no_improvement_counter = 0
    
    while generation < limit:
        
        # 1. Faza konstrukcji rozwiązań
        solutions = []
        for _ in range(ants_per_gen):
            adj = select_edges_probabilistically(n, k, pheromones)
            energy = get_integrality_energy(adj)
            solutions.append((adj, energy))
            
            # Weryfikacja rozwiązania idealnego (Energia ~ 0)
            if energy < 1e-7:
                G_out = nx.from_numpy_array(adj)
                # Konwersja do formatu graph6 (kompatybilność z NetworkX 3.0+)
                output = nx.to_graph6_bytes(G_out, header=False).decode('ascii').strip()
                sys.stdout.write(output + '\n')
                sys.stdout.flush()
                
                # Reset po znalezieniu rozwiązania
                pheromones = np.ones((n, n))
                best_global_energy = float('inf')

            # Logowanie minimów lokalnych (Energia < 0.9) do analizy
            elif energy < 0.9:
                G_out = nx.from_numpy_array(adj)
                g6 = nx.to_graph6_bytes(G_out, header=False).decode('ascii').strip()
                sys.stderr.write(f"PACZKA {package_id} ENERGY {energy:.5f} {g6}\n")
                sys.stderr.flush()

        # 2. Sortowanie populacji wg funkcji przystosowania (energii)
        solutions.sort(key=lambda x: x[1])
        best_ant_adj, best_ant_energy = solutions[0]
        
        # Aktualizacja najlepszego globalnego rozwiązania
        if best_ant_energy < best_global_energy:
            best_global_energy = best_ant_energy
            no_improvement_counter = 0
        else:
            no_improvement_counter += 1

        # 3. Aktualizacja feromonów
        # a) Globalne parowanie (Evaporation)
        pheromones *= (1.0 - evaporation_rate)
        
        # b) Wzmacnianie śladu (Reinforcement) przez najlepsze jednostki (Elitism)
        top_ants = solutions[:3]
        for adj, energy in top_ants:
            # Depozyt odwrotnie proporcjonalny do energii
            deposit = 1.0 / (energy + 0.5) 
            pheromones += (adj * deposit) * 0.2 

        # Ograniczenie wartości feromonów (zapobieganie niestabilności numerycznej)
        pheromones = np.clip(pheromones, 0.01, 50.0)

        # 4. Mechanizm restartu w przypadku stagnacji
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