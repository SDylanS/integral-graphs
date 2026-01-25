#!/bin/bash
# KTZ 2025 - Tabu Search wrapper
#./tabu_search.sh 15 37 $((2**29)) 0 
 
n=$1
e=$2
mod=$3
pierwszy=$4
t=640000
 
echo czas: $(date)  
 
for (( res=$pierwszy; res < $mod ; res+=1 ))
do 
 echo "time python3 generator_Tabu_search.py $n $e $res/$mod 2>/dev/null | ./sito5 $t | tee -a wynikTabu$n_$e.txt"
 echo "./checkTabu.sh $n $e $mod $res" > tabu_todo$n_$e.sh
 time python3 generator_Tabu_search.py $n $e $res/$mod 2>/dev/null | ./sito5 $t | tee -a wynikTabu$n_$e.txt
done 
 
echo czas: $(date) 
echo "# wszystko zrobione " > tabu_todo$n_$e.sh