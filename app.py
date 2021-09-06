from flask import Flask, request, jsonify
import voyager
import yaml
import dask

CONFIG_PATH = './configs/config.yml'

app = Flask(__name__)


@app.route('/voyager', methods=['GET'])
def run():

    with open(CONFIG_PATH, 'r') as f:
            CONFIG = yaml.safe_load(f)
    bbox = CONFIG['example']
    traverser = voyager.Traverser(vessel_config=CONFIG['vessels']['path'], 
                                  data_directory=CONFIG['data']['path'],
                                 **CONFIG['example'])

    with dask.config.set(**CONFIG['dask']):

        results = traverser.run(model_kwargs = CONFIG['model'],
                                chart_kwargs = CONFIG['chart'])
            
        dicts = voyager.utils.to_GeoJSON(results)

        return jsonify(dicts)