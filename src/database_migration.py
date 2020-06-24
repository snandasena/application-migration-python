import csv
import logging

import mysql.connector

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    filename='../logs/db-migrate.log', filemode='w')

insert_data_file = '../data/migration-data.csv'
update_data_file = '../data/update_migration-data.csv'

myconfig = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "temp"
}

conn = mysql.connector.connect(**myconfig)


def execute_query(query, params):
    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor


def insert_data(data):
    query = "INSERT INTO {tname} (name, address) VALUES (%s, %s)".format(tname='customers')
    execute_query(query, data)


def update_data(data):
    query = "UPDATE customers set address =%s WHERE name = %s "
    log_message = [query, data]
    logging.info(log_message)
    curr = conn.cursor()
    curr.execute(query, data)
    conn.commit()
    logging.info((curr.column_names, curr.rowcount))
    curr.close()


if __name__ == "__main__":
    with open(insert_data_file, newline='') as csv_file:
        data_csv = csv.reader(csv_file, delimiter=',', quotechar='|')
        for r in data_csv:
            logging.info(r)
            insert_data(tuple(r))

    with open(update_data_file, newline='') as csv_file:
        data_csv = csv.reader(csv_file, delimiter=',', quotechar='|')
        for r in data_csv:
            logging.info(r)
            update_data(tuple(r))
