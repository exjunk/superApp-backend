import mysql.connector
import query_manager as query_manager
# Replace with your credentials
hostname = "localhost"
username = "root"
password = ""
database_name = "super_app"



def db_connection():
    global connection
    connection = mysql.connector.connect(host=hostname, user=username, password=password, database=database_name)

db_connection()

def insert_order(data,table_name):
    try:
        if not connection.is_connected():
            db_connection()

        with connection.cursor() as cursor:
            sql = query_manager.generate_insert_query(data=data,table_name=table_name)   
            cursor.execute(sql)         
        connection.commit()   
    except Exception as e:
        connection.close()
    # finally:
    #     connection.close()


def get_config_details(client_id):
    try:
        if not connection.is_connected():
            db_connection()

        with connection.cursor(dictionary=True) as cursor:
            sql = f"SELECT * from users where dhanClientId = {client_id}"
            cursor.execute(sql) 
            return cursor.fetchall()

    except Exception as e:
        connection.close()

def get_index_details(client_id,index):
    
    try:
        if not connection.is_connected():
            db_connection()

        with connection.cursor(dictionary=True) as cursor:
            sql = f"SELECT * from market_indices where dhanClientId = {client_id} and index_name = '{index}'"
            cursor.execute(sql) 
            return cursor.fetchall()

    except Exception as e:
        connection.close()

def get_trade_trigger_levels(client_id):
    try:
        if not connection.is_connected():
            db_connection()

        with connection.cursor(dictionary=True) as cursor:
            sql = f"SELECT * from trade_trigger where dhanClientId = {client_id}"
            cursor.execute(sql) 
            return cursor.fetchall()

    except Exception as e:
        connection.close()

def get_trade_trigger_levels_with_index(client_id,index_name):
    try:
        if not connection.is_connected():
            db_connection()

        with connection.cursor(dictionary=True) as cursor:
            sql = f"SELECT * from trade_trigger where dhanClientId = {client_id} and index_name = '{index_name}'"
            cursor.execute(sql) 
            return cursor.fetchall()

    except Exception as e:
        connection.close()


