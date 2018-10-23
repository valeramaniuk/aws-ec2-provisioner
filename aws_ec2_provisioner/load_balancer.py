def _get_client(session):
    return session.client('elb')


def _get_elb_name(project_name):
    return "elb-{}".format(str(project_name))


def provision_and_configure_elb(configuration, session):
    client = _get_client(session)
    elb_response = None
    project_name = configuration.get("project_name")
    elb_name = _get_elb_name(project_name)
    try:
        elb_response = _create_elb(configuration, elb_name, client)
        print(elb_response)
    except Exception as e:
        print(str(e))

    try:
        _configure_health_check(elb_name, client)
    except Exception as e:
        print(str(e))

    return {"elb_name": elb_name, "elb_response": elb_response}


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
    print("ELB Created OK")
    return response


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
    print("HealthCheck Created OK")
    return response
