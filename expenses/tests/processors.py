from expenses.processors.factory import EmailProcessorFactory


def processors_payment_test():
    """
    This test checks the processors are working properly.
    """
    transactions_emails = [
        {
            "Pago": "Bancolombia te informa Pago por $99,999.00 a ESTABLECIMIENTO COM desde producto *9999. 06/08/2023 14:30. Inquietudes al 6045109095/018000931987."  # noqa
        },
        {
            "Pago": "Bancolombia: Pagaste $99,999.00 a ESTABLECIMIENTO desde tu producto *9999 el 05/02/2024 09:55. ¿Dudas? 6045109095/018000931987."  # noqa
        },
        {
            "Retiro": "Bancolombia informa retiro en Corresponsal BARRIO CARLOS E RESTREPO MEDEL en MEDELLÍN por $100,000 el 06/02/24 a las 08:37. Dudas al 018000931987"  # noqa
        },
    ]
    for transaction_test in transactions_emails:
        transaction_type, email_str = transaction_test.popitem()
        processor_factory = EmailProcessorFactory()
        transaction_type_finded = (
            processor_factory._identify_transaction_type(email_str)
        )

        # Check the transaction type is correct.
        assert transaction_type_finded == transaction_type


if __name__ == "__main__":
    processors_payment_test()
