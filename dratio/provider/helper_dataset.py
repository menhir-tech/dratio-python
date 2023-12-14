from typing import TYPE_CHECKING, Optional, Union

import geopandas as gpd
import pandas as pd

from dratio.exceptions import ObjectNotFound

if TYPE_CHECKING:
    from ..client import Client
    from ..models.dataset import Dataset

dataset_fileds_mapping = {
    "name": {
        "comment": "# Name of the dataset (English)",
        "default": "Here the name in English",
    },
    "name_es": {
        "comment": "# Name of the dataset (Spanish)",
        "default": "Nombre en Español",
    },
    "description": {
        "comment": "# Description of the dataset (English)",
        "default": "Here the description in English",
    },
    "description_es": {
        "comment": "# Description of the dataset (Spanish)",
        "default": "Descripción en Español",
    },
    "license": {
        "comment": "# License of the dataset (e.g. 'ine') -> get existing with client.list('license')",
        "default": "",
    },
    "publisher": {
        "comment": "# Publisher of the dataset (e.g. 'ine') -> get existing with client.list('publisher')",
        "default": "ine",
    },
    "scope": {
        "comment": "# Scope of the dataset -> get all scopes with client.list('scope')\n    # Example scopes: ['europe', 'spain', 'without-scope']",
        "default": "spain",
    },
    "order": {
        "comment": "# Order of the dataset in the marketplace (lower is first)",
        "default": 5,
    },
    "is_public": {
        "comment": "# Should be the dataset shown to non-admin users?",
        "default": True,
    },
    "categories": {
        "comment": "# list of categories of the dataset -> get existing with client.list('category')\n    # Example categories: ['employment', 'geospatial', 'population', 'socioeconomic']",
        "default": ["socioeconomic", "population"],
    },
    "level": {
        "comment": "# Level of detail the dataset -> get existing with client.list('data-level')\n    # Example data levels: ['census', 'postal-code', 'municipalities', 'provinces', 'regiones', ...]",
        "default": "Here the level",
    },
    "timestamp_column": {
        "comment": "# Timestamp column of the dataset",
        "default": None,
    },
    "start_data": {
        "comment": "# Start date of the dataset (if it is a time series)",
        "default": None,
    },
    "last_data": {
        "comment": "# Last date of the dataset (if it is a time series)",
        "default": None,
    },
    "n_time_slices": {
        "comment": "# Number of time points of the dataset (if it is a time series)",
        "default": 0,
    },
    "n_values": {
        "comment": "# Number of values of the dataset (number of rows)",
        "default": 0,
    },
    "n_variables": {
        "comment": "# Number of variables of the dataset (number of columns with references to other datasets)",
        "default": 0,
    },
    "n_features": {
        "comment": "# Number of features of the dataset (number of columns with values)",
        "default": 0,
    },
    "next_update": {
        "comment": "# Next estimated update of the dataset",
        "default": None,
    },
    "update_frequency": {
        "comment": "# Update frequency of the dataset (e.g. 'monthly', 'annual', 'triennial', ...).",
        "default": "custom",
    },
    "granularity": {
        "comment": "# Time granularity of the dataset (if it is a time series one month between time points would be 'monthly', ...)",
        "default": "custom",
    },
    "dataset_documentation": {
        "comment": "# Code of a dataset documentation",
        "default": None,
    },
    "related_datasets": {
        "comment": "# List of related datasets (e.g. ['municipalities', 'provinces'])",
        "default": [],
    },
}


feature_fields_mapping = {
    "name": {
        "comment": "# Name of the feature (English)",
        "default": "Here the name of the feature in English",
    },
    "name_es": {
        "comment": "# Name of the feature (Spanish)",
        "default": "Nombre en Español",
    },
    "description": {
        "comment": "# Description of the feature (English)",
        "default": "Here the description of the feature in English",
    },
    "description_es": {
        "comment": "# Description of the feature (Spanish)",
        "default": "Descripción en Español",
    },
    "feature_type": {
        "comment": '# Type of feature: "cat", "geo", "stat", "inter", "id", "number", "perc"',
        "default": "cat",
    },
    "data_type": {
        "comment": '# Data type of feature: "str", "int", "float", "text", "interval", "date". "datetime", "geo"',
        "default": "str",
    },
    "license": {"comment": "# Code of the feature license", "default": "ine-license"},
    "reference_feature": {
        "comment": "# Does this column reference another feature? Code of the feature or None",
        "default": None,
    },
}


