import mysql.connector
import query_manager as query_manager
# Replace with your credentials
hostname = "localhost"
username = "root"
password = ""
database_name = "super_app"

connection = mysql.connector.connect(host=hostname, user=username, password=password, database=database_name)


def insert_order(data,table_name):
    try:
        with connection.cursor() as cursor:
            sql = query_manager.generate_insert_query(data=data,table_name=table_name)   
            cursor.execute(sql)         
        connection.commit()   
    except Exception as e:
        print(e)     
        connection.close()
    # finally:
    #     connection.close()



