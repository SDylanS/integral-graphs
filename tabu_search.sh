#!/bin/bash

# ==========================================
# Skrypt uruchamiający generator Tabu Search
# ==========================================

# Parametry domyślne (można edytować)
N_VERTICES=8          # Liczba wierzchołków
OUTPUT_FILE="wynik_tabu.g6"
ITERATIONS=2000       # Ile prób wykonać
TABU_SIZE=15          # Jak długo pamiętać zabronione ruchy

# Sprawdzenie zależności
if ! python3 -c "import numpy, networkx" &> /dev/null; then
    echo "[BLAD] Brakuje bibliotek Pythona."
    echo "Zainstaluj: pip install numpy networkx"
    exit 1
fi

echo "--- Uruchamianie Tabu Search ---"
echo "Szukam grafu całkowitego dla N=$N_VERTICES..."

# Uruchomienie skryptu Python z poprawną nazwą
python3 generator_Tabu_search.py \
    $N_VERTICES \
    $OUTPUT_FILE \
    --iter $ITERATIONS \
    --tabu $TABU_SIZE

# Sprawdzenie wyniku
if [ $? -eq 0 ]; then
    echo "--- Sukces ---"
    echo "Zawartość pliku $OUTPUT_FILE:"
    cat $OUTPUT_FILE
else
    echo "[BLAD] Wystąpił błąd podczas wykonywania skryptu Python."
fi