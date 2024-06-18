import json_management as json_parser
import json

def generate_insert_query(data,table_name)->str:
    clean_json = json_parser.preprocess_json(data=data)
    print(clean_json)
    data_dict = json.loads(clean_json)

    column_name = []
    column_value = []
    for key in data_dict:
        column_name.append(key)
        if(data_dict[key] == ''):
            column_value.append('\'\'')
        elif(type(data_dict[key]) == str):
             column_value.append('\'{}\''.format(data_dict[key]))
        elif(data_dict[key] == None):
            column_value.append('NULL')
        else:
            column_value.append(str(data_dict[key]))
        
    columns = ",".join(column_name)
    columns_value = ",".join(column_value)

    query_string = "INSERT INTO {} ({}) VALUES ({})".format(table_name,columns,columns_value)
    return query_string