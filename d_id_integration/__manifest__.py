# -*- coding: utf-8 -*-
{
    'name': "D-ID API Integration",
    'version': '0.1',
    'summary': "Integrate Odoo with D-ID API to create talking avatars from text.",
    'description': """
D-ID API Integration for Odoo
=============================

This module allows you to:
- Generate talking avatars from text.
- Fetch the video result from D-ID.
- Store the video in Odoo and preview it directly.
    """,
    'author': "Ezzeldin Mohamed",
    'website': "https://github.com/ezzElzoz123",
    'category': 'Tools',
    'depends': ['base', 'portal'],
    'data': [
        # Access rights
        'security/ir.model.access.csv',
        # Views for D-ID
        'views/portal_template.xml',
        'reports/d_id_api_report.xml',
        'views/d_id_api_view.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
