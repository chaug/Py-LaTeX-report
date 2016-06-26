VERSION = (1, 0, 0, 'beta', 0)

def get_version(*args, **kwargs):
    "Returns a PEP 386-compliant version number from VERSION."
    assert len(VERSION) == 5
    assert VERSION[3] in ('beta', 'rc', 'final')

    parts = 2 if VERSION[2] == 0 else 3
    main = '.'.join(str(x) for x in VERSION[:parts])

    sub = ''
    if VERSION[3] != 'final':
        mapping = {'beta': 'b', 'rc': 'c'}
        sub = mapping[VERSION[3]] + str(VERSION[4])

    return str(main + sub)
