from datetime import datetime
from decimal import Decimal
import json
import logging
import re
import boto3
from django.http import JsonResponse
import openpyxl
from core.portal_base import ViewBase
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')

logger = logging.getLogger(__name__)


class UserDashboardView(ViewBase):
    TEMPLATE_NAME = 'dashboard/user_dashboard.html'

    def get(self, request, *args, **kwargs):

        context = {}

        return self.render(context)
    

class ClientProjectListingView(ViewBase):
    TEMPLATE_NAME = 'dashboard/client_project_listing.html'

    def get(self, request, *args, **kwargs):

        context = {}

        return self.render(context)
    

class ClientProjectDetailView(ViewBase):
    TEMPLATE_NAME = 'dashboard/client_project_details.html'

    def get(self, request, *args, **kwargs):

        context = {}

        return self.render(context)
    

class CostDashboardView(ViewBase):
    TEMPLATE_NAME = 'dashboard/cost_dashboard.html'

    def get(self, request, *args, **kwargs):
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-2", )
        new_cost_summary_table = dynamodb.Table("new_cost_summary")
        new_contract_sum_table = dynamodb.Table("new_contract_sum")
        new_change_table = dynamodb.Table("new_change")
        new_cost_reporting_table = dynamodb.Table("new_cost_reporting")

        new_cost_summary_table_response = new_cost_summary_table.scan()
        new_cost_summary_records = new_cost_summary_table_response.get('Items', [])

        sorted_records = sorted(new_cost_summary_records, key=lambda x: float(x.get('Ref', 0)))

        sorted_cost_summary_records = {}
        if sorted_records:
            keys = sorted_records[0].keys()
            for key in keys:
                sorted_cost_summary_records[key.replace(" ", "").replace("&", "").replace("-", "")] = [record.get(key, '') for record in sorted_records]


        new_contract_sum_table_response = new_contract_sum_table.scan()
        new_contract_sum_records = new_contract_sum_table_response.get('Items', [])

        sorted_records = sorted(new_contract_sum_records, key=lambda x: float(x.get('Ref', 0)))

        sorted_contract_sum_records = {}
        if sorted_records:
            keys = sorted_records[0].keys()
            for key in keys:
                sorted_contract_sum_records[key.replace(" ", "").replace("&", "").replace("-", "")] = [record.get(key, '') for record in sorted_records]


        new_change_table_response = new_change_table.scan()
        new_change_table_records = new_change_table_response.get('Items', [])

        sorted_records = sorted(new_change_table_records, key=lambda x: float(x.get('Ref', 0)))

        sorted_new_change_records = {}
        if sorted_records:
            keys = sorted_records[0].keys()
            for key in keys:
                sorted_new_change_records[key.replace(" ", "").replace("&", "").replace("-", "")] = [record.get(key, '') for record in sorted_records]

        
        total_contract_sum = sum(float(item.get('CONTRACT SUM', 0)) for item in new_cost_summary_table_response.get('Items', []))
        certified_payments_sum = sum(float(item.get('CERTIFIED PAYMENTS TO CONTRACTOR', 0)) for item in new_cost_summary_table_response.get('Items', []))
        anticipated_payments_sum = sum(float(item.get('ACCRUED & ANTICIPATED PAYMENTS', 0)) for item in new_cost_summary_table_response.get('Items', []))
        forecast_expenditures_sum = sum(float(item.get('TOTAL FORECAST EXPENDITURE', 0)) for item in new_cost_summary_table_response.get('Items', []))
        total_variance_sum = sum(float(item.get('VARIANCE - TOTAL', 0)) for item in new_cost_summary_table_response.get('Items', []))
        total_variance_period_sum = sum(float(item.get('VARIANCE - IN PERIOD', 0)) for item in new_cost_summary_table_response.get('Items', []))
        
        new_cost_reporting_table_response = new_cost_reporting_table.scan()
        forecast_monthly = sum(float(item.get('Forecast Monthly', 0)) for item in new_cost_reporting_table_response.get('Items', []))
        actual_monthly = sum(float(item.get('Actual Monthly', 0)) for item in new_cost_reporting_table_response.get('Items', []))

        months = sorted(
            new_cost_reporting_table_response.get("Items", []),
            key=lambda x: x.get("Interim Payments", 0)
        )

        months = [item["Month"] for item in months if "Month" in item]

        forecast = sorted(
            new_cost_reporting_table_response.get("Items", []),
            key=lambda x: x.get("Interim Payments", 0)
        )

        forecast = [item["Forecast Monthly"] for item in forecast if "Forecast Monthly" in item]

        cumulative = sorted(
            new_cost_reporting_table_response.get("Items", []),
            key=lambda x: x.get("Interim Payments", 0)
        )

        cumulative = [item["Forecast Cumulative"] for item in cumulative if "Forecast Cumulative" in item]

        # cost reporting graph
        
        sns.set_style("whitegrid")
        fig, ax1 = plt.subplots(figsize=(8, 4))

        ax1.bar(months, forecast, color='royalblue')

        ax2 = ax1.twinx()
        ax2.plot(months, cumulative, color='dodgerblue', marker='o', linestyle='-', linewidth=2)

        ax1.set_xlabel("Months", fontsize=12)
        ax1.set_xticklabels(months, fontsize=12)

        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax2.spines['top'].set_visible(False)

        ax1.set_xlabel("")
        ax2.set_ylabel("")

        ax2.set_yticklabels([])
        ax2.tick_params(right=False)

        plt.title("")

        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        cost_reporting_graph = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close(fig)


        # top graphs
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]

        payment_sums = {
            'certified_payments_sum': certified_payments_sum,
            'anticipated_payments_sum': anticipated_payments_sum,
            'forecast_expenditures_sum': forecast_expenditures_sum,
            'total_variance_sum': total_variance_sum,
            'total_variance_period_sum': total_variance_period_sum,
        }

        graphs = {}

        for key, value in payment_sums.items():
            values = [0, 0, value, 0, 0, 0, 0]
            
            x = np.linspace(0, len(values) - 1, 300)
            y = np.interp(x, range(len(values)), values)

            plt.figure(figsize=(6, 2), dpi=100)
            plt.plot(x, y, color='#86CD57', linewidth=2)
            plt.fill_between(x, y, min(values), color='#d3e7c7', alpha=0.4)

            plt.xticks([])
            plt.yticks([])
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['left'].set_visible(False)
            plt.gca().spines['bottom'].set_visible(False)
            plt.grid(False)

            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
            buffer.seek(0)

            graphs[key] = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()
            plt.close(fig)
        
        context = {
            'new_cost_summary_records': sorted_cost_summary_records,
            'new_contract_sum_records': sorted_contract_sum_records,
            'new_change_records': sorted_new_change_records,
            'total_contract_sum': total_contract_sum,
            'certified_payments_sum': certified_payments_sum,
            'anticipated_payments_sum': anticipated_payments_sum,
            'forecast_expenditures_sum': forecast_expenditures_sum,
            'total_variance_sum': total_variance_sum,
            'total_variance_period_sum': total_variance_period_sum,
            'forecast_monthly': forecast_monthly,
            'actual_monthly': actual_monthly,
            'cost_reporting_graph': cost_reporting_graph,
            "graphs": {
                "certified_payments_sum": graphs["certified_payments_sum"],
                "anticipated_payments_sum": graphs["anticipated_payments_sum"],
                "forecast_expenditures_sum": graphs["forecast_expenditures_sum"],
                "total_variance_sum": graphs["total_variance_sum"],
                "total_variance_period_sum": graphs["total_variance_period_sum"]
            }
        }

        return self.render(context)
    
    def post(self, request, *args, **kwargs):
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-2", )
        new_cost_summary_table = dynamodb.Table("new_cost_summary")
        new_contract_sum_table = dynamodb.Table("new_contract_sum")
        new_change_table = dynamodb.Table("new_change")
        new_cost_reporting_table = dynamodb.Table("new_cost_reporting")

        if "file" not in request.FILES:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        file = request.FILES["file"]

        wb = openpyxl.load_workbook(file, data_only=True)
        
        if "NEW Cost Summary" not in wb.sheetnames:
            return JsonResponse({"error": "Sheet 'NEW Cost Summary' not found"}, status=400)

        new_cost_summary_sheet = wb["NEW Cost Summary"]

        headers = [cell.value for cell in new_cost_summary_sheet[1]]

        items = []
        for row in new_cost_summary_sheet.iter_rows(min_row=2, values_only=True):
            item = {headers[i]: str(row[i]) if isinstance(row[i], (int, float)) else (row[i] if row[i] not in [None, ""] else "0") for i in range(len(headers))}
            new_cost_summary_table.put_item(Item=item)
            items.append(item)


        if "NEW Contract Sum" not in wb.sheetnames:
            return JsonResponse({"error": "Sheet 'NEW Contract Sum' not found"}, status=400)

        new_contract_sum_sheet = wb["NEW Contract Sum"]

        headers = [cell.value for cell in new_contract_sum_sheet[1]]

        required_columns = ["Item", "CONTRACT SUM", "CERTIFIED PAYMENTS TO CONTRACTOR", "ACCRUED & ANTICIPATED PAYMENTS", "TOTAL FORECAST EXPENDITURE"]
        required_indexes = [headers.index(col) for col in required_columns if col in headers]

        items = []
        for row in new_contract_sum_sheet.iter_rows(min_row=3, values_only=True):
            if all(row[i] not in [None, ""] for i in required_indexes):
                item = {headers[i]: str(row[i]) if isinstance(row[i], (int, float)) else (row[i] if row[i] not in [None, ""] else "0") for i in range(len(headers))}
                new_contract_sum_table.put_item(Item=item)
                items.append(item)


        if "NEW EAChange" not in wb.sheetnames:
            return JsonResponse({"error": "Sheet 'NEW EAChange' not found"}, status=400)

        new_change_sheet = wb["NEW EAChange"]

        headers = [cell.value for cell in new_change_sheet[1]]

        required_columns = ["CONTRACT SUM", "CERTIFIED PAYMENTS TO CONTRACTOR", "ACCRUED & ANTICIPATED PAYMENTS", "TOTAL FORECAST EXPENDITURE", "VARIANCE - TOTAL", "VARIANCE - IN PERIOD"]
        required_indexes = [headers.index(col) for col in required_columns if col in headers]

        items = []
        for row in new_change_sheet.iter_rows(min_row=3, values_only=True):
            if not any(row[i] not in [None, ""] for i in required_indexes):
                continue
            
            item = {headers[i]: str(row[i]) if isinstance(row[i], (int, float)) else (row[i] if row[i] not in [None, ""] else "0") for i in range(len(headers))}
            new_change_table.put_item(Item=item)
            items.append(item)

        if "New Cost Reporting " not in wb.sheetnames:
            return JsonResponse({"error": "Sheet 'New Cost Reporting' not found"}, status=400)

        new_cost_reporting_sheet = wb["New Cost Reporting "]

        headers = [cell.value for cell in new_cost_reporting_sheet[1]]

        required_columns = ["Interim Payments", "Month", "Forecast Monthly", "Actual Monthly", "Forecast Cumulative", "Actual Cumulative"]
        required_indexes = {col: headers.index(col) for col in required_columns if col in headers}

        items = []
        for row in new_cost_reporting_sheet.iter_rows(min_row=2, values_only=True):
            if all(row[i] not in [None, "", "#REF!"] for i in required_indexes.values()):
                item = {}
                for col, i in required_indexes.items():
                    value = row[i]

                    if col == "Month":
                        if isinstance(value, datetime):
                            value = value.strftime("%b")
                        elif isinstance(value, str) and value.strip():
                            try:
                                value = datetime.strptime(value, "%m/%d/%Y").strftime("%b")
                            except ValueError:
                                value = ""
                        else:
                            value = ""

                    elif isinstance(value, float):
                        value = Decimal(str(value))

                    else:
                        value = str(value) if value not in [None, ""] else "0"

                    item[col] = value

                new_cost_reporting_table.put_item(Item=item)
                items.append(item)

        return JsonResponse({"message": "File processed successfully"}, status=201)
    

