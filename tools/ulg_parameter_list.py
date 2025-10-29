#!/usr/bin/env python3

from pyulog import ULog
import os

def extract_parameters(filepath):
    try:
        if not os.path.exists(filepath):
            return {'error': f"File not found: {filepath}"}

        ulog = ULog(filepath)
        parameters = ulog.initial_parameters

        if not parameters:
            return {'error': "No parameters found in .ulg file"}

        return {'parameters': dict(sorted(parameters.items()))}

    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract parameter list from PX4 .ulg log")
    parser.add_argument("input_file", help="Path to .ulg log file")
    args = parser.parse_args()

    result = extract_parameters(args.input_file)

    if 'error' in result:
        print(f"❌ {result['error']}")
    else:
        print(f"📄 Parameters extracted from {os.path.basename(args.input_file)}:")
        for key, value in result['parameters'].items():
            print(f"  {key}: {value}")
