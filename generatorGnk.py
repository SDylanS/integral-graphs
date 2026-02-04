#!/usr/bin/env python3
import networkx as nx
import sys
import random

# Domyślny limit prób w trybie wsadowym
DEFAULT_LIMIT = 640000

def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: python3 generatorGnk.py <n> <k> [limit/seed]\n")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        k = int(sys.argv[2]) # Liczba krawędzi (m)

        # Parsowanie argumentów operacyjnych (Batch ID lub Limit iteracji)
        arg3 = sys.argv[3] if len(sys.argv) > 3 else str(DEFAULT_LIMIT)
        
        limit = DEFAULT_LIMIT
        
        # Konfiguracja generatora liczb pseudolosowych (PRNG)
        if '/' in arg3:
            # Tryb deterministyczny: ziarno oparte na ID paczki (dla powtarzalności eksperymentu)
            parts = arg3.split('/')
            seed_val = int(parts[0])
            random.seed(seed_val)
        else:
            # Tryb stochastyczny: losowe ziarno systemowe, określony limit iteracji
            limit = int(arg3)
            random.seed() 

        count = 0

        # Pętla próbkowania przestrzeni grafów
        while count < limit:
            # Losowanie z modelu G(n, m) Erdősa-Rényiego (rozkład jednostajny)
            G = nx.gnm_random_graph(n, k)
            
            # Weryfikacja topologii (odrzucenie grafów niespójnych)
            if nx.is_connected(G):
                # Serializacja do formatu graph6 (kompatybilność z NetworkX 3.x)
                output = nx.to_graph6_bytes(G, header=False).decode('ascii').strip()
                sys.stdout.write(output + '\n')
            
            count += 1

    except ValueError:
        sys.stderr.write("Error: Invalid arguments provided.\n")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Obsługa sygnału SIGINT
        pass
    except BrokenPipeError:
        # Obsługa zamknięcia strumienia wyjściowego (np. przez head lub sito5)
        sys.stderr.close()