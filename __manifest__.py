{
    'name': 'INTC Product Barcode Print',
    'version': '19.0.1.0.0',
    'summary': "Impression de codes-barres produits sur imprimante thermique ESC/POS",
    'author': 'INTC',
    'license': 'LGPL-3',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'views/barcode_print_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}
