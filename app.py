#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import Environment
from data_pipeline.data_pipeline_stack import DataPipelineStack

app = cdk.App()

env = Environment(
    account=app.node.try_get_context('account') or None,
    region=app.node.try_get_context('region') or 'us-east-1'
)

DataPipelineStack(
    app, 
    "DataPipelineStack",
    env=env,
    description="AWS Data Engineering Pipeline Stack"
)

app.synth()