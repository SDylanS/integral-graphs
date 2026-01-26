#!/bin/bash
# KTZ 2025 - Algorytm Mrowkowy (ACO) wrapper
# Użycie: ./mrowkowy.sh <n> <k> <mod> <start>
# Np.: ./mrowkowy.sh 15 37 $((2**29)) 0

n=$1
e=$2
mod=$3
pierwszy=$4

# Limit generacji
t=20000

echo czas: $(date)  
echo "Start generatora mrowkowego dla N=$n K=$e..."

for (( res=$pierwszy; res < $mod ; res+=1 ))
do 
 # Wywołujemy nowy plik: generatorMrowkowy.py
 # Wynik zapisujemy do: wynikMrowkowy...
 echo "time python3 generatorMrowkowy.py $n $e $res/$mod 2>/dev/null | ./sito5 $t | tee -a wynikMrowkowy$n_$e.txt"
 echo "./checkMrowkowy.sh $n $e $mod $res" > mrowkowy_todo$n_$e.sh
 
 time python3 generatorMrowkowy.py $n $e $res/$mod 2>/dev/null | ./sito5 $t | tee -a wynikMrowkowy$n_$e.txt
done 

echo czas: $(date) 
echo "# wszystko zrobione " > mrowkowy_todo$n_$e.sh