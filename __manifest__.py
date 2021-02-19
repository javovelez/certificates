# -*- coding: utf-8 -*-
{
    'name': "Gestión de certificados",

    'summary': """
        Permite la gestión de certificados, sub-contratistas y materiales""",

    'description': """
    """,

    'author': "TIMSA",
    'website': "www.timsasa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sales',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sales_team', 'payment','product'],

    # always loaded
    'data': [
        'security/certificates_security.xml',
        'security/ir.model.access.csv',
        'views/certificates_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True, 
}
