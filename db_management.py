import mysql.connector

# Replace with your credentials
hostname = "localhost"
username = "root"
password = ""
database_name = "super_app"

connection = mysql.connector.connect(host=hostname, user=username, password=password, database=database_name)

def get_realised_pnl(date):
    return connection._execute_query("select * from daily_pnl where date = \'date\';")

def update_realised_pnl(date):
    realised_pnl = connection._execute_query("SELECT SUM(realizedProfit) FROM `user_positions` WHERE positionType = 'CLOSED';")
    
    return connection._execute_query("INSERT INTO `daily_pnl` (`day_start_balance`, `current_profit_loss`, `date`) VALUES ('12000', '12', '2024-05-19');")