class RiskDashboardView(ViewBase):
    TEMPLATE_NAME = 'dashboard/risk_dashboard.html'

    def get(self, request, *args, **kwargs):

        # top graphs
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]

        payment_sums = {
            'total_risk': np.random.randint(5, 1000),
            'total_unmitigated_risk': np.random.randint(5, 1000),
            'total_mitigated_risk': np.random.randint(5, 1000),
            'total_design_development_risk': np.random.randint(5, 1000),
            'total_construction_risk': np.random.randint(5, 1000),
            'total_employer_change_risk': np.random.randint(5, 1000),
            'total_employer_other_risk': np.random.randint(5, 1000),
        }

        graphs = {}

        for key, value in payment_sums.items():
            values = [0, 0, value, 0, 0, 0, 0]
            
            x = np.linspace(0, len(values) - 1, 300)
            y = np.interp(x, range(len(values)), values)

            plt.figure(figsize=(6, 2), dpi=100)
            plt.plot(x, y, color='#86CD57', linewidth=2)
            plt.fill_between(x, y, min(values), color='#d3e7c7', alpha=0.4)

            plt.ylim(0, 1000)
            plt.xticks([])
            plt.yticks([])
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['left'].set_visible(False)
            plt.gca().spines['bottom'].set_visible(False)
            plt.grid(False)

            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
            buffer.seek(0)

            graphs[key] = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()
            # plt.close(fig)


        # pie charts
        pie_charts = {}
        pie_charts_values = {}

        for i in range(5):
            open_percent = np.random.randint(10, 90)
            close_percent = 100 - open_percent       # Close percentage

            values = [open_percent, close_percent]
            colors = ['#86CD57', '#d3e7c7']  # Green for open, Light green for close

            # Create pie chart
            fig, ax = plt.subplots(figsize=(2, 2), dpi=100)
            ax.pie(values, colors=colors, startangle=90, counterclock=False, wedgeprops={'edgecolor': 'white'})

            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
            buffer.seek(0)
            
            pie_charts[f'chart_{i+1}'] = base64.b64encode(buffer.getvalue()).decode()
            pie_charts_values[f'chart_{i+1}'] = {'open': open_percent, 'close': close_percent}
            buffer.close()
            plt.close(fig)  


        # Generate 3 heatmaps
        heatmaps = {}
        for _ in range(3):
            data = np.random.randint(1, 100, size=(5, 5))

            fig, ax = plt.subplots(figsize=(3, 3), dpi=100)

            cmap = plt.cm.get_cmap("RdYlGn_r")

            ax.matshow(data, cmap=cmap, alpha=0.8)

            ax.set_xticks([])
            ax.set_yticks([])

            for spine in ax.spines.values():
                spine.set_visible(False)

            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
            buffer.seek(0)
            heatmaps[f'chart_{_+1}'] = base64.b64encode(buffer.getvalue()).decode()

            buffer.close()
            plt.close(fig)

        context = {
            "graphs": {
                'total_risk': graphs["total_risk"],
                'total_unmitigated_risk': graphs["total_unmitigated_risk"],
                'total_mitigated_risk': graphs["total_mitigated_risk"],
                'total_design_development_risk': graphs["total_design_development_risk"],
                'total_construction_risk': graphs["total_construction_risk"],
                'total_employer_change_risk': graphs["total_employer_change_risk"],
                'total_employer_other_risk': graphs["total_employer_other_risk"]
            },
            "pie_charts": pie_charts,
            "pie_charts_values": pie_charts_values,
            "heatmaps": heatmaps
        }

        return self.render(context)
    

