{
    'name': "Mission Form Management",
    'summary': "Manage employee mission form",
    'version': '1.0',
    'category': 'Human Resources',
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'hr'],  # List of dependencies
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
