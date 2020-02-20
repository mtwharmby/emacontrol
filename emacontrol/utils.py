def input_to_int(value):
    """
    Checks that user (string) input is an integer.

    Parameters
    ----------
    value : user input to check

    Returns
    -------
    integer : n cast to an integer

    Raises
    ------
    ValueError : if n is not an integer
    """
    if str(value).isdigit():
        return num_to_int(float(value))
    else:
        raise ValueError('Expecting integer. Got: "{0}" ({1})'
                         .format(value, type(value)))


def num_to_int(num):
    """
    Checks that a numerical value (e.g. returned by robot) is an integer and
    not a float.

    Parameters
    ----------
    num : number to check

    Returns
    -------
    integer : num cast to an integer

    Raises
    ------
    ValueError : if n is not an integer
    """
    if num % 1 == 0:
        return int(num)
    else:
        raise ValueError('Expecting integer. Got: "{0}" ({1})'
                         .format(num, type(num)))
