from setuptools import setup

setup(
    name='traintimes',
    version='0.1.0.dev0',

    author="Tom Viner",
    author_email="traintimes@viner.tv",

    description="A Python SDK for realtimetrains' API",
    long_description=open('README.rst').read(),

    packages=(
        'traintimes',
    ),
    install_requires=(
        'purl==1.1',
        'requests==2.8.1',
        'requests-cache==0.4.10',
    ),

)
