# import networkx as nx
# import matplotlib.pyplot as plt

# grafy_g6 = [
#     "N@rIASH_CP_Z@Hr~_?g"
# ]

# for i, g6 in enumerate(grafy_g6):
#     G = nx.from_graph6_bytes(g6.encode('ascii'))
#     plt.figure(figsize=(6, 6))
#     pos = nx.circular_layout(G) 
#     nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500)
#     plt.title(f"Graf Całkowity #{i+1}")
#     plt.savefig(f"graf_{i+1}.png")
#     print(f"Wygenerowano graf_{i+1}.png")

import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Nazwa pliku z danymi (musi być taka sama jak w skrypcie generującym)
FILE_NAME = "statystyki_populacji.csv"

def main():
    if not os.path.exists(FILE_NAME):
        print(f"Błąd: Nie znaleziono pliku '{FILE_NAME}'. Uruchom najpierw symulację.")
        return

    # 1. Wczytanie danych za pomocą Pandas
    print("Wczytywanie danych...")
    try:
        df = pd.read_csv(FILE_NAME)
    except Exception as e:
        print(f"Błąd odczytu CSV: {e}")
        return

    if df.empty:
        print("Plik jest pusty.")
        return

    # 2. Konfiguracja wykresu
    plt.figure(figsize=(12, 7))
    plt.title("Ewolucja populacji mrówek (Poszukiwanie grafu całkowitego)", fontsize=16)
    plt.xlabel("Generacja", fontsize=12)
    plt.ylabel("Energia (Mniejsza = Lepsza)", fontsize=12)

    # 3. Rysowanie linii
    # Linia średniej energii populacji
    plt.plot(df['Generation'], df['AvgEnergy'], 
             label='Średnia energia populacji', 
             color='blue', alpha=0.6, linewidth=1)

    # Linia najlepszej energii (minimum)
    plt.plot(df['Generation'], df['MinEnergy'], 
             label='Najlepszy osobnik (Min)', 
             color='red', linewidth=2)

    # 4. Cieniowanie odchylenia standardowego (pokazuje różnorodność populacji)
    # Im szerszy pasek, tym bardziej mrówki "szukają" w różnych miejscach.
    # Im węższy, tym bardziej populacja jest zgodna (zbieżność).
    plt.fill_between(df['Generation'], 
                     df['AvgEnergy'] - df['StdDevEnergy'], 
                     df['AvgEnergy'] + df['StdDevEnergy'], 
                     color='blue', alpha=0.1, label='Odchylenie standardowe (Różnorodność)')

    # 5. Opcjonalnie: Skala logarytmiczna
    # Jeśli energia spada bardzo nisko (blisko 0), odkomentuj poniższą linię:
    # plt.yscale('log')

    # Dodatki wizualne
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend(fontsize=12)
    plt.tight_layout()

    # 6. Wyświetlenie
    print("Generowanie wykresu...")
    plt.show()

if __name__ == "__main__":
    main()