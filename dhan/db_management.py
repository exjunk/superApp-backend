import mysql.connector
import query_manager as query_manager
from logger import logger
from config import hostname,username,password,database_name


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
    except mysql.connector.Error as err:
        logger.info(f"mysql.connector.Error: {err}")
    except Exception as e:
        logger.info(f"Exception: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()        
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

    except mysql.connector.Error as err:
        logger.info(f"mysql.connector.Error: {err}")
    except Exception as e:
        logger.info(f"Exception: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()        

def get_index_details(client_id,index):
    
    try:
        if not connection.is_connected():
            db_connection()

        with connection.cursor(dictionary=True) as cursor:
            sql = f"SELECT * from market_indices where dhanClientId = {client_id} and index_name = '{index}'"
            cursor.execute(sql) 
            return cursor.fetchall()

    except mysql.connector.Error as err:
        logger.info(f"mysql.connector.Error: {err}")
    except Exception as e:
        logger.info(f"Exception: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()        
        

def get_trade_trigger_levels(client_id):
    try:
        if not connection.is_connected():
            db_connection()

        with connection.cursor(dictionary=True) as cursor:
            sql = f"SELECT * from trade_trigger where dhanClientId = {client_id}"
            #logger.info(sql)
            cursor.execute(sql) 
            return cursor.fetchall()

    except mysql.connector.Error as err:
        logger.info(f"mysql.connector.Error: {err}")
    except Exception as e:
        logger.info(f"Exception: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()        

def get_trade_trigger_levels_with_index(client_id,index_name):
    try:
        if not connection.is_connected():
            db_connection()

        with connection.cursor(dictionary=True) as cursor:
            sql = f"SELECT * from trade_trigger where dhanClientId = {client_id} and index_name = '{index_name}'"
            cursor.execute(sql) 
            return cursor.fetchall()

    except mysql.connector.Error as err:
        logger.info(f"mysql.connector.Error: {err}")
    except Exception as e:
        logger.info(f"Exception: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()        
    

def delete_trade_trigger_levels_with_index(client_id,index_name,level):
    try:
        if not connection.is_connected():
            db_connection()

        with connection.cursor(dictionary=True) as cursor:
            sql = f" DELETE from trade_trigger where dhanClientId = '{client_id}' and index_name = '{index_name}' and price_level = {level}"
            #logger.info(sql)
            cursor.execute(sql) 
            connection.commit()

    except mysql.connector.Error as err:
        logger.info(f"mysql.connector.Error: {err}")
    except Exception as e:
        logger.info(f"Exception: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()        

def add_trade_trigger_levels(id,dhanClientId,index_name,option_type,level):
    try:
        if not connection.is_connected():
            db_connection()

        with connection.cursor(dictionary=True) as cursor:
            if id == '' or id == None :
                sql = f"INSERT INTO `trade_trigger` (`dhanClientId`, `index_name`, `option_type`, `price_level`) VALUES ('{dhanClientId}', '{index_name}', '{option_type}', {level})"
            else:
                sql = f"UPDATE `trade_trigger` SET `dhanClientId` = {dhanClientId}, `index_name` = '{index_name}', `option_type` = '{option_type}', `price_level` = {level} WHERE `id` = {id}"
  
              # sql = "INSERT INTO trade_trigger (dhanClientId, index_name,option_type,price_level) VALUES (%s, %s,%s,%s)", (dhanClientId, index_name,option_type,level)
            logger.info(sql)
            
            cursor.execute(sql) 
            connection.commit()
            
            
             # Fetch the last inserted row
            last_id = cursor.lastrowid
            if last_id:
                cursor.execute("SELECT * FROM trade_trigger WHERE id = %s", (last_id,))
                last_row = cursor.fetchone()
            else:
            # If lastrowid is 0, it means an existing row was updated, not inserted.
                cursor.execute("SELECT * FROM trade_trigger WHERE id = %s", (id,))
                last_row = cursor.fetchone()
        logger.info(f"LAST_ROW --> {last_row}")
        return last_row

    except mysql.connector.Error as err:
        logger.info(f"mysql.connector.Error: {err}")
    except Exception as e:
        logger.info(f"Exception: {err}")
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()        
       






