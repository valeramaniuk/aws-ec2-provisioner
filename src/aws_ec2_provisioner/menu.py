FILL = 8
EXTENDED_FILL = FILL*3
HORIZONTAL_DIVIDER = '-'*FILL*10


def display_select_subnet_menu(available_subnets, vpc_id):
    print("\nSubnets available in the VPC {vpc_id}:".format(vpc_id=vpc_id))
    print("{choice: <{fill}} {name: <{fill}}\t{id: <{extended_fill}}"
          "\t{az: <{fill}}\t{ips: <{fill}}".format(
                                                choice="option#",
                                                name="name",
                                                id="subnet-id",
                                                az="AZ",
                                                ips="IPs left",
                                                fill=str(FILL),
                                                extended_fill=str(EXTENDED_FILL)
                                            )
          )
    print(HORIZONTAL_DIVIDER)
    for i, subnet in enumerate(available_subnets):
        print("{choice: <{fill}} {name: <{fill}}\t{id: <{extended_fill}}"
              "\t{az: <{fill}}\t{ips: <{fill}}".format(
                                                    choice=i,
                                                    name=subnet["name"],
                                                    id=subnet["id"],
                                                    az=subnet["az"],
                                                    ips=subnet["ips_available"],
                                                    fill=str(FILL),
                                                    extended_fill=str(EXTENDED_FILL)
                                                )
              )
    subnet_choice = int(input("\nChoose your option: "))
    subnet_id = available_subnets[subnet_choice].get("id")
    return subnet_id


def display_select_vpc_menu(available_vpcs, region):
    print("\nVPCs available in the {region}:".format(region=region))
    print("{choice: <{fill}} {name: <{fill}}\t{id: <{extended_fill}}"
          "\t{default: <{fill}}".format(
                                            choice="option#",
                                            name="name",
                                            id="vpc-id",
                                            default="default VPC",
                                            fill=str(FILL),
                                            extended_fill=str(EXTENDED_FILL)
                                       )
          )
    print(HORIZONTAL_DIVIDER)
    for i, vpc in enumerate(available_vpcs):
        print("{choice: <{fill}} {name: <{fill}}\t{id: <{extended_fill}}"
              "\t{default: <{fill}}".format(
                                                choice=i,
                                                name=vpc.get("name", " "),
                                                id=vpc["id"],
                                                default="x" if vpc["default"] else " ",
                                                fill=str(FILL),
                                                extended_fill=str(EXTENDED_FILL)
                                           )
              )
    vpc_choice = int(input("\nChoose your option: "))

    vpc_id = available_vpcs[vpc_choice].get("id")
    return vpc_id


def display_select_aws_profile_menu(available_profiles):
    print("\nAvailabe AWS profiles (~/.aws/credentials):")
    print(HORIZONTAL_DIVIDER)
    for i, profile in enumerate(available_profiles):
        print("{option}. {profile: <{extended_fill}} ".format(
            option=i,
            profile=profile,
            extended_fill=str(EXTENDED_FILL)
        ),
            end='')
        if (i+1) % 3 == 0:
            print("\n")

    profile_option = int(input("\nChoose your option: "))
    return available_profiles[profile_option]
