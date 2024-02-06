{
    'name': 'BG Store',
    'version': '1.0',
    'author': 'Hiworth',
    'description': '''
        A custom module to change default STORE
    ''',
    'category': '',
    'depends': [
        'base','stock','stock_account',
    ],
    # "images": ["static/image/bg_header.png"],
    'data': [
        'views/store_view.xml',
    ],
    'css': [''],
    'auto_install': False,
    'installable': True,
}