import random

def make_bank_payment():
    """
    Simulate the bank operation to make a payment.
    The result can be 'successful', 'unsuccessful', or 'pending'.
    """
    return random.choice(['successful', 'unsuccessful', 'pending'])


def track_bank_payment(payment):
    """
    Simulate the bank operation to track the status of a specific payment.
    If the payment is in 'pending' status, this function returns the final result
    as either 'successful' or 'unsuccessful'.
    """
    if payment.status == 'pending':
        return random.choice(['successful', 'unsuccessful'])
    return payment.status