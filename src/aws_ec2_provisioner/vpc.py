import pprint

import boto3
from aws_ec2_provisioner.errors import RequestToAWSError

pp = pprint.PrettyPrinter(indent=4)


def _get_resource(session):
    return session.resource('ec2')


def _get_client(session):
    return session.client('ec2')


def get_available_vpcs(session):
    client = _get_client(session)
    resource = _get_resource(session)

    vpc_collection = resource.vpcs.all()

    vpc_ids = [x.id for x in vpc_collection]

    response = client.describe_vpcs(
        VpcIds=vpc_ids
    )

    _validate_response_http_code(response)
    vpcs = response.get("Vpcs", [])
    return [_get_vpc_data(vpc) for vpc in vpcs]


def get_subnets_for_vpc(session, vpc_id):
    client = _get_client(session)
    resource = _get_resource(session)


    subnets_collection = resource.subnets.all()
    subnet_ids = [x.id for x in subnets_collection]
    response = client.describe_subnets(
        SubnetIds=subnet_ids
    )
    _validate_response_http_code(response)

    all_subnets = response["Subnets"]
    subnets_in_the_vpc = [x for x in all_subnets if x["VpcId"] == vpc_id]

    return [_get_subnet_data(subnet) for subnet in subnets_in_the_vpc]


def _get_vpc_data(vpc):
    name = _get_name_tag(vpc)
    return {
        "name": name if name else "",
        "id": _get_vpc_id(vpc),
        "default": _is_default(vpc)
    }


def _get_subnet_data(subnet):
    name = _get_name_tag(subnet)
    return {
        "name": name if name else "",
        "id": _get_subnet_id(subnet),
        "ips_available": _get_ips_available_in_subnet(subnet),
        "az": _get_subnet_az(subnet)
    }


def _is_default(vpc):
    return True if vpc.get("IsDefault") == True else False


def _get_name_tag(vpc):
    tags = vpc.get('Tags', [])
    for tag in tags:
        if tag["Key"] == "Name":
            return tag["Value"]


def _get_vpc_id(vpc):
    return vpc["VpcId"]


def _get_subnet_id(subnet):
    return subnet["SubnetId"]


def _get_ips_available_in_subnet(subnet):
    return subnet["AvailableIpAddressCount"]


def _get_subnet_az(subnet):
    return subnet["AvailabilityZone"]

def _validate_response_http_code(response):
    status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
    if status_code != 200:
        raise RequestToAWSError



# -------------------_-------_--__---------__---__-----_-_---_--_-----_-_-_-_------_---_--_
def _get_boto3_session(region, profile):
    return boto3.session.Session(profile_name=profile, region_name=region)

vpc_id ='vpc-09966440e874f08ae'
sesion = _get_boto3_session("us-west-1", "valera")
get_subnets_for_vpc(sesion, vpc_id)