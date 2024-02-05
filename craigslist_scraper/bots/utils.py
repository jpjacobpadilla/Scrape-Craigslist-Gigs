import re
import time

import numpy as np


def estimate_compensation(comp_msg: str) -> float:
    """
    Takes the compensation message from Craigslist and attempts
    to extract a dollar amount for the gig.

    Args:
        comp_msg: The compensation message from the gig offerer
    
    Returns:
        A float which is the estimated compensation.
    """
    regex = r"\$(\d{1,3}(?:,\d{3})*|\d+)(\.\d{2})?"

    # Search for the pattern in the text
    match = re.search(regex, comp_msg)

    # If a match is found, extract and print the dollar amount
    if match:
        dollar_amount = match.group()
        return float(dollar_amount.strip('$').replace(',', ''))

    return None


def gaussian_number_generator(
        low: int | float, 
        high: int | float, 
        Kurtosis: int = 4
    ) -> float:
    """
    Generates a random number based on a normal distribution 
    with automatically determined standard deviation.

    Args:
        low: The minimum acceptable value.
        high: The maximum acceptable value.
        kurtosis: Roughly how spread out the data is.

    Returns:
        A number to then probably use to sleep.
    """
    mean = (high + low) / 2
    std_dev = (high - low) / Kurtosis
    
    while (number := np.random.normal(mean, std_dev)) < low:
        pass
    
    return round(number, 3)


def human_sleep_seconds(low: int | float, high: int | float) -> float:
    return time.sleep(gaussian_number_generator(low, high))


def human_sleep_milliseconds(low: int | float, high: int | float) -> float:
    return time.sleep(gaussian_number_generator(low, high) / 1000)