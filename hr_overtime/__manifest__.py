{
    'name': "Overtime Management",
    'summary': "Manage employee overtime requests",
    'version': '1.0',
    'category': 'Human Resources',
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'hr', 'hr_payroll'],  # List of dependencies
    'data': [
        'security/ir.model.access.csv',

        'views/hr_overtime_views.xml',  # Your tree view definition
        'views/actions.xml',  # Your action definition
        'views/menu.xml',   # Your menu and menu item definitions
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
