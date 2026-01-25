#!/usr/bin/env python3
import networkx as nx
import sys
import random

# Domyślny limit, jeśli nie zostanie podany w argumencie
DEFAULT_LIMIT = 640000

def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Użycie: python3 generator_gnk.py <n> <k> [limit/seed]\n")
        sys.exit(1)

    n = int(sys.argv[1])
    k = int(sys.argv[2])

    # Argument 3: może być liczbą prób (z gnk.sh) lub seedem (ułamkiem)
    arg3 = sys.argv[3] if len(sys.argv) > 3 else str(DEFAULT_LIMIT)
    
    limit = DEFAULT_LIMIT
    
    # Logika obsługi argumentu (dostosowana do gnk.sh)
    if '/' in arg3:
        # Jeśli podano ułamek (styl geng), używamy go jako seeda
        parts = arg3.split('/')
        seed_val = int(parts[0])
        random.seed(seed_val)
    else:
        # Jeśli podano liczbę (styl gnk.sh), traktujemy to jako limit pętli
        limit = int(arg3)
        # Seed losujemy, żeby każda paczka była inna
        random.seed() 

    count = 0

    # Pętla generująca grafy
    while count < limit:
        # Generujemy losowy graf G(n, k)
        G = nx.gnm_random_graph(n, k)
        
        # Sprawdzamy spójność (jak w Twoim przykładzie)
        if nx.is_connected(G):
            # Wypisujemy w formacie graph6 BEZ nagłówka
            output = nx.to_graph6_string(G, header=False)
            sys.stdout.write(output + '\n')
        
        # Zliczamy próby (niezależnie czy graf był spójny, czy nie, 
        # żeby nie utknąć w nieskończoność przy rzadkich grafach)
        count += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        # Obsługa zamknięcia potoku przez sito5/head
        sys.stderr.close()