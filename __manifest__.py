# -*- coding: utf-8 -*-
# Custom implementation of purchase module

{
    'name': 'custom_purchases',
    'version': '2.0',
    'summary': 'Custom implementation of purchases',
    'depends': {
        'purchase',
    },
    'data': {
        # 'views/purchase_request_views.xml',
        'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/purchase_order_offer_views.xml',
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'sequence': -700,
}
