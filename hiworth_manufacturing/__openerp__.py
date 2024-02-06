{
    'name': 'Hiworth Construction Management',
    'version': '1.0',
    'category': 'Project',
    'sequence': 21,
    'description': """ Project Cost Estimation """,
    'depends': ['sale','mrp'],
    'data': [

            'report/sale_order_report.xml',
            'views/interlocks_menu_items.xml',
            'views/sales_order_views.xml',


    ],

    'qweb': [
                
            ],

    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
