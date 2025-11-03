#!/usr/bin/env python3

import os
from pyulog import ULog

def extract_ulg_info(filepath):
    try:
        if not os.path.exists(filepath):
            return {'error': f"File not found: {filepath}"}

        ulog = ULog(filepath)
        message_types = sorted(set(entry.name for entry in ulog.data_list))
        total_messages = sum(len(entry.data['timestamp']) for entry in ulog.data_list)
        duration = (ulog.last_timestamp - ulog.start_timestamp) / 1e6

        return {
            'filename': os.path.basename(filepath),
            'message_types': message_types,
            'total_messages': total_messages,
            'log_duration': f"{duration:.2f} seconds",
        }

    except Exception as e:
        return {'error': str(e)}

def generate_ulg_info(filepath, mode="cli"):
    result = extract_ulg_info(filepath)
    if mode == "cli":
        if 'error' in result:
            print(f"❌ {result['error']}")
        else:
            print(f"📄 Log Summary for {result['filename']}")
            print(f"Total Messages: {result['total_messages']}")
            print(f"Log Duration: {result['log_duration']}")
            print("Message Types:")
            for msg_type in result['message_types']:
                print(f"  - {msg_type}")
    return result

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract summary info from PX4 .ulg log")
    parser.add_argument("input_file", help="Path to .ulg log file")
    args = parser.parse_args()

    generate_ulg_info(args.input_file, mode="cli")
