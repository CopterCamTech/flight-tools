#!/usr/bin/env python3

from pyulog import ULog
import os

def extract_parameters(filepath):
    try:
        if not os.path.exists(filepath):
            return {'error': f"File not found: {filepath}"}

        ulog = ULog(filepath)
        param_dict = {}

        # Handle initial_parameters (dict OR list of tuples)
        if isinstance(ulog.initial_parameters, dict):
            for name, value in ulog.initial_parameters.items():
                param_dict[name] = value
        elif isinstance(ulog.initial_parameters, list):
            for entry in ulog.initial_parameters:
                if isinstance(entry, tuple) and len(entry) == 2:
                    name, value = entry
                    param_dict[name] = value

        # Handle changed_parameters (dict of lists of ParameterChange objects)
        if isinstance(ulog.changed_parameters, dict):
            for name, changes in ulog.changed_parameters.items():
                if isinstance(changes, list) and changes:
                    last_change = changes[-1]
                    param_dict[name] = last_change.parameter_value

        if not param_dict:
            return {'error': "No parameters found in .ulg file"}

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
            print(f"📄 Parameters (last known values) from {summary['filename']}:")
            for key, value in summary['parameters'].items():
                print(f"  {key}: {value}")

    return summary

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract last parameter values from PX4 .ulg log")
    parser.add_argument("input_file", help="Path to .ulg log file")
    args = parser.parse_args()

    generate_parameter_list(args.input_file, mode="cli")
