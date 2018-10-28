import pprint

from aws_ec2_provisioner.errors import RequestToAWSError, LaunchCfgCretationError
from aws_ec2_provisioner.utils import validate_response_http_code, bcolors

ASSOCIATE_PUBLIC_IP_BY_DEFAULT = True


DEFAULT_COOLDOWN_SECONDS = 300
HEATHCHECK_GRACE_PERIOD_SECONDS = 120

pp = pprint.PrettyPrinter(indent=4)


def _get_client(session):
    return session.client('autoscaling')


def create_launch_conf_and_asg(configuration, session):
    client = _get_client(session)
    try:
        launch_cfg_name = create_launch_configuration(configuration, client)
        print("Launch configuration created  {green}OK{end}".format(green=bcolors.OKGREEN, end=bcolors.ENDC))
    except RequestToAWSError:
        print("Launch configuration creation  {green}FAILED{end}. Aborting".format(green=bcolors.FAIL, end=bcolors.ENDC))
        raise LaunchCfgCretationError

    try:
        asg_name = create_autoscaling_group(configuration, launch_cfg_name, client)
        message = "Autoscating group created"
        print("{message: <40}  {green}OK{end}".format(green=bcolors.OKGREEN, end=bcolors.ENDC, message=message))
    except RequestToAWSError:
        print("Launch configuration creation  {green}FAILED{end}".format(green=bcolors.FAIL, end=bcolors.ENDC))
        raise LaunchCfgCretationError

    try:
        message = "Scaling policy created"
        create_scaling_policy(configuration, asg_name, client)
        print("{message: <40}  {green}OK{end}".format(green=bcolors.OKGREEN, end=bcolors.ENDC, message=message))
    except RequestToAWSError:
        print("Launch configuration creation  {green}FAILED{end}".format(green=bcolors.FAIL, end=bcolors.ENDC))
        raise LaunchCfgCretationError


def create_autoscaling_group(configuration, launch_cfg_name, client):

    project_name = configuration.get("project_name")
    min_size = configuration.get("min_size")
    max_size = configuration.get("max_size", 1)
    elb_name = configuration.get("elb_name")
    subnets = configuration.get("subnets")
    name = _get_autoscaling_group_name(project_name)

    response = client.create_auto_scaling_group(
        AutoScalingGroupName=name,
        LaunchConfigurationName=launch_cfg_name,
        MinSize=min_size,
        MaxSize=max_size,
        DesiredCapacity=min_size,
        DefaultCooldown=DEFAULT_COOLDOWN_SECONDS,
        LoadBalancerNames=[elb_name, ],
        HealthCheckType='ELB',
        HealthCheckGracePeriod=HEATHCHECK_GRACE_PERIOD_SECONDS,
        VPCZoneIdentifier=subnets,
        NewInstancesProtectedFromScaleIn=False,
        Tags=[
            {
                'ResourceId': name,
                'ResourceType': 'auto-scaling-group',
                'Key': 'Name',
                'Value': project_name,
                'PropagateAtLaunch': True
            },
        ],
    )
    validate_response_http_code(response)

    return name


def create_launch_configuration(configuration, client):
    project_name = configuration.get("project_name")
    user_data = configuration.get("user_data")
    image_id = configuration.get("image_id")
    security_group = configuration.get("security_groups").get("APP", {}).get("id")
    instance_type = configuration.get("instance_type")
    name = _get_launch_configuration_name(project_name)
    associate_public_address = ASSOCIATE_PUBLIC_IP_BY_DEFAULT or not configuration.get("debug_mode")
    response = client.create_launch_configuration(
        LaunchConfigurationName=name,
        ImageId=image_id,
        SecurityGroups=[security_group, ],
        UserData=user_data,
        InstanceType=instance_type,
        InstanceMonitoring={
            'Enabled': True
        },
        PlacementTenancy='default',
        AssociatePublicIpAddress=associate_public_address,
    )
    validate_response_http_code(response)

    return name


def create_scaling_policy(configuration, asg_name, client):
    project_name = configuration.get("project_name")
    scaling_target_value_percent = configuration.get("scaling_target_value_percent")
    name = _get_scaling_policy_name(project_name)
    response = client.put_scaling_policy(
        AutoScalingGroupName=asg_name,
        PolicyName=name,
        PolicyType='TargetTrackingScaling',
        TargetTrackingConfiguration={
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': 'ASGAverageCPUUtilization',
            },
            'TargetValue': scaling_target_value_percent,
            'DisableScaleIn': False
        }
    )
    validate_response_http_code(response)

    return name


def _get_autoscaling_group_name(project_name):
    return "asg-{}".format(str(project_name))


def _get_launch_configuration_name(project_name):
    return "lcfg-{}".format(str(project_name))


def _get_scaling_policy_name(project_name):
    return "scaling_policy-{}".format(str(project_name))
