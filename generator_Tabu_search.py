#!/usr/bin/env python3
import networkx as nx
import sys
import random
import numpy as np

# Domyślny limit iteracji, jeśli nie zostanie podany
DEFAULT_LIMIT = 640000

def get_eigen_cost(adj_matrix):
    """
    Oblicza koszt: suma odchyleń wartości własnych od liczb całkowitych.
    0.0 oznacza graf całkowity.
    """
    # Obliczamy wartości własne (macierz jest symetryczna/hermitowska)
    eigenvalues = np.linalg.eigvalsh(adj_matrix)
    # Koszt = suma odległości do najbliższej liczby całkowitej
    cost = sum(abs(ev - round(ev)) for ev in eigenvalues)
    return cost

def flip_edge_matrix(matrix, n):
    """Odwraca losową krawędź w macierzy sąsiedztwa (mutacja)"""
    u = random.randint(0, n - 1)
    v = random.randint(0, n - 1)
    while u == v:
        v = random.randint(0, n - 1)
    
    # Odwracamy (0->1 lub 1->0)
    val = 1 - matrix[u, v]
    matrix[u, v] = val
    matrix[v, u] = val
    return matrix, (u, v)

def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Użycie: python3 generator_Tabu_search.py <n> <k> [limit/seed]\n")
        sys.exit(1)

    n = int(sys.argv[1])
    k = int(sys.argv[2]) # Używamy k jako startowej liczby krawędzi

    # Argument 3: limit lub seed (format ułamkowy)
    arg3 = sys.argv[3] if len(sys.argv) > 3 else str(DEFAULT_LIMIT)
    
    limit = DEFAULT_LIMIT
    
    # Logika obsługi seeda/limitu (identyczna jak w gnk)
    if '/' in arg3:
        parts = arg3.split('/')
        seed_val = int(parts[0])
        random.seed(seed_val)
        np.random.seed(seed_val)
    else:
        limit = int(arg3)
        random.seed()
        np.random.seed(None)

    # --- INICJALIZACJA TABU SEARCH ---
    # Tworzymy startowy graf losowy o zadanej gęstości
    current_G = nx.gnm_random_graph(n, k)
    current_matrix = nx.to_numpy_array(current_G)
    
    best_cost = get_eigen_cost(current_matrix)
    
    tabu_list = []
    tabu_len = 15  # Długość pamięci Tabu
    
    count = 0

    # Pętla generująca/szukająca
    # W tym przypadku 'limit' traktujemy jako liczbę kroków algorytmu
    while count < limit:
        
        # 1. Wykonujemy ruch (prosta wersja: losowy sąsiad + tabu check)
        # Kopiujemy macierz, żeby sprawdzić ruch
        candidate_matrix = current_matrix.copy()
        candidate_matrix, move = flip_edge_matrix(candidate_matrix, n)
        
        # Sprawdzamy koszt kandydata
        candidate_cost = get_eigen_cost(candidate_matrix)
        
        # Logika Tabu: Akceptujemy jeśli nie jest Tabu LUB jest lepszy niż cokolwiek co widzieliśmy (aspiracja)
        is_tabu = move in tabu_list
        
        if (not is_tabu) or (candidate_cost < best_cost - 0.001):
            # Akceptujemy ruch
            current_matrix = candidate_matrix
            
            # Aktualizacja Tabu
            tabu_list.append(move)
            if len(tabu_list) > tabu_len:
                tabu_list.pop(0)
                
            # Czy to graf całkowity? (Koszt bliski 0)
            if candidate_cost < 1e-7:
                # Konwersja do NetworkX dla graph6
                G_out = nx.from_numpy_array(current_matrix)
                
                # Wypisujemy w formacie graph6 BEZ nagłówka
                output = nx.to_graph6_string(G_out, header=False)
                sys.stdout.write(output + '\n')
                sys.stdout.flush() # Ważne przy pipe
                
                # Restartujemy szukanie z nowego losowego punktu, 
                # żeby nie wypisywać w kółko tego samego grafu
                current_G = nx.gnm_random_graph(n, k)
                current_matrix = nx.to_numpy_array(current_G)
                tabu_list = []
                best_cost = get_eigen_cost(current_matrix)
            
            # Aktualizacja najlepszego kosztu lokalnego
            if candidate_cost < best_cost:
                best_cost = candidate_cost

        # Co jakiś czas (np. co 1000 iteracji bez sukcesu) warto zrobić restart,
        # żeby nie utknąć w minimum lokalnym
        if count % 2000 == 0:
             current_G = nx.gnm_random_graph(n, k)
             current_matrix = nx.to_numpy_array(current_G)
             tabu_list = []
        
        count += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        # Obsługa zamknięcia potoku przez sito5/head
        sys.stderr.close()