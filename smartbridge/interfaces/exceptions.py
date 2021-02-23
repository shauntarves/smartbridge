"""
Specification for exceptions raised by a provider
"""


class SmartbridgeBaseException(Exception):
    """
    Base class for all Smartbridge exceptions
    """
    pass


class WaitStateException(SmartbridgeBaseException):
    """
    Marker interface for object wait exceptions.
    Thrown when a timeout or errors occurs waiting for an object does not reach
    the expected state within a specified time limit.
    """
    pass


class InvalidConfigurationException(SmartbridgeBaseException):
    """
    Marker interface for invalid launch configurations.
    Thrown when a combination of parameters in a LaunchConfig
    object results in an illegal state.
    """
    pass


class ProviderInternalException(SmartbridgeBaseException):
    """
    Marker interface for provider specific errors.
    Thrown when Smartbridge encounters an error internal to a
    provider.
    """
    pass


class ProviderConnectionException(SmartbridgeBaseException):
    """
    Marker interface for connection errors to a provider.
    Thrown when Smartbridge is unable to connect with a provider,
    for example, when credentials are incorrect, or connection
    settings are invalid.
    """
    pass


class InvalidNameException(SmartbridgeBaseException):
    """
    Marker interface for any attempt to set an invalid name on
    a Smartbridge resource. An example would be setting uppercase
    letters, which are not allowed in a resource name.
    """

    def __init__(self, msg):
        super(InvalidNameException, self).__init__(msg)


class InvalidValueException(SmartbridgeBaseException):
    """
    Marker interface for any attempt to set an invalid value on a Smartbridge
    resource. An example would be setting an unrecognized value for the
    suction level of a vacuum other than what is defined by VacuumSuction.
    """

    def __init__(self, param, value):
        super(InvalidValueException, self).__init__(
            "Param %s has been given an unrecognized value %s" %
            (param, value))


class InvalidParamException(InvalidNameException):
    """
    Marker interface for an invalid or unexpected parameter, for example,
    to a service.find() method.
    """

    def __init__(self, msg):
        super(InvalidParamException, self).__init__(msg)
