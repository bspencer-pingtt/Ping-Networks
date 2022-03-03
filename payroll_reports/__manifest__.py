# -*- coding: utf-8 -*-

{
    "name": "Payroll Reports",
    'summary': """Payroll Reports""",
    "category": "Human Resources/Payroll Reports",
    "version": "14.0.0.0.1",
    "author": "PING TECHNOLOGIES LIMITED",
    "license": "OPL-1",
    "website": "pingtt.com",
    "description": """Payroll Reports""",
    "depends": ['hr_payroll','hr'],
    "data": [
            'security/ir.model.access.csv',
            'wizard/td4_report_wizard_view.xml',
            'views/year_periods_view.xml',
            'views/report_employee.xml',
            'views/employee_report.xml',
            'views/assets.xml',
            'views/hr_employee_view.xml',
            'views/res_company_view.xml',
             ],
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    'sequence': 1
}