VOYAGER_PARAMS = ['start_date', 'end_date', 'launch_freq', 'duration', 
                  'timestep', 'mode', 'craft', 'destination', 'departure_points', 'bbox']
LIST_PARAMS = ['destination', 'departure_points', 'bbox']
FLOAT_PARAMS = ['duration', 'timestep']
INT_PARAMS = ['launch_freq','craft']

def parse_query_string(args):

    params = {}

    for param in VOYAGER_PARAMS:

        params[param] = parse_param(args, param)

    return params


def parse_param(args, param):

    if param in FLOAT_PARAMS:
        return float(args.get(param))
    elif param in INT_PARAMS:
        return int(args.get(param))
    elif param == 'departure_points':
        l = args.getlist(param)
        return [[float(first), float(second)] for first, second in zip(l[0::2], l[1::2])]
    elif param in LIST_PARAMS:
        return [float(p) for p in args.getlist(param)]
    elif param in VOYAGER_PARAMS:
        return args.get(param)
    else:
        raise ValueError
    
    