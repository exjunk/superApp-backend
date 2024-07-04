# Function to update the plot with new data
import matplotlib.pyplot as plt
from datetime import datetime
import utils as utils


def init_plot():
    plt.ion()  # Enable interactive mode
    plt.show()
    return [],[]

def update_plot(data,timestamps,prices):
  try:
    price, timestamp = data.split(",")
    #timestamp = utils.convert_to_unix_timestamp(timestamp)#datetime.strptime(timestamp, "%H:%M:%S.%f")  # Parse timestamp format
    timestamps.append(timestamp)
    prices.append(float(price))
    
    # Limit data points to avoid overwhelming the plot
    max_points = 100
    if len(timestamps) > max_points:
      timestamps = timestamps[-max_points:]
      prices = prices[-max_points:]

    # Update plot
    plt.clf()  # Clear previous plot
    plt.plot(timestamps, prices)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title("Live Price Stream")
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
    plt.tight_layout()
    plt.draw()
    plt.pause(0.1)  # Pause to avoid overwhelming the UI
  except Exception as e:
    print(f"Error processing data: {e}")
