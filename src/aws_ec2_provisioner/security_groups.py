import pprint
from botocore.exceptions import ClientError

from aws_ec2_provisioner.errors import RequestToAWSError
from aws_ec2_provisioner.utils import bcolors, validate_response_http_code

pp = pprint.PrettyPrinter(indent=4)


def _get_client(session):
    return session.client('ec2')


def provision_security_groups(configuration, session):
    client = _get_client(session)
    project_name = configuration.get("project_name")
    vpc_id = configuration.get("vpc_id")

    try:
        elb_sg_data = _create_elb_security_group(project_name, vpc_id, client)
        bcolors.message("Creating ELB Security Group")
        bcolors.ok()
    except RequestToAWSError:
        bcolors.message("Creating ELB Security Group")
        bcolors.fail()
        elb_sg_data = dict()

    try:
        app_sg_data = _create_application_security_group(
            project_name,
            vpc_id,
            client,
            source_sg=elb_sg_data["name"]
        )
        bcolors.message("Creating Application Security Group")
        bcolors.ok()
    except RequestToAWSError:
        bcolors.message("Creating Application Security Group")
        bcolors.fail()
        app_sg_data = dict()

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
        validate_response_http_code(response)
        security_group_id = response.get('GroupId')

    except ClientError as e:
        if _is_sg_duplicate_exception(e):
            security_group_id = _get_sg_id_by_name(sg_name, client)
            return security_group_id
        else:
            raise e
    return security_group_id


def _authorize_sg_ingress(security_group_name, client, in_permissions=None, source_sg=None):
    bcolors.message("Creating SG {sg_name} Ingress Rules".format(sg_name=security_group_name))
    try:
        if source_sg:
            client.authorize_security_group_ingress(
                GroupName=security_group_name,
                SourceSecurityGroupName=source_sg
            )
        else:
            client.authorize_security_group_ingress(
                GroupName=security_group_name,
                IpPermissions=in_permissions
            )
        bcolors.ok()
    except ClientError as e:
        if _is_sg_permissions_duplicate_exception(e):
            bcolors.exists()
        else:
            bcolors.fail()


def _get_sg_name(name):
    return "{}".format(str(name))


def _is_sg_duplicate_exception(exception):
    if '(InvalidGroup.Duplicate)' in exception.args[0]:
        return True
    else:
        return False


def _is_sg_permissions_duplicate_exception(exception):
    if '(InvalidPermission.Duplicate)' in exception.args[0]:
        return True
    else:
        return False


def _get_sg_id_by_name(sg_name, client):
    response = client.describe_security_groups(
        Filters=[
            {
                'Name': 'group-name',
                'Values': [
                    sg_name,
                ]
            },
        ],
    )

    security_groups = response.get('SecurityGroups', [dict()])
    sg_id = security_groups[0].get('GroupId')
    return sg_id
