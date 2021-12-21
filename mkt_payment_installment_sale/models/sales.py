from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import calendar


class Installment_Sale(models.Model):
	_inherit = 'sale.order'

	option = fields.Boolean(compute='get_vals')
	installment_yesno = fields.Boolean(string='Installment')

	total_amount = fields.Float(string="Total Amount", compute='for_total')
	tenure = fields.Float(string="Tenure(months)")
	number = fields.Float(string="No")
	down_payment = fields.Float(string="Down Payment")
	payable_amount = fields.Float(string="Payable Amount", compute='for_payable')
	installment_amount = fields.Float(string="Installment Amount", compute='for_installment_amount')
	next_payment_date = fields.Date(string="Next Payment Date")
	notebook_ids = fields.One2many('notebook.class', 'installment_ids', string="Installment Sale class")
	difference_amount = fields.Float(string="Difference Amount", default = 0.00)
	installment_status = fields.Selection(string='Installment Status', selection=[('new', 'New'), ('generate', 'Generate'), ('sent', 'Sent'),('received', 'Received'),], tracking=True)
	installment_send_date = fields.Date(string='Installment send date')

	@api.onchange('payment_term_id')
	def setInstallment(self):
		self.installment_yesno = self.payment_term_id.installment_yesno

	@api.onchange('installment_yesno')
	def setPaymentTerm(self):
		if self.installment_yesno:
			if not self.installment_status:
				self.installment_status = "new"

	def action_generate_installment_test(self):
		for order in self:
			if order.installment_yesno and order.state in 'sale' and order.installment_status == 'new' and order.amount_total != 0 and order.commitment_date:
				print("Order: ",order.id)
				#define month pace
				month_pace = 0
				if order.amount_total <= 1000:
					month_pace = 1
				if order.amount_total > 1000 and order.amount_total <=6000:
					month_pace = 2
				if order.amount_total > 6000 and order.amount_total <=12000:
					month_pace = 3
				if order.amount_total > 12000:
					month_pace = 4
				order.tenure = month_pace
				order.next_payment_date = order.commitment_date + timedelta(30)
				date = order.next_payment_date
				lines = list()
				order.difference_amount = round(order.total_amount - (order.installment_amount * order.tenure) - order.down_payment, 2)
				val = {
					'description': "Plan de financement",
					'amt': order.installment_amount + order.difference_amount,
					'payment_date': date
				}
				lines.append((0, 0, val))
				for months in range(2, int(order.tenure) + 1):

					if order.next_payment_date:
						date += timedelta(days=30)
						val = {
							'description': "Plan de financement",
							'amt': order.installment_amount,
							'payment_date': date
						}
						lines.append((0, 0, val))
				order.notebook_ids = lines
				order.installment_status = "generate"

	@staticmethod
	def get_payment_date(oder_date):
		day = 15
		if oder_date.day > 15:
			day = calendar.monthrange(oder_date.year, oder_date.month)[1]

		return datetime(oder_date.year, oder_date.month, day).date()

	@staticmethod
	def generate_plf_description(order, cpt):
		return 'PF - ' + str(order.name or '') + ' - ' + str(order.season_id.name or '') + ' - ' + str(cpt)

	# generate function for PLF from customer rules
	def action_generate_installment(self):
		cpt = 1
		for order in self:
			print("Begin :", order.id)
			if order.installment_yesno and order.state in 'sale' and order.installment_status == 'new':
				if order.amount_total == 0:
					raise UserError('Generation plf impossible pas de montant')
				elif not order.commitment_date:
					raise UserError('La date de livraison n\'est pas saisie')
				else:
					print("Good lets generate : ",order.id )
					month_pace = 0
					if order.amount_total <= 1000:
						month_pace = 1
					if order.amount_total > 1000 and order.amount_total <=6000:
						month_pace = 2
					if order.amount_total > 6000 and order.amount_total <=12000:
						month_pace = 3
					if order.amount_total > 12000:
						month_pace = 4
					if not order.tenure:
						order.tenure = month_pace
						order.next_payment_date = order.commitment_date + timedelta(30)
					# Round 15 or Max day from month from next_payment_date
					payment_date = order.get_payment_date(order.next_payment_date)
					lines = list()
					order.difference_amount = round(order.total_amount - (order.installment_amount * order.tenure) - order.down_payment, 2)
					description = order.generate_plf_description(order, cpt)
					val = {
						'description': description,
						'amt': order.installment_amount + order.difference_amount,
						'payment_date': payment_date
					}
					lines.append((0, 0, val))
					for months in range(2, int(order.tenure) + 1):
						cpt += 1
						description = order.generate_plf_description(order, cpt)
						if order.next_payment_date:
							payment_date += timedelta(days=25)
							payment_date = order.get_payment_date(payment_date)
							val = {
								'description': description,
								'amt': order.installment_amount,
								'payment_date': payment_date
							}
							lines.append((0, 0, val))
					order.notebook_ids = lines
					order.installment_status = "generate"
				return
			else:
				raise UserError('Pas de plan a générer, déja généré ou vous êtes en devis.')
				return

	def action_plf_send_by_email(self):
		for record in self:
			if record.installment_yesno:
				template_id = record.env.ref('mkt_payment_installment_sale.email_template_send_plf')
				record.message_post_with_template(template_id.id)
				record.installment_status = 'sent'
				record.installment_send_date = datetime.today()

	def action_plf_generate_payment(self):
		for record in self.notebook_ids:
			new_ap = self.env['account.payment'].create({
				'payment_type': 'inbound',
				'partner_type': 'customer',
				'partner_id': self.partner_id.id,
				'company_id': self.company_id.id,
				'journal_id': self.company_id.journal_PLF_id.id,
				'amount': record.amt,
				'date': record.payment_date,
				'ref': record.description
			})

			new_ap.action_post()

		self.installment_status = 'received'

	def receipts_plf(self):
		for record in self:
			record.installment_status = 'received'

	def action_plf_send_reminder_by_mail(self):
		if self.installment_yesno and self.installment_status == 'sent':
			template_id = self.env.ref('mkt_payment_installment_sale.email_template_send_plf_reminder')
			self.message_post_with_template(template_id.id)

	def get_vals(self):
		self.option = self.env['ir.config_parameter'].sudo().get_param('mkt_payment_installment_sale.installment_option')

	@api.depends('total_amount', 'amount_total')
	def for_total(self):
		for order in self:
			order.total_amount = order.amount_total

	@api.depends('payable_amount', 'down_payment', 'total_amount')
	def for_payable(self):
		for order in self:
			order.payable_amount = order.total_amount - order.down_payment

	@api.depends('installment_amount', 'payable_amount', 'tenure')
	def for_installment_amount(self):
		for order in self:
			if order.tenure:
				order.installment_amount = round(order.payable_amount / order.tenure, 2)
			else:
				order.installment_amount = 0.00

