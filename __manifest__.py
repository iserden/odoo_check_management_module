{
    'name': 'Çek Yönetimi Modülü',
    'version': '1.0',
    'category': 'Accounting/Localizations',
    'summary': 'Alınan ve verilen çeklerin yönetimi',
    'description': """
        Bu modül, alınan ve verilen çeklerin takibini sağlar.
        Durum yönetimi ve temel muhasebe entegrasyonu içerir.
    """,
    'author': 'Erden',
    'website': 'http://www.yourcompany.com',
    'depends': ['base', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/account_check_form_view.xml',
        'views/account_check_list_view.xml',
        'views/account_check_search_view.xml',
        'views/account_check_actions.xml',
        'views/account_check_menus.xml',
        'views/circulated_check_form.xml',
        'views/account_check_circulation_inherit.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {},
    'license': 'LGPL-3',
    'web_icon': 'account_check_management,static/description/icon.png',
}