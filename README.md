<p align="center">
  <a href="https://dratio.io">
    <img src="https://user-images.githubusercontent.com/16774925/184549419-b05ebfd2-436e-41e2-9172-a05d53e67c1d.svg">
  </a>
</p>

# Welcome to the Dratio Python client!

[![PyPI version](https://badge.fury.io/py/dratio.svg)](https://pypi.org/project/dratio/)
[![ReadTheDocs](https://readthedocs.org/projects/dratio/badge/?version=latest)](https://dratio.readthedocs.io/en/latest/?badge=latest)
[![Python version](https://img.shields.io/pypi/pyversions/dratio)](https://pypi.org/project/dratio/)
[![GitHub](https://img.shields.io/github/license/dratio-io/dratio-python)](https://github.com/dratio-io/dratio-python/blob/main/LICENSE)

This client allows you to easily access and download data from the Dratio API using Python. With this client, you can seamlessly integrate Dratio's comprehensive range of data sets into your data science projects related to marketing, consumption, demographics, or income. Start leveraging the power of data to make data-driven decisions and drive innovation in your organization.

To get started, simply install the client and authenticate with your Dratio API key. Then, you can use the provided methods to access and download the data you need. The data will be returned as a Pandas DataFrame, making it easy to manipulate and analyze.


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

Before you can start using the API,
you will need to [create an API key](https://dratio.io/app/api/).
If you are not registered you can [create an account on dratio.io](https://dratio.io/getstarted/).

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

The use of the data offered by this client must be in accordance with dratio's terms and conditions. You may obtain a copy of the terms at [dratio.io](https://dratio.io/legal/terms)

## Support

If you find a bug, or have a feature suggestion, please log an issue or
contact us through [our page](https://dratio.io/contact/) or via mail
to [info@dratio.io](mailto:info@dratio.io).
