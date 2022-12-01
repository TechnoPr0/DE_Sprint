import csv

def count_r():
    r = csv.reader("https://people.sc.fsu.edu/~jburkardt/data/csv/snakes_count_10000.csv")
   
  #  print (f"Количество строк исключая заголовок = {row_sum}")
    return r

print (count_r())
