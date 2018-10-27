class EC2ProvisionerRootException(Exception):
    pass


class RequestToAWSError(EC2ProvisionerRootException):
    pass
