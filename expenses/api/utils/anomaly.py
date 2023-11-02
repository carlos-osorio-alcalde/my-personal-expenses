import os
import pickle

import neptune
from sklearn.ensemble import IsolationForest


def get_model() -> IsolationForest:
    """
    This function downloads the model from Neptune.

    Returns
    -------
    model : IsolationForest
        The model to predict anomalies.
    """
    # Load the model from neptune
    model_neptune = neptune.init_model(
        with_id="EX-ANOMODEL",
        project="carlos.osorio/expenses-anomaly",
        api_token=os.environ["NEPTUNE_API_TOKEN"] + "==",
    )

    # Get all the model versions
    model_versions_df = (
        model_neptune.fetch_model_versions_table().to_pandas()
    )

    # Get the latest model version
    latest_model_version_id = model_versions_df.sort_values(
        by=["sys/creation_time"], ascending=False
    ).iloc[0]["sys/id"]

    # Download the model
    neptune.init_model_version(
        project="carlos.osorio/expenses-anomaly",
        with_id=latest_model_version_id,
        api_token=os.environ["NEPTUNE_API_TOKEN"] + "==",
    )["model"].download("anomaly_model.pkl")

    # Load the model
    with open("anomaly_model.pkl", "rb") as file:
        model = pickle.load(file)

    return model
