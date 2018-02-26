# -*- coding: utf-8 -*-

{
    'name': 'Registros',
    'version': '1.0',
    'website': 'www.minsa.gob.pe',
    'category': 'hhrr',
    'depends': [
        'base',
        'product',
        'hr',
    ],
    'author': 'MINSA',
    'description': 'Minsa SGHCE - Registros VPH',
    'data': [
        'security/security.xml',
        'data/data.xml',
        'reports/vph_report.xml',
        'reports/vph_report_templates.xml',
        'views/trees.xml',
        'views/forms.xml',
        'views/pivot.xml',
        'views/wizards.xml',
        'views/calendar.xml',
        'views/search.xml',
        'views/actions.xml',
        'views/menus.xml',
        'views/graph.xml',
        'views/assets.xml',
        # 'views/dashboard.xml',
        # 'data/dashboard.xml',

    ],
    'active': False,
    'installable': True
}
