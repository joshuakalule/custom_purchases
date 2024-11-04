from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Purchase order with RFQ one-to-many relationship"

    # ability to assign rfq to many vendors
    # partner_refs = ...
    vendor_ids = fields.One2many("res.partner", "rfq_ids", required=True, tracking=True,
                                 help="You can find vendors by Name, TIN, Email or Internal Reference.",
                                 string="Vendors")
    offer_ids = fields.One2many("purchase.order.offer", "order_id")
    number_of_offers = fields.Integer("Number of offers", compute="_compute_number_of_offers")
    best_offer = fields.Float("Highest Bid", compute="_compute_best_offer")

    selected_vendor = fields.Many2one("res.partner", string="Selected Vendor", compute="_compute_selected_vendor")

    vendors_with_bids = fields.Many2many("res.partner", string="Vendors with Bids", compute="_compute_vendors_with_bids")

    def action_create_purchase_request(self):
        for order in self:
            product_ids = [product.id for product in order.order_line]
            self.env['purchase.request'].create({
                # 'display_name': 'Request for ' + str(order.name),
                'name': 'Request ' + order.name,
                'employee_id': order.user_id.id,
                'order_id': order.id,
                'product_ids': [(6, 0, product_ids)]
            })
            # form_view_id = self.env.ref('custom_purchases.purchase_request_view_form').id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Purchase Request',
                'res_model': 'purchase.request',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.env['purchase.request'].search([('order_id', '=', order.id)], limit=1).id,
                # 'views': [(form_view_id, 'form')],
                'target': 'current',
            }

    @api.depends('offer_ids')
    def _compute_vendors_with_bids(self):
        for order_record in self:
            _vendor_ids = [offer_record.partner_id.id for offer_record in order_record.offer_ids]
            order_record.vendors_with_bids = [(6, 0, _vendor_ids)]

    @api.depends('offer_ids.status')
    def _compute_selected_vendor(self):
        for order_record in self:
            _selected = None
            for offer_record in order_record.offer_ids:
                if offer_record.status == 'accepted':
                    _selected = offer_record.partner_id
            order_record.selected_vendor = _selected

    @api.depends('offer_ids')
    def _compute_best_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_offer = max([offer.price for offer in record.offer_ids])
            else:
                record.best_offer = 0

    @api.depends("offer_ids")
    def _compute_number_of_offers(self):
        for record in self:
            record.number_of_offers = len(record.offer_ids)

    @api.onchange('vendor_ids')
    def _onchange_vendor_ids(self):
        '''
        set the first vendor in the list as the partner to avoid changing lots of code
        '''
        if self.vendor_ids:
            self.partner_id = self.vendor_ids[0]

    # Then manipulate all dependecies on partner_id
    def _compute_receipt_reminder_email(self):
        for order in self:
            order.receipt_reminder_email = True
            order.reminder_date_before_receipt = 1

    def button_confirm(self):
        '''
        Add validate: ensure that bid accepted
        set partner_id
        '''
        for order in self:
            if not order.selected_vendor:
                raise ValidationError("Please accept a Bid first before confirming order")
            if order.state not in ['draft', 'sent']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            for vendor_id in self.vendor_ids:
                if vendor_id not in order.message_partner_ids:
                    order.message_subscribe([vendor_id.id])
            order.partner_id = order.selected_vendor
        return True

    def _add_supplier_to_product(self):
        # Add the partner in the supplier list of the product if the supplier is not registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
        # could be caused for some generic products ("Miscellaneous").
        for line in self.order_line:
            # Do not add a contact as a supplier
            for vendor_id in self.vendor_ids:
                partner = vendor_id if not vendor_id.parent_id else vendor_id.parent_id
                already_seller = (partner | self.partner_id) & line.product_id.seller_ids.mapped('partner_id')
                if line.product_id and not already_seller and len(line.product_id.seller_ids) <= 10:
                    # Convert the price in the right currency.
                    currency = partner.property_purchase_currency_id or self.env.company.currency_id
                    price = self.currency_id._convert(
                        line.price_unit, currency, line.company_id, line.date_order or fields.Date.today(), round=False)
                    # Compute the price for the template's UoM, because the supplier's UoM is related to that UoM.
                    if line.product_id.product_tmpl_id.uom_po_id != line.product_uom:
                        default_uom = line.product_id.product_tmpl_id.uom_po_id
                        price = line.product_uom._compute_price(price, default_uom)

                    supplierinfo = self._prepare_supplier_info(partner, line, price, currency)
                    # In case the order partner is a contact address, a new supplierinfo is created on
                    # the parent company. In this case, we keep the product name and code.
                    seller = line.product_id._select_seller(
                        partner_id=line.partner_id,
                        quantity=line.product_qty,
                        date=line.order_id.date_order and line.order_id.date_order.date(),
                        uom_id=line.product_uom)
                    if seller:
                        supplierinfo['product_name'] = seller.product_name
                        supplierinfo['product_code'] = seller.product_code
                    vals = {
                        'seller_ids': [(0, 0, supplierinfo)],
                    }
                    # supplier info should be added regardless of the user access rights
                    line.product_id.product_tmpl_id.sudo().write(vals)

    def action_rfq_send(self):
        '''
        add vendors and composition_mode to context
        '''
        res = super(PurchaseOrder, self).action_rfq_send()
        res['context']['vendor_ids'] = [v.id for v in self.vendor_ids]
        return res
