from aws_cdk import core
from aws_cdk import core as cdk

from aws_cdk.aws_appsync import (
    CfnGraphQLSchema,
    CfnGraphQLApi,
    CfnApiKey,
    MappingTemplate,
    CfnDataSource, CfnResolver

)
from aws_cdk.aws_dynamodb import (
    Table,
    Attribute,
    AttributeType,
    StreamViewType,

    BillingMode,

)
from aws_cdk.aws_iam import (
    Role,
    ServicePrincipal,
    ManagedPolicy
)
import os.path

dirname = os.path.dirname(__file__)

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.

with open(os.path.join(dirname, "../graphql/schema.txt"), 'r') as file:
            data_schema = file.read().replace('\n', '')
with open(os.path.join(dirname, "../resolver_functions/create_trainer"), 'r') as file:
            create_trainer = file.read().replace('\n', '')             
with open(os.path.join(dirname, "../resolver_functions/update_trainer"), 'r') as file:
            update_trainer = file.read().replace('\n', '')
with open(os.path.join(dirname, "../resolver_functions/get_trainer"), 'r') as file:
            get_trainer = file.read().replace('\n', '')   
with open(os.path.join(dirname, "../resolver_functions/all_trainers"), 'r') as file:
            all_trainers = file.read().replace('\n', '')   
with open(os.path.join(dirname, "../resolver_functions/delete_trainer"), 'r') as file:
            delete_trainer = file.read().replace('\n', '')                                   


class CdkTrainerStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        table_name = "trainers"

        trainers_graphql_api = CfnGraphQLApi(
            self,'trainersApi',
            name="trainers-api",
            authentication_type='API_KEY'
        )
        
        CfnApiKey(
            self,'TrainersApiKey',
            api_id = trainers_graphql_api.attr_api_id

        )

        api_schema = CfnGraphQLSchema(
            self,"TrainersSchema",
            api_id = trainers_graphql_api.attr_api_id,
            definition=data_schema
        )

        trainers_table = Table(
            self, 'TrainersTable',
            table_name=table_name,
            partition_key=Attribute(
                name='id',
                type=AttributeType.STRING,

            ),

        
            billing_mode=BillingMode.PAY_PER_REQUEST,
            stream=StreamViewType.NEW_IMAGE,

            # The default removal policy is RETAIN, which means that cdk
            # destroy will not attempt to delete the new table, and it will
            # remain in your account until manually deleted. By setting the
            # policy to DESTROY, cdk destroy will delete the table (even if it
            # has data in it)
            removal_policy=core.RemovalPolicy.DESTROY  # NOT recommended for production code
        )

        trainers_table_role = Role(
            self, 'TrainersDynamoDBRole',
            assumed_by=ServicePrincipal('appsync.amazonaws.com')
        )

        trainers_table_role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name(
                'AmazonDynamoDBFullAccess'
            )
        )

        data_source = CfnDataSource(
            self, 'TrainersDataSource',
            api_id=trainers_graphql_api.attr_api_id,
            name='TrainersDynamoDataSource',
            type='AMAZON_DYNAMODB',
            dynamo_db_config=CfnDataSource.DynamoDBConfigProperty(
                table_name=trainers_table.table_name,
                aws_region=self.region
            ),
            service_role_arn=trainers_table_role.role_arn
        )

        get_Trainer_resolver = CfnResolver(
            self, 'GetOneQueryResolver',
            api_id=trainers_graphql_api.attr_api_id,
            type_name='Query',
            field_name='getTrainer',
            data_source_name=data_source.name,
            request_mapping_template=get_trainer,
            response_mapping_template="$util.toJson($ctx.result)"
        )

        get_Trainer_resolver.add_depends_on(api_schema)

        get_all_trainers_resolver = CfnResolver(
            self, 'GetAllQueryResolver',
            api_id=trainers_graphql_api.attr_api_id,
            type_name='Query',
            field_name='allTrainers',
            data_source_name=data_source.name,
            request_mapping_template=all_trainers,
            response_mapping_template="$util.toJson($ctx.result)"
        )

        get_all_trainers_resolver.add_depends_on(api_schema)
     
        create_trainers_resolver = CfnResolver(
            self, 'CreateTrainerMutationResolver',
            api_id=trainers_graphql_api.attr_api_id,
            type_name='Mutation',
            field_name='createTrainer',
            data_source_name=data_source.name,
            request_mapping_template=create_trainer,
            response_mapping_template="$util.toJson($ctx.result)"
        )

        create_trainers_resolver.add_depends_on(api_schema)

        update_trainers_resolver = CfnResolver(
            self,'UpdateMutationResolver',
            api_id=trainers_graphql_api.attr_api_id,
            type_name="Mutation",
            field_name="updateTrainers",
            data_source_name=data_source.name,
            request_mapping_template=update_trainer,
            response_mapping_template="$util.toJson($ctx.result)"
        )
        update_trainers_resolver.add_depends_on(api_schema)

        delete_trainer_resolver = CfnResolver(
            self, 'DeleteMutationResolver',
            api_id=trainers_graphql_api.attr_api_id,
            type_name='Mutation',
            field_name='deleteTrainer',
            data_source_name=data_source.name,
            request_mapping_template=delete_trainer,
            response_mapping_template="$util.toJson($ctx.result)"
        )

        delete_trainer_resolver.add_depends_on(api_schema)