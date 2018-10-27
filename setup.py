from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()



setup(
    name='aws_ec2_provisioner',
    version='0.0.5',
    author="Valera Maniuk",
    author_email='valeramaniuk@protonmail.com',
    description="POC boto3 resource provisioner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/valeramaniuk/aws-ec2-provisioner',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'click',
        'boto3>=1.4.5',
    ],
    entry_points='''
        [console_scripts]
        aws_ec2_provisioner=aws_ec2_provisioner.main:main
    ''',
    zip_safe=False
)
