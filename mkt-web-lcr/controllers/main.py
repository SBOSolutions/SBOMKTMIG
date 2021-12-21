# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo.addons.base_iban.models.res_partner_bank import validate_iban
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.base.models.res_bank import sanitize_account_number

import base64
import logging

logger = logging.getLogger(__name__)


class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/payment/transaction/',
                 '/shop/payment/transaction/<int:so_id>',
                 '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public",
                website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, web_other_comment=None, **kwargs):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.

        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """
        # Ensure a payment acquirer is selected
        if not acquirer_id:
            return False

        try:
            acquirer_id = int(acquirer_id)
        except:
            return False

        # Retrieve the sale order
        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()

        # Ensure there is something to proceed
        if not order or (order and not order.order_line):
            return False

        assert order.partner_id.id != request.website.partner_id.id
        # Create transaction
        vals = {'acquirer_id': acquirer_id,
                'return_url': '/shop/payment/validate'}

        if save_token:
            vals['type'] = 'form_save'
        if token:
            vals['payment_token_id'] = int(token)

        transaction = order._create_payment_transaction(vals)

        # store the new transaction into the transaction list and if there's an old one, we remove it
        # until the day the ecommerce supports multiple orders at the same time
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentProcessing.remove_payment_transaction(last_tx)
        PaymentProcessing.add_payment_transaction(transaction)
        request.session['__website_sale_last_tx_id'] = transaction.id
        if web_other_comment:
            sub_type_note_record = request.env['mail.message.subtype'].search([('name', '=', 'Note')])[0]
            user_connected = request.env['res.users'].browse(request.env.context.get('uid'))
            request.env['mail.message'].create({
                'author_id': user_connected.partner_id.id,
                'message_type': 'comment',
                'subtype_id': sub_type_note_record.id,
                'model': 'sale.order',
                'res_id': order.id,
                'record_name': order.name,
                'body': 'Commentaire de la commande : ' + web_other_comment
            })
        return transaction.render_sale_button(order)

    def _get_shop_payment_values(self, order, **kwargs):
        values = super(WebsiteSaleInherit, self)._get_shop_payment_values(order, **kwargs)
        values['user_connected'] = request.env['res.users'].browse(request.env.context.get('uid'))
        return values

    @http.route('/delete_web_rib', type='http', auth='public', website=True, sitemap=False)
    def delete_web_rib_file(self, **kwargs):
        user_connected = request.env['res.users'].browse(request.env.context.get('uid'))
        user_connected.web_rib_name = ''
        user_connected.web_rib = False
        return request.redirect('/shop/payment')

    @http.route('/download_web_rib', type='http', auth='public', website=True, sitemap=False)
    def download_web_rib_file(self, **kwargs):
        user_connected = request.env['res.users'].browse(request.env.context.get('uid'))
        filecontent = base64.b64decode(user_connected.web_rib or '')

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(filecontent)),
            ('Content-Disposition', 'attachment; filename=' + user_connected.web_rib_name)
        ]
        return request.make_response(filecontent, headers=pdfhttpheaders)

    def generate_bank_account(self, user_connected, sanitize, code_swift, company_id, is_company=False):
        create_bank = True
        if request.env['res.partner.bank'].sudo().search([('acc_number', '=', sanitize)]):
            create_bank = False
        for bank in user_connected.bank_ids:
            if sanitize == bank.sanitized_acc_number:
                create_bank = False
            if bank.bank_id.filtered(lambda r: r.bic == code_swift):
                create_bank = False
        if create_bank:
            # Search bank code swift exist
            bank_id = request.env['res.bank'].sudo().search([('bic', '=', code_swift)], limit=1)
            if not bank_id:
                bank_id = request.env['res.bank'].sudo().create({
                    'name': 'A définir',
                    'bic': code_swift
                })

            vals = {
                'acc_number': sanitize,
                'acc_type': 'iban',
                'bank_id': bank_id.id,
                'partner_id': user_connected.id if is_company else user_connected.partner_id.id
            }
            if company_id:
                vals['company_id'] = company_id.id
            request.env['res.partner.bank'].sudo().create(vals)

    @http.route('/shop/payment/token', type='http', auth='public', website=True, sitemap=False)
    def payment_token(self, pm_id=None, **kwargs):
        """ Method that handles payment using saved tokens

        :param int pm_id: id of the payment.token that we want to use to pay.
        """

        user_connected = request.env['res.users'].browse(request.env.context.get('uid'))
        if kwargs.get('web_iban', False) and user_connected and kwargs.get('web_iban', False) != user_connected.web_iban:
            user_connected.web_iban = kwargs.get('web_iban', False)
        if kwargs.get('web_bic_swift', False) and user_connected and kwargs.get('web_bic_swift', False) != user_connected.web_bic_swift:
            user_connected.web_bic_swift = kwargs.get('web_bic_swift', False)
        if kwargs.get('web_rib', False) and user_connected:
            file = kwargs.get('web_rib', False)
            try:
                mimetype = file.content_type
                attachment_value = {
                    'name': file.filename,
                    'datas': base64.encodebytes(file.read()),
                    'res_model': 'res.users',
                    'res_id': user_connected.id,
                    'res_field': 'web_rib',
                    'mimetype': mimetype,
                }
                attachment = request.env['ir.attachment'].sudo().create(attachment_value)
                if attachment:
                    user_connected.web_rib = attachment.datas
                    user_connected.web_rib_name = attachment.name

            except Exception as e:
                logger.exception("Fail to upload document %s" % file.filename)
                result = {'error': str(e)}
        # Create bank account for user
        if kwargs.get('web_iban', False) and user_connected and kwargs.get('web_bic_swift', False):
            sanitize = sanitize_account_number(kwargs.get('web_iban', False))
            if not user_connected.parent_id:
                self.generate_bank_account(user_connected, sanitize, kwargs.get('web_bic_swift', False), user_connected.company_id)
            if user_connected.parent_id:
                self.generate_bank_account(user_connected.parent_id, sanitize, kwargs.get('web_bic_swift', False), user_connected.company_id,  True)

        order = request.website.sale_get_order()
        # do not crash if the user has already paid and try to pay again
        if not order:
            return request.redirect('/shop/?error=no_order')

        assert order.partner_id.id != request.website.partner_id.id

        try:
            pm_id = int(pm_id)
        except ValueError:
            return request.redirect('/shop/?error=invalid_token_id')

        # We retrieve the token the user want to use to pay
        if not request.env['payment.token'].sudo().search_count([('id', '=', pm_id)]):
            return request.redirect('/shop/?error=token_not_found')

        # Create transaction
        vals = {'payment_token_id': pm_id, 'return_url': '/shop/payment/validate'}

        tx = order._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(tx)
        # Get LCR payment mode
        payment_lcr_mode = request.env['account.payment.mode'].search([('payment_method_code', '=', 'fr_lcr')])
        if len(payment_lcr_mode) > 1:
            payment_lcr_mode = request.env['account.payment.mode'].search([('payment_method_code', '=', 'fr_lcr')])[0]
        if not order.payment_mode_id:
            order.payment_mode_id = payment_lcr_mode.id

        return request.redirect('/payment/process')


    @http.route('/payment/lcr/new', type="json", auth="public", website=True)
    def create_lcr(self, **kwargs):
        if not kwargs.get('partner_id'):
            kwargs = dict(kwargs, partner_id=request.env.user.partner_id.id)
        acquirer = request.env['payment.acquirer'].browse(int(kwargs.get('acquirer_id')))
        token = acquirer.s2s_process(kwargs)

        return {
            'result': True,
            'id': token.id,
            'short_name': 'short_name',
            '3d_secure': False,
            'verified': True,
        }



