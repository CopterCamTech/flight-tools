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

        return {'parameters': dict(sorted(param_dict.items()))}

    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract parameter list from ArduPilot .bin log")
    parser.add_argument("input_file", help="Path to .bin log file")
    args = parser.parse_args()

    result = extract_parameters(args.input_file)

    if 'error' in result:
        print(f"❌ {result['error']}")
    else:
        print(f"📄 Parameters extracted from {os.path.basename(args.input_file)}:")
        for key, value in result['parameters'].items():
            print(f"  {key}: {value}")
