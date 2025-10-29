#!/usr/bin/env python3

import os
import sys
import pymavlink
from pymavlink import DFReader

# Set MAVLink dialect explicitly
os.environ['MAVLINK_DIALECT'] = 'ardupilotmega'

def extract_bin_info(filepath):
    try:
        if not os.path.exists(filepath):
            return {'error': f"File not found: {filepath}"}

        reader = DFReader.DFReader_binary(filepath)

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
            'filename': os.path.basename(filepath),
            'message_types': sorted(message_types),
            'total_messages': total_messages,
            'log_duration': duration_str,
        }

    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract summary info from ArduPilot .bin log")
    parser.add_argument("input_file", help="Path to .bin log file")
    args = parser.parse_args()

    result = extract_bin_info(args.input_file)

    if 'error' in result:
        print(f"❌ {result['error']}")
    else:
        print(f"📄 Log Summary for {result['filename']}")
        print(f"Total Messages: {result['total_messages']}")
        print(f"Log Duration: {result['log_duration']}")
        print("Message Types:")
        for msg_type in result['message_types']:
            print(f"  - {msg_type}")
