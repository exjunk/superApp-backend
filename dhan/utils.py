import random
import string
import time as time
from datetime import datetime
from logger import logger

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def get_truncated_timestamp(length):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]  # microseconds truncated to milliseconds
    return timestamp[:length]

def generate_correlation_id(max_length=10):
    timestamp_length = min(10, max_length - 5)  # Adjust the length if necessary
    random_string_length = max_length - timestamp_length
    
    timestamp_part = get_truncated_timestamp(timestamp_length)
    random_string_part = generate_random_string(random_string_length)    
    return timestamp_part + random_string_part

def parse_timestamp(timestamp):
  """
  Parses a timestamp string in the format "HH:MM:SS" and returns a datetime.datetime object.

  Args:
      timestamp: The timestamp string in the format "HH:MM:SS".

  Returns:
      A datetime.datetime object representing the parsed timestamp.
  """

  try:
    hours, minutes, seconds = map(int, timestamp.split(':'))
    return datetime.datetime(hours, minutes, seconds)
  except ValueError:
    raise ValueError(f"Invalid timestamp format: {timestamp}")

def convert_to_unix_timestamp(time_str):
  """
  Converts a time string (HH:MM:SS) to Unix timestamp (seconds since epoch).

  Args:
      time_str: Time string in HH:MM:SS format.

  Returns:
      Unix timestamp (number of seconds since epoch).
  """
  hours, minutes, seconds = map(int, time_str.split(':'))
  return hours * 3600 + minutes * 60 + seconds

def convert_to_millis_since_reference(time_str, reference_date="2024-07-03 00:00:00"):
  """
  Converts a time string (HH:MM:SS) to milliseconds since a reference date.

  Args:
      time_str: Time string in HH:MM:SS format.
      reference_date: Reference date and time in YYYY-MM-DD HH:MM:SS format (default: 2024-07-03 00:00:00).

  Returns:
      Number of milliseconds elapsed since the reference date.
  """
  # Convert reference date to timestamp
  reference_timestamp = datetime.strptime(reference_date, "%Y-%m-%d %H:%M:%S").timestamp()
  
  # Convert time string to seconds
  hours, minutes, seconds = map(int, time_str.split(':'))
  time_in_seconds = hours * 3600 + minutes * 60 + seconds

  # Convert seconds to milliseconds and add to reference timestamp
  time_in_millis = time_in_seconds * 1000
  return int(reference_timestamp + time_in_millis)

def get_current_time_stamp_and_date():
    
    
   # Get the current timestamp
    now = datetime.now()
    curr_ta = now.microsecond()
    logger.info(f"timstamp = {curr_ta}")

    # Convert the timestamp to the desired format
    formatted_time = now.strftime('%d-%m-%Y %H:%M:%S')
    
    return f"{curr_ta}",formatted_time

def format_number(number):
    return f"{number:.2f}"