{
    'name': 'BG Purchase',
    'version': '1.0',
    'author': 'Hiworth',
    'description': '''
        A custom module to change default purchase
    ''',
    'category': '',
    'depends': [
        'base','purchase',
    ],
    "images": ["static/image/bg_header.png"],
    'data': [
        'views/purchase_view.xml',
        'reports/purchase_report_template.xml',
    ],
    'css': [''],
    'auto_install': False,
    'installable': True,
}