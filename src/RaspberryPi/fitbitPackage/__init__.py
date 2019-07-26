from .fitbit_api import *

import cfg

fitbit_api = FitbiAapi(
    client_id = cfg.global_configs.fitbit_client_id,
    client_secret = cfg.global_configs.fitbit_client_secret
)