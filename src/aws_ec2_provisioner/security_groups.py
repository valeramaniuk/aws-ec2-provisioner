from botocore.exceptions import ClientError


def _get_client(session):
    return session.client('ec2')


def _get_sg_name(name):
    return "{}".format(str(name))


def provision_security_groups(configuration, session):
    client = _get_client(session)
    project_name = configuration.get("project_name")
    vpc_id = configuration.get("vpc_id")

    elb_sg_data = _create_elb_security_group(project_name, vpc_id, client)
    print("ELB SG OK")
    app_sg_data = _create_application_security_group(
        project_name,
        vpc_id,
        client,
        source_sg=elb_sg_data["name"]
    )
    print("Application SG created OK")
    return {"ELB": elb_sg_data, "APP": app_sg_data}


def _create_elb_security_group(project_name, vpc_id, client):

    elb_sg_name = _get_sg_name("{}-elb".format(project_name))

    in_permissions = [
        {'IpProtocol': 'tcp',
         'FromPort': 80,
         'ToPort': 80,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
         }
    ]

    sg_id = _create_security_group(elb_sg_name, vpc_id, client,
                                   description="ELB for {}".format(project_name)
                                   )
    _authorize_sg_ingress(elb_sg_name, client, in_permissions)

    return {"id": sg_id, "name": elb_sg_name}


def _create_application_security_group(project_name, vpc_id, client, source_sg):
    app_sg_name = _get_sg_name("{}-application".format(project_name))

    sg_id = _create_security_group(app_sg_name, vpc_id, client,
                                   description="App servers for {}".format(project_name)
                                   )
    _authorize_sg_ingress(app_sg_name, client, source_sg=source_sg)
    return {"id": sg_id, "name": app_sg_name}


def _create_security_group(sg_name, vpc_id, client, description="generic description"):

    try:
        response = client.create_security_group(
            GroupName=sg_name,
            Description=description,
            VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))
        return security_group_id
    except ClientError as e:
        print(e)


def _authorize_sg_ingress(security_group_name, client, in_permissions=None, source_sg=None):
    try:
        if source_sg:
            data = client.authorize_security_group_ingress(
                GroupName=security_group_name,
                SourceSecurityGroupName=source_sg
            )
        else:
            data = client.authorize_security_group_ingress(
                GroupName=security_group_name,
                IpPermissions=in_permissions
            )
        print('Ingress Successfully Set %s' % data)
    except ClientError as e:
        print(e)
