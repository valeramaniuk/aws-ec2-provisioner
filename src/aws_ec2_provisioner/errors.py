class EC2ProvisionerRootException(Exception):
    pass


class RequestToAWSError(EC2ProvisionerRootException):
    pass


class LaunchCfgCreationError(EC2ProvisionerRootException):
    pass


class SecurityGroupCreationError(EC2ProvisionerRootException):
    pass


class LCfgAlreadyExists(EC2ProvisionerRootException):
    pass


class ASGAlreadyExists(EC2ProvisionerRootException):
    pass
