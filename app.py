from flask import Flask, request, jsonify, url_for
from flask_cors import cross_origin
import voyager
import dask
import utils

CONFIG_PATH         = './configs/config.yml'
VESSEL_CONFIG_PATH  = './configs/vessels.yml'

app = Flask(__name__)

@app.route('/api/vessels/', methods=['GET'])
@cross_origin()
def vessel_config():

    # Load the vessel configuration
    vessel_cfg = utils.load_yaml(VESSEL_CONFIG_PATH)

    # Fetch the API parameters
    mode = request.args.get('mode', None)
    idx  = request.args.get('id', None)

    # Two different modes:
    # One lists all vessel ids based on the mode of propulsion
    # The second lists a specific vessel given id and mode of propulsion
    if not idx:
        vessel = vessel_cfg.get(mode, {})
        vessel = [{'id': k, ** v} for k, v in vessel.items()]
    else:
        vessel = vessel_cfg.get(mode, {}).get(int(idx), {})

    return jsonify(vessel)


@app.route('/api/trajectory/', methods=['GET'])
@cross_origin()
def trajectory():

    # Load the general backend configuration
    cfg         = utils.load_yaml(CONFIG_PATH)
    vessel_cfg  = utils.load_yaml(VESSEL_CONFIG_PATH)

    # Fetch the API parameters
    params = utils.parse_query_string(request.args)

    if params:
        with dask.config.set(**cfg['dask']):

            # Create the chart
            # Should possibly be pre-computed if computation is too slow
            chart = voyager.Chart(params['bbox'], 
                                params['start_date'], 
                                params['end_date']).load(cfg['data']['path'], **cfg['chart'])

            # Create the model that steps throught time
            model = voyager.Model(params['duration'], params['timestep'], **cfg['model'])

            # Calculate the trajectories
            results = voyager.Traverser.trajectory(
                mode = params['mode'],
                craft = params['craft'], 
                duration = params['duration'],
                timestep = params['timestep'], 
                destination = params['destination'], 
                speed = params['speed'], 
                bbox = params['bbox'], 
                departure_point = params['departure_point'], 
                vessel_params=vessel_cfg,
                chart = chart, 
                model = model
            )

            return jsonify(results)
    else:
        return jsonify([{}])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)