{
    'name': 'INTC Product Barcode Print',
    'version': '19.0.1.2.0',
    'summary': "Impression de codes-barres produits sur imprimante thermique ESC/POS",
    'author': 'INTC',
    'license': 'LGPL-3',
    'depends': ['product', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/barcode_print_wizard_views.xml',
        'views/product_template_actions.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'product_barcode_print_intc/static/src/js/barcode_print_action.js',
        ],
    },
    'installable': True,
    'application': False,
}
