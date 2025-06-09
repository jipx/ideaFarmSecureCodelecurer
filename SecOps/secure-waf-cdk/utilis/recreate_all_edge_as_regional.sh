#!/bin/bash

REGION="ap-northeast-1"
STAGE_NAME="prod"

echo "Fetching all Edge-optimized REST APIs in $REGION..."

# Get all Edge APIs
edge_api_ids=$(aws apigateway get-rest-apis --region "$REGION" --query 'items[?endpointConfiguration.types[0]==`EDGE`].id' --output text)

if [ -z "$edge_api_ids" ]; then
    echo "No Edge-optimized APIs found in $REGION."
    exit 0
fi

for api_id in $edge_api_ids; do
    echo ""
    echo "Processing API: $api_id"

    # Export to OpenAPI
    EXPORT_FILE="exported-$api_id.json"
    aws apigateway get-export \
        --parameters extensions='integrations' \
        --rest-api-id $api_id \
        --stage-name $STAGE_NAME \
        --export-type oas30 \
        $EXPORT_FILE \
        --region $REGION \
        --output text

    if [ ! -f "$EXPORT_FILE" ]; then
        echo "❌ Failed to export API $api_id"
        continue
    fi

    # Re-import as Regional
    echo "Importing as new Regional API..."
    new_api_id=$(aws apigateway import-rest-api \
        --region $REGION \
        --parameters endpointConfigurationTypes=REGIONAL \
        --body "fileb://$EXPORT_FILE" \
        --query 'id' --output text)

    echo "✅ New Regional API created: $new_api_id"

    # Deploy it
    aws apigateway create-deployment \
        --rest-api-id $new_api_id \
        --stage-name $STAGE_NAME \
        --region $REGION

    echo "🌐 Stage deployed: arn:aws:apigateway:$REGION::/restapis/$new_api_id/stages/$STAGE_NAME"
done
