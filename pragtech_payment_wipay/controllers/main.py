import logging
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from datetime import datetime
from odoo.addons.payment.controllers.portal import PaymentProcessing

_logger = logging.getLogger(__name__)


class WebsiteSaleDigitalConfirmation(WebsiteSale):

    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def payment_validate(self, odoo_transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if 'message' in post and post.get('message'):
            _logger.info('WIPAY RESPONSE MESSAGE ::::  %s', post.get('message'))

        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if odoo_transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(odoo_transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        # /////////////////////////////////////////////////////////////////////////////////
        request.session['wipay_response'] = False
        if 'data' in post and 'wipay_order_transaction' in post.get('data'):

            pay_transaction = request.env['payment.transaction'].sudo().search(
                [('sale_order_ids', 'in', [order.id])])
            if pay_transaction:
                tx = max(pay_transaction)
            if not order or (order.amount_total and not tx):
                return request.redirect('/shop')

            if post.get('status') == 'success':
                # Transaction created successfully in WiPay
                tx.acquirer_reference = post.get('transaction_id')
                tx.date = datetime.now()
                tx.state = 'done'
                tx.state_message = post.get('message')
                order.action_confirm()
            elif post.get('status') == 'failed':
                # Transaction failed in WiPay
                tx.acquirer_reference = post.get('transaction_id')
                tx.date = datetime.now()
                tx.state = 'cancel'
                tx.state_message = post.get('message')
                request.session['wipay_response'] = post.get('message')
                if tx and tx.state == 'cancel':
                    return request.redirect('/shop/payment')

        # /////////////////////////////////////////////////////////////////////////////////

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if order and not order.amount_total and not tx:
            order.with_context(send_email=True).action_confirm()
            return request.redirect(order.get_portal_url())

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        PaymentProcessing.remove_payment_transaction(tx)
        return request.redirect('/shop/confirmation')

    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
        payment.acquirer. State at this point :

         - a draft sales order with lines; otherwise, clean context / session and
           back to the shop
         - no transaction in context / session, or only a draft one, if the customer
           did go to a payment.acquirer website but closed the tab without
           paying / canceling
        """
        order = request.website.sale_get_order()
        if request.session.get('wipay_response') == 'False' or request.session.get('wipay_response') == None or not request.session.get(
                'wipay_response'):
            redirection = self.checkout_redirection(order)
            if redirection:
                return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False

        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')

        if request.session.get('wipay_response'):
            if 'return_url' in render_values and render_values['return_url'] == '/shop/payment/validate':
                render_values.update({'return_url': ''})
            render_values.update({'wipay_response': request.session.get('wipay_response')})

        if 'wipay_response' in request.session:
            del request.session['wipay_response']

        return request.render("website_sale.payment", render_values)
