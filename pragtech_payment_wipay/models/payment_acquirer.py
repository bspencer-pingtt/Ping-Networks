from odoo import models, api, fields, _
from odoo.http import request
from odoo.exceptions import Warning
import logging
import json
import requests
import datetime

_logger = logging.getLogger(__name__)


class TransferPaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('wipay', 'WiPay')])
    account_number = fields.Char('Account Number')

    @api.model
    def _get_wipay_urls(self, environment):
        """ WiPay URL """
        return {
            'wipay_form_url': 'https://tt.wipayfinancial.com/plugins/payments/request',
        }

    def wipay_get_form_action_url(self):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_wipay_urls(environment)['wipay_form_url']

    def wipay_form_generate_values(self, values):
        base_url = self.get_base_url()
        users = self.env['res.users'].search([('partner_id', '=', values['partner_id'])])
        environment = 'live' if self.state == 'enabled' else 'sandbox'
        wipay_tx_values = dict(values)
        wipay_tx_values.update({
            'wipay_account_number': self.account_number,
            'wipay_avs': '0',
            'wipay_country_code': users.company_id.country_id.code,
            'wipay_currency': users.company_id.currency_id.name,
            'wipay_environment': environment,
            'wipay_fee_structure': 'customer_pay',
            'wipay_method': 'credit_card',
            'wipay_order_id': values['reference'],
            'wipay_origin': users.company_id.name,
            'wipay_response_url': base_url + 'shop/payment/validate/',
            'wipay_total': "{:.2f}".format(values['amount']),
            'wipay_data': json.dumps({"wipay_order_transaction": "is_wipay_transaction"}),
        })
        return wipay_tx_values
