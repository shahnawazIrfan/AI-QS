from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging
import os
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
from bson import ObjectId
from django.forms.models import model_to_dict
from django.db.models import Sum
from django.conf import settings
from openpyxl.styles import Font
from web_app import models
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
        # top card counts
        cost_summary = models.CostSummary.objects.all()
        total_contract_sum = round(sum(Decimal(str(obj.contract_sum)) for obj in cost_summary if obj.contract_sum), 2)
        certified_payments_sum = round(sum(Decimal(str(obj.certified_payments)) for obj in cost_summary if obj.certified_payments), 2)
        anticipated_payments_sum = round(sum(Decimal(str(obj.accrued_payments)) for obj in cost_summary if obj.accrued_payments), 2)
        forecast_expenditures_sum = round(sum(Decimal(str(obj.total_expenditure)) for obj in cost_summary if obj.total_expenditure), 2)
        total_variance_sum = round(sum(Decimal(str(obj.variance_total)) for obj in cost_summary if obj.variance_total), 2)
        total_variance_period_sum = round(sum(Decimal(str(obj.variance_period)) for obj in cost_summary if obj.variance_period), 2)

        # cost summary table
        total_new_cost_summary_sections = models.CostSummarySection.objects.count()
        costSummarySections = models.CostSummarySection.objects.prefetch_related("cost_summaries").all()

        new_cost_summary_data = []

        for section in costSummarySections:
            section_dict = {
                "section_id": section._id,
                "section_name": section.name,
                "rows": []
            }

            for cost_summary in section.cost_summaries.all():
                cost_summary_dict = model_to_dict(cost_summary, exclude=["section"])
                cost_summary_dict["id"] = str(cost_summary._id)
                section_dict["rows"].append(cost_summary_dict)

            new_cost_summary_data.append(section_dict)


        # contract sum table
        total_new_contract_sum_sections = models.ContractSumSection.objects.count()
        ContractSumSections = models.ContractSumSection.objects.prefetch_related("contract_sums").all()

        new_contract_sum_data = []

        for section in ContractSumSections:
            section_dict = {
                "section_id": section._id,
                "section_name": section.name,
                "rows": []
            }

            for contract_sum in section.contract_sums.all():
                contract_sum_dict = model_to_dict(contract_sum, exclude=["section"])
                contract_sum_dict["id"] = str(contract_sum._id)
                section_dict["rows"].append(contract_sum_dict)

            new_contract_sum_data.append(section_dict)


        # change breakdown table
        total_new_change_breakdown_sections = models.ChangeBreakDownSection.objects.count()
        ChangeBreakDownSections = models.ChangeBreakDownSection.objects.prefetch_related("change_breakdown").all()

        new_change_breakdown_data = []

        for section in ChangeBreakDownSections:
            section_dict = {
                "section_id": section._id,
                "section_name": section.name,
                "rows": []
            }

            for change_breakdown in section.change_breakdown.all():
                change_breakdown_dict = model_to_dict(change_breakdown, exclude=["section"])
                change_breakdown_dict["id"] = str(change_breakdown._id)
                section_dict["rows"].append(change_breakdown_dict)

            new_change_breakdown_data.append(section_dict)


        # cost reporting graph sum values

        cost_reporting = models.CostReporting.objects.all()
        total_forecast_monthly = round(sum(Decimal(str(obj.forecast_monthly)) for obj in cost_reporting if obj.forecast_monthly), 2)
        total_actual_monthly = round(sum(Decimal(str(obj.actual_monthly)) for obj in cost_reporting if obj.actual_monthly), 2)
        total_forecast_comulative = round(sum(Decimal(str(obj.forecast_comulative)) for obj in cost_reporting if obj.forecast_comulative), 2)
        total_actual_comulative = round(sum(Decimal(str(obj.actual_comulative)) for obj in cost_reporting if obj.actual_comulative), 2)
        
        # cost reporting graph month values

        months = models.CostReporting.objects.values("month").distinct().order_by("month")
        months = [m["month"] for m in months if m["month"]]
        months = [date.strftime("%b %y") for date in months]

        context = {
            'new_cost_summary_data': new_cost_summary_data,
            'total_new_cost_summary_sections': total_new_cost_summary_sections,
            'new_contract_sum_data': new_contract_sum_data,
            'total_new_contract_sum_sections': total_new_contract_sum_sections,
            'new_change_breakdown_data': new_change_breakdown_data,
            'total_new_change_breakdown_sections': total_new_change_breakdown_sections,
            'total_contract_sum': total_contract_sum,
            'certified_payments_sum': certified_payments_sum,
            'anticipated_payments_sum': anticipated_payments_sum,
            'forecast_expenditures_sum': forecast_expenditures_sum,
            'total_variance_sum': total_variance_sum,
            'total_variance_period_sum': total_variance_period_sum,
            'total_forecast_monthly': total_forecast_monthly,
            'total_actual_monthly': total_actual_monthly,
            'total_forecast_comulative': total_forecast_comulative,
            'total_actual_comulative': total_actual_comulative,
            'months': months
        }

        return self.render(context)
    
    def post(self, request, *args, **kwargs):
        if "file" not in request.FILES:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        file = request.FILES["file"]

        wb = openpyxl.load_workbook(file, data_only=True)

        # new cost summary sheet
        
        if "NEW Cost Summary" not in wb.sheetnames:
            return JsonResponse({"error": "Sheet 'NEW Cost Summary' not found"}, status=400)

        new_cost_summary_sheet = wb["NEW Cost Summary"]

        new_cost_summary_required_columns = {"Ref", "Item", "CONTRACT SUM", "CERTIFIED PAYMENTS TO CONTRACTOR", "ACCRUED & ANTICIPATED PAYMENTS", "TOTAL FORECAST EXPENDITURE", "VARIANCE - TOTAL ", "VARIANCE - IN PERIOD"}

        new_cost_summary_headers = [cell.value for cell in new_cost_summary_sheet[1]]

        new_cost_summary_missing_columns = new_cost_summary_required_columns - set(new_cost_summary_headers)
        if new_cost_summary_missing_columns:
            return JsonResponse({"error": f"Invalid format for Sheet 'NEW Cost Summary': Missing columns - {', '.join(new_cost_summary_missing_columns)}"}, status=400)

        new_cost_summary_section_id = ""

        for row in new_cost_summary_sheet.iter_rows(min_row=2, values_only=True):
            item = {new_cost_summary_headers[i]: str(row[i]) if isinstance(row[i], (int, float)) else (row[i] if row[i] not in [None, ""] else 0.0) for i in range(len(new_cost_summary_headers))}
            
            try:
                if "." not in item['Ref'] and item['Item'] != "" and all(v == 0.0 for k, v in item.items() if k not in ["Ref", "Item"]):
                    section = models.CostSummarySection.objects.create(_id=str(ObjectId()), name=item['Item'])
                    new_cost_summary_section_id = section._id

                elif "." in item['Ref'] and any(v not in [0.0, ""] for k, v in item.items() if k != "Ref"):
                    row = models.CostSummary.objects.create(_id=str(ObjectId()), ref=item['Ref'], item=item['Item'], contract_sum=item['CONTRACT SUM'], certified_payments=item['CERTIFIED PAYMENTS TO CONTRACTOR'], accrued_payments=item['ACCRUED & ANTICIPATED PAYMENTS'], total_expenditure=item['TOTAL FORECAST EXPENDITURE'], variance_total=item['VARIANCE - TOTAL '], variance_period=item['VARIANCE - IN PERIOD'], section_id=new_cost_summary_section_id)

            except Exception as e:
                print(e)
                pass


        # new contract sum sheet

        if "NEW Contract Sum" not in wb.sheetnames:
            return JsonResponse({"error": "Sheet 'NEW Contract Sum' not found"}, status=400)

        new_contract_sum_sheet = wb["NEW Contract Sum"]

        new_contract_sum_required_columns = {"Ref", "Item", "CONTRACT SUM", "CERTIFIED PAYMENTS TO CONTRACTOR"}

        new_contract_sum_headers = [cell.value for cell in new_contract_sum_sheet[1]]

        new_contract_sum_missing_columns = new_contract_sum_required_columns - set(new_contract_sum_headers)
        if new_contract_sum_missing_columns:
            return JsonResponse(
                {"error": f"Invalid format for Sheet 'NEW Contract Sum': Missing columns - {', '.join(new_contract_sum_missing_columns)}"},
                status=400
            )

        new_contract_sum_section_id = ""

        for row in new_contract_sum_sheet.iter_rows(min_row=2, values_only=True):
            item = {
                new_contract_sum_headers[i]: str(row[i]) if isinstance(row[i], (int, float)) else (row[i] if row[i] not in [None, ""] else 0.0)
                for i in range(len(new_contract_sum_headers))
            }

            try:
                if "." not in item['Ref'] and item['Item'] != "" and all(v == 0.0 for k, v in item.items() if k not in ["Ref", "Item"]):
                    section = models.ContractSumSection.objects.create(_id=str(ObjectId()), name=item['Item'])
                    new_contract_sum_section_id = section._id

                elif "." in item['Ref'] and any(v not in [0.0, ""] for k, v in item.items() if k != "Ref"):
                    row = models.ContractSum.objects.create(
                        _id=str(ObjectId()),
                        ref=item['Ref'],
                        item=item['Item'],
                        contract_sum=item['CONTRACT SUM'],
                        certified_payments=item['CERTIFIED PAYMENTS TO CONTRACTOR'],
                        section_id=new_contract_sum_section_id
                    )

            except Exception:
                pass

        # new change breakdown sheet

        if "NEW EAChange" not in wb.sheetnames:
            return JsonResponse({"error": "Sheet 'NEW EAChange' not found"}, status=400)

        new_change_breakdown_sheet = wb["NEW EAChange"]

        new_change_breakdown_required_columns = {"Ref", "Item", "CONTRACT SUM", "CERTIFIED PAYMENTS TO CONTRACTOR", "ACCRUED & ANTICIPATED PAYMENTS", "TOTAL FORECAST EXPENDITURE", "VARIANCE - TOTAL ", "VARIANCE - IN PERIOD"}

        new_change_breakdown_headers = [cell.value for cell in new_change_breakdown_sheet[1]]

        new_change_breakdown_missing_columns = new_change_breakdown_required_columns - set(new_change_breakdown_headers)
        if new_change_breakdown_missing_columns:
            return JsonResponse(
                {"error": f"Invalid format for Sheet 'NEW Change Breakdown': Missing columns - {', '.join(new_change_breakdown_missing_columns)}"},
                status=400
            )

        new_change_breakdown_section_id = ""

        for row in new_change_breakdown_sheet.iter_rows(min_row=2, values_only=True):
            item = {
                new_change_breakdown_headers[i]: str(row[i]) if isinstance(row[i], (int, float)) else (row[i] if row[i] not in [None, ""] else 0.0)
                for i in range(len(new_change_breakdown_headers))
            }

            try:
                if "." not in item['Ref'] and item['Item'] != "" and all(v == 0.0 for k, v in item.items() if k not in ["Ref", "Item"]):
                    section = models.ChangeBreakDownSection.objects.create(_id=str(ObjectId()), name=item['Item'])
                    new_change_breakdown_section_id = section._id

                elif "." in item['Ref'] and any(v not in [0.0, ""] for k, v in item.items() if k != "Ref"):
                    row = models.ChangeBreakDown.objects.create(
                        _id=str(ObjectId()),
                        ref=item['Ref'],
                        item=item['Item'],
                        certified_payments=item['CERTIFIED PAYMENTS TO CONTRACTOR'],
                        total_expenditure=item['TOTAL FORECAST EXPENDITURE'],
                        variance_total=item['VARIANCE - TOTAL '],
                        variance_period=item['VARIANCE - IN PERIOD'],
                        section_id=new_change_breakdown_section_id
                    )

            except Exception:
                pass

        
        # new cost reporting sheet

        if "New Cost Reporting " not in wb.sheetnames:
            return JsonResponse({"error": "Sheet 'New Cost Reporting' not found"}, status=400)

        new_cost_reporting_sheet = wb["New Cost Reporting "]

        new_cost_reporting_required_columns = {"Interim Payments", "Month", "Forecast Monthly", "Actual Monthly", "Forecast Cumulative", "Actual Cumulative"}

        new_cost_reporting_headers = [cell.value for cell in new_cost_reporting_sheet[1]]

        new_cost_reporting_missing_columns = new_cost_reporting_required_columns - set(new_cost_reporting_headers)
        if new_cost_reporting_missing_columns:
            return JsonResponse(
                {"error": f"Invalid format for Sheet 'New Cost Reporting': Missing columns - {', '.join(new_cost_reporting_missing_columns)}"},
                status=400
            )

        for row in new_cost_reporting_sheet.iter_rows(min_row=2, values_only=True):
            item = {
                new_cost_reporting_headers[i]: str(row[i]) if isinstance(row[i], (int, float)) 
                else (row[i] if row[i] not in [None, "", "#REF!"] else 0.0)
                for i in range(len(new_cost_reporting_headers))
            }

            try:
                models.CostReporting.objects.create(
                    _id=str(ObjectId()),
                    interim_payments=item['Interim Payments'],
                    month=item['Month'] + timedelta(days=1),
                    forecast_monthly=item['Forecast Monthly'],
                    actual_monthly=item['Actual Monthly'],
                    forecast_comulative=item['Forecast Cumulative'],
                    actual_comulative=item['Actual Cumulative']
                )
            except Exception:
                pass

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
    

