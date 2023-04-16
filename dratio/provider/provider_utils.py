#
# Copyright 2022 dratio.io. All rights reserved.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#
#
# The use of the services offered by this client must be in accordance with
# dratio's terms and conditions. You may obtain a copy of the terms at
#
#     https://dratio.io/legal/terms/
#
"""
Functionalities to help with the creation of datasets
"""
from typing import TYPE_CHECKING, Union, Optional
import pandas as pd
import geopandas as gpd
import json
import re

if TYPE_CHECKING:
    from ..models.dataset import Dataset, Feature
    from ..models.publisher import Publisher
    from ..models.license import License

__all__ = ["metadata_from_pandas"]

# ['code', 'name',
# 'name_es', 'is_public',
# 'description', 'description_es',
# 'order', 'last_update',
# 'preview', 'timestamp_column',
# 'start_data', 'last_data',
# 'n_time_slices', 'n_values',
# 'n_variables', 'n_features',
# 'next_update', 'update_frequency',
# 'granularity', 'categories',
# 'level', "license", "scope"]


def metadata_from_pandas(dataset: Dataset,
                         df: Union["pd.DataFrame", "gpd.GeoDataFrame"],
                         publisher: Union[str, "Publisher"],
                         license: Optional[Union[str, "License"]] = None,
                         timestamp_column: str = "timestamp", ) -> "Dataset":
    """Given a dataset and a pandas dataframe, it will update the metadata of the dataset
    with the information from the dataframe.

    """

    has_geom = isinstance(df, gpd.GeoDataFrame)
    has_timestamp = timestamp_column in df.columns
    if has_geom:
        geo_feature = geometry_column_feature(
            df, "geometry", order=len(df.columns))
        df = pd.DataFrame(df.drop(columns=["geometry"]))

    for order, column in enumerate(df.columns):
        feature = column_feature(df[column], column, order=order+1)
        dataset.add_feature(feature)

    preview = extract_table_preview(df)

    if has_geom:
        preview['geometry'] = '<geometry>'
        dataset.add_feature(geo_feature)

    dataset['preview'] = json.loads(preview.to_json(orient='records'))

    if has_timestamp:
        dataset['start_data'] = pd.to_datetime(
            df[timestamp_column].min()).isoformat()
        dataset['last_data'] = pd.to_datetime(
            df[timestamp_column].max()).isoformat()
        dataset['n_time_slices'] = int(df[timestamp_column].nunique())

    for feature in dataset.features:
        feature["publisher"] = publisher
        feature["license"] = license or publisher.license or None

    # Time metadata

    return dataset


def infer_granularity(timestamp_column: pd.Series) -> str:
    import numpy as np

    median = np.median(
        np.diff(np.array(pd.to_datetime(timestamp_column).unique())))

    seconds = np.timedelta64(median, 's').astype(int)
    days = np.timedelta64(median, 'D').astype(int)

    if seconds < 500:
        s = 'everyminute'  # Every minute
    elif seconds < 5000:
        s = 'hourly'  # Every hour
    elif days < 1.1:
        s = 'daily'  # Daily
    elif days < 2.1:
        s = 'dailybusiness'  # Daily Businness
    elif days < 10:
        s = 'weekly'  # Weekly
    elif days < 20:
        s = 'twicemonthly'  # Twice a month
    elif days < 40:
        s = 'Monthly'  # Monthly
    elif days < 80:
        s = 'every2months'  # Every two months
    elif days < 100:
        s = 'quarterly'  # Quarterly (every 3 months)
    elif days < 150:
        s = '4monthly'  # Every four months
    elif days < 200:
        s = 'semiannual'  # Semiannual (every 6 months)
    elif days < 400:
        s = 'annual'  # Annual
    elif days < 800:
        s = 'biennial'  # Biennial (every 2 years)
    elif days < 1200:
        s = 'triennial'  # Triennial (every 3 years)
    elif days < 1600:
        s = 'quadrennial'  # Quadrennial (Every 4 years)
    else:
        s = 'qustom'  # Custom

    return s


def slugify(text: str) -> str:
    name = text.strip().lower().replace(' ', '-').replace('_', '-')
    # Also substitutes multiple '-' into a single one
    return re.sub(r'[-]+', '-', name)


def infer_data_type(column: "pd.Series") -> Union[str, None]:
    name = str(column.dtype)
    value_type = str(type(column.values[0]))

    if 'interval' in name:
        return 'interval'
    elif 'int' in name:
        return 'int'
    elif 'float' in name:
        return "float"
    elif 'category' in name:
        return value_type
    elif 'bool' in name:
        return 'str'
    elif 'date' in name:
        return 'datetime'
    elif 'O' in name:
        if 'str' in value_type:
            return str
        if 'datetime.date' in value_type:
            return 'date'
        if 'datetime' in value_type:
            return 'datetime'

    return None


def infer_feature_type(column: "pd.Series") -> Union[str, None]:
    data_type = infer_data_type(column)

    if data_type == 'interval':
        return 'interval'
    elif data_type == 'category':
        return 'cat'
    elif data_type == 'float':
        return 'number'
    elif data_type == 'str':
        return 'cat'
    elif column.is_unique:
        return 'id'
    elif data_type == 'int':
        return 'number'

    return None


def column_feature(dataset: Dataset, column: "pd.Series", column_name: str) -> "Feature":
    subcode = slugify(column_name)
    code = f"{dataset.code}__{subcode}"
    feature = dataset._client.get_feature(code)
    feature["name"] = subcode.replace('-', ' ').replace('_', ' ').capitalize()
    feature["dataset"] = dataset
    feature["column"] = column_name
    feature["data_type"] = infer_data_type(column)
    feature["feature_type"] = infer_feature_type(column)

    feature["is_unique"] = bool(column.is_unique)
    feature["n_values"] = len(column)
    feature["n_not_null"] = int(column.notna().sum())

    return feature


def geometry_column_feature(dataset: Dataset, gdf: "gpd.GeoDataFrame", column_name: str, order: int) -> "Feature":
    subcode = slugify(column_name)
    code = f"{dataset.code}__{subcode}"
    feature = dataset._client.get_feature(code)

    feature["name"] = subcode.replace('-', ' ').replace('_', ' ').capitalize()
    feature["dataset"] = dataset
    feature["column"] = column_name
    feature["data_type"] = 'geo'
    feature["feature_type"] = 'geo'
    feature["crs"] = gdf.crs.name

    return feature


def extract_table_preview(df: "pd.DataFrame", n_rows: int = 50) -> "pd.DataFrame":

    preview = df.head(n_rows).copy().reset_index(drop=True)
    if "id" not in preview.columns:
        preview = preview.rename_axis('id').reset_index()
    return preview
