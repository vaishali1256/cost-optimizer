import os
import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient

def main(mytimer):
    logging.info("Cost analysis started")

    credential = DefaultAzureCredential()
    client = CostManagementClient(credential)

    subscription_id = os.getenv("SUBSCRIPTION_ID")
    scope = f"/subscriptions/{subscription_id}"

    query = {
        "type": "Usage",
        "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "Daily",
            "aggregation": {
                "totalCost": {
                    "name": "PreTaxCost",
                    "function": "Sum"
                }
            },
            "grouping": [
                {
                    "type": "Dimension",
                    "name": "ResourceGroup"
                },
                {
                    "type": "Dimension",
                    "name": "ServiceName"
                }
            ]
        }
    }

    result = client.query.usage(scope, query)

    total_cost = 0
    service_costs = {}

    for row in result.rows:
        cost = float(row[0])
        resource_group = row[1]
        service_name = row[2]

        total_cost += cost

        # Aggregate per service
        if service_name not in service_costs:
            service_costs[service_name] = 0
        service_costs[service_name] += cost

        logging.info(f"RG: {resource_group}, Service: {service_name}, Cost: {cost}")

    # 🔥 Insight 1: Total cost
    logging.info(f"Total cost so far: {total_cost}")

    # 🔥 Insight 2: Most expensive service
    if service_costs:
        top_service = max(service_costs, key=service_costs.get)
        logging.info(f"Top service: {top_service}, Cost: {service_costs[top_service]}")

    # 🔔 Alert logic
    if total_cost > 40:
        logging.warning(f"⚠️ Cost exceeded 80% threshold: {total_cost}")