class costSummaryOperationsView(ViewBase):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            type = data.get("type")
            section_id = data.get("section_id")
            section_name = data.get("section_name")
            row_id = data.get("row_id")
            ref = data.get("ref")
            item = data.get("item")
            contract_sum = data.get("contract_sum")
            certified_payments = data.get("certified_payments")
            accrued_payments = data.get("accrued_payments")
            total_expenditure = data.get("total_expenditure")
            variance_total = data.get("variance_total")
            variance_period = data.get("variance_period")

            if type == "section" and not section_id:
                section = models.CostSummarySection.objects.create(_id=str(ObjectId()), name=section_name)
                return JsonResponse({"message": "Cost summary saved successfully", "id": section._id}, status=201)
            
            if type == "section" and section_id:
                section = models.CostSummarySection.objects.filter(_id=section_id).update(name=section_name)
                return JsonResponse({"message": "Cost summary updated successfully", "id": section_id}, status=200)
            
            if type == "row" and not row_id and section_id:
                row = models.CostSummary.objects.create(_id=str(ObjectId()), ref=ref, item=item, contract_sum=contract_sum, certified_payments=certified_payments, accrued_payments=accrued_payments, total_expenditure=total_expenditure, variance_total=variance_total, variance_period=variance_period, section_id=section_id)
               
                cost_summary = models.CostSummary.objects.all()
                total_contract_sum = sum(Decimal(str(obj.contract_sum)) for obj in cost_summary if obj.contract_sum)
                certified_payments_sum = sum(Decimal(str(obj.certified_payments)) for obj in cost_summary if obj.certified_payments)
                anticipated_payments_sum = sum(Decimal(str(obj.accrued_payments)) for obj in cost_summary if obj.accrued_payments)
                forecast_expenditures_sum = sum(Decimal(str(obj.total_expenditure)) for obj in cost_summary if obj.total_expenditure)
                total_variance_sum = sum(Decimal(str(obj.variance_total)) for obj in cost_summary if obj.variance_total)
                total_variance_period_sum = sum(Decimal(str(obj.variance_period)) for obj in cost_summary if obj.variance_period)
                
                return JsonResponse({"message": "Cost summary row saved successfully", "id": row._id, "total_contract_sum": total_contract_sum, "certified_payments_sum": certified_payments_sum, "anticipated_payments_sum": anticipated_payments_sum, "forecast_expenditures_sum": forecast_expenditures_sum, "total_variance_sum": total_variance_sum, "total_variance_period_sum": total_variance_period_sum}, status=201)
            
            if type == "row" and row_id and section_id:
                row = models.CostSummary.objects.filter(_id=row_id).update(ref=ref, item=item, contract_sum=contract_sum, certified_payments=certified_payments, accrued_payments=accrued_payments, total_expenditure=total_expenditure, variance_total=variance_total, variance_period=variance_period, section_id=section_id)
                
                cost_summary = models.CostSummary.objects.all()
                total_contract_sum = sum(Decimal(str(obj.contract_sum)) for obj in cost_summary if obj.contract_sum)
                certified_payments_sum = sum(Decimal(str(obj.certified_payments)) for obj in cost_summary if obj.certified_payments)
                anticipated_payments_sum = sum(Decimal(str(obj.accrued_payments)) for obj in cost_summary if obj.accrued_payments)
                forecast_expenditures_sum = sum(Decimal(str(obj.total_expenditure)) for obj in cost_summary if obj.total_expenditure)
                total_variance_sum = sum(Decimal(str(obj.variance_total)) for obj in cost_summary if obj.variance_total)
                total_variance_period_sum = sum(Decimal(str(obj.variance_period)) for obj in cost_summary if obj.variance_period)
                
                return JsonResponse({"message": "Cost summary row updated successfully", "id": row_id, "total_contract_sum": total_contract_sum, "certified_payments_sum": certified_payments_sum, "anticipated_payments_sum": anticipated_payments_sum, "forecast_expenditures_sum": forecast_expenditures_sum, "total_variance_sum": total_variance_sum, "total_variance_period_sum": total_variance_period_sum}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            type = data.get("type")
            delete_row_id = request.GET.get("delete_row_id")
            delete_section_id = request.GET.get("delete_section_id")

            if type == "delete_section" and delete_section_id:
                models.CostSummarySection.objects.filter(_id=delete_section_id).delete()
                return JsonResponse({"message": "Cost summary section deleted successfully"}, status=200)

            if type == "delete_row" and delete_row_id:
                models.CostSummary.objects.filter(_id=delete_row_id).delete()

                cost_summary = models.CostSummary.objects.all()
                total_contract_sum = sum(Decimal(str(obj.contract_sum)) for obj in cost_summary if obj.contract_sum)
                certified_payments_sum = sum(Decimal(str(obj.certified_payments)) for obj in cost_summary if obj.certified_payments)
                anticipated_payments_sum = sum(Decimal(str(obj.accrued_payments)) for obj in cost_summary if obj.accrued_payments)
                forecast_expenditures_sum = sum(Decimal(str(obj.total_expenditure)) for obj in cost_summary if obj.total_expenditure)
                total_variance_sum = sum(Decimal(str(obj.variance_total)) for obj in cost_summary if obj.variance_total)
                total_variance_period_sum = sum(Decimal(str(obj.variance_period)) for obj in cost_summary if obj.variance_period)

                return JsonResponse({"message": "Cost summary row deleted successfully", "total_contract_sum": total_contract_sum, "certified_payments_sum": certified_payments_sum, "anticipated_payments_sum": anticipated_payments_sum, "forecast_expenditures_sum": forecast_expenditures_sum, "total_variance_sum": total_variance_sum, "total_variance_period_sum": total_variance_period_sum}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        

class contractSumOperationsView(ViewBase):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            type = data.get("type")
            section_id = data.get("section_id")
            section_name = data.get("section_name")
            row_id = data.get("row_id")
            ref = data.get("ref")
            item = data.get("item")
            contract_sum = data.get("contract_sum")
            certified_payments = data.get("certified_payments")

            if type == "section" and not section_id:
                section = models.ContractSumSection.objects.create(_id=str(ObjectId()), name=section_name)
                return JsonResponse({"message": "Contract sum saved successfully", "id": section._id}, status=201)
            
            if type == "section" and section_id:
                section = models.ContractSumSection.objects.filter(_id=section_id).update(name=section_name)
                return JsonResponse({"message": "Contract sum updated successfully", "id": section_id}, status=200)
            
            if type == "row" and not row_id and section_id:
                row = models.ContractSum.objects.create(_id=str(ObjectId()), ref=ref, item=item, contract_sum=contract_sum, certified_payments=certified_payments, section_id=section_id)
                return JsonResponse({"message": "Contract sum row saved successfully", "id": row._id}, status=201)
            
            if type == "row" and row_id and section_id:
                row = models.ContractSum.objects.filter(_id=row_id).update(ref=ref, item=item, contract_sum=contract_sum, certified_payments=certified_payments, section_id=section_id)
                return JsonResponse({"message": "Contract sum row updated successfully", "id": row_id}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            type = data.get("type")
            delete_row_id = request.GET.get("delete_row_id")
            delete_section_id = request.GET.get("delete_section_id")

            if type == "delete_section" and delete_section_id:
                models.ContractSumSection.objects.filter(_id=delete_section_id).delete()
                return JsonResponse({"message": "Cost summary section deleted successfully"}, status=200)

            if type == "delete_row" and delete_row_id:
                models.ContractSum.objects.filter(_id=delete_row_id).delete()
                return JsonResponse({"message": "Cost summary row deleted successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        

class changeBreakDownOperationsView(ViewBase):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            type = data.get("type")
            section_id = data.get("section_id")
            section_name = data.get("section_name")
            row_id = data.get("row_id")
            ref = data.get("ref")
            item = data.get("item")
            certified_payments = data.get("certified_payments")
            total_expenditure = data.get("total_expenditure")
            variance_total = data.get("variance_total")
            variance_period = data.get("variance_period")

            if type == "section" and not section_id:
                section = models.ChangeBreakDownSection.objects.create(_id=str(ObjectId()), name=section_name)
                return JsonResponse({"message": "Change break down saved successfully", "id": section._id}, status=201)
            
            if type == "section" and section_id:
                section = models.ChangeBreakDownSection.objects.filter(_id=section_id).update(name=section_name)
                return JsonResponse({"message": "Change break down updated successfully", "id": section_id}, status=200)
            
            if type == "row" and not row_id and section_id:
                row = models.ChangeBreakDown.objects.create(_id=str(ObjectId()), ref=ref, item=item, certified_payments=certified_payments, total_expenditure=total_expenditure, variance_total=variance_total, variance_period=variance_period, section_id=section_id)
                return JsonResponse({"message": "Change break down row saved successfully", "id": row._id}, status=201)
            
            if type == "row" and row_id and section_id:
                row = models.ChangeBreakDown.objects.filter(_id=row_id).update(ref=ref, item=item, certified_payments=certified_payments, total_expenditure=total_expenditure, variance_total=variance_total, variance_period=variance_period, section_id=section_id)
                return JsonResponse({"message": "Change break down row updated successfully", "id": row_id}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            type = data.get("type")
            delete_row_id = request.GET.get("delete_row_id")
            delete_section_id = request.GET.get("delete_section_id")

            if type == "delete_section" and delete_section_id:
                models.ChangeBreakDownSection.objects.filter(_id=delete_section_id).delete()
                return JsonResponse({"message": "Change break down section deleted successfully"}, status=200)

            if type == "delete_row" and delete_row_id:
                models.ChangeBreakDown.objects.filter(_id=delete_row_id).delete()
                return JsonResponse({"message": "Change break down row deleted successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        

class getCostChartDataView(ViewBase):
    def get(self, request, *args, **kwargs):
        data = models.CostReporting.objects.values("month").distinct().order_by("month")
        months = [d["month"] for d in data if d["month"]]

        forecast_monthly_data = []
        actual_monthly_data = []
        forecast_cumulative_data = []
        actual_cumulative_data = []

        for month in months:
            forecast_monthly = models.CostReporting.objects.filter(month=month).aggregate(Sum("forecast_monthly"))["forecast_monthly__sum"] or 0
            actual_monthly = models.CostReporting.objects.filter(month=month).aggregate(Sum("actual_monthly"))["actual_monthly__sum"] or 0
            forecast_cumulative = models.CostReporting.objects.filter(month=month).aggregate(Sum("forecast_comulative"))["forecast_comulative__sum"] or 0
            actual_cumulative = models.CostReporting.objects.filter(month=month).aggregate(Sum("actual_comulative"))["actual_comulative__sum"] or 0

            forecast_monthly_data.append(forecast_monthly)
            actual_monthly_data.append(actual_monthly)
            forecast_cumulative_data.append(forecast_cumulative)
            actual_cumulative_data.append(actual_cumulative)

        months = [date.strftime("%b %y") for date in months]

        chart_data = {
            "labels": months,
            "datasets": [
                {
                    "type": "bar",
                    "label": "Forecast Monthly",
                    "data": forecast_monthly_data,
                    "backgroundColor": "rgba(133, 204, 87, 1)",
                    "borderColor": "rgba(101, 225, 193, 1)",
                    "borderWidth": 1,
                    "stack": "Stack 0"
                },
                {
                    "type": "bar",
                    "label": "Actual Monthly",
                    "data": actual_monthly_data,
                    "backgroundColor": "rgba(133, 204, 87, 1)",
                    "borderColor": "rgba(101, 225, 193, 1)",
                    "borderWidth": 1,
                    "stack": "Stack 0"
                },
                {
                    "type": "line",
                    "label": "Forecast Cumulative",
                    "data": forecast_cumulative_data,
                    "borderColor": "rgba(101, 225, 193, 1)",
                    "borderWidth": 2,
                    "fill": False
                },
                {
                    "type": "line",
                    "label": "Actual Cumulative",
                    "data": actual_cumulative_data,
                    "borderColor": "rgba(101, 225, 193, 1)",
                    "borderWidth": 2,
                    "fill": False
                }
            ]
        }
        
        return JsonResponse(chart_data)
    

class downloadCostReportView(ViewBase):

    @staticmethod
    def clear_sheet_except_header(sheet):
        max_row = sheet.max_row
        if max_row > 1:
            sheet.delete_rows(2, max_row - 1)

    def post(self, request, *args, **kwargs):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f'cost_report_{timestamp}.xlsx'

            template_path = os.path.join(settings.BASE_DIR, 'static/cost_report_template.xlsx')
            new_file_path = os.path.join(settings.BASE_DIR, f'static/{file_name}')

            wb = openpyxl.load_workbook(template_path)

            # ==================== SHEET 1: NEW Cost Summary ====================
            cost_summary_sheet = wb["NEW Cost Summary"]
            self.clear_sheet_except_header(cost_summary_sheet)
            row = 2
            ref_counter = 1

            sections = models.CostSummarySection.objects.all()
            for section in sections:
                cost_summary_sheet.cell(row=row, column=1).value = str(ref_counter)
                cost_summary_sheet.cell(row=row, column=2).value = section.name
                cost_summary_sheet_cell = cost_summary_sheet.cell(row=row, column=2)
                cost_summary_sheet_cell.font = Font(bold=True, size=12)
                row += 1

                summaries = models.CostSummary.objects.filter(section=section)
                for summary in summaries:
                    cost_summary_sheet.cell(row=row, column=1).value = summary.ref
                    cost_summary_sheet.cell(row=row, column=2).value = summary.item
                    cost_summary_sheet.cell(row=row, column=3).value = float(summary.contract_sum or 0)
                    cost_summary_sheet.cell(row=row, column=4).value = float(summary.certified_payments or 0)
                    cost_summary_sheet.cell(row=row, column=5).value = float(summary.accrued_payments or 0)
                    cost_summary_sheet.cell(row=row, column=6).value = float(summary.total_expenditure or 0)
                    cost_summary_sheet.cell(row=row, column=7).value = float(summary.variance_total or 0)
                    cost_summary_sheet.cell(row=row, column=8).value = float(summary.variance_period or 0)
                    row += 1

                ref_counter += 1

            # ==================== SHEET 2: NEW Contract Sum ====================
            contract_sum_sheet = wb["NEW Contract Sum"]
            self.clear_sheet_except_header(contract_sum_sheet)
            row = 2
            ref_counter = 1

            contract_sections = models.ContractSumSection.objects.all()
            for section in contract_sections:
                contract_sum_sheet.cell(row=row, column=1).value = str(ref_counter)
                contract_sum_sheet.cell(row=row, column=2).value = section.name
                contract_sum_sheet_cell = contract_sum_sheet.cell(row=row, column=2)
                contract_sum_sheet_cell.font = Font(bold=True, size=12)
                row += 1

                items = models.ContractSum.objects.filter(section=section)
                for item in items:
                    contract_sum_sheet.cell(row=row, column=1).value = item.ref
                    contract_sum_sheet.cell(row=row, column=2).value = item.item
                    contract_sum_sheet.cell(row=row, column=3).value = float(item.contract_sum or 0)
                    contract_sum_sheet.cell(row=row, column=4).value = float(item.certified_payments or 0)
                    row += 1

                ref_counter += 1

            # ==================== SHEET 3: NEW EAChange ====================
            change_sheet = wb["NEW EAChange"]
            self.clear_sheet_except_header(change_sheet)
            row = 2
            ref_counter = 1

            change_sections = models.ChangeBreakDownSection.objects.all()
            for section in change_sections:
                change_sheet.cell(row=row, column=1).value = str(ref_counter)
                change_sheet.cell(row=row, column=2).value = section.name
                change_sheet_cell = change_sheet.cell(row=row, column=2)
                change_sheet_cell.font = Font(bold=True, size=12)
                row += 1

                changes = models.ChangeBreakDown.objects.filter(section=section)
                for change in changes:
                    change_sheet.cell(row=row, column=1).value = change.ref
                    change_sheet.cell(row=row, column=2).value = change.item
                    change_sheet.cell(row=row, column=3).value = float(change.certified_payments or 0)
                    change_sheet.cell(row=row, column=4).value = float(change.total_expenditure or 0)
                    change_sheet.cell(row=row, column=5).value = float(change.variance_total or 0)
                    change_sheet.cell(row=row, column=6).value = float(change.variance_period or 0)
                    row += 1

                ref_counter += 1

            wb.save(new_file_path)

            # Upload to S3
            bucket_name = 'ai-qs'
            s3_key = f"cost_reports/cost_report_{timestamp}.xlsx"

            aws_access_key_id = ''
            aws_secret_access_key = ''
            region_name = 'eu-west-2'

            s3 = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )

            s3.upload_file(
                Filename=new_file_path,
                Bucket=bucket_name,
                Key=s3_key,
                ExtraArgs={'ContentType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
            )

            s3.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=s3_key)

            file_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{s3_key}"

            os.remove(new_file_path)

            return JsonResponse({'success': True, 'file_url': file_url, 'file_name': file_name})

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Something went wrong while exporting cost report', 'error': str(e)})