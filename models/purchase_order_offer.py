from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderOffer(models.Model):

    _name = "purchase.order.offer"
    _description = "Purchase order offer"

    price = fields.Float(required=True)
    status = fields.Selection(selection=[("accepted", "Accepted"), ("refused", "Refused")])
    order_id = fields.Many2one("purchase.order", string="Order")
    partner_id = fields.Many2one("res.partner", string="Vendor", required=True)

    def action_accept_offer(self):
        for record in self:
            record.status = "accepted"
            other_orders = self.search([('id', '!=', record.id)])
            other_orders.write({'status': 'refused'})

    def action_refuse_offer(self):
        for record in self:
            record.status = "refused"

    @api.constrains('partner_id')
    def _validate_partner_id(self):
        for record in self:
            if record.partner_id not in record.order_id.vendor_ids:
                raise ValidationError(
                    f"Unknown Vendor: '{record.partner_id.name}' cannot bid on this order")
