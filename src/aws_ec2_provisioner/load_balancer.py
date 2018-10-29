from botocore.exceptions import ClientError

from aws_ec2_provisioner.utils import bcolors


def _get_client(session):
    return session.client('elb')


def _get_elb_name(project_name):
    return "elb-{}".format(str(project_name))


def provision_and_configure_elb(configuration, session):
    client = _get_client(session)
    project_name = configuration.get("project_name")
    elb_name = _get_elb_name(project_name)
    dns_name = None

    bcolors.message("Creating Elastic Load Balancer({name})".format(name=elb_name))
    try:
        elb_response = _create_elb(configuration, elb_name, client)
        dns_name = elb_response.get('DNSName')
        bcolors.ok()
    except ClientError as e:
        if _is_duplicate_elb_exception(e):
            bcolors.exists()
            dns_name = _get_elb_dns_by_name(elb_name, client)
        else:
            bcolors.fail()

    bcolors.message("Configuring Health Checks for ELB({name})".format(name=elb_name))
    try:
        _configure_health_check(elb_name, client)
        bcolors.ok()
    except ClientError as e:
        bcolors.fail()
        raise e

    return {"elb_name": elb_name, "elb_dns": dns_name}


def _create_elb(configuration, elb_name, client):
    project_name = configuration.get("project_name")
    security_group = configuration.get("security_groups").get("ELB", {}).get("id", {})
    subnets = configuration.get("subnets")

    response = client.create_load_balancer(
        LoadBalancerName=elb_name,
        Listeners=[
            {
                'Protocol': 'HTTP',
                'LoadBalancerPort': 80,
                'InstanceProtocol': 'HTTP',
                'InstancePort': 80,
                'SSLCertificateId': 'string'
            },
        ],
        Subnets=[subnets],
        SecurityGroups=[security_group],
        Tags=[
            {
                'Key': 'Project',
                'Value': project_name
            },
        ]
    )
    return response or {}


def _configure_health_check(elb_name, client):

    response = client.configure_health_check(
        LoadBalancerName=elb_name,
        HealthCheck={
            'Target': 'HTTP:80/',
            'Interval': 30,
            'Timeout': 5,
            'UnhealthyThreshold': 2,
            'HealthyThreshold': 2
        }
    )
    return response


def _is_duplicate_elb_exception(exception):
    if '(DuplicateLoadBalancerName)' in exception.args[0]:
        return True
    else:
        return False


def _get_elb_dns_by_name(elb_name, client):
    response = client.describe_load_balancers(
        LoadBalancerNames=[elb_name]
    )
    elbs = response.get('LoadBalancerDescriptions', [dict()])
    dns_name = elbs[0].get('DNSName')
    return dns_name
