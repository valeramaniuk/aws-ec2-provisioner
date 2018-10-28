class EC2ProvisionerRootException(Exception):
    pass


class RequestToAWSError(EC2ProvisionerRootException):
    pass


class LaunchCfgCretationError(EC2ProvisionerRootException):
    pass
