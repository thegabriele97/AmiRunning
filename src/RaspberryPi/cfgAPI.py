import json

class cfg:
    def __init__(self, dict : dict = None):
        if not dict is None:
            for k, v in dict.items():
                setattr(self, k, v)

class cfgJSONEncoder(json.JSONEncoder):
    def default(self, obj : cfg):
        return obj.__dict__


def load_configs(file : str) -> cfg:
    with open(file, 'r') as json_file:
        loaded = json.loads(json_file.read())
        cfgObj = cfg(dict=loaded)

    return cfgObj

def save_configs(obj : cfg, file : str):
    with open(file, 'w') as json_file:
        json.dump(
            obj=obj, 
            fp=json_file, 
            cls=cfgJSONEncoder,
            indent=3
        )

if __name__ == "__main__":
    cfgObj = load_configs('../configs.json')
    print(cfgObj.__dict__)
    cfgObj2 = load_configs('../configs.json');
    cfgObj.fitbit_client_id = 0
    print(cfgObj2)
