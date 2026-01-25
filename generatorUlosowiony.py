import networkx as nx
import numpy as np
import random
import math
import sys
import signal

# Obsługa przerwania Ctrl+C bez błędów
def signal_handler(sig, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# --- FUNKCJE POMOCNICZE (SZYBKIE) ---

def get_eigenvalues(G):
    # Używamy numpy array zamiast matrix (szybciej i bez warningów)
    try:
        A = nx.to_numpy_array(G)
        return np.linalg.eigvalsh(A)
    except:
        return []

def calculate_energy(eigenvalues):
    if len(eigenvalues) == 0: return float('inf')
    # Energia = suma odległości od liczb całkowitych
    return sum(abs(lam - round(lam)) for lam in eigenvalues)

def get_random_neighbor_swap(G):
    # Szybka wersja swapowania krawędzi
    G_new = G.copy()
    edges = list(G_new.edges())
    if not edges: return G_new
    
    # 1. Usuń losową krawędź
    u, v = random.choice(edges)
    G_new.remove_edge(u, v)
    
    # 2. Dodaj losową krawędź (szukamy dziury losując, zamiast generować listę wszystkich)
    nodes = list(G_new.nodes())
    while True:
        x, y = random.sample(nodes, 2)
        if not G_new.has_edge(x, y):
            G_new.add_edge(x, y)
            break
    return G_new

def simulated_annealing(n, k, max_steps=2000, initial_temp=1.5):
    current_G = nx.gnm_random_graph(n, k)
    
    # Jeśli startowy niespójny, trudno, SA może go naprawi, 
    # albo odrzucimy go na końcu.
    
    current_vals = get_eigenvalues(current_G)
    current_energy = calculate_energy(current_vals)
    temp = initial_temp
    
    for step in range(max_steps):
        # Jeśli energia ~ 0, znaleźliśmy graf całkowity!
        if current_energy < 1e-9:
            return current_G
        
        neighbor_G = get_random_neighbor_swap(current_G)
        neighbor_vals = get_eigenvalues(neighbor_G)
        neighbor_energy = calculate_energy(neighbor_vals)
        
        delta_E = neighbor_energy - current_energy

        if delta_E < 0 or random.random() < math.exp(-delta_E / temp):
            current_G = neighbor_G
            current_energy = neighbor_energy
            
        temp *= 0.99
        if temp < 0.001: temp = initial_temp * 0.5 # Reheating

    # Zwracamy graf końcowy (nawet jak nie jest idealny - sito5 go oceni)
    # W wersji SA zazwyczaj interesują nas tylko sukcesy, ale tu zwracamy wynik procesu.
    return current_G

# --- MAIN ---

def main():
    if len(sys.argv) < 4:
        # Fallback jeśli uruchamiasz ręcznie bez parametrów
        sys.stderr.write("Użycie: python3 generatorUlosowiony.py <n> <k> <seed_part/total> <limit>\n")
        sys.exit(1)

    n = int(sys.argv[1])
    k = int(sys.argv[2])
    
    # Obsługa formatu res/mod dla seeda
    seed_arg = sys.argv[3]
    limit = int(sys.argv[4]) # To jest parametr 't' z basha

    if '/' in seed_arg:
        parts = seed_arg.split('/')
        res = int(parts[0])
        # Ustawiamy seed w oparciu o numer paczki (res), żeby każda była inna
        random.seed(res)
    else:
        random.seed(int(seed_arg))

    # Pętla generująca
    for _ in range(limit):
        # Uruchamiamy proces wyżarzania
        # max_steps można dostosować (mniej = szybciej, ale mniejsza szansa na sukces)
        result_G = simulated_annealing(n, k, max_steps=2500)
        
        if result_G is not None:
            # Wypisujemy wynik w formacie graph6
            # Sito5 sprawdzi, czy graf jest faktycznie całkowity
            try:
                output = nx.to_graph6_bytes(result_G, header=False).decode('ascii').strip()
                print(output)
                sys.stdout.flush()
            except BrokenPipeError:
                sys.exit(0)

if __name__ == "__main__":
    main()