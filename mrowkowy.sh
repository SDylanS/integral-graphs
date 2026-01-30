#!/bin/bash
# KTZ 2025 - Algorytm Mrowkowy (ACO) wrapper
# Użycie: ./mrowkowy.sh <n> <k> <mod> <start>

# Pułapka na Ctrl+C (zabija skrypt natychmiast)
trap "exit" INT

n=$1
e=$2
mod=$3
pierwszy=$4

# Limit generacji (20k generacji * 25 mrówek = 500k prób, porównywalne z Tabu)
t=20000

echo czas: $(date)  
echo "Start ACO (Energy minimization) dla N=$n K=$e..."

for (( res=$pierwszy; res < $mod ; res+=1 ))
do 
    cmd="python3 generatorMrowkowy.py $n $e $res/$mod"
    
    # stdout -> sito5 (wyniki idealne)
    # stderr -> plik bliskie_mrowki.txt (analiza minimów lokalnych)
    
    echo "time $cmd 2>> bliskie_mrowki.txt | ./sito5 $t | tee -a wynikMrowkowy$n_$e.txt"
    echo "./checkMrowkowy.sh $n $e $mod $res" > mrowkowy_todo$n_$e.sh
 
    time $cmd 2>> bliskie_mrowki.txt | ./sito5 $t | tee -a wynikMrowkowy$n_$e.txt
done 

echo czas: $(date) 
echo "# wszystko zrobione " > mrowkowy_todo$n_$e.sh