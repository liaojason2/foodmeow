def convertAmountToCent(amount, digits=2):
    """
    Convert the amount to cents.

    :param amount: The amount in dollars (e.g., 140.00)
    :return: The amount in cents (e.g., 14000)
    """
    if type(amount) == float:
        return int(amount * (10 ** digits))
    if type(amount) == str:
        if '.' in amount:
            dollars, cents = amount.split('.')
            cents = (cents + '00')[:2]  # ensure 2 digits
            return int(dollars) * 100 + int(cents)
        else:
            return int(amount) * 100

def convertCentToDecimalString(amount):
    """
    Convert the amount in cents to a decimal string.

    :param amount: The amount in cents (e.g., 14000)
    :return: The amount in dollars as a string (e.g., "140.00")
    """
    if type(amount) == int:
        dollars = amount // 100
        cents = amount % 100
        return f"{dollars}.{cents:02d}"
    elif type(amount) == float:
        amount = str(amount)
        dollars, cents = amount.split('.')
        cents = (cents + '00')[:2]  # ensure 2 digits
        return f"{dollars}.{cents}"
        
    else:
        raise ValueError("Amount must be an integer.")