import os
import time
from hashlib import md5
import hmac


def _flat(f, xs): return [y for ys in xs for y in f(ys)]


def md5_string(str=''):
    return md5(str.encode('utf-8')).hexdigest()


def request_id():
    return md5(str(int(time.time())).encode('utf-8')).hexdigest()


def get_writeable_properties(clazz):
    return _flat(
        lambda clazz: [
            attr for attr,
            value in vars(clazz).items() if isinstance(
                value,
                property) and value.fset is not None],
        clazz.__mro__)


def has_writeable_property(cls, prop):
    import collections
    if [property for property in get_writeable_properties(cls) if isinstance(
            property, collections.Iterable) and (prop in property)]:
        return True
    return False


def get_env(varname, default_value=None):
    """
    Return the value of the environment variable or default_value.
    This is a helper method that wraps ``os.environ.get`` to ensure type
    compatibility across py2 and py3. For py2, any value obtained from an
    environment variable, ensure ``unicode`` type and ``str`` for py3. The
    casting is done only for string variables.
    :type varname: ``str``
    :param varname: Name of the environment variable for which to check.
    :param default_value: Return this value is the env var is not found.
                          Defaults to ``None``.
    :return: Value of the supplied environment if found; value of
             ``default_value`` otherwise.
    """
    value = os.environ.get(varname, default_value)
    return value
