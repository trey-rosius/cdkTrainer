from aws_cdk import core

from cdk_trainer.cdk_trainer_stack import CdkTrainerStack

class WebServiceStage(core.Stage):
  def __init__(self, scope: core.Construct, id: str, **kwargs):
    super().__init__(scope, id, **kwargs)

    service = CdkTrainerStack(self, 'WebService')

