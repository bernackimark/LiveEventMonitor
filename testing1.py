from datetime import datetime
import pytz

# Your original timestamp
utc_time_str = "2025-04-08T00:58:59.764Z"

# Parse the UTC timestamp string into a datetime object
utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")

# Set the timezone of the datetime object to UTC
utc_time = pytz.utc.localize(utc_time)

# Convert to Eastern Time (ET)
eastern = pytz.timezone('US/Eastern')
eastern_time = utc_time.astimezone(eastern)

# Print the result
print(eastern_time)
