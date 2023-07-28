# -*- coding: utf-8 -*-
{
    'name' : 'P Employee',
    'version' : '1.0',
    'summary': 'Employee module custom by Phuong2711',
    'category': 'P Erp/Employee',
    'sequence': 20,
    'description': """
    Employee module custom by Phuong2711
    """,
    'website': 'https://github.com/Phuong2711/p_erp',
    'depends': [
        'hr',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/position_views.xml',
        'views/document_views.xml',
        'views/hr_department_views.xml',
        'views/hr_employee_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'p_employee/static/src/xml/*.xml',
        ],
    },
    'license': 'LGPL-3',
}
