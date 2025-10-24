import logging
import os

import requests_cache


logging.basicConfig(level=logging.DEBUG)

cache_dir = '.requests_cache'
os.makedirs(cache_dir, exist_ok=True)
requests_cache.install_cache(
    cache_name=os.path.join(cache_dir, 'cache'),
    allowable_codes=(200,),
)
