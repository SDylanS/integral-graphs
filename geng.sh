#!/bin/bash
# KTZ 2025 
# plik: calkowite15.sh
#./calkowite15.sh 15 37 $((2**29)) 0

n=$1
e=$2
mod=$3
pierwszy=$4
t=640000
 
echo czas: $(date)  
 
for (( res=$pierwszy; res < $mod ; res+=1 ))
do 
 echo "time geng -c $n $e:$e $res/$mod 2>/dev/null | ./sito5 $t | tee -a wynik$n_$e.txt"
 echo "./calkowite15.sh $n $e $mod $res" > ktz2025_todo$n_$e.sh
 time geng -c $n $e:$e $res/$mod 2>/dev/null | ./sito5 $t | tee -a wynik$n_$e.txt
done 
 
echo czas: $(date) 
echo "# wszystko zrobione " > ktz2025_todo$n_$e.sh