#SBO comment : don't understand purpose, lack of fields ?
	# @api.onchange('payment_installment_inv')
	# def compute_payment_status(self):
	# 	lines = []
	# 	val = {
	# 		'payment_status': 'payment_status_inv'
	# 	}
	# 	lines.append((1, 0, val))
	# 	self.notebook_ids = lines

	def _prepare_invoice(self):
		res = super(Installment_Sale, self)._prepare_invoice()

		res['tenure_inv'] = self.tenure
		res['installment_amount_inv'] = self.installment_amount
		res['pay_date'] = self.next_payment_date
		res['down_payment_inv'] = self.down_payment
		return res

class NotebookClass(models.Model):
	_name = 'notebook.class'
	_description = 'Notebook for installment'

	installment_ids = fields.Many2one('sale.order', string="Notebook Class")
	payment_date = fields.Date(string="Payment Date")
	amt = fields.Float(string="Amount")
	description = fields.Char(string="Description")

class For_options(models.TransientModel):
	_inherit = 'res.config.settings'

	installment_option = fields.Boolean(string="Installments", default = False)

	def set_values(self):
		res = super(For_options, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('mkt_payment_installment_sale.installment_option', self.installment_option)
		return res

	def get_values(self):
		res = super(For_options, self).get_values()
		installment_option = bool(self.env['ir.config_parameter'].get_param('mkt_payment_installment_sale.installment_option'))
		res.update({
			'installment_option': installment_option
		})
		return res
	

