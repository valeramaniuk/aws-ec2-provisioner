import boto3


DEFAULT_COOLDOWN_SECONDS = 300

def _get_client():
    return boto3.client('autoscaling')


def _get_autoscaling_group_name(project_name):
    return "asg-{}".format(str(project_name))


def _get_launch_configuration_name(project_name):
    return "lcfg-{}".format(str(project_name))


def create_autoscaling_group(configuration, launch_cfg_name):
    client = _get_client()

    project_name = configuration.get("project_name")
    min_size = configuration.get("min_size")
    max_size = configuration.get("max_size", 1)
    desired_capacity = configuration.get("desired_capacity", 1)
    elb_name = configuration.get("elb_name")
    subnets = configuration.get("subnets")
    name = _get_autoscaling_group_name(project_name)

    response = client.create_auto_scaling_group(
        AutoScalingGroupName=name,
        LaunchConfigurationName=launch_cfg_name,
        MinSize=min_size,
        MaxSize=max_size,
        DesiredCapacity=desired_capacity,
        DefaultCooldown=DEFAULT_COOLDOWN_SECONDS,
        LoadBalancerNames=[elb_name, ],
        HealthCheckType='ELB',
        HealthCheckGracePeriod=60,
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
    return response


def create_launch_configuration(configuration):
    client = _get_client()
    project_name = configuration.get("project_name")
    user_data = configuration.get("user_data")
    image_id = configuration.get("image_id")
    security_group = configuration.get("security_groups").get("APP", {}).get("id")
    instance_type = configuration.get("instance_type")
    name = _get_launch_configuration_name(project_name)

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
        AssociatePublicIpAddress=False,
    )
    print(response)
    return name


def create_launch_conf_and_asg(configuration):
    try:
        launch_cfg_name = create_launch_configuration(configuration)
        print("Launch configuration created OK")
        create_autoscaling_group(configuration, launch_cfg_name)
        print("ASG created OK")
    except Exception as e:
        print(str(e))

