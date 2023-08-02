# -*- coding: utf-8 -*-
{
    'name': 'P Attendance',
    'version': '1.0',
    'summary': 'Attendance module custom by Phuong2711',
    'category': 'P Erp/Attendance',
    'sequence': 20,
    'description': """
    Attendance module custom by Phuong2711
    """,
    'website': 'https://github.com/Phuong2711/p_erp',
    'depends': [
        'p_employee',
        'hr_attendance',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'report/report.xml',
        'report/attendance_xlsx_views.xml',
        'views/res_config_settings_views.xml',
        'views/hr_attendance_views.xml',
        'views/menu.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
        ],
    },
    'license': 'LGPL-3',
}
