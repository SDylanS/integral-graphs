#!/usr/bin/env python3
import networkx as nx
import sys
import random
import numpy as np

# Limit iteracji
DEFAULT_LIMIT = 500000 

def get_integrality_energy(adj_matrix):
    eigenvalues = np.linalg.eigvalsh(adj_matrix)
    energy = sum(abs(ev - round(ev)) for ev in eigenvalues)
    return energy

def swap_edge_matrix(matrix, n):
    rows, cols = np.triu_indices(n, k=1)
    existing_edges = [(r, c) for r, c in zip(rows, cols) if matrix[r, c] == 1]
    non_edges = [(r, c) for r, c in zip(rows, cols) if matrix[r, c] == 0]
    
    if not existing_edges or not non_edges:
        return matrix, (0, 0, 0, 0)
    
    u, v = random.choice(existing_edges)
    x, y = random.choice(non_edges)
    
    matrix[u, v] = 0; matrix[v, u] = 0
    matrix[x, y] = 1; matrix[y, x] = 1
    
    return matrix, (u, v, x, y)

def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Użycie: python3 generator_Tabu_search.py <n> <k> [limit/seed]\n")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        k = int(sys.argv[2])
        
        # --- ZMIANA 1: Zapisujemy ID paczki do zmiennej ---
        arg3 = sys.argv[3] if len(sys.argv) > 3 else str(DEFAULT_LIMIT)
        package_id = arg3  # <--- Zapamiętujemy to (np. "25/536870912")
        
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

    current_G = nx.gnm_random_graph(n, k)
    current_matrix = nx.to_numpy_array(current_G)
    best_energy = get_integrality_energy(current_matrix)
    
    tabu_list = []
    tabu_tenure = 18       
    max_no_imp = 2000      
    no_improvement_iter = 0
    iter_count = 0
    
    while iter_count < limit:
        candidate_matrix = current_matrix.copy()
        candidate_matrix, move = swap_edge_matrix(candidate_matrix, n)
        candidate_energy = get_integrality_energy(candidate_matrix)
        
        is_tabu = move in tabu_list
        is_aspiration = candidate_energy < best_energy 
        
        if (not is_tabu) or is_aspiration:
            current_matrix = candidate_matrix
            current_energy = candidate_energy
            tabu_list.append(move)
            if len(tabu_list) > tabu_tenure:
                tabu_list.pop(0)
            
            if current_energy < best_energy:
                best_energy = current_energy
                no_improvement_iter = 0
            else:
                no_improvement_iter += 1
                
            if current_energy < 1e-7:
                G_out = nx.from_numpy_array(current_matrix)
                # stdout bez zmian (dla sito5)
                output = nx.to_graph6_bytes(G_out, header=False).decode('ascii').strip()
                sys.stdout.write(output + '\n')
                sys.stdout.flush()
                
                # Restart
                current_G = nx.gnm_random_graph(n, k)
                current_matrix = nx.to_numpy_array(current_G)
                best_energy = get_integrality_energy(current_matrix)
                tabu_list = []
                no_improvement_iter = 0

            # --- ZMIANA 2: Dodajemy package_id do wypisu ---
            elif current_energy < 0.9:
                G_out = nx.from_numpy_array(current_matrix)
                g6 = nx.to_graph6_bytes(G_out, header=False).decode('ascii').strip()
                
                # Format: PACZKA [ID] ENERGY [WARTOŚĆ] [GRAPH6]
                sys.stderr.write(f"PACZKA {package_id} ENERGY {current_energy:.5f} {g6}\n")
                sys.stderr.flush()

        else:
            no_improvement_iter += 1

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
        pass
    except BrokenPipeError:
        sys.stderr.close()