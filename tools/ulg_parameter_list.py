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

        return {
            'filename': os.path.basename(filepath),
            'parameters': dict(sorted(parameters.items()))
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

    parser = argparse.ArgumentParser(description="Extract parameter list from PX4 .ulg log")
    parser.add_argument("input_file", help="Path to .ulg log file")
    args = parser.parse_args()

    generate_parameter_list(args.input_file, mode="cli")
