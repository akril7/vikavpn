class ServiceError(Exception):
    pass


class ConfiguratorError(ServiceError):
    pass


class ControllerError(ServiceError):
    pass


class InstallerError(ServiceError):
    pass
