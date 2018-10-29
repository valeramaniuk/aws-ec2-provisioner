DEFAULT_REGION = 'us-west-1'
AMAZON_LINUX_AMI_US_WEST_2 = "ami-04534c96466647bfb"

# installs and starts ngnix, nothing else
USER_DATA = """
#!/bin/bash
sudo amazon-linux-extras install nginx1.12 -y
sudo chkconfig nginx on
sudo service nginx start
# to generate CPU load on start up for autoscaling debugging
#cat /dev/zero > /dev/null
"""

SCALING_DEFAULT_TARGET_VALUE_PERCENT = 70
ASSOCIATE_PUBLIC_IP_BY_DEFAULT = True
DEFAULT_COOLDOWN_SECONDS = 300
HEATHCHECK_GRACE_PERIOD_SECONDS = 120


LOGGING_STR_SIZE = 60
