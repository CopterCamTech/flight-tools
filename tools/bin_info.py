#!/usr/bin/env python3

# ✅ Enables CLI execution from tools/ by patching sys.path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

def generate_bin_info(filepath, mode="cli"):
    result = extract_bin_info(filepath)
    if 'error' in result:
        return {'error': result['error']}

    if mode == "cli":
        print(f"📄 Log Summary for {result['filename']}")
        print(f"Total Messages: {result['total_messages']}")
        print(f"Log Duration: {result['log_duration']}")
        print("Message Types:")
        for msg_type in result['message_types']:
            print(f"  - {msg_type}")
        return {'output': 'Summary printed to console'}

    elif mode == "flask":
        return result

    elif mode == "file":
        output_path = filepath + "_info.txt"
        try:
            with open(output_path, "w") as f:
                f.write(f"Log Summary for {result['filename']}\n")
                f.write(f"Total Messages: {result['total_messages']}\n")
                f.write(f"Log Duration: {result['log_duration']}\n")
                f.write("Message Types:\n")
                for msg_type in result['message_types']:
                    f.write(f"  - {msg_type}\n")
            return {'output': output_path}
        except Exception as e:
            return {'error': str(e)}

    else:
        return {'error': f"Unknown mode: {mode}"}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract summary info from ArduPilot .bin log")
    parser.add_argument("input_file", help="Path to .bin log file")
    parser.add_argument("--mode", choices=["cli", "file", "flask"], default="cli")
    args = parser.parse_args()

    result = generate_bin_info(args.input_file, mode=args.mode)
    print(result.get('error') or f"✅ {result['output']}")
