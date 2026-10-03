import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import format_amount

from ..tools import escpos


class ProductBarcodePrintWizard(models.TransientModel):
    _name = 'product.barcode.print.wizard'
    _description = "Impression d'étiquettes code-barres"

    product_ids = fields.Many2many('product.product', string="Produits")
    quantity = fields.Integer("Nombre d'étiquettes par produit", default=1)
    show_name = fields.Boolean("Afficher le nom", default=True)
    show_price = fields.Boolean("Afficher le prix")
    show_digits = fields.Boolean("Afficher les chiffres", default=True)
    show_reference = fields.Boolean("Afficher la référence")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        model = self.env.context.get('active_model')
        ids = self.env.context.get('active_ids', [])
        if model == 'product.template':
            variants = self.env['product.template'].browse(ids).product_variant_ids
            res['product_ids'] = [fields.Command.set(variants.ids)]
        elif model == 'product.product':
            res['product_ids'] = [fields.Command.set(ids)]
        return res

    def _build_escpos(self):
        """Octets ESC/POS de toutes les étiquettes demandées."""
        self.ensure_one()
        sans_code = self.product_ids.filtered(lambda p: not p.barcode)
        if sans_code:
            raise UserError(_("Ces produits n'ont pas de code-barres : %s",
                              ", ".join(sans_code.mapped('display_name'))))
        if self.quantity < 1:
            raise UserError(_("Le nombre d'étiquettes doit être au moins 1."))
        data = b''
        for product in self.product_ids:
            prix = format_amount(self.env, product.lst_price, product.currency_id)
            data += escpos.etiquette(
                product.barcode,
                nom=product.name if self.show_name else None,
                prix=prix if self.show_price else None,
                reference=product.default_code if self.show_reference else None,
                afficher_chiffres=self.show_digits,
            ) * self.quantity
        return data

    def _build_escpos_base64(self):
        """Même chose, en texte base64 : le format pour l'envoyer au navigateur."""
        return base64.b64encode(self._build_escpos()).decode()

    def action_download(self):
        """Test : télécharge les octets ESC/POS dans un fichier .bin."""
        attachment = self.env['ir.attachment'].create({
            'name': 'etiquettes.bin',
            'raw': self._build_escpos(),
            'mimetype': 'application/octet-stream',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
