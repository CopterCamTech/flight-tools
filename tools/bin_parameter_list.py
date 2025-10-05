from pymavlink import mavutil

def extract_parameters(filepath):
    try:
#        print("Received file path:", filepath)

        mlog = mavutil.mavlink_connection(filepath)
        param_dict = {}

        while True:
            msg = mlog.recv_match(blocking=False)
            if msg is None:
                break

            msg_type = msg.get_type()
#            print("Message type:", msg_type)

            if msg_type == 'PARAM_VALUE':
#                print("Found PARAM_VALUE:", msg.param_id, msg.param_value)
                param_dict[msg.param_id] = msg.param_value

            elif msg_type == 'PARM':
#                print("Found PARM:", msg.Name, msg.Value)
                param_dict[msg.Name] = msg.Value

        if not param_dict:
            return {'error': "No parameters found in .bin file"}

        return {'parameters': dict(sorted(param_dict.items()))}

    except Exception as e:
        return {'error': str(e)}

