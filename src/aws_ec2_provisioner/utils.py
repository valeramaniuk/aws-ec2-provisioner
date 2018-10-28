from aws_ec2_provisioner.errors import RequestToAWSError


def validate_response_http_code(response):
    status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
    if status_code != 200:
        raise RequestToAWSError


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
