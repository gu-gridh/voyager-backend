from flask import Flask, request, jsonify
import voyager
import yaml
import dask
import utils

CONFIG_PATH = './configs/config.yml'

app = Flask(__name__)


@app.route('/voyager', methods=['GET'])
def run():

    # http://127.0.0.1:5000/voyager?start_date=2017-01-01&end_date=2017-01-30&launch_freq=8&duration=7&timestep=3600&mode=sailing&craft=2&destination=2.347&destination=52.084&departure_points=4.474&departure_points=58.962&departure_points=7.655&departure_points=54.718&bbox=-10&bbox=20&bbox=45&bbox=65

    params = utils.parse_query_string(request.args)
    print(params)

    with open(CONFIG_PATH, 'r') as f:
            CONFIG = yaml.safe_load(f)

    traverser = voyager.Traverser(vessel_config=CONFIG['vessels']['path'], 
                                  data_directory=CONFIG['data']['path'],
                                 **params)

    with dask.config.set(**CONFIG['dask']):

        results = traverser.run(model_kwargs = CONFIG['model'],
                                chart_kwargs = CONFIG['chart'])
            
        dicts = voyager.utils.to_GeoJSON(results)

        return jsonify(dicts)
