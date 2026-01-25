import networkx as nx
import numpy as np
import random
import sys
import signal

# --- KONFIGURACJA ---
# Ile sąsiadów sprawdzamy w jednym kroku (zgodnie z Twoim kodem)
NEIGHBORS_TO_CHECK = 20 

# Obsługa Ctrl+C (czyste wyjście)
def signal_handler(sig, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# --- FUNKCJE POMOCNICZE ---

def get_eigenvalues(G):
    # SZYBKA METODA (NumPy array)
    try:
        A = nx.to_numpy_array(G)
        return np.linalg.eigvalsh(A)
    except:
        return []

def calculate_energy(eigenvalues):
    if len(eigenvalues) == 0: return float('inf')
    # Suma odległości od najbliższej liczby całkowitej
    return sum(abs(lam - round(lam)) for lam in eigenvalues)

def get_random_neighbor_copy(G):
    """
    Tworzy kopię grafu i modyfikuje jedną krawędź (swap).
    Zoptymalizowane: nie tworzy listy non_edges.
    """
    G_new = G.copy()
    edges = list(G_new.edges())
    
    # Jeśli graf pusty lub pełny, nic nie robimy
    if not edges: return G_new
    
    # 1. Usuń losową krawędź
    u, v = random.choice(edges)
    G_new.remove_edge(u, v)
    
    # 2. Dodaj losową krawędź (metoda próbkowania)
    nodes = list(G_new.nodes())
    # Próbujemy znaleźć dziurę (brakującą krawędź)
    # W rzadkich grafach trafimy niemal natychmiast.
    for _ in range(50): # Limit prób, żeby nie wisieć w pętli
        x, y = random.sample(nodes, 2)
        if not G_new.has_edge(x, y):
            G_new.add_edge(x, y)
            break
            
    return G_new

def greedy_search(n, k, max_steps=100):
    """
    Algorytm wspinaczkowy (Hill Climbing) - wersja 'First Choice' lub 'Best of N'.
    Tutaj: Best of 20 random neighbors.
    """
    current_G = nx.gnm_random_graph(n, k)
    current_vals = get_eigenvalues(current_G)
    current_energy = calculate_energy(current_vals)

    for step in range(max_steps):
        # Sprawdzenie sukcesu
        if current_energy < 1e-9:
            return current_G, step
        
        # Szukamy najlepszego sąsiada
        best_neighbor = None
        best_neighbor_energy = float('inf')
        
        # Generujemy N kandydatów i wybieramy najlepszego
        for _ in range(NEIGHBORS_TO_CHECK):
            cand_G = get_random_neighbor_copy(current_G)
            cand_vals = get_eigenvalues(cand_G)
            cand_en = calculate_energy(cand_vals)
            
            if cand_en < best_neighbor_energy:
                best_neighbor_energy = cand_en
                best_neighbor = cand_G
        
        # Decyzja o ruchu (tylko jeśli polepsza wynik - zachłanność)
        if best_neighbor_energy < current_energy:
            current_G = best_neighbor
            current_energy = best_neighbor_energy
            # W tym wariancie (Strict Hill Climbing) nie akceptujemy gorszych
        else:
            # Utknęliśmy w lokalnym minimum
            # Możemy tu przerwać (return None) lub dać szansę na 'sideways move'
            # Dla wydajności przerywamy, bo startujemy od nowa w pętli głównej
            return None, step
            
    return None, max_steps

# --- MAIN ---
def main():
    if len(sys.argv) < 4:
        sys.stderr.write("Użycie: python3 generatorZachlanny.py <n> <k> <seed_arg> <attempts>\n")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        k = int(sys.argv[2])
        seed_arg = sys.argv[3]
        attempts = int(sys.argv[4])
    except ValueError:
        sys.exit(1)

    # Obsługa seeda (res/mod)
    if '/' in seed_arg:
        parts = seed_arg.split('/')
        seed_val = int(parts[0])
        random.seed(seed_val)
    else:
        random.seed(int(seed_arg))

    # Pętla prób
    for _ in range(attempts):
        # max_steps=100 wystarczy, zachłanny szybko utyka w minimum lokalnym
        found_G, steps = greedy_search(n, k, max_steps=100)
        
        if found_G:
            # Sukces -> graph6 na stdout
            try:
                out = nx.to_graph6_bytes(found_G, header=False).decode('ascii').strip()
                print(out)
                sys.stdout.flush()
            except BrokenPipeError:
                sys.exit(0)

if __name__ == "__main__":
    main()