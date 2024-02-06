import importlib
from typing import Dict

from expenses.constants import TRANSACTION_TYPES_
from expenses.processors.base import EmailProcessor


def import_processors() -> Dict[str, EmailProcessor]:
    """
    This function imports the processors of the transactions. It returns a
    dictionary with the transaction type and the corresponding processor.

    Returns
    -------
    Dict[str, EmailProcessor]
        The dictionary with the transaction type and the corresponding
        processor.
    """
    implemented_processors = {
        transaction: getattr(
            importlib.import_module(
                f"expenses.processors.{implementation['module_name']}"
            ),
            implementation["class_name"],
        )
        for transaction, implementation in TRANSACTION_TYPES_.items()
        if implementation["implemented"]
    }
    return implemented_processors
