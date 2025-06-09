from aws_cdk import App
from secure_waf_stack import SecureWafStack

app = App()
api_config = app.node.try_get_context("apis") or []
SecureWafStack(app, "SecureWafStack", apis=api_config)
app.synth()
