from django.urls import path
from web_app.views.dashboard import views

urlpatterns = [
    path('client/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('project-listing/', views.ClientProjectListingView.as_view(), name='client_project_listing'),
    path('project-detail/', views.ClientProjectDetailView.as_view(), name='client_project_detail'),
    path('cost/', views.CostDashboardView.as_view(), name='cost_dashboard'),
    path('risk/', views.RiskDashboardView.as_view(), name='risk_dashboard'),  
    path('net-carbon/', views.NetCarbonDashboardView.as_view(), name='net_carbon'),
    path('retro-fit/', views.RetroFitDashboardView.as_view(), name='retro_fit'),
    path('information-management/', views.InformationManagementDashboardView.as_view(), name='information_management'),
    path('cost-summary-operations/', views.costSummaryOperationsView.as_view(), name='cost_summary_operations'),
    path('contract-sum-operations/', views.contractSumOperationsView.as_view(), name='contract_sum_operations'),
    path('change-breakdown-operations/', views.changeBreakDownOperationsView.as_view(), name='change_breakdown_operations'),
    path("cost-chart-data/", views.getCostChartDataView.as_view(), name="cost-chart-data"),
    path("download-cost-report/", views.downloadCostReportView.as_view(), name="download_cost_report"),
    path('add-dynamic-column/', views.addCostSummaryColumnView.as_view(), name='add_cost_summary_column'),
]