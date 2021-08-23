import array

def ReadNInput(binary_input, n):
    """ Returns n binary values """
    result = binary_input.read(n)
    if len(result) < n:
        raise EOFError()
    return result


def ConvertToSmallInt(binary_input, n):
    '''Convert binary to small integer'''
    result = 0
    for (i, b) in enumerate(ReadNInput(binary_input, n)):
        result |= b << (i * 8)
    return result


def CheckFile(condition, message):
    '''Raise Value error if condition '''
    if condition:
        raise ValueError(message)