import random
import string
from datetime import datetime

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def get_truncated_timestamp(length):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]  # microseconds truncated to milliseconds
    return timestamp[:length]

def generate_correlation_id(max_length=15):
    timestamp_length = min(10, max_length - 5)  # Adjust the length if necessary
    random_string_length = max_length - timestamp_length
    
    timestamp_part = get_truncated_timestamp(timestamp_length)
    random_string_part = generate_random_string(random_string_length)    
    return timestamp_part + random_string_part