def helper_dataset(
    client: "Client",
    dataset: Union["Dataset", str],
    df: Optional[Union[pd.DataFrame, gpd.GeoDataFrame]] = None,
    publisher: str = "ine",
    license: str = "ine-license",
) -> str:
    """Prints a code snnipet to update the fields of a dataset

    Args:
        dataset: A dratio.Dataset object or a string with the dataset code
        df: A pandas dataframe with the same columns as the dataset
        publisher: The publisher code
        license: The license code
    """

    if isinstance(dataset, str):
        dataset = client.get_dataset(dataset)

    # Checks if the dataset exists and loads previous values
    try:
        dataset = dataset.fetch()
        exists = True
    except ObjectNotFound:
        exists = False

    # Updates metadata from the dataframe
    if df is not None:
        dataset.metadata_from_pandas(df, publisher=publisher, license=license)

    # Code snippet
    if exists:
        initial_comment = (
            f"# Code for updating the dataset '{dataset.code}' (already exists)\n\n"
        )
    else:
        initial_comment = (
            f"# Code for creating the dataset '{dataset.code}' (new dataset)\n\n"
        )

    get_dataset = (
        f"# Get the dataset object\ndataset = client.get_dataset('{dataset.code}')\n"
    )
    if exists:
        get_dataset += (
            "dataset = dataset.fetch(fail_not_found=False) # Get previous values \n"
        )
    get_dataset += "\n"

    if df is not None:
        metadata_from_pandas = f"dataset.metadata_from_pandas(df, publisher='{publisher}', license='{license}') # Update metadata from the dataframe\n\n"
    else:
        metadata_from_pandas = ""

    dataset_fields = ""
    for key, comment in dataset_fileds_mapping.items():
        value = dataset._metadata.get(key, comment["default"])
        if key == "timestamp_column" and value is None:
            dataset_fields += f"    # '{key}': None, # No timestamp column detected\n"
            continue
        if isinstance(value, str):
            value = value.replace("\n", "\\n")
            value = value.replace("'", "\\'")
            value = value.replace('"', '\\"')
            value = "'" + value + "'"

        dataset_fields += f"    '{key}': {value}, {comment['comment']}\n"

    dataset_dictionary = "# Edit this block to update the dataset fields\n"
    dataset_dictionary += f"dataset.from_dict({{\n{dataset_fields}}})\n\n"
    dataset_dictionary += "# Tip for the update frequency and granularity:\n"
    dataset_dictionary += "# Allowed values: ['without', 'custom', 'quinquennial', 'quadrennial', 'triennial', 'biennial',\n"
    dataset_dictionary += "#                'annual', 'semiannual', '4monthly', 'quarterly', 'every2months',\n"
    dataset_dictionary += "#                'Monthly', 'twicemonthly', 'weekly', 'daily', 'dailybusiness', 'hourly', 'everyminute']\n\n"

    if not exists and df is None:
        feature_fields = "# PLEASE! -> provide a df to infer the columns and call again the code generator\n"
        feature_fields += "# -> helper_dataset(client, dataset, df)\n\n"
    elif dataset.features:
        feature_fields = "# Review and edit this block to update the feature fields\n\n"

        for i, feature in enumerate(dataset.features):
            if exists:
                try:
                    feature = feature.fetch()
                except ObjectNotFound:
                    pass
            feature_str = f"#Feature {i}: {feature.code} (column {feature._metadata.get('column', '-')})\n"
            feature_str += f"dataset.features[{i}].from_dict({{\n"

            for key, comment in feature_fields_mapping.items():
                value = feature._metadata.get(key, comment["default"])

                if isinstance(value, str):
                    value = value.replace("\n", "\\n")
                    value = value.replace("'", "\\'")
                    value = value.replace('"', '\\"')
                    value = "'" + value + "'"

                feature_str += f"    '{key}': {value}, {comment['comment']}\n"

            feature_str += "})\n\n"
            feature_fields += feature_str

    save = "\n# Uncomment this to save the dataset and the features\n# dataset.save() # <- Uncomment this\n\n"

    if df is not None:
        upload_df = "# Upload the files\n"
        if isinstance(df, gpd.GeoDataFrame):
            upload_df += "# Uncomment this upload a GEOPANDAS dataframe (assuming is called gdf)\n"
            upload_df += "# dataset.upload_file(gdf, filetype='geoparquet') # If file exists and want to replace add update=True\n\n"

            upload_df += "# Uncomment this upload a pandas without the geometry column (assuming the geopandas if called gdf)\n"
            upload_df += "# dataset.upload_file(gdf.drop(columns=['geometry']), filetype='parquet') # If file exists and want to replace add update=True\n\n"

        else:
            upload_df += (
                "# Uncomment this upload a pandas dataframe (assuming is called df)\n"
            )
            upload_df += "# dataset.upload_file(df, filetype='parquet') # If file exists and want to replace add update=True\n\n"

    else:
        upload_df = ""

    string = (
        initial_comment
        + get_dataset
        + metadata_from_pandas
        + dataset_dictionary
        + feature_fields
        + save
        + upload_df
    )
    return string
