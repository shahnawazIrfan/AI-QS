from django.urls import reverse_lazy

SITE_VERSION = '0.1.0'

SITE_TABS = [
    {
        'display_name': 'Home',
        'icon': 'dashboard',
        'id': 'user_dashboard',
        'link_url': reverse_lazy('user_dashboard'),
        'visible': ['user'],
        'pendingCount': None,
        'active': False,
        'actions': [],
    },
    {
        'display_name': 'Overiew',
        'icon': 'chart',
        'id': 'overview',
        'link_url': reverse_lazy('client_project_listing'),
        'visible': ['user'],
        'pendingCount': None,
        'active': False,
        'actions': [],
    },
    {
        'display_name': 'Projects',
        'icon': 'connect-data-source',
        'id': 'projects',
        'link_url': '#',
        'visible': ['user'],
        'pendingCount': None,
        'active': False,
        'actions': [
            {
                'display_name': 'Overview',
                'id': 'project_overview',
                'link_url': reverse_lazy('client_project_detail'),
                'visible': ['user']
            },
            {
                'display_name': 'Cost Report Dashboard',
                'id': 'cost_dashboard',
                'link_url': reverse_lazy('cost_dashboard'),
                'visible': ['user']
            },
            {
                'display_name': 'Risk Report Dashboard',
                'id': 'risk_Dashboard',
                'link_url': reverse_lazy('risk_dashboard'),
                'visible': ['user']
            },
            {
                'display_name': 'Net Zero Carbon Dashboard',
                'id': 'net_carbon_Dashboard',
                'link_url': reverse_lazy('net_carbon'),
                'visible': ['user']
            },
            {
                'display_name': 'RetroFit Dashboard',
                'id': 'retrofit_Dashboard',
                'link_url': reverse_lazy('retro_fit'),
                'visible': ['user']
            },
            {
                'display_name': 'Information Dashboard',
                'id': 'information_Management_Dashboard',
                'link_url': reverse_lazy('information_management'),
                'visible': ['user']
            }
        ],
    },
    # {
    #     'display_name': 'Cost/Risk Report',
    #     'icon': 'cost-report',
    #     'id': 'cost-report',
    #     'link_url': '#',
    #     'visible': ['user'],
    #     'pendingCount': None,
    #     'active': False,
    #     'actions': [],
    # },
    # {
    #     'display_name': '3D Model',
    #     'icon': 'data-model',
    #     'id': 'data-model',
    #     'link_url': '#',
    #     'visible': ['user'],
    #     'pendingCount': None,
    #     'active': False,
    #     'actions': [],
    # },
    # {
    #     'display_name': 'Import Data',
    #     'icon': 'import-data',
    #     'id': 'import-data',
    #     'link_url': '#',
    #     'visible': ['user'],
    #     'pendingCount': None,
    #     'active': False,
    #     'actions': [],
    # },
    # {
    #     'display_name': 'Upload Data',
    #     'icon': 'upload-data',
    #     'id': 'upload-data',
    #     'link_url': '#',
    #     'visible': ['user'],
    #     'pendingCount': None,
    #     'active': False,
    #     'actions': [],
    # },
    # {
    #     'display_name': 'Export Data',
    #     'icon': 'export-data',
    #     'id': 'export-data',
    #     'link_url': '#',
    #     'visible': ['user'],
    #     'pendingCount': None,
    #     'active': False,
    #     'actions': [],
    # }
]