from aws_ec2_provisioner.conf import LOGGING_STR_SIZE
from aws_ec2_provisioner.errors import RequestToAWSError


def validate_response_http_code(response):
    status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
    if status_code != 200:
        raise RequestToAWSError


# TODO: rename!
class Bcolors:
    def __init__(self, message_width):
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.LOGGING_STR_SIZE = message_width

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

    def green(self, text):
        print("{begin}{text}{end}".format(begin=self.OKGREEN, text=text, end=self.ENDC))

    def ok(self):
        text = "OK"
        print("{begin}{text}{end}".format(begin=self.OKGREEN, text=text, end=self.ENDC))

    def exists(self):
        text = "Already EXISTS"
        print("{begin}{text}{end}".format(begin=self.OKBLUE, text=text, end=self.ENDC))

    def fail(self):
        text = "FAIL"
        print("{begin}{text}{end}".format(begin=self.FAIL, text=text, end=self.ENDC))

    def warinig(self):
        text = "WARNING"
        print("{begin}{text}{end}".format(begin=self.WARNING, text=text, end=self.ENDC))

    def header(self):
        text = "HEADER"
        print("{begin}{text}{end}".format(begin=self.HEADER, text=text, end=self.ENDC))

    def message(self, text):
        print("{text}".format(text=text).ljust(self.LOGGING_STR_SIZE, '.'), end='')


bcolors = Bcolors(LOGGING_STR_SIZE)
