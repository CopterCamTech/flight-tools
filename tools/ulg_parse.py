import os
import pandas as pd
from pyulog import ULog

# Parse the uploaded .ulg file and return ULog object + message types
def parse_ulg_file(filepath):
    ulog = ULog(filepath)
    message_types = sorted(set(msg.name for msg in ulog.data_list))
    return ulog, message_types

# Dynamically extract fields from the log for a given message type
def get_fields_from_log(ulog, msg_type):
    try:
        dataset = ulog.get_dataset(msg_type).data
        return [{"Field": k, "Description": ""} for k in dataset.keys()]
    except KeyError:
        return []

# Extract timestamped data for a specific field
def extract_field_data(ulog, msg_type, field_name):
    try:
        dataset = ulog.get_dataset(msg_type).data
        timestamps = dataset["timestamp"]
        values = dataset[field_name]
        return list(zip(timestamps, values))
    except KeyError:
        return []

# Check if field values are numeric
def is_field_numeric(ulog, msg_type, field_name):
    try:
        values = ulog.get_dataset(msg_type).data[field_name]
        return pd.Series(values).apply(lambda x: isinstance(x, (int, float))).all()
    except KeyError:
        return False
