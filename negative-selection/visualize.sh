#!/bin/bash

for i in $(seq 1 9);
do
    java -jar negsel2.jar -self english.train -n 10 -r $i -c -l < english.test > negresults$i
    java -jar negsel2.jar -self english.train -n 10 -r $i -c -l < tagalog.test > posresults$i
    python3 auc.py posresults$i negresults$i fig$i.png
done