
from aws_cdk import (
    Stack, Duration,
    aws_wafv2 as wafv2,
    aws_ssm as ssm,
    aws_lambda as _lambda,
    aws_iam as iam
)
from constructs import Construct

class SecureWafStack(Stack):
    def __init__(self, scope: Construct, id: str, *, apis: list[dict], **kwargs):
        super().__init__(scope, id, **kwargs)

        ssm.StringParameter(self, "EmergencyToggle",
            parameter_name="/waf/emergency-block",
            string_value="false"
        )

        ip_set = wafv2.CfnIPSet(self, "AdminIPSet",
            name="AllowAdminIP",
            scope="REGIONAL",
            ip_address_version="IPV4",
            addresses=["203.0.113.5/32"]
        )

        rules = [
            wafv2.CfnWebACL.RuleProperty(
                name="AllowAdminIP",
                priority=0,
                action=wafv2.CfnWebACL.RuleActionProperty(allow={}),
                statement=wafv2.CfnWebACL.StatementProperty(
                    ip_set_reference_statement=wafv2.CfnWebACL.IPSetReferenceStatementProperty(
                        arn=ip_set.attr_arn
                    )
                ),
                visibility_config=self.visibility("AllowAdmin")
            ),
            wafv2.CfnWebACL.RuleProperty(
                name="RateLimit",
                priority=1,
                action=wafv2.CfnWebACL.RuleActionProperty(block={}),
                statement=wafv2.CfnWebACL.StatementProperty(
                    rate_based_statement=wafv2.CfnWebACL.RateBasedStatementProperty(
                        limit=100,
                        aggregate_key_type="IP"
                    )
                ),
                visibility_config=self.visibility("RateLimit")
            ),
            wafv2.CfnWebACL.RuleProperty(
                name="RegionCheck",
                priority=2,
                action=wafv2.CfnWebACL.RuleActionProperty(block={}),
                statement=wafv2.CfnWebACL.StatementProperty(
                    byte_match_statement=wafv2.CfnWebACL.ByteMatchStatementProperty(
                        field_to_match=wafv2.CfnWebACL.FieldToMatchProperty(
                            single_header={"Name": "X-Client-Region"}
                        ),
                        positional_constraint="EXACTLY",
                        search_string="SG",
                        text_transformations=[{"priority": 0, "type": "LOWERCASE"}]
                    )
                ),
                visibility_config=self.visibility("RegionCheck")
            )
        ]

        web_acl = wafv2.CfnWebACL(self, "SecureWebACL",
            name="SecureWebACL",
            scope="REGIONAL",
            default_action={"block": {}},
            visibility_config=self.visibility("SecureWebACL"),
            rules=rules
        )

        for idx, api in enumerate(apis):
            resource_arn = api["arn"] if "arn" in api else                 f"arn:aws:apigateway:{self.region}::/restapis/{api['id']}/stages/{api['stage']}"
            wafv2.CfnWebACLAssociation(self, f"Assoc{idx}",
                resource_arn=resource_arn,
                web_acl_arn=web_acl.attr_arn
            )

        toggle_lambda = _lambda.Function(self, "UpdateWafLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.InlineCode("""
import boto3

ssm = boto3.client("ssm")
waf = boto3.client("wafv2")

def handler(event, context):
    toggle = ssm.get_parameter(Name="/waf/emergency-block")['Parameter']['Value']
    acl = waf.get_web_acl(Name='SecureWebACL', Scope='REGIONAL')
    token = acl['LockToken']
    id = acl['WebACL']['Id']
    config = acl['WebACL']

    waf.update_web_acl(
        Name='SecureWebACL',
        Scope='REGIONAL',
        Id=id,
        LockToken=token,
        DefaultAction={"Block": {}} if toggle == 'true' else config['DefaultAction'],
        VisibilityConfig=config['VisibilityConfig'],
        Rules=[] if toggle == 'true' else config['Rules']
    )
    return {"mode": toggle}
"""),
            timeout=Duration.seconds(30)
        )

        toggle_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["wafv2:GetWebACL", "wafv2:UpdateWebACL", "ssm:GetParameter"],
            resources=["*"]
        ))

    def visibility(self, name):
        return wafv2.CfnWebACL.VisibilityConfigProperty(
            cloud_watch_metrics_enabled=True,
            sampled_requests_enabled=True,
            metric_name=name
        )
