#!/usr/bin/env python3
"""
ulg_parameter_compare.py
Compare parameters between two PX4 .ulg log files.
Reports parameter values in CSV format, with options to use first or last values.
"""

import os
import argparse
from pyulog import ULog

def extract_parameters(filepath, mode="last"):
    """Extract parameter values from a PX4 .ulg file."""
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
                    if mode == "last":
                        param_dict[name] = changes[-1].parameter_value
                    elif mode == "first":
                        param_dict[name] = changes[0].parameter_value

        if not param_dict:
            return {'error': "No parameters found in .ulg file"}

        return {
            'filename': os.path.basename(filepath),
            'parameters': dict(sorted(param_dict.items()))
        }

    except Exception as e:
        return {'error': str(e)}

def compare_parameters(file1, file2, mode1="last", mode2="last"):
    """Compare parameters between two .ulg files with mode options."""
    params1 = extract_parameters(file1, mode=mode1)
    params2 = extract_parameters(file2, mode=mode2)

    if 'error' in params1:
        return {'error': f"{file1}: {params1['error']}"}
    if 'error' in params2:
        return {'error': f"{file2}: {params2['error']}"}

    diffs = {}
    all_keys = set(params1['parameters'].keys()) | set(params2['parameters'].keys())
    for key in all_keys:
        val1 = params1['parameters'].get(key)
        val2 = params2['parameters'].get(key)
        if val1 != val2:
            diffs[key] = (val1, val2)

    return {
        'file1': params1['filename'],
        'file2': params2['filename'],
        'differences': diffs,
        'total': len(all_keys)
    }

def main():
    parser = argparse.ArgumentParser(description="Compare PX4 parameters in two .ulg files")
    parser.add_argument("log1", help="First .ulg file")
    parser.add_argument("log2", help="Second .ulg file")
    parser.add_argument("--file1_mode", choices=["first", "last"], default="last",
                        help="Use 'first' or 'last' values for file1 (default: last)")
    parser.add_argument("--file2_mode", choices=["first", "last"], default="last",
                        help="Use 'first' or 'last' values for file2 (default: last)")
    args = parser.parse_args()

    result = compare_parameters(args.log1, args.log2,
                                mode1=args.file1_mode,
                                mode2=args.file2_mode)

    if 'error' in result:
        print(f"❌ {result['error']}")
    else:
        if result['differences']:
            print("Parameter,File1,File2")  # CSV header
            for key, (val1, val2) in sorted(result['differences'].items()):
                def fmt(val):
                    if val is None:
                        return "missing"
                    if isinstance(val, float):
                        return f"{val:.6f}"
                    return str(val)
                print(f"{key},{fmt(val1)},{fmt(val2)}")
            print(f"\n🔎 {len(result['differences'])} parameters differ out of {result['total']} compared.")
        else:
            print("✅ No parameter differences found.")

if __name__ == "__main__":
    main()
