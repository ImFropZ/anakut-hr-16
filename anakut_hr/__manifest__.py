{
    'name': "Anakut HR Management",
    'summary': "Manage Anakut HR",
    'version': '1.0',
    'category': 'Human Resources',
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'hr', 'hr_contract', 'hr_payroll', 'hr_work_entry_contract_enterprise', 'approvals'],  # List of dependencies
    'data': [
        'security/hr_employee_security.xml',
        'security/ir.model.access.csv',
    
        'views/approval_views.xml',
        'menu/op_menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
