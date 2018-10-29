import pprint
from botocore.exceptions import ClientError

from aws_ec2_provisioner.conf import DEFAULT_COOLDOWN_SECONDS, HEATHCHECK_GRACE_PERIOD_SECONDS, \
    ASSOCIATE_PUBLIC_IP_BY_DEFAULT
from aws_ec2_provisioner.errors import RequestToAWSError, LaunchCfgCreationError, \
    LCfgAlreadyExists, ASGAlreadyExists
from aws_ec2_provisioner.utils import validate_response_http_code, bcolors


pp = pprint.PrettyPrinter(indent=4)


def _get_client(session):
    return session.client('autoscaling')


def create_launch_conf_and_asg(configuration, session):
    client = _get_client(session)
    project_name = configuration.get("project_name")

    bcolors.message("Creating Launch configuration")
    launch_cfg_name = _get_launch_configuration_name(project_name)
    try:
        create_launch_configuration(launch_cfg_name, configuration, client)
        bcolors.ok()
    except RequestToAWSError:
        bcolors.fail()
        launch_cfg_name = None
    except LCfgAlreadyExists:
        bcolors.exists()

    bcolors.message("Creating Autoscaling Group")
    asg_name = _get_autoscaling_group_name(project_name)
    try:
        asg_name = create_autoscaling_group(asg_name, configuration, launch_cfg_name, client)
        bcolors.ok()
    except RequestToAWSError:
        bcolors.fail()
        asg_name = None
    except ASGAlreadyExists:
        bcolors.exists()

    bcolors.message("Creating the Scaling Policy")
    try:
        create_scaling_policy(configuration, asg_name, client)
        bcolors.ok()

    except RequestToAWSError:
        bcolors.fail()
        raise LaunchCfgCreationError
    except ClientError as e:
        print(e)
        raise e


def create_autoscaling_group(name, configuration, launch_cfg_name, client):

    project_name = configuration.get("project_name")
    min_size = configuration.get("min_size")
    max_size = configuration.get("max_size", 1)
    elb_name = configuration.get("elb_name")
    subnets = configuration.get("subnets")

    try:
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
    except ClientError as e:
        if _is_duplicate_exception(e):
            raise ASGAlreadyExists
        else:
            raise e
    return name


def create_launch_configuration(lcfg_name, configuration, client):
    user_data = configuration.get("user_data")
    image_id = configuration.get("image_id")
    security_group = configuration.get("security_groups").get("APP", {}).get("id")
    instance_type = configuration.get("instance_type")
    associate_public_address = ASSOCIATE_PUBLIC_IP_BY_DEFAULT or not configuration.get("debug_mode")
    try:
        response = client.create_launch_configuration(
            LaunchConfigurationName=lcfg_name,
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
    except ClientError as e:
        if _is_duplicate_exception(e):
            raise LCfgAlreadyExists
        else:
            raise e


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


def _is_duplicate_exception(exception):
    if '(AlreadyExists)' in exception.args[0]:
        return True
    else:
        return False
