import sys

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3

if PY3:
    string_types = (str,)
    text_type = str
else:
    string_types = (basestring,)  # noqa
    text_type = unicode  # noqa

def write_bytes(out_data):
    """Write Python2 and Python3 compatible byte stream."""
    if sys.version_info[0] >= 3:
        if isinstance(out_data, type(u'')):
            return out_data.encode('ascii', 'ignore')
        elif isinstance(out_data, type(b'')):
            return out_data
    else:
        if isinstance(out_data, type(u'')):
            return out_data.encode('ascii', 'ignore')
        elif isinstance(out_data, type(str(''))):
            return out_data
    msg = "Invalid value for out_data neither unicode nor byte string: {0}".format(out_data)
    raise ValueError(msg)

