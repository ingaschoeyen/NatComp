#!/bin/bash

for i in $(seq 1 9);
do
    java -jar negsel2.jar -self lang/english.train -n 10 -r $i -c -l < lang/english.test > negresults$i
    java -jar negsel2.jar -self lang/english.train -n 10 -r $i -c -l < lang/middle-english.txt > posresults$i
    python3 auc.py posresults$i negresults$i fig$i.png
done