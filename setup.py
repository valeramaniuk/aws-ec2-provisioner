import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws_ec2_provisioner_pkg",
    version="0.0.1",
    author="Valera Maniuk",
    author_email='valeramaniuk@protonmail.com',
    description="POC boto3 resource provisioner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/valeramaniuk/aws-ec2-provisioner',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)