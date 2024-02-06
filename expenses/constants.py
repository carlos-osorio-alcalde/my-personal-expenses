TRANSACTION_MESSAGES_TYPES_ = [
    "Bancolombia le informa",
    "Bancolombia te informa",
    "Bancolombia informa",
    "Realizaste una transferencia",
    "Bancolombia: ",
]

# This list includes all the possible names of the transaction types.
TRANSACTION_TYPES_NAMES_ = [
    "Compra",
    "Retiro",
    "Pago",
    "recepcion transferencia",
    "QR",
    "Transferencia",
    "Pagaste",
]

# This mapping is used to identify relationships between transactions.
# For example, the transaction type "Pago" also could be "Pagaste"
# and the transaction type "Compra" also could be "Compraste".
# The values of this diccionary must be part of the keys of the
# TRANSACTION_TYPES_ dictionary.
TRANSACTION_TYPES_MAPPING_ = {"Pagaste": "Pago"}


# This is the dictionary that contains the transaction types and their
# corresponding processors.
TRANSACTION_TYPES_ = {
    "Compra": {
        "module_name": "transactions.purchase",
        "class_name": "PurchaseEmailProcessor",
        "implemented": True,
    },
    "Retiro": {
        "module_name": "transactions.withdrawal",
        "class_name": "WithdrawalEmailProcessor",
        "implemented": True,
    },
    "Pago": {
        "module_name": "transactions.payment",
        "class_name": "PaymentEmailProcessor",
        "implemented": True,
    },
    "recepcion transferencia": {
        "module_name": "transactions.transfer_reception",
        "class_name": "TransferReceptionEmailProcessor",
        "implemented": True,
    },
    "QR": {
        "module_name": "transactions.transfer_qr",
        "class_name": "QREmailProcessor",
        "implemented": True,
    },
    "Transferencia": {
        "module_name": "transactions.transfer",
        "class_name": "TransferEmailProcessor",
        "implemented": True,
    },
}
