from aws_cdk import core
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as cpactions
from aws_cdk import pipelines
from cdk_trainer.webservice_stage import WebServiceStage

from .cdk_trainer_stack import CdkTrainerStack

class PipelineStack(core.Stack):
    def __init__(self,scope:core.Construct,id:str,**kwargs):
        super().__init__(scope,id,**kwargs)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        pipeline = pipelines.CdkPipeline(self, 'Pipeline',

            cloud_assembly_artifact=cloud_assembly_artifact,
            pipeline_name='TrainerPipeline',

            source_action=cpactions.GitHubSourceAction(
                action_name='Github',
                output=source_artifact,
                oauth_token=core.SecretValue.secrets_manager('trainer-github-token'),
                owner='trey-rosius',
                repo='cdkTrainer',
                trigger=cpactions.GitHubTrigger.POLL),

            synth_action=pipelines.SimpleSynthAction(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                install_command='npm install -g aws-cdk && pip install -r requirements.txt',
                synth_command= 'cdk synth'))
        pipeline.add_application_stage(WebServiceStage(self,'Pre-Produc',env={
    
        'account':'132260253285',
        'region': 'us-east-2'}))    

        pipeline.add_application_stage(WebServiceStage(self, 'Production', env={
        'account':'132260253285',
        'region': 'us-east-2'}))

   
             
        





