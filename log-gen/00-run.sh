for i in {1..100} ; do
  i=$(printf "%03d" $i)
  echo $i  
  python3 random-date-generator.py > $i.log
done
