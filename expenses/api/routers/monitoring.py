import os
import pickle
import tempfile
from typing import Literal

import neptune
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from numpy import where
from pandas import read_sql, to_datetime
from sklearn.ensemble import IsolationForest

from expenses.api.schemas import AnomalyPredictionOutput
from expenses.api.security import check_access_token
from expenses.api.utils import get_cursor, get_model

router = APIRouter(prefix="/monitoring")


@router.post("/model", dependencies=[Depends(check_access_token)])
def retrain_anomaly_model(
    max_samples: int, contamination: float, bootstrap: bool
) -> str:
    """
    This function retrains the anomaly model with the current data
    and save the model as a pkl file
    """
    conn, _ = get_cursor(return_conn=True)

    # Get the data from the database
    query = """
        SELECT
            CAST(datetime AS DATE) AS date_,
            (-1) * AVG(CAST(amount AS float)) AS avg_amount,
            (-1) * MIN(CAST(amount AS float)) AS max_amount,
            COUNT(DISTINCT id) AS total_trx
        FROM [dbo].[transactions]
        WHERE transaction_type = 'Compra' or
              transaction_type = 'QR' or
              transaction_type = 'Transferencia'
        GROUP BY CAST(datetime AS DATE)
        ORDER BY CAST(datetime AS DATE) DESC;
        """
    df = read_sql(query, conn)

    # Make modifications to the data
    df["date_"] = to_datetime(df["date_"])
    df["weekend"] = where(df["date_"].dt.dayofweek < 5, 0, 1)

    # Create the dataset
    X = df[["avg_amount", "max_amount", "total_trx", "weekend"]]

    # Initialize Neptune run to log the model
    run = neptune.init_run(
        project="carlos.osorio/expenses-anomaly",
        api_token=os.environ["NEPTUNE_API_TOKEN"] + "==",
    )

    # Fit the Isolation Forest model
    params = {
        "max_samples": max_samples,
        "contamination": contamination,
        "bootstrap": bootstrap,
    }
    model = IsolationForest(**params)
    model.fit(X)

    # Save the model to a temporary file
    with tempfile.NamedTemporaryFile(
        suffix=".pkl", delete=False
    ) as temp_file:
        pickle.dump(model, temp_file)

        # Log the model
        run["parameters"] = params
        run["number_of_samples"] = X.shape[0]

        model = neptune.init_model_version(
            model="EX-ANOMODEL",
            project="carlos.osorio/expenses-anomaly",
            api_token=os.environ["NEPTUNE_API_TOKEN"] + "==",
        )
        model["model"].upload(temp_file.name)
        model.change_stage("staging")

    run.stop()
    return "Model retrained successfully"


@router.get(
    "/prediction",
    dependencies=[Depends(check_access_token)],
)
def predict_anomaly(
    avg_amount: float,
    max_amount: float,
    total_trx: int,
    weekend: Literal["yes", "no"],
) -> AnomalyPredictionOutput:
    """
    This function predicts if the input is an anomaly or not.

    Parameters
    ----------
    input : AnomalyPredictionInput
        The input to predict.

    Returns
    -------
    Tuple[float, int]
        The score and the prediction.
    """
    # This is made here to avoid loading the model at the start of the
    # application. This is efficient since, altough the model is loaded
    # every time the endpoint is called, the endpoint is called less
    # frequently than the application is started.
    model = get_model()

    # Data to predict
    data = [
        [avg_amount, max_amount, total_trx, 1 if weekend == "yes" else 0]
    ]

    try:
        # Predict the anomaly
        prediction = model.predict(data)

        # Get the score
        score = model.score_samples(data)

        return AnomalyPredictionOutput(
            score=score[0],
            prediction="anomaly" if prediction[0] == -1 else "normal",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
