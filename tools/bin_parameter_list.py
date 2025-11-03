#!/usr/bin/env python3

import os
from pymavlink import mavutil

def extract_parameters(filepath):
    try:
        if not os.path.exists(filepath):
            return {'error': f"File not found: {filepath}"}

        mlog = mavutil.mavlink_connection(filepath)
        param_dict = {}

        while True:
            msg = mlog.recv_match(blocking=False)
            if msg is None:
                break

            msg_type = msg.get_type()

            if msg_type == 'PARAM_VALUE':
                param_dict[msg.param_id] = msg.param_value
            elif msg_type == 'PARM':
                param_dict[msg.Name] = msg.Value

        if not param_dict:
            return {'error': "No parameters found in .bin file"}

        return {
            'filename': os.path.basename(filepath),
            'parameters': dict(sorted(param_dict.items()))
        }

    except Exception as e:
        return {'error': str(e)}

def generate_parameter_list(filepath, mode="cli"):
    summary = extract_parameters(filepath)

    if mode == "cli":
        if 'error' in summary:
            print(f"❌ {summary['error']}")
        else:
            print(f"📄 Parameters extracted from {summary['filename']}:")
            for key, value in summary['parameters'].items():
                print(f"  {key}: {value}")

    return summary

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract parameter list from ArduPilot .bin log")
    parser.add_argument("input_file", help="Path to .bin log file")
    args = parser.parse_args()

    generate_parameter_list(args.input_file, mode="cli")
