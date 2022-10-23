<p align="center">
  <a href="https://dratio.io">
    <img src="https://user-images.githubusercontent.com/16774925/184549419-b05ebfd2-436e-41e2-9172-a05d53e67c1d.svg">
  </a>
</p>

# Python Client for dratio.io API web services

[![PyPI version](https://badge.fury.io/py/dratio.svg)](https://pypi.org/project/dratio/)
[![ReadTheDocs](https://readthedocs.org/projects/dratio/badge/?version=latest)](https://dratio.readthedocs.io/en/latest/?badge=latest)
[![Python version](https://img.shields.io/pypi/pyversions/dratio)](https://pypi.org/project/dratio/)
[![GitHub](https://img.shields.io/github/license/dratio-io/dratio-python)](https://github.com/dratio-io/dratio-python/blob/main/LICENSE)

**Data as-a-service to make better decisions based on technology**

## What is dratio?

Dratio is the result of our experience creating solutions for data-driven decision making in a wide variety of industries. We provide tools and data as-a-service that enable to create robust data solutions in an agile way.

### Python client

This client allows you to interact with the services offered by the [dratio.io](https://dratio.io) platform from Python.
You will be able to download ready-to-use datasets for all types of industries. All data is reviewed, documented and linked together by common variables, allowing you to reference directly with your data without spending time on integration.

## Installation

Currently, dratio’s client is available in Python 3.7 to 3.10, regardless of the platform. The stable version can be installed via [PyPI](https://pypi.org/project/dratio/).

```bash
pip install dratio
```

In case of using datasets with geographic information, you must have [geopandas](https://geopandas.org/en/stable/) installed in your Python environment. You can also install the package with all the necessary dependencies directly using pip.

```bash
pip install dratio[geo]
```

## Create API Keys

Before you can start using the services offered and access all the datasets,
you will need to [create an API key](https://dratio.io/app/api/).
If you are not registered you can [create an account](https://dratio.io/getstarted/) on
[dratio.io](https://dratio.io/).

| Please, store your API Keys in a safe place and never share them publicly, as they give access to all services offered on your behalf. In case of a leak, you can delete and create new keys.

## Get started

The `Client` class allows you to access all API resources using your key.

```python
from dratio import Client

client = Client('<your_api_key>')
```

Basic functionalities allow you to search and filter datasets available for download.

```python
client.get_datasets()
```

Once a `Dataset` is selected, you can access its information and
download its content as a Pandas `DataFrame` or, in case of datasets with geographic
information, as a `GeoDataFrame`.

```python
dataset = client.get('municipalities')

df = dataset.to_pandas() # Download as DataFrame
gdf = dataset.to_geopandas() # GeoDataFrame with geographic information
```

## License & Terms and conditions

This source code is licensed under the Apache License, Version 2.0. You may obtain a copy of
the License at [apache.org](https://www.apache.org/licenses/LICENSE-2.0).

The use of the services offered by this client must be in accordance with dratio's terms and conditions. You may obtain a copy of the terms at [dratio.io](https://dratio.io/legal/terms)

## Support

This library is supported by dratio's team.
If you find a bug, or have a feature suggestion, please log an issue or
contact us through [our page](https://dratio.io/contact/) or via mail
to [info@dratio.io](mailto:info@dratio.io).
