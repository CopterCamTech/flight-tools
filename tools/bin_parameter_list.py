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

