import click

from security_groups import provision_security_groups
from load_balancer import provision_and_configure_elb
from autoscaling import create_launch_conf_and_asg


AMAZON_LINUX_AMI = "ami-04534c96466647bfb"
# installs and starts ngnix, nothing else
USER_DATA = """
#!/bin/bash
sudo amazon-linux-extras install nginx1.12 -y
sudo chkconfig nginx on
sudo service nginx start
"""


@click.command()
@click.option('--aws-profile', prompt='AWS profile name(accept default)', default="default",
              help='The name of access key (~/.aws/credentials)')

@click.option('--vpc-id', prompt='VPC-id', help='The id of the VPC in which you want to deploy the application')
@click.option('--subnet-id', prompt='subnet-id', help='The id of the subnet in which you want to deploy'
                                                    ' the application. Only the single subnet architecture '
                                                     'is supported at the moment')
@click.option('--project-name', prompt='Project name', help='The name of the application')
@click.option('--instance-type', prompt='Instance type [1] t2.micro [2] t2.medium]',
             default=1, help='Type of instances.\n1.t2.micro *default*\n2.t2.medium')
@click.option('--min-asg-size', prompt='Min group size', default=1, help='Min group size.')
@click.option('--max-asg-size', prompt='Max group size', default=1, help='Max group size')
@click.option('--region', prompt='Region [1] us-west-2', default=1, help='The region where the system will be deployed.'
                                                                        ' Only us-west-2 is supported at the moment')


def main(region, max_asg_size, min_asg_size, instance_type, project_name, subnet_id, vpc_id, aws_profile):

   instance_type = _get_instace_type(instance_type)

   configuration = {
       "project_name": project_name,
       "min_size": min_asg_size,
       "max_size": max_asg_size,
       "desired_capacity": 1,
       "image_id": AMAZON_LINUX_AMI,
       "user_data": USER_DATA,
       "instance_type": instance_type,
       "subnets": subnet_id,
       "vpc_id": vpc_id,
       "aws_profile": aws_profile,
       "region": region
   }

   sg_provisioning_result = provision_security_groups(configuration)
   configuration["security_groups"] = sg_provisioning_result

   elb_creation_data = provision_and_configure_elb(configuration)
   configuration["elb_name"] = elb_creation_data["elb_name"]
   configuration["elb_response"] = elb_creation_data["elb_response"]

   create_launch_conf_and_asg(configuration)

   print(configuration["elb_response"].get("DNSName", "Failed, sorry!"))


def _get_instace_type(user_choice):
    default = "t2.micro"
    instance_mapping = {
        1: "t2.micro",
        2: "t2.medium"
    }
    return instance_mapping.get(user_choice, default)


if __name__ == '__main__':
    main()
