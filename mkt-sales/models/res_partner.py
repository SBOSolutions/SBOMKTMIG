# -*- coding: utf-8 -*-

from odoo import models, fields, api

    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_code_texas = fields.Char(string='Code client', help="Code client de l'ancien system TEXAS, ...")
    customer_code_sage = fields.Char(string='Code client Compta', help="Code client de la compta sage, ...")
    credit_insurance_number = fields.Char(string='N° assurance crédit')
    store_code = fields.Char(string='Code dépot')
    carrier_code = fields.Char(string='Code Transporteur')
    main_contact_name = fields.Char(string='Contact principal')
    brand = fields.Char(string='Marque')
    status = fields.Selection(string='Status', selection=[('open', 'Ouvert'), ('block', 'Bloqué'),])
    payment_by = fields.Selection(string='Paiement par', selection=[('check','Chèque'),('plv30','PLV 30J'),('LCR','LCR'),
                                ('VIR','Virement'),('mandat','Mandat Administratif'),('check_ech','Chèque à échéance'),('cb','Carte bleue'),], help="methode de paiement")



    rib_code_banque = fields.Char(string='Code banque')
    rib_code_guichet = fields.Char(string='Code guichet')
    rib_compte = fields.Char(string='N° de compte')
    rib_cle = fields.Char(string='Cle')
    rib_code_bic = fields.Char(string='Code bic')

    
    sepa_iban = fields.Char(string='IBAN')
    sepa_rum = fields.Char(string='RUM')
    sepa_creation_date = fields.Date(string='Date de création')
    
    
    
