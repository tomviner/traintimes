.. image:: https://travis-ci.org/tomviner/traintimes.svg
        :target: https://travis-ci.org/tomviner/traintimes
        :alt: Build Status

.. image:: https://coveralls.io/repos/tomviner/traintimes/badge.svg?branch=master&service=github
        :target: https://coveralls.io/github/tomviner/traintimes?branch=master
        :alt: Coverage Status

traintimes
==========
A Python SDK for `realtimetrains <http://www.realtimetrains.co.uk/>`_' API `api.rtt.io <https://api.rtt.io/>`_ (`docs <http://www.realtimetrains.co.uk/api>`_)


Development setup
-----------------

The project now targets Python 3.  You can create a virtual environment and
install the dependencies using `uv <https://github.com/astral-sh/uv>`_::

    uv venv --python 3.11 .venv
    source .venv/bin/activate
    uv pip install -e .
    uv pip install pytest pytest-cov freezegun

The SDK requires access to the RealTimeTrains API.  Obtain credentials from
https://api.rtt.io/ and expose them to the process in the
``RTT_AUTH`` environment variable, formatted as ``username:password``.

Running the test suite
----------------------

With the dependencies installed you can execute the unit tests via::

    pytest

The integration tests in ``tests/test_sdk_integration.py`` make live requests
against the RealTimeTrains API.  They count against the daily free tier limit
and therefore require valid ``RTT_AUTH`` credentials.  When running in an
environment without outbound network access, or without API credentials, the
tests will fail during collection because their dependencies (``requests``,
``requests-cache`` and ``freezegun``) cannot be installed.


SDK Classes
-----------
- Location List
- Service Information
