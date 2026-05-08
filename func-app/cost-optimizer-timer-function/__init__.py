import os
import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient

def main(mytimer):
    logging.info("Cost analysis started")

    credential = DefaultAzureCredential()
    client = CostManagementClient(credential)

    subscription_id = os.getenv("SUBSCRIPTION_ID")
    budget = float(os.getenv("MONTHLY_BUDGET", "1"))        # your total budget in $
    alert_percent = float(os.getenv("ALERT_PERCENT", "0.001")) # 0.001% of budget
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

        if service_name not in service_costs:
            service_costs[service_name] = 0
        service_costs[service_name] += cost

        logging.info(f"RG: {resource_group}, Service: {service_name}, Cost: ${cost:.4f}")

    # Insight 1: Total cost
    logging.info(f"Total cost so far: ${total_cost:.4f}")

    # Insight 2: Most expensive service
    if service_costs:
        top_service = max(service_costs, key=service_costs.get)
        logging.info(f"Top service: {top_service}, Cost: ${service_costs[top_service]:.4f}")

    # Daily alert: fires if ANY spend detected above 0.001% of budget
    threshold = budget * (alert_percent / 100)
    percent_used = (total_cost / budget) * 100

    logging.info(f"Budget: ${budget} | Threshold: ${threshold:.6f} | Used: {percent_used:.6f}%")

    if total_cost > threshold:
        logging.warning(
            f"⚠️ DAILY COST ALERT: ${total_cost:.4f} spent this month "
            f"({percent_used:.6f}% of ${budget} budget) — "
            f"exceeded {alert_percent}% threshold!"
        )