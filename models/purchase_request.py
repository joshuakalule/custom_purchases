from odoo import api, fields, models


class PurchaseRequest(models.Model):

    _name = "purchase.request"
    _description = "Purchase Request"

    name = fields.Char()
    employee_id = fields.Many2one("res.users", string="Employee", required=True, readonly=True)
    order_id = fields.Many2one("purchase.order", string="Purchase Order", readonly=True)
    product_ids = fields.Many2many("purchase.order.line", string="Products", readonly=True)
