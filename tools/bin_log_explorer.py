import os
import pandas as pd
from pymavlink import DFReader

# Ensure ArduPilot dialect is used
os.environ['MAVLINK_DIALECT'] = 'ardupilotmega'

# Step 1: Parse .BIN file and return message types + raw message map
def parse_bin_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    reader = DFReader.DFReader_binary(filepath)
    message_types = set()
    messages_by_type = {}

    while True:
        msg = reader.recv_msg()
        if msg is None:
            break
        msg_type = msg.get_type()
        message_types.add(msg_type)
        messages_by_type.setdefault(msg_type, []).append(msg)

    return sorted(message_types), messages_by_type

# Step 2: Extract available fields from a selected message type
def get_fields_from_bin(messages_by_type, msg_type):
    try:
        sample_msg = messages_by_type[msg_type][0]
        return [{"Field": k, "Description": ""} for k in sample_msg.to_dict().keys()]
    except (KeyError, IndexError):
        return []

# Step 3: Extract timestamped values for a selected field
def extract_field_data_bin(messages_by_type, msg_type, field_name):
    try:
        data = []
        for msg in messages_by_type[msg_type]:
            msg_dict = msg.to_dict()
            timestamp = getattr(msg, '_timestamp', None)
            value = msg_dict.get(field_name)
            if timestamp is not None and value is not None:
                data.append((timestamp, value))
        return data
    except KeyError:
        return []

# Optional: Check if a field is numeric (for future charting)
def is_field_numeric_bin(messages_by_type, msg_type, field_name):
    try:
        values = [
            msg.to_dict().get(field_name)
            for msg in messages_by_type[msg_type]
            if field_name in msg.to_dict()
        ]
        return pd.Series(values).apply(lambda x: isinstance(x, (int, float))).all()
    except KeyError:
        return False
