#!/usr/bin/env python3
import networkx as nx
import sys
import random
import numpy as np
import csv
import json
import os

# Limit generacji
DEFAULT_LIMIT = 5000
STATS_FILE = "statystyki_populacji.csv"
BEST_RESULT_FILE = "najlepszy_wynik.json"  # Zmiana rozszerzenia na .json

def get_integrality_energy(adj_matrix):
    """
    Oblicza energię oraz zwraca spektrum.
    """
    try:
        # Weryfikacja spójności
        G_temp = nx.from_numpy_array(adj_matrix)
        if not nx.is_connected(G_temp):
            return 1000.0, []

        eigenvalues = np.linalg.eigvalsh(adj_matrix)
        # Energia = suma odległości od najbliższej liczby całkowitej
        energy = sum(abs(ev - round(ev)) for ev in eigenvalues)
        return energy, eigenvalues

    except np.linalg.LinAlgError:
        return float('inf'), []

def select_edges_probabilistically(n, k, pheromones):
    rows, cols = np.triu_indices(n, k=1)
    probs = pheromones[rows, cols]
    
    prob_sum = probs.sum()
    if prob_sum == 0:
        probs = np.ones_like(probs) / len(probs)
    else:
        probs = probs / prob_sum
    
    selected_indices = np.random.choice(len(rows), size=k, replace=False, p=probs)
    
    adj = np.zeros((n, n), dtype=int)
    adj[rows[selected_indices], cols[selected_indices]] = 1
    adj = adj + adj.T
    return adj

def save_best_result(adj, energy, spectrum, generation, filename):
    """
    Zapisuje graf wraz ze szczegółowymi parametrami do pliku JSON.
    """
    n = adj.shape[0]
    G = nx.from_numpy_array(adj)
    g6 = nx.to_graph6_bytes(G, header=False).decode('ascii').strip()
    
    # Czy jest całkowity? (z tolerancją błędu numerycznego)
    is_integral = bool(energy < 1e-9)
    
    # "W jakim stopniu?" - Średnie odchylenie na jedną wartość własną
    # Im bliżej 0, tym bardziej "całkowity" jest graf.
    mean_deviation = energy / n if n > 0 else 0

    data = {
        "graph6": g6,
        "is_integral": is_integral,
        "energy_total": round(energy, 6),
        "mean_deviation": round(mean_deviation, 6), # Stopień "całkowitości"
        "generation_found": generation,
        "spectrum": [round(x, 4) for x in spectrum], # Zaokrąglenie dla czytelności JSON
        "nodes": int(n),
        "edges": int(np.sum(adj) // 2)
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    
    return data

def main():
    if len(sys.argv) < 3:
        print("Użycie: python3 generator.py <n> <k> [limit/seed]")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        k = int(sys.argv[2])
        arg3 = sys.argv[3] if len(sys.argv) > 3 else str(DEFAULT_LIMIT)
        
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

    ants_per_gen = 30
    evaporation_rate = 0.1
    pheromones = np.ones((n, n))
    
    best_global_energy = float('inf')
    
    # Inicjalizacja pliku statystyk
    with open(STATS_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Generation", "MinEnergy", "AvgEnergy", "StdDevEnergy"])

    print(f"Start: n={n}, k={k}. Wyniki w: {BEST_RESULT_FILE}")

    generation = 0
    no_improvement = 0

    while generation < limit:
        population_results = []
        
        for _ in range(ants_per_gen):
            adj = select_edges_probabilistically(n, k, pheromones)
            energy, spectrum = get_integrality_energy(adj)
            population_results.append({
                "adj": adj,
                "energy": energy,
                "spectrum": spectrum
            })

        population_results.sort(key=lambda x: x["energy"])
        best_ant = population_results[0]
        
        # Logowanie statystyk
        energies = [p["energy"] for p in population_results if p["energy"] < 900]
        if not energies: energies = [1000.0]
        
        with open(STATS_FILE, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([generation, np.min(energies), np.mean(energies), np.std(energies)])

        # Sprawdzenie rekordu
        if best_ant["energy"] < best_global_energy:
            best_global_energy = best_ant["energy"]
            no_improvement = 0
            
            # ZAPIS ROZSZERZONYCH PARAMETRÓW
            saved_data = save_best_result(
                best_ant["adj"], 
                best_ant["energy"], 
                best_ant["spectrum"], 
                generation, 
                BEST_RESULT_FILE
            )
            
            print(f"GEN {generation}: Nowy rekord! Energia: {best_global_energy:.5f}")
            print(f" -> Stopień całkowitości (odchylenie/wierzchołek): {saved_data['mean_deviation']:.5f}")
            
            if best_global_energy < 1e-9:
                print("!!! ZNALEZIONO GRAF CAŁKOWITY !!!")
        else:
            no_improvement += 1

        # Aktualizacja feromonów
        pheromones *= (1.0 - evaporation_rate)
        top_elite = population_results[:4]
        for ant in top_elite:
            if ant["energy"] > 900: continue
            deposit = 1.0 / (ant["energy"] + 0.1)
            pheromones += (ant["adj"] * deposit) * 0.3
        pheromones = np.clip(pheromones, 0.05, 20.0)

        if no_improvement > 300:
            pheromones = np.ones((n, n))
            no_improvement = 0
        
        generation += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrzerwano.")