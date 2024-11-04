## Notes about the purchase module

## MailHog

##
It seems like sending mass mails requires composition_mode set to mass_mail

In Odoo, the `MailComposer` model from the `mail_compose_message.py` file is used to prepare and send mail messages, including notifications and email communications. To send mass mail, you can use the `mail.compose.message` model along with the `send_mail` method to batch-send emails.

Here’s a guide to use `MailComposer` in the context of sending a mass email:

### Step 1: Set Up MailComposer in Your Python Code
Create an instance of the `mail.compose.message` model and prepare the data for sending emails.

### Example Code

```python
from odoo import models, api

class MailComposerMassMail(models.Model):
    _inherit = 'mail.compose.message'

    @api.model
    def send_mass_mail(self, recipient_ids, subject, body, model, res_id):
        # Prepare the context with message details
        context = dict(
            self.env.context,
            default_composition_mode='mass_mail',  # Set mode to mass mail
            default_use_template=False,
            default_model=model,
            default_res_id=res_id,
            default_subject=subject,
            default_body=body,
        )

        # Create a composer object with the specified context
        composer = self.env['mail.compose.message'].with_context(context).create({
            'subject': subject,
            'body': body,
            'model': model,
            'res_id': res_id,
        })

        # Send the email to all specified recipients
        composer.write({'partner_ids': [(6, 0, recipient_ids)]})  # Set recipient IDs
        composer.send_mail()  # Send the email

```

### Explanation of the Code
1. **Set Up Context**: Context options include setting the mode to `mass_mail`, indicating that it’s a bulk operation.
2. **Create the Composer Object**: Initialize `mail.compose.message` with the context you set up, providing it with message details (like `subject`, `body`, etc.).
3. **Set Recipients**: The `partner_ids` field is set to contain the recipient IDs.
4. **Send the Email**: `send_mail()` is called on the `composer` object to initiate sending the mass mail.

### Using the Code
After setting up the above method, you can call `send_mass_mail` with the required parameters like this:

```python
# Sample call
recipient_ids = [1, 2, 3]  # List of recipient partner IDs
subject = "Newsletter"
body = "<p>This is a newsletter for all customers</p>"
model = 'res.partner'  # Model to associate the mail with
res_id = 1  # A record ID for reference

# Call the method
self.env['mail.compose.message'].send_mass_mail(recipient_ids, subject, body, model, res_id)
```

### Additional Notes
- Ensure `recipient_ids` corresponds to the partner IDs in Odoo.
- `res_id` and `model` should relate to a specific record and model, which could be `res.partner`, `sale.order`, or any other model in your use case.
- You can also extend this to use email templates by setting `default_use_template=True` in the context if needed.
