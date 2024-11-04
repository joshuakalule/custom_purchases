from odoo import models
from markupsafe import Markup


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'
    _description = 'Email composition wizard to allow sending to multiple partners'

    def _compute_partner_ids(self):
        '''
        Add partners from the context key 'vendor_ids'
        '''
        super(MailComposer, self)._compute_partner_ids()
        for composer in self:
            vendor_ids = self.env.context.get('vendor_ids', False)
            composer.partner_ids = self.env['res.partner'].browse(vendor_ids)

    def _compute_body(self):
        '''
        Manipulate the body of the email
        '''
        super(MailComposer, self)._compute_body()

        body_template = '<div style="margin: 0px; padding: 0px;">\n    <p style="margin: 0px; padding: 0px; font-size: 13px;">\n        Greetings,\n        <br/><br/>\n        Here is in attachment a request for quotation <span style="font-weight:bold;">{}</span>\n        from your Company.\n        <br/><br/>\n        If you have any questions, please do not hesitate to contact us.\n        <br/><br/>\n        Best regards,\n            <br/><br/>\n            <span data-o-mail-quote="1">-- <br data-o-mail-quote="1">{}</span>\n    </p>\n</div>'

        for composer in self:
            model_id = self.env.context.get('active_id')
            order = self.env['purchase.order'].browse(model_id)
            order_name = order.name
            body_str = body_template.format(order_name, self.env.user.name)
            composer.body = Markup(body_str)
