#!/bin/bash

REGION="ap-northeast-1"

echo "Fetching all API Gateway REST APIs in $REGION..."

aws apigateway get-rest-apis --region "$REGION" --query 'items[*].{id:id,name:name}' --output table

echo ""
echo "To filter only Edge-optimized APIs, run:"
echo ""
echo "aws apigateway get-rest-apis --region \"$REGION\" --query 'items[?endpointConfiguration.types[0]==\`EDGE\`].{id:id,name:name}' --output table"
