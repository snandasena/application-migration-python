import mysql.connector

myconfig = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "temp"
}

conn = mysql.connector.connect(**myconfig)


def show_databases():
    cursor = conn.cursor()
    query = "show databases"
    cursor.execute(query)

    for r in cursor:
        print(r[0])

    print("\n")
    cursor.close()


def show_tables(database_name='temp'):
    curr = conn.cursor()
    qury = 'show tables'
    curr.execute(qury)
    for r in curr:
        print (r[0])

    print("\n")
    curr.close()


def create_table():
    curr = conn.cursor()
    query = "CREATE TABLE IF NOT EXISTS customers (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), address VARCHAR(255))"
    curr.execute(query)
    curr.close()


def insert_table(table_name='customers'):
    curr = conn.cursor()
    query = "INSERT INTO {tname} (name, address) VALUES (%s, %s)".format(tname=table_name)

    # This is a tuple
    values = ("John", "Highway 21")
    # []
    #  {}
    # {key:value}
    curr.execute(query, values)

    values = ("Doe", "Highway 21")
    curr.execute(query, values)
    values = ("John Doe", "Highway 21")
    curr.execute(query, values)

    curr.close()


def select_from_table(table_name='customers'):
    curr = conn.cursor()
    query = "SELECT * FROM {tname}".format(tname=table_name)
    curr.execute(query)

    for r in curr.fetchall():
        print(r)
    print('\n')
    curr.close()


def update_table(table_name='customers'):
    curr = conn.cursor()
    query = "UPDATE customers set address =%s WHERE name = %s "
    curr.execute(query, ('Canyon 123', 'John'))
    conn.commit()  # This is very important
    curr.close()


def delete_table(table_name='customers'):
    curr = conn.cursor()
    query = "DELETE FROM customers"
    curr.execute(query)
    conn.commit()
    curr.close()
    print ('deleted\n')


if __name__ == '__main__':
    show_tables()
    create_table()
    show_tables()

    insert_table()
    select_from_table()

    update_table()
    select_from_table()

    delete_table()
    select_from_table()
    conn.close()
