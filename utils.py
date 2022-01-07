
import pandas as pd
import yaml

STR_PARAMS = ['start_date', 'end_date', 'mode']                  
FLOAT_PARAMS = ['duration', 
                'timestep', 
                'destination_lat', 'destination_lon', 
                'departure_lat', 'departure_lon',
                'lon_min', 'lat_min', 'lon_max', 'lat_max']
INT_PARAMS = ['launch_freq','craft', 'speed']

def parse_query_string(args):

    params = {}

    try: 

        # Parse every parameter depending on its type
        # Could probably be streamlined with FastAPI
        for param in [*STR_PARAMS, *FLOAT_PARAMS, *INT_PARAMS]:

            params[param] = parse_param(args, param)

        # Further parse the parameters
        params['start_date']        = pd.to_datetime(params['start_date'], infer_datetime_format=True)
        params['end_date']          = params['start_date'] + pd.Timedelta(params['duration'], unit='days')
        params['bbox']              = [params['lon_min'], params['lat_min'], params['lon_max'], params['lat_max']]
        params['destination']       = [params['destination_lon'], params['destination_lat']]
        params['destination_point'] = [params['departure_lon'], params['departure_lat']]
        
    except Exception as e:
        print(e)
        return None

    return params

def parse_param(args, param):

    if param in FLOAT_PARAMS:
        return float(args.get(param))
    elif param in INT_PARAMS:
        return int(args.get(param))
    elif param == 'departure_points':
        return args.getlist(param)
    elif param in STR_PARAMS:
        return args.get(param)
    else:
        print(param)
        raise ValueError
    
def load_yaml(file):

    with open(file, 'r') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

    return config