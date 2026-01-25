#!/bin/bash
# KTZ 2025 - Algorytm Zachłanny (Greedy)
# plik: zachlanny.sh
# Użycie: ./zachlanny.sh 15 37 1000 0

n=$1
e=$2
mod=$3       # Liczba paczek
pierwszy=$4  # Start (np. 0)

# t = ile prób algorytmu zachłannego w jednej paczce.
# 100 prób jest OK dla zachłannego (jest wolniejszy niż genrang, ale szybszy niż SA)
t=100 

echo czas: $(date)  

for (( res=$pierwszy; res < $mod ; res+=1 ))
do 
 # Wyświetlamy dokładnie tę komendę, która zaraz się wykona (styl z ulosowiony.sh)
 echo "time python3 generatorZachlanny.py $n $e $res/$mod $t 2>/dev/null | ./sito5 $t | tee -a wynikGreedy$n_$e.txt"
 
 # Tworzymy plik do wznawiania (checkpoint)
 echo "./zachlanny.sh $n $e $mod $res" > greedy_todo$n_$e.sh
 chmod +x greedy_todo$n_$e.sh

 # WŁAŚCIWE URUCHOMIENIE
 # Przekazujemy res/mod (seed) oraz t (liczbę prób)
 time python3 generatorZachlanny.py $n $e $res/$mod $t 2>/dev/null | ./sito5 $t | tee -a wynikGreedy$n_$e.txt

done 

echo czas: $(date) 
echo "# wszystko zrobione " > greedy_todo$n_$e.sh