#!/usr/bin/env python3
import networkx as nx
import sys
import random
import numpy as np

# Domyślny limit iteracji, jeśli nie podano w argumentach
DEFAULT_LIMIT = 500000 

def get_integrality_energy(adj_matrix):
    """
    Oblicza funkcję celu (energię niecałkowitości).
    E(G) = suma odległości wartości własnych od liczb całkowitych.
    Zawiera mechanizm penalty function (kara 1000.0) dla grafów niespójnych.
    """
    try:
        # Weryfikacja spójności grafu (constraint checking)
        G_temp = nx.from_numpy_array(adj_matrix)
        
        if not nx.is_connected(G_temp):
            # Wysoka kara wymuszająca odrzucenie rozwiązań niespójnych
            return 1000.0
            
        # Obliczenie widma dla grafu spójnego
        eigenvalues = np.linalg.eigvalsh(adj_matrix)
        energy = sum(abs(ev - round(ev)) for ev in eigenvalues)
        return energy
        
    except np.linalg.LinAlgError:
        # Zabezpieczenie przed błędami numerycznymi biblioteki LAPACK
        return float('inf')

def swap_edge_matrix(matrix, n):
    """
    Operator sąsiedztwa (Neighborhood Operator).
    Generuje sąsiada poprzez usunięcie jednej istniejącej krawędzi 
    i dodanie jednej nowej w miejscu, gdzie jej nie było (zachowanie liczby krawędzi).
    """
    rows, cols = np.triu_indices(n, k=1)
    
    # Identyfikacja krawędzi istniejących i potencjalnych
    existing_edges = [(r, c) for r, c in zip(rows, cols) if matrix[r, c] == 1]
    non_edges = [(r, c) for r, c in zip(rows, cols) if matrix[r, c] == 0]
    
    if not existing_edges or not non_edges:
        return matrix, (0, 0, 0, 0)
    
    # Losowy wybór pary do zamiany
    u, v = random.choice(existing_edges)
    x, y = random.choice(non_edges)
    
    # Wykonanie ruchu (SWAP)
    matrix[u, v] = 0; matrix[v, u] = 0
    matrix[x, y] = 1; matrix[y, x] = 1
    
    # Zwraca zmodyfikowaną macierz oraz sygnaturę ruchu (do listy Tabu)
    return matrix, (u, v, x, y)

def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Użycie: python3 generator_Tabu_search.py <n> <k> [limit/seed]\n")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        k = int(sys.argv[2])
        
        # Parsowanie argumentów dla przetwarzania wsadowego (Batch Processing)
        arg3 = sys.argv[3] if len(sys.argv) > 3 else str(DEFAULT_LIMIT)
        package_id = arg3
        
        # Obsługa formatu SEED/LIMIT lub samego LIMITu
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

    # Inicjalizacja rozwiązania początkowego (Initial Solution)
    current_G = nx.gnm_random_graph(n, k)
    current_matrix = nx.to_numpy_array(current_G)
    best_energy = get_integrality_energy(current_matrix)
    
    # Parametry Tabu Search
    tabu_list = []
    tabu_tenure = 18       # Długość pamięci krótkotrwałej (Short-term memory)
    max_no_imp = 2000      # Próg stagnacji dla restartu
    no_improvement_iter = 0
    
    iter_count = 0
    
    while iter_count < limit:
        # Generowanie kandydata w sąsiedztwie
        candidate_matrix = current_matrix.copy()
        candidate_matrix, move = swap_edge_matrix(candidate_matrix, n)
        
        candidate_energy = get_integrality_energy(candidate_matrix)
        
        is_tabu = move in tabu_list
        # Kryterium aspiracji (Aspiration Criterion) - akceptacja ruchu tabu, jeśli poprawia globalne optimum
        is_aspiration = candidate_energy < best_energy 
        
        if (not is_tabu) or is_aspiration:
            current_matrix = candidate_matrix
            current_energy = candidate_energy
            
            # Aktualizacja listy Tabu (FIFO)
            tabu_list.append(move)
            if len(tabu_list) > tabu_tenure:
                tabu_list.pop(0)
            
            # Aktualizacja najlepszego znalezionego rozwiązania
            if current_energy < best_energy:
                best_energy = current_energy
                no_improvement_iter = 0
            else:
                no_improvement_iter += 1
                
            # Przypadek 1: Znaleziono graf całkowity (lub bardzo bliski)
            if current_energy < 1e-7:
                G_out = nx.from_numpy_array(current_matrix)
                # Konwersja do graph6 bytes i dekodowanie (dla kompatybilności NetworkX 3.x)
                output = nx.to_graph6_bytes(G_out, header=False).decode('ascii').strip()
                sys.stdout.write(output + '\n')
                sys.stdout.flush()
                
                # Restart po znalezieniu sukcesu
                current_G = nx.gnm_random_graph(n, k)
                current_matrix = nx.to_numpy_array(current_G)
                best_energy = get_integrality_energy(current_matrix)
                tabu_list = []
                no_improvement_iter = 0

            # Przypadek 2: Znaleziono minimum lokalne o niskiej energii
            elif current_energy < 0.9:
                G_out = nx.from_numpy_array(current_matrix)
                g6 = nx.to_graph6_bytes(G_out, header=False).decode('ascii').strip()
                
                # Logowanie diagnostyczne do stderr
                sys.stderr.write(f"PACZKA {package_id} ENERGY {current_energy:.5f} {g6}\n")
                sys.stderr.flush()

        else:
            no_improvement_iter += 1

        # Mechanizm Dywersyfikacji (Restart) w przypadku stagnacji
        if no_improvement_iter > max_no_imp:
            current_G = nx.gnm_random_graph(n, k)
            current_matrix = nx.to_numpy_array(current_G)
            best_energy = get_integrality_energy(current_matrix)
            tabu_list = []
            no_improvement_iter = 0
            
        iter_count += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Obsługa przerwania (Ctrl+C)
        pass
    except BrokenPipeError:
        sys.stderr.close()