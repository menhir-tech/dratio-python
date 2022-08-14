![dratio.io logo](https://user-images.githubusercontent.com/16774925/184549419-b05ebfd2-436e-41e2-9172-a05d53e67c1d.svg)

---

# Python Client for dratio.io API web services

Data as-a-service to help make better decisions based on technology

## Description

### What is dratio?
Dratio is the result of our experience creating solutions for data-driven decision making in a wide variety of industries. We provide tools and data as-a-service that enable to create robust data solutions in an agile way.

### Python client

This client allows you to interact with the services offered by the [dratio.io](https://dratio.io) platform from Python.
You will be able to download ready-to-use datasets for all types of industries. All data is reviewed, documented and linked together by common variables, allowing you to reference directly with your data without spending time on integration.

## Support

This library is supported by dratio's team.
If you find a bug, or have a feature suggestion, please log an issue or
contact us through [our page](https://dratio.io/contact/) or via mail
to [info@dratio.io](mailto:info@dratio.io).

## Requirements

- Python 3.5 or later.
- A dratio.io API key.

## API Keys

Each dratio.io Web Service request requires an API key. API keys
are generated in the 'API' section
of the [dratio.io](https://dratio.io/app/api/) platform.

**Important:** This key should be kept secret on your server.

## Installation

You can install this client through PyPI

    $ pip install -U dratio

or by downloading the source code and installing the package locally

    $ git clone git@github.com:dratio-io/dratio-client.git
    $ cd dratio-client
    $ python setup.py install

## Usage

```python
from dratio import Client

client = Client('<your api token>')

df = client.get('employment-municipality-sector')
```

## License & Terms and conditions

Copyright 2022 _dratio.io_. All rights reserved.

This source code is licensed under the Apache License, Version 2.0. You may obtain a copy of
the License at [apache.org](https://www.apache.org/licenses/LICENSE-2.0).

The use of the services offered by this client must be in accordance with dratio's terms and conditions. You may obtain a copy of the terms at [dratio.io](https://dratio.io/legal/terms)
