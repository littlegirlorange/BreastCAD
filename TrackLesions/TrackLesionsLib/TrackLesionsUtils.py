def enum(*sequential, **named):
    '''
    http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    To call:
    >>> Numbers = enum('ZERO', 'ONE', 'TWO')
    >>> Numbers.ZERO
    0
    >>> Numbers.ONE
    1
    '''
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)




