import pprint
import click
import boto3

from aws_ec2_provisioner.conf import SCALING_DEFAULT_TARGET_VALUE_PERCENT, \
    AMAZON_LINUX_AMI_US_WEST_2, USER_DATA, DEFAULT_REGION
from aws_ec2_provisioner.menu import display_select_vpc_menu, display_select_subnet_menu, \
    display_select_aws_profile_menu
from aws_ec2_provisioner.utils import bcolors
from aws_ec2_provisioner.vpc import get_available_vpcs, get_subnets_for_vpc

from aws_ec2_provisioner.security_groups import provision_security_groups
from aws_ec2_provisioner.load_balancer import provision_and_configure_elb
from aws_ec2_provisioner.autoscaling import create_launch_conf_and_asg


pp = pprint.PrettyPrinter(indent=4)


@click.command()
@click.option('--aws-profile',
              help='The name of access key/secret key pair (~/.aws/credentials)')
@click.option('--region', prompt='Region [1] us-west-1 (is the only supported at the moment)',
              default=1,
              help='The region where the system will be deployed.'
                   ' Only us-west-1 is supported at the moment'
              )
@click.option('--vpc-id', help='The id of the VPC in which you want to deploy the application')
@click.option('--subnet-id', help='The id of the subnet in which you want to deploy'
                                  ' the application. Only the single subnet architecture '
                                  'is supported at the moment')
@click.option('--project-name', prompt='Project name', help='The name of the application')
@click.option('--instance-type', prompt='Instance type [1] t2.micro [2] t2.medium]',
              default=1, help='Type of instances.\n1.t2.micro *default*\n2.t2.medium')
@click.option('--min-asg-size', prompt='Min group size', default=1, help='Min group size.')
@click.option('--max-asg-size', prompt='Max group size', default=1, help='Max group size')
@click.option('--debug-mode', default='n', help='DEBUG mode')
@click.option('--scaling-target-value', help='Scaling policy target value %')
def main(
    region, max_asg_size, min_asg_size,
    instance_type, project_name, subnet_id,
    vpc_id, aws_profile, debug_mode, scaling_target_value
):

    if not aws_profile:
        aws_profile = _select_aws_profile()

    region = _get_region_name(region)
    session = _get_boto3_session(region=region, profile=aws_profile)

    instance_type = _get_instace_type(instance_type)
    debug_mode = _get_debug_mode(debug_mode)

    if not vpc_id:
        vpc_id = _select_vpc(session, region)

    if not subnet_id:
        subnet_id = _select_subnet(session, vpc_id)

    if not scaling_target_value:
        scaling_target_value = SCALING_DEFAULT_TARGET_VALUE_PERCENT

    configuration = {
       "project_name": project_name,
       "min_size": min_asg_size,
       "max_size": max_asg_size,
       "image_id": AMAZON_LINUX_AMI_US_WEST_2,
       "user_data": USER_DATA,
       "instance_type": instance_type,
       "aws_profile": aws_profile,
       "region": region,
       "debug_mode": debug_mode,
       "vpc_id": vpc_id,
       "subnets": subnet_id,
       "scaling_target_value_percent": scaling_target_value
    }

    sg_provisioning_result = provision_security_groups(configuration, session)
    configuration["security_groups"] = sg_provisioning_result

    elb_creation_data = provision_and_configure_elb(configuration, session)
    configuration["elb_name"] = elb_creation_data["elb_name"]
    dns_name = elb_creation_data["elb_dns"]

    create_launch_conf_and_asg(configuration, session)

    _report_final_status(dns_name)


def _report_final_status(dns_name):
    bcolors.message("Application will shortly be available at")
    if dns_name:
        bcolors.green(dns_name)
    else:
        bcolors.fail()


def _get_instace_type(user_choice):
    default = "t2.micro"
    instance_mapping = {
        1: "t2.micro",
        2: "t2.medium"
    }
    return instance_mapping.get(user_choice, default)


def _get_region_name(region):
    region_mapping = {
        1: DEFAULT_REGION
    }
    return region_mapping.get(region, DEFAULT_REGION)


def _get_debug_mode(debug_mode):
    if debug_mode.lower() == 'y':
        return True
    else:
        return False


def _select_vpc(session, region):
    available_vpcs = get_available_vpcs(session)
    vpc_choice = display_select_vpc_menu(available_vpcs, region=region)
    return vpc_choice


def _get_boto3_session(region, profile):
    return boto3.session.Session(profile_name=profile, region_name=region)


def _select_subnet(session, vpc_id):
    available_subnets = get_subnets_for_vpc(session, vpc_id)
    subnet_choice = display_select_subnet_menu(available_subnets, vpc_id)
    return subnet_choice


def _select_aws_profile():
    available_profiles = boto3.session.Session().available_profiles
    aws_profile_choice = display_select_aws_profile_menu(available_profiles)
    return aws_profile_choice


if __name__ == '__main__':
    main()
