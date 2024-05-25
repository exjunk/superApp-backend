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
    finally:
        connection.close()


if(__name__ == '__main__'):
    data = '''
            {
            "dhanClientId": "1000000003",
            "orderId": "112111182198",
            "correlationId":"123abc678",
            "orderStatus": "PENDING",
            "transactionType": "BUY",
            "exchangeSegment": "NSE_EQ",
            "productType": "INTRADAY",
            "orderType": "MARKET",
            "validity": "DAY",
            "tradingSymbol": "",
            "securityId": "11536",
            "quantity": 5,
            "disclosedQuantity": 0,
            "price": 0.0,
            "triggerPrice": 0.0,
            "afterMarketOrder": false,
            "boProfitValue": 0.0,
            "boStopLossValue": 0.0,
            "legName":"" ,
            "createTime": "2021-11-24 13:33:03",
            "updateTime": "2021-11-24 13:33:03",
            "exchangeTime": "2021-11-24 13:33:03",
            "drvExpiryDate": null,
            "drvOptionType": null,
            "drvStrikePrice": 0.0,
            "omsErrorCode": null,
            "omsErrorDescription": null,
            "filled_qty": 0,
            "algoId": "string"
        }'''
    
    new_data = '''{
    "dhanClientId": "1000000003",
    "orderId": "112111182198",
    "correlationId":"123abc678",
    "orderStatus": "PENDING",
    "transactionType": "BUY",
    "exchangeSegment": "NSE_EQ",
    "productType": "INTRADAY",
    "orderType": "MARKET",
    "validity": "DAY",
    "tradingSymbol": "",
    "securityId": "11536",
    "quantity": 5,
    "disclosedQuantity": 0,
    "price": 0.0,
    "triggerPrice": 0.0,
    "afterMarketOrder": false,
    "boProfitValue": 0.0,
    "boStopLossValue": 0.0,
    "legName": ,
    "createTime": "2021-11-24 13:33:03",
    "updateTime": "2021-11-24 13:33:03",
    "exchangeTime": "2021-11-24 13:33:03",
    "drvExpiryDate": null,
    "drvOptionType": null,
    "drvStrikePrice": 0.0,
    "filled_qty": 0,
    "algoId": "string"
}
'''
    insert_order(data=new_data,table_name="order_desc")


