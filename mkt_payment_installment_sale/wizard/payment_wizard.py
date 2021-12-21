from odoo import models, fields, api, _
import datetime

class Payment_wizard(models.TransientModel):
	_inherit = 'account.payment.register'
	
	payment_ids = fields.Many2one('account.move', string="For Invoice class")
	note_ids = fields.Many2one('notebook.invoice', string="For Notebook class")
	option = fields.Boolean(compute='get_vals')
	down_bool = fields.Boolean(default=False)
	installment_bool = fields.Boolean(default=False)
	
	def get_vals(self):
		self.option = self.env['ir.config_parameter'].sudo().get_param('mkt_payment_installment_sale.installment_option')
	
	def _compute_amount(self):
		res = super(Payment_wizard, self)._compute_amount()
		rec = self.env['account.move'].browse(self.env.context.get('active_ids'))
		val1 = self._context['installment_bool']
		val2 = self._context['down_bool']
		if val1:
			vals = self._context['note_ids']
			record = self.env['notebook.invoice'].search([('id', '=', vals)])
			self.amount = record.amt_inv
			return res
		elif val2:
			self.amount = rec.down_payment_inv
			return res
		else:
			return res
	
	def action_create_payments(self):
		res = super(Payment_wizard, self).action_create_payments()
		val1 = self._context['installment_bool']
		if val1:
			val2 = self._context['note_ids']
			relation = self.env['notebook.invoice'].search([])
			for r in relation:
				if r.id == val2:
					r.write({'payment_status_inv': 'paid'})
		return res
