import networkx as nx
import numpy as np

# --- WKLEJ TUTAJ SWÓJ STRING ---
g6_string = "N@rIASH_CP_Z@Hr~_?g" 
# np. g6_string = "N??..."
# -------------------------------

# Wczytanie grafu
try:
    G = nx.from_graph6_bytes(g6_string.encode('ascii'))
except ValueError:
    print("Błąd: Źle skopiowany string graph6!")
    exit()

print(f"--- ANALIZA GRAFU ---")
print(f"Liczba wierzchołków: {G.number_of_nodes()}")
print(f"Liczba krawędzi: {G.number_of_edges()}")

# 1. Sprawdzenie spójności
is_connected = nx.is_connected(G)
print(f"\nCZY JEST SPÓJNY? -> {'TAK' if is_connected else 'NIE (!!!)'}")

# 2. Jeśli niespójny, analiza kawałków
if not is_connected:
    components = [G.subgraph(c).copy() for c in nx.connected_components(G)]
    print(f"Znaleziono {len(components)} rozłączne składowe.")
    
    total_energy = 0
    
    for i, comp in enumerate(components):
        n_comp = comp.number_of_nodes()
        e_comp = comp.number_of_edges()
        
        # Oblicz widmo kawałka
        eigenvalues = np.linalg.eigvalsh(nx.adjacency_matrix(comp).todense())
        
        # Sprawdź błędy (ile brakuje do całkowitej)
        errors = [abs(ev - round(ev)) for ev in eigenvalues]
        comp_energy = sum(errors)
        total_energy += comp_energy
        
        print(f"\n  [Składowa #{i+1}]")
        print(f"  Nodes: {n_comp}, Edges: {e_comp}")
        print(f"  Widmo: {np.round(eigenvalues, 3)}")
        
        if comp_energy < 1e-7:
            print(f"  STATUS: CAŁKOWITA! (Energia = 0.0)")
        else:
            print(f"  STATUS: BŁĘDNA (Energia = {comp_energy:.5f})")
            print(f"  To tu jest problem!")

    print(f"\nSuma energii wszystkich kawałków: {total_energy:.5f}")