
import yaml
    
def load_yaml(file):

    with open(file, 'r') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

    return config