class NetCarbonDashboardView(ViewBase):
    TEMPLATE_NAME = 'dashboard/net_carbon_dashboard.html'

    def get(self, request, *args, **kwargs):

        context = {}

        return self.render(context)
    

class RetroFitDashboardView(ViewBase):
    TEMPLATE_NAME = 'dashboard/retro_fit_dashboard.html'

    def get(self, request, *args, **kwargs):

        context = {}

        return self.render(context)
    

class InformationManagementDashboardView(ViewBase):
    TEMPLATE_NAME = 'dashboard/information_management_dashboard.html'

    def get(self, request, *args, **kwargs):

        context = {}

        return self.render(context)
    

def update_dynamo_record(request):
    if request.method == "POST":
        try:
            dynamodb = boto3.resource("dynamodb", region_name="eu-west-2", )
            data = json.loads(request.body)
            search_value = data.get("search_value")
            search_column = data.get("search_column")
            new_value = data.get("new_value")
            table_name = data.get("table_name")
            table = dynamodb.Table(table_name)

            if not search_value or not search_column or new_value is None:
                return JsonResponse({"error": "Missing required parameters"}, status=400)
            
            if "£" in new_value:
                cleaned_value = new_value.replace("£", "")
                cleaned_value = re.sub(r"[^\d.]", "", cleaned_value)
                new_value = Decimal(str(cleaned_value)) if '.' in cleaned_value else int(cleaned_value)

            try:
                if "." in str(search_value):
                    search_value = Decimal(str(search_value))
                else:
                    search_value = int(search_value)
            except ValueError:
                search_value = str(search_value)
            
            response = table.scan(
                FilterExpression=f"#{'_'.join(search_column.lower().split())} = :val",
                ExpressionAttributeNames={f"#{'_'.join(search_column.lower().split())}": search_column},
                ExpressionAttributeValues={":val": search_value}
            )
            items = response.get('Items', [])
            items = sorted(items, key=lambda x: float(x.get('Ref', 0)))

            if not items:
                return JsonResponse({"error": "Item not found"}, status=404)

            ref_id = items[0]['Ref']

            table.update_item(
                Key={'Ref': ref_id},
                UpdateExpression=f"set #{'_'.join(search_column.lower().split())} = :value",
                ExpressionAttributeNames={f"#{'_'.join(search_column.lower().split())}": search_column},
                ExpressionAttributeValues={':value': new_value}
            )

            return JsonResponse({"message": f"Field '{search_column}' updated successfully!"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)