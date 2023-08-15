{
    'name': "Anakut Payroll Management",
    'summary': "Manage employee payroll",
    'version': '1.0',
    'category': 'Human Resources',
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'hr', 'hr_payroll'],  # List of dependencies
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
