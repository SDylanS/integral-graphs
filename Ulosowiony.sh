#!/bin/bash
# KTZ 2025 - Wersja SA (Symulowane Wyżarzanie)
# plik: ulosowiony.sh
# Użycie: ./ulosowiony.sh 15 37 1000 0

n=$1
e=$2
mod=$3       # Liczba paczek
pierwszy=$4  # Start (np. 0)

# UWAGA: Wyżarzanie jest wolne! 
# t to liczba uruchomień algorytmu SA w jednej paczce.
# Nie ustawiaj tu 640000, bo nigdy się nie skończy. 100-500 jest OK.
t=100 

echo czas: $(date)  

for (( res=$pierwszy; res < $mod ; res+=1 ))
do 
 # Wyświetlamy komendę (dla logów)
 echo "time python3 generatorUlosowiony.py $n $e $res/$mod $t 2>/dev/null | ./sito5 $t | tee -a wynikSA$n_$e.txt"
 
 # Tworzymy plik do wznawiania (checkpoint)
 echo "./ulosowiony.sh $n $e $mod $res" > sa_todo$n_$e.sh
 chmod +x sa_todo$n_$e.sh

 # WŁAŚCIWE URUCHOMIENIE
 # Przekazujemy res/mod (jako seed) oraz t (jako limit pętli)
 time python3 generatorUlosowiony.py $n $e $res/$mod $t 2>/dev/null | ./sito5 $t | tee -a wynikSA$n_$e.txt

done 

echo czas: $(date) 
echo "# wszystko zrobione " > sa_todo$n_$e.sh