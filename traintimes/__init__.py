import os
import logging

import requests_cache


logging.basicConfig(level=logging.DEBUG)

cache_dir = '.requests_cache'
try:
    os.mkdir(cache_dir)
except OSError:
    pass
requests_cache.install_cache(
    cache_name=os.path.join(cache_dir, 'cache'),
    allowable_codes=(200,),
)
