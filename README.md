<p align="center">
  <a href="https://dratio.io">
    <img src="https://user-images.githubusercontent.com/16774925/184549419-b05ebfd2-436e-41e2-9172-a05d53e67c1d.svg">
  </a>
</p>

# Dratio Python client

[![PyPI version](https://badge.fury.io/py/dratio.svg)](https://pypi.org/project/dratio/)
[![ReadTheDocs](https://readthedocs.org/projects/dratio/badge/?version=latest)](https://dratio.readthedocs.io/en/latest/?badge=latest)
[![Python version](https://img.shields.io/pypi/pyversions/dratio)](https://pypi.org/project/dratio/)
[![GitHub](https://img.shields.io/github/license/dratio-io/dratio-python)](https://github.com/dratio-io/dratio-python/blob/main/LICENSE)

The Dratio Python client allows you to effortlessly access and download data from the Dratio API using Python. Integrate a wide range of datasets from Dratio into your data science projects related to marketing, consumption, demographics, or income, and make data-driven decisions to drive innovation within your organization.

Get started by installing the client and authenticating with your Dratio API key. The client provides methods to access and download the data you need, returning the data as a Pandas DataFrame for easy manipulation and analysis.

## Installation

The stable version of the Dratio Python client is available on [PyPI](https://pypi.org/project/dratio/) for Python 3.7 to 3.11, regardless of the platform. Install it using pip:

```bash
pip install dratio
```

For datasets with geographic information, ensure [geopandas](https://geopandas.org/en/stable/) is installed in your Python environment. Alternatively, install the package with all necessary dependencies using pip:

```bash
pip install dratio[geo]
```

## API Keys

To use the API, [create an API key](https://dratio.io/app/api/). If you haven't registered, [create an account on dratio.io](https://dratio.io/getstarted/).

| Remember to securely store your API keys and avoid sharing them publicly. API keys grant access to all services on your behalf. If a key is compromised, delete and create new keys.

## Getting Started

The `Client` class enables access to all API resources using your API key.

```python
from dratio import Client

client = Client('Your API key')
```

Basic functionality allows you to search and filter available datasets for download.

```python
client.list_datasets()
```

After selecting a `Dataset`, access its information and download its content as a Pandas `DataFrame` or, for datasets with geographic information, as a `GeoDataFrame`.

```python
dataset = client.get_dataset('municipalities')

df = dataset.to_pandas() # Download as DataFrame
gdf = dataset.to_geopandas() # GeoDataFrame with geographic information
```

To gain a comprehensive understanding of the Dratio Python client and explore all its features, visit the [official documentation](https://dratio.readthedocs.com) on Read the Docs.

## License & Terms and Conditions

This source code is licensed under the Apache License, Version 2.0. Obtain a copy of the License at [apache.org](https://www.apache.org/licenses/LICENSE-2.0).

The use of the data offered by this client must comply with Dratio's terms and conditions. Obtain a copy of the terms at [dratio.io/legal/](https://dratio.io/legal/terms/).

## Support

If you encounter a bug or have a feature suggestion, please log an issue or contact us through our page or via email at [info@dratio.io](mailto:info@dratio.io)