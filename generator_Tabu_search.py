import argparse
import random
import numpy as np
import networkx as nx
import sys

# --- KONFIGURACJA LOGIKI TABU SEARCH ---

def objective_function(adj_matrix):
    """
    Funkcja celu dla grafów całkowitych (Integral Graphs).
    Oblicza sumę odchyleń wartości własnych od najbliższej liczby całkowitej.
    0.0 = graf całkowity.
    """
    # Obliczamy wartości własne (eigenvalues) dla macierzy symetrycznej
    eigenvalues = np.linalg.eigvalsh(adj_matrix)
    
    # Koszt to suma różnic między wartością własną a jej zaokrągleniem
    cost = sum(abs(ev - round(ev)) for ev in eigenvalues)
    return cost

def get_neighbors_random_subset(n, sample_size=20):
    """
    Zwraca losowy podzbiór możliwych ruchów (par wierzchołków), 
    aby przyspieszyć działanie dla większych grafów.
    """
    moves = []
    # Generujemy losowe pary (u, v)
    for _ in range(sample_size):
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        while u == v:
            v = random.randint(0, n - 1)
        # Sortujemy, żeby (u,v) było to samo co (v,u)
        if u > v:
            u, v = v, u
        moves.append((u, v))
    # Usuwamy duplikaty
    return list(set(moves))

def flip_edge(adj_matrix, u, v):
    """Zwraca nową macierz z odwróconą krawędzią między u i v"""
    new_matrix = adj_matrix.copy()
    val = 1 - new_matrix[u, v]
    new_matrix[u, v] = val
    new_matrix[v, u] = val
    return new_matrix

def tabu_search(n_vertices, max_iter, tabu_tenure):
    # 1. Inicjalizacja: Losowy graf
    current_matrix = np.random.randint(0, 2, (n_vertices, n_vertices))
    np.fill_diagonal(current_matrix, 0)
    # Symetryzacja
    current_matrix = np.tril(current_matrix) + np.tril(current_matrix, -1).T
    
    best_matrix = current_matrix.copy()
    current_score = objective_function(current_matrix)
    best_score = current_score
    
    tabu_list = [] # Lista par (u, v), które są 'zablokowane'
    
    print(f"Start Tabu Search | N={n_vertices} | Iter={max_iter} | TabuLen={tabu_tenure}")
    
    for it in range(1, max_iter + 1):
        # Pobieramy próbkę sąsiadów (dla szybkości nie sprawdzamy wszystkich N*(N-1)/2)
        # Dla małych grafów można zwiększyć sample_size
        moves = get_neighbors_random_subset(n_vertices, sample_size=int(n_vertices * 2))
        
        best_neighbor_matrix = None
        best_neighbor_score = float('inf')
        move_to_tabu = None
        found_move = False
        
        for (u, v) in moves:
            neighbor = flip_edge(current_matrix, u, v)
            score = objective_function(neighbor)
            
            # Sprawdzenie statusu Tabu
            is_tabu = (u, v) in tabu_list
            
            # Kryterium aspiracji: akceptujemy Tabu tylko jeśli wynik jest lepszy niż GLOBALNE optimum
            if (not is_tabu) or (score < best_score):
                if score < best_neighbor_score:
                    best_neighbor_matrix = neighbor
                    best_neighbor_score = score
                    move_to_tabu = (u, v)
                    found_move = True

        # Jeśli nie znaleziono ruchu w wylosowanej próbce, idziemy dalej
        if not found_move:
            continue

        # Aktualizacja bieżącego stanu
        current_matrix = best_neighbor_matrix
        current_score = best_neighbor_score
        
        # Aktualizacja najlepszego globalnie
        if current_score < best_score:
            best_score = current_score
            best_matrix = current_matrix.copy()
            # print(f"Iter {it}: Nowy najlepszy koszt = {best_score:.4f}")
            
            # Jeśli graf jest idealnie całkowity
            if best_score < 1e-7:
                print(f"ZNALEZIONO GRAF CAŁKOWITY w iteracji {it}!")
                break

        # Aktualizacja listy Tabu
        tabu_list.append(move_to_tabu)
        if len(tabu_list) > tabu_tenure:
            tabu_list.pop(0)

    return best_matrix, best_score

def save_to_graph6(adj_matrix, filename):
    """Konwersja macierzy numpy do formatu graph6 i zapis do pliku"""
    G = nx.from_numpy_array(adj_matrix)
    # Header=False jest ważne, żeby inne narzędzia (np. labelg) to czytały bez problemów
    g6_string = nx.to_graph6_bytes(G, header=False).decode("ascii").strip()
    
    with open(filename, "w") as f:
        f.write(g6_string + "\n")
    print(f"Wynik zapisano w: {filename}")

# --- URUCHOMIENIE ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int, help="Liczba wierzchołków")
    parser.add_argument("output_file", type=str, help="Ścieżka do pliku wynikowego")
    parser.add_argument("--iter", type=int, default=1000, help="Max iteracji")
    parser.add_argument("--tabu", type=int, default=10, help="Długość listy tabu")

    args = parser.parse_args()

    # Uruchomienie algorytmu
    result_matrix, final_score = tabu_search(args.n, args.iter, args.tabu)
    
    # Zapis wyniku
    save_to_graph6(result_matrix, args.output_file)