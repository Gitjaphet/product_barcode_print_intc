from odoo import models, _
from odoo.exceptions import UserError


def _ean13_check_digit(code12):
    """Clé EAN-13 : poids 1 et 3 alternés depuis la gauche."""
    total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(code12))
    return str((10 - total % 10) % 10)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _intc_last_barcode_base(self):
        """Plus grand préfixe à 12 chiffres '20…' déjà utilisé en base."""
        Product = self.env['product.product'].sudo().with_context(active_test=False)
        barcodes = Product.search([('barcode', '=like', '20%')]).mapped('barcode')
        bases = [int(b[:12]) for b in barcodes if len(b) == 13 and b.isdigit()]
        return max(bases, default=200000000000)

    def action_intc_generate_barcodes(self):
        variants = self.mapped('product_variant_ids').filtered(
            lambda p: not p.barcode and p.type != 'service'
        )
        if not variants:
            raise UserError(_(
                "Aucun produit à traiter : ils ont déjà un code-barres "
                "ou sont de type service."
            ))

        base = self._intc_last_barcode_base()
        for variant in variants:
            base += 1
            code12 = str(base)
            variant.barcode = code12 + _ean13_check_digit(code12)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Codes-barres générés"),
                'message': _("%s code(s)-barres créé(s).", len(variants)),
                'type': 'success',
                'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
            },
        }
