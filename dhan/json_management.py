import re

def preprocess_json(data):
    # Regular expression to find keys with missing values or white space as values
    pattern = r'\"(\w+)\":(\s*[^,}\s]*)(?=,|})'
    
    # Replace keys with missing values with null
    def replace_with_null(match):
        key, value = match.groups()
        if value == '' or value.isspace():
            return f'"{key}": null'
        return f'"{key}": {value}'

    corrected_json_str = re.sub(pattern, replace_with_null, data)
    return corrected_json_str

def replace_empty_with_null(data):
    if isinstance(data, dict):
        return {k: replace_empty_with_null(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_empty_with_null(item) for item in data]
    elif data == "" or data is None:
        return None
    else:
        return data
    
def dict_to_string_json(data):
    def convert_to_string(item):
        if isinstance(item, dict):
            return {str(k): convert_to_string(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [convert_to_string(i) for i in item]
        else:
            return str(item)
    
    string_dict = convert_to_string(data)
    return string_dict

