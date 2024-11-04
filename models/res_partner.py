from odoo import api, fields, models


class Vendor(models.Model):
    _inherit = "res.partner"

    rfq_ids = fields.Many2one("purchase.order", string="RFQs")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        '''
        Only list vendors who are attached to the RFQ
        '''
        results = super(Vendor, self).name_search(name, args=args, operator=operator, limit=limit)

        if self.env.context.get('name', None) != 'offer_ids.partner_id':
            return results

        valid_vendor_ids = self.env.context.get('valid_vendor_ids', None)

        vendors_with_bids = self.env.context.get('vendors_with_bids', None)

        new_results = []
        if valid_vendor_ids:
            for partner in results:
                if partner[0] in valid_vendor_ids and partner[0] not in vendors_with_bids:
                    new_results.append(partner)
            return new_results
        return results
