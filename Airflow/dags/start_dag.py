from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
import pandas as pd
import json
def read_csv():
    url = Variable.get("url_csv")
    r = pd.read_csv(url)
    print(r)
    return r.to_json()
def count_r(**kwargs):
    json_table = kwargs['ti']
    r = json_table.xcom_pull(task_ids='read')
    r = json.loads(r)
    return len(r["Game Number"])

def create_column(**kwargs):
    reverse_list = []
    input = kwargs["ti"]
    table = input.xcom_pull(task_ids = "read")
    count = input.xcom_pull(task_ids = "count")
    df = pd.read_json(table)
    
    for i in range(count, 0, -1):
        reverse_list.append(i)
    df["reverse"] = reverse_list
    df.to_csv('files/file.csv')

with DAG(dag_id="a_start_dag", start_date=datetime(2022, 1, 1), schedule="0 0 * * *") as dag:
    

    python_read = PythonOperator(task_id = "read", python_callable = read_csv)
    python_count = PythonOperator(task_id = "count", python_callable = count_r)
    python_create_column = PythonOperator(task_id = "create", python_callable = create_column)
    
    bash_success = BashOperator(task_id = "Success", bash_command = "echo Success")



    python_read >> python_count >> python_create_column >> bash_success
