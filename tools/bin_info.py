import os
import sys
import importlib.util

# Add the renamed pymavlink source folder to sys.path
pymavlink_path = os.path.abspath('pymavlink_src')
sys.path.insert(0, pymavlink_path)

# Set MAVLink dialect explicitly
os.environ['MAVLINK_DIALECT'] = 'ardupilotmega'

# Load DFReader.py dynamically
dfreader_path = os.path.join(pymavlink_path, 'DFReader.py')
spec = importlib.util.spec_from_file_location("DFReader", dfreader_path)
DFReader_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(DFReader_module)
DFReader_binary = DFReader_module.DFReader_binary

def extract_bin_info(filepath):
    try:
        if not os.path.exists(filepath):
            return {'error': f"File not found: {filepath}"}

        reader = DFReader_binary(filepath)

        message_types = set()
        total_messages = 0
        timestamps = []

        while True:
            msg = reader.recv_msg()
            if msg is None:
                break
            try:
                msg_type = msg.get_type()
                message_types.add(msg_type)
                total_messages += 1

                # Extract timestamp if available
                if hasattr(msg, '_timestamp') and msg._timestamp is not None:
                    timestamps.append(msg._timestamp)

            except Exception:
                message_types.add('UNKNOWN')

        if timestamps:
            duration_sec = max(timestamps) - min(timestamps)
            duration_min = round(duration_sec / 60, 2)
            duration_str = f"{duration_min} minutes"
        else:
            duration_str = "Unknown (no valid timestamps)"

        return {
            'message_types': sorted(message_types),
            'total_messages': total_messages,
            'log_duration': duration_str,
        }

    except Exception as e:
        return {'error': str(e)}

