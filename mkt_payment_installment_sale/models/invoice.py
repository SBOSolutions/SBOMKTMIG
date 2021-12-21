from odoo import models, fields, api, _
from datetime import datetime, date, timedelta

class Installment_invoice(models.Model):
	_inherit = 'account.move'
	
	option = fields.Boolean(compute='get_vals')
	tenure_inv = fields.Float(string="Tenure(months)")
	installment_amount_inv = fields.Float(string="Installment Amount")
	down_payment_inv = fields.Float(string="Down Payment Amount")
	pay_date = fields.Date(string="First Payment Date")
	relation_ids = fields.One2many('notebook.invoice', 'inv_ids', string="Installment Invoice class")
	pay_ids = fields.One2many('account.payment.register', 'payment_ids', string="For Payment Wizard")
	soid = fields.Many2one('sale.order', string="For Sale order")
	difference_amount_inv = fields.Float(string="Difference Amount", default=0.00)
	total_amount_inv = fields.Float(string="Total Amount", compute='for_total')
	
	@api.depends('total_amount_inv', 'amount_total')
	def for_total(self):
		self.total_amount_inv = self.amount_total
	
	def get_vals(self):
		self.option = self.env['ir.config_parameter'].sudo().get_param('mkt_payment_installment_sale.installment_option')

	@api.depends('next_payment_date', 'tenure_inv', 'pay_date')
	def view_installments(self):
		ctx = self._context
		date = self.pay_date
		self.difference_amount_inv = round(self.total_amount_inv - (self.installment_amount_inv * self.tenure_inv) - self.down_payment_inv, 2)
		lines = []
		val = {
			'payment_status_inv': self.payment_state,
			'description_inv': "Installment",
			'amt_inv': self.installment_amount_inv + self.difference_amount_inv,
			'payment_date_inv': date
		}
		lines.append((0, 0, val))
		for months in range(2, int(self.tenure_inv) + 1):
			if self.pay_date:
				date += timedelta(days=30)
				val = {
					'payment_status_inv': self.payment_state,
					'description_inv': "Installment",
					'amt_inv': self.installment_amount_inv,
					'payment_date_inv': date
				}
				lines.append((0, 0, val))
		self.relation_ids = lines
		
	def action_register_payment(self):
		return {
			'name': _('Register Payment'),
			'res_model': 'account.payment.register',
			'view_mode': 'form',
			'context': {
				'installment_bool': False,
				'down_bool': False,
				'active_model': 'account.move',
				'active_ids': self.ids,
			},
			'target': 'new',
			'type': 'ir.actions.act_window',
		}
	
	def custom_action_register_payment(self, order_line):
		return {
			'name': _('Register Payment'),
			'res_model': 'account.payment.register',
			'view_mode': 'form',
			'context': {
				'note_ids': order_line,
				'installment_bool': True,
				'down_bool': False,
				'active_model': 'account.move',
				'active_ids': self.ids,
			},
			'target': 'new',
			'type': 'ir.actions.act_window',
		}

	def custom_action_register_payment1(self):
		return {
			'name': _('Register Payment'),
			'res_model': 'account.payment.register',
			'view_mode': 'form',
			'context': {
				'down_bool': True,
				'installment_bool': False,
				'active_model': 'account.move',
				'active_ids': self.ids,
			},
			'target': 'new',
			'type': 'ir.actions.act_window',
		}
	
class Notebook_Invoice(models.Model):
	_name = 'notebook.invoice'
	_description = 'Notebook for installment'
	
	inv_ids = fields.Many2one('account.move', string="Notebook Invoice class")
	payment_date_inv = fields.Date(string="Payment Date")
	payment_status_inv = fields.Selection([
		('draft', 'Draft'),
		('not_paid', 'Not Paid'),
		('in_payment', 'In Payment'),
		('paid', 'Paid'),
		('partial', 'Partially Paid'),
		('reversed', 'Reversed'),
		('invoicing_legacy', 'Invoicing App Legacy')
	], string='Payment Status')
	amt_inv = fields.Float(string="Amount")
	description_inv = fields.Char(string="Description")
	wizard_ids = fields.One2many('account.payment.register', 'note_ids', string="For Payment Wizard")

	def action_payment(self):
		order_line = self.id
		res = self.inv_ids.custom_action_register_payment(order_line)
		return res
