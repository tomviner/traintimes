from setuptools import setup

setup(
    name='traintimes',
    version='0.1.0.dev0',
    py_modules=(
        'sdk',
    ),
    install_requires=(
        'purl==1.1',
        'requests==2.8.1',
        'requests-cache==0.4.10',
    ),

)
