.. image:: https://github.com/tomviner/traintimes/actions/workflows/ci.yml/badge.svg?branch=main
        :target: https://github.com/tomviner/traintimes/actions/workflows/ci.yml
        :alt: CI Status

.. image:: https://coveralls.io/repos/tomviner/traintimes/badge.svg?branch=master&service=github
        :target: https://coveralls.io/github/tomviner/traintimes?branch=master
        :alt: Coverage Status

traintimes
==========
A Python SDK for `realtimetrains <http://www.realtimetrains.co.uk/>`_' API `api.rtt.io <https://api.rtt.io/>`_ (`docs <https://www.realtimetrains.co.uk/about/developer/pull/docs/>`_)


Development setup
-----------------

The project is managed with `uv <https://github.com/astral-sh/uv>`_.  To create
an isolated environment with the runtime and development dependencies run::

    uv sync --dev

This will create ``.venv`` (if it does not already exist) and install the
package along with the test tools declared in ``pyproject.toml``.

The SDK requires access to the RealTimeTrains API.  Obtain credentials from
https://api.rtt.io/ and expose them to the process in the
``RTT_AUTH`` environment variable, formatted as ``username:password``.  When the
variable is not defined the test suite substitutes a placeholder so that unit
tests can be executed offline; the integration suite is skipped in that case.

Running the test suite
----------------------

With the dependencies installed you can execute the unit tests via::

    uv run --group test pytest

The integration tests in ``tests/test_sdk_integration.py`` make live requests
against the RealTimeTrains API.  They count against the daily free tier limit
and therefore require valid ``RTT_AUTH`` credentials.  Without credentials the
integration suite is skipped automatically; provide real values to exercise the
live API calls.


SDK Classes
-----------
- Location List
- Service Information
