import requests
from bs4 import BeautifulSoup
import logging
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime


def scrape_quotes():
    url = Variable.get("quotes_url") 
    all_quotes = []
    page_number = 1

    while url:

        logging.info(f"Scraping página {page_number}...")
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            for item in soup.select(".quote"):
                quote_text = item.select_one(".text").text.strip()
                quote_author = item.select_one(".author").text.strip()
                tags = [tag.text for tag in item.select(".tag")]

                all_quotes.append({
                    "quote_text": quote_text,
                    "quote_author": quote_author,
                    "tags": tags
                })


            next_page = soup.select_one('.next > a')
            if next_page:
   
                url = Variable.get("quotes_url") + next_page['href']
                page_number += 1
            else:
                url = None 
        else:
            raise Exception(f"Erro ao acessar o site: {response.status_code}")

    return all_quotes


def insert_quotes_into_db(**kwargs):
    quotes = kwargs['ti'].xcom_pull(task_ids='scrape_quotes')

    logging.info(f"Citações encontradas: {len(quotes)}")

    if not quotes:
        raise ValueError("Nenhuma citação encontrada para inserção.")

  
    hook = PostgresHook(postgres_conn_id='airflow-merx')  
    conn = hook.get_conn()
    cursor = conn.cursor()
    existing_quotes = set() 

    cursor.execute("SELECT quote_text FROM quotes")
    rows = cursor.fetchall()
    for row in rows:
        existing_quotes.add(row[0])  

   
    for quote in quotes:
        if quote["quote_text"] not in existing_quotes:
            logging.info(f"Inserindo citação: {quote['quote_text']} de {quote['quote_author']}")
            tags = '{' + ', '.join(quote["tags"]) + '}'
            cursor.execute("""
                INSERT INTO quotes (quote_text, quote_author, tags)
                VALUES (%s, %s, %s)
            """, (quote["quote_text"], quote["quote_author"], tags))
            existing_quotes.add(quote["quote_text"])  
            
    conn.commit()
    cursor.close()
    conn.close()


with DAG('scrape_quotes',
         start_date=datetime(2024, 11, 15),
         schedule_interval='0 0 * * *',  
         catchup=False) as dag:

   
    scrape_task = PythonOperator(
        task_id='scrape_quotes',
        python_callable=scrape_quotes
    )

 
    insert_task = PythonOperator(
        task_id='insert_quotes_into_db',
        python_callable=insert_quotes_into_db,
        provide_context=True  
    )
    scrape_task >> insert_task
