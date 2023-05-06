#!/usr/bin/env python3
import os

import aws_cdk as cdk
from lib.cdk_stack import CdkStack

app = cdk.App()
CdkStack(app, "CdkStack")

app.synth()
