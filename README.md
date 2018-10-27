
CLI tool to create a simple web app.
 
To simplify the design all the infrastructure are being created in the single
subnet, and this subnet is required to be a **public** one. Because of the architecture doesn't include a NAT gateway all the provisioned instances **will be assigned a public IP** address, so they can download the necessary packages.
#### Installation
    pip install aws_ec2_provisioner
or

    git clone git@github.com:valeramaniuk/aws-ec2-provisioner.git
    cd aws-ec2-provisioner
    pip install .

#### Usage
run `aws_ec2_provisioner` with the following options:

    --vpc-id <VPC where you want to deploy the app>
    --subnet-id <Subnet where you want to deploy the app. Should in the selected VPC>
    --project-name <Name of the project. You won't be able to create 2 projects with the same name>
    --aws-profile <The name of access key/secret key pair (~/.aws/credentials)>
    --min-asg-size <Minimum size of the autoscaling group>
    --max-asg-size <Maximum size of the autoscaling group>
    --instance-type <INT. Choose from a predefined list>

If you omit any of the options you will be prompted interactively.
##### Available instace types:
    1. t2.micro
    2. t2.meduim

#### Infrastructure to be created:
- ELB
    - Listener **80**
    - Instance port **80**
    - Health check **HTTP:80/**
- Autoscaling group
    - Launch configuration associates public IP by default
    - User data in Launch configuration installs and starts **ngnix**
- Security Groups
    - ELB security group
        - ingress tcp:80 from anywhere
    - APP security group
        - ingress only from `ELB security group`
        - **no SSH access** because the APP servers are in the public subnet (architecture limitation)
    
#### TODO:
- [ ] Load based autoscaling
- [ ] Additional region
- [x] Choose aws_profile interactively based on ~/.aws/credentials
- [x] Choose vpc-id interactively after specifying the aws-profile and region
- [x] Choose subnet-id interactively after specifying the subnet
- [ ] Proper logging instead of print statements
- [ ] Tests
- [ ] Idempotency
- [ ] Ability to rollback
- [ ] Move instance user data to separate file, so the `user data` file may be specified at runtime
 