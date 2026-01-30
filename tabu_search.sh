#!/bin/bash
# KTZ 2025 - Tabu Search (Spectral Energy version)
trap "exit" INT
# Użycie: ./tabu_search.sh <n> <k> <mod> <start>

n=$1
e=$2
mod=$3
pierwszy=$4

# Liczba iteracji wewnątrz skryptu Python
t=500000

echo czas: $(date)  
echo "Start Tabu Search (Energy minimization) dla N=$n K=$e..."

for (( res=$pierwszy; res < $mod ; res+=1 ))
do 
    # Logika potoków:
    # 1. stdout -> leci do sito5 (sprawdza poprawność) -> tee (zapisuje sukcesy)
    # 2. stderr -> leci do pliku bliskie_tabu.txt (zapisuje grafy o niskiej energii)
    
    cmd="python3 generator_Tabu_search.py $n $e $res/$mod"
    
    echo "time $cmd 2>> bliskie_tabu.txt | ./sito5 $t | tee -a wynikTabu$n_$e.txt"
    echo "./checkTabu.sh $n $e $mod $res" > tabu_todo$n_$e.sh
 
    time $cmd 2>> bliskie_tabu.txt | ./sito5 $t | tee -a wynikTabu$n_$e.txt

done 
 
echo czas: $(date) 
echo "# wszystko zrobione " > tabu_todo$n_$e.sh