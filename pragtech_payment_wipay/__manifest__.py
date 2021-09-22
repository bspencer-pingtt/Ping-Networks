{
    'name': 'WiPay Payment Gateway',
    'version': '13.0.1.0',
    'category': 'Payment Integration',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'www.pragtech.co.in',
    'summary': '',
    'description': """""",
    'depends': ['payment', 'website', 'account', 'website_sale'],
    'data': [
        'data/payment_acquirer.xml',
        'views/payment_acquirer.xml',
        'views/payment.xml',
    ],
    'images': [],
    'license': 'OPL-1',
    'installable': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
}
