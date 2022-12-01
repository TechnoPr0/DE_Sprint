from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
import pandas as pd
import json

# a.Скачайте произвольный csv-файл (ссылка на файл указана в Variables)
def read_csv():
    url = Variable.get("url_csv")
    r = pd.read_csv(url)
    return r.to_json()

# В этой функции производится подсчёт строк
def count_r(**kwargs):
    json_table = kwargs['ti']
    r = json_table.xcom_pull(task_ids='read')
    r = json.loads(r)
    return len(r["Game Number"])

#  b. Создайте еще один python-оператор, передайте в него из первого python-оператора количество строк. 
# Прочитайте файл(с использованием переменных) и добавьте к данному файлу колонку справа, 
# которая будет номеровать строки в обратном порядке
# (т.е. первая строка должна принять значение кол-ва строк файла, каждая следующая строка -1 от значения в предыдущей). 
# Сохраните полученный файл.
def create_column(**kwargs):
    
    # Вытаскиваем результаты из предыдущих операторов с помощью Xcom
    input = kwargs["ti"]
    table = input.xcom_pull(task_ids = "read")
    count = input.xcom_pull(task_ids = "count")

    df = pd.read_json(table)
    reverse_list = []
    for i in range(count, 0, -1):
        reverse_list.append(i)
    # Добавляем столбец в DataFrame, конвертируем в csv и сохраняем.
    df["reverse"] = reverse_list
    df.to_csv('files/file.csv')

with DAG(dag_id="a_start_dag", start_date=datetime(2022, 1, 1), schedule="0 0 * * *") as dag:
    

    python_read = PythonOperator(task_id = "read", python_callable = read_csv)
    python_count = PythonOperator(task_id = "count", python_callable = count_r)
    python_create_column = PythonOperator(task_id = "create", python_callable = create_column)

    bash_read = BashOperator(task_id = "bash_cat", bash_command = "mv /opt/airflow/files/file.csv /opt/airflow/finish/")
    bash_success = BashOperator(task_id = "Success", bash_command = "echo Success")



    python_read >> python_count >> python_create_column >> bash_read >> bash_success
