# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import date,timedelta,datetime
from odoo.tools.float_utils import float_round

class ReportInventoryCoverage(models.AbstractModel):
    _name = 'report.bi_product_stocks_report.template_report'
    _description = " Report"




    def _compute_quantities_product_quant_dic(self,lot_id, owner_id, package_id,from_date,to_date,product_obj,location):

        loc_list = []

        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_obj._get_domain_locations()
        custom_domain = []


        if location :
            custom_domain.append(('location_id','=',location.id))



        domain_quant = [('product_id', 'in', product_obj.ids)] + domain_quant_loc + custom_domain
        dates_in_the_past = False





        todate_date =  datetime.strptime(to_date,"%Y-%m-%d %H:%M:%S").date()
        if to_date and todate_date < date.today():

            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', product_obj.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', product_obj.ids)] + domain_move_out_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            domain_move_in += [('date', '>=', from_date)]
            domain_move_out += [('date', '>=', from_date)]
        if to_date:
            domain_move_in += [('date', '<=', to_date)]
            domain_move_out += [('date', '<=', to_date)]

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
        domain_move_out_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        quants_res = dict((item['product_id'][0], item['quantity']) for item in Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))

        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

        res = dict()
        for product in product_obj.with_context(prefetch_fields=False):
            product_id = product.id
            rounding = product.uom_id.rounding
            res[product_id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(product_id, 0.0) - moves_in_res_past.get(product_id, 0.0) + moves_out_res_past.get(product_id, 0.0)
            else:
                qty_available = quants_res.get(product_id, 0.0)
            res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
            res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['virtual_available'] = float_round(
                qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                precision_rounding=rounding)




        return res
    @api.model
    def _get_report_values(self, docids, data=None):
        end_date = data['form']['end_date']
        location = data['form']['location_id']
        category =  data['form']['category_id']
        season_id =  self.env['res.season'].browse(data['form']['season_id'])
        product_tmpl_ids =  data['form']['product_tmpl_ids']
        vertical= data['form']['vertical_id']
        horizontal = data['form']['horizontal_id']
        location_id = self.env['stock.location'].browse(location)
        category_id = self.env['product.category'].browse(category)
        product_tmpl_ids = self.env['product.template'].browse(product_tmpl_ids)
        vertical_id = self.env['product.attribute'].browse(int(vertical))
        horizontal_id = self.env['product.attribute'].browse(int(horizontal))

        horizontal_list =[]
        vertical_list = []
        if not product_tmpl_ids:
            product_template_obj = self.env['product.template'].search([('attribute_line_ids.attribute_id','=',horizontal_id.id),('attribute_line_ids.attribute_id','=',vertical_id.id),('season_id','=',season_id.id)])
        else:
            product_template_obj = product_tmpl_ids
        header_val = []
        product_list = []

        template_dict = {}
        pro_hor_list = []
        product_dict = {}
        for product_template in product_template_obj:
            flag = True
            for att_line in product_template.attribute_line_ids:
                for att_val in att_line.value_ids:

                    if att_val.attribute_id == horizontal_id:
                        if att_val.name not in header_val :
                            horizontal_list.append(att_val.id)
                            header_val.append(att_val.name)

                    if att_val.attribute_id == vertical_id:
                        if att_val.id not in vertical_list :
                            
                            vertical_list.append(att_val.id)
                        if flag == True:
                            flag = False
                            product_list.append(product_template.id)

            template_dict[product_template.id] = {'horizontal_list' : horizontal_list,'vertical_list' : vertical_list}

            product_dict={'product_list':product_list,'horizontal_list' : horizontal_list,'vertical_list' : vertical_list}
 
        for product in template_dict:
            for hor in template_dict[product]['horizontal_list'] :

                for ver in template_dict[product]['vertical_list'] :
                    att_final_val = [hor,ver]
                    varient = self.env['product.product'].search([('product_tmpl_id','=',product)])
                    for pro_v in varient :
                        if hor in [i.product_attribute_value_id.id for i in pro_v.product_template_attribute_value_ids] and ver in [i.product_attribute_value_id.id for i in pro_v.product_template_attribute_value_ids]:
                            quant_obj = self.env['stock.quant'].search([('location_id','=',location_id.id),('product_id','=',pro_v.id)])
                            total = 0

        hor1 = horizontal_list
        product_list = product_list
        v_list = vertical_list

        ver_product_data = []
        for pro_temp in product_template_obj:

            border_data = [True,True]
            for hor_bor in self.env['product.attribute.value'].browse(hor1) :
                border_data.append(True)

            ver_product_data.append(border_data)

            product_ver = self.env['product.product'].search([('product_tmpl_id','=',pro_temp.id)])

            flag = True
            filter_value_ids = pro_temp.attribute_line_ids.mapped('value_ids').filtered(lambda v: v.attribute_id == vertical_id )
            for line in filter_value_ids:


                if flag == True:
                    ver_data = [pro_temp.name,line.name]
                    flag = False

                else :
                    ver_data = ['  ',line.name]
                for hor in self.env['product.attribute.value'].browse(hor1) :

                    for pro in product_ver :
                        if hor.id in [i.product_attribute_value_id.id for i in pro.product_template_attribute_value_ids] and line.id in [i.product_attribute_value_id.id for i in pro.product_template_attribute_value_ids]:

                            quant_obj = self.env['stock.quant'].search([('location_id','=',location_id.id),('product_id','=',pro.id)])
                            quantity_p = self._compute_quantities_product_quant_dic(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'),False,end_date,pro,location_id)

                            total = quantity_p[pro.id]['qty_available']
                            ver_data.append(total)
                ver_product_data.append(ver_data)

        return {
        'v_list':self.env['product.attribute.value'].browse(v_list),
        'product_list':self.env['product.template'].browse(product_list),
        'h_list':self.env['product.attribute.value'].browse(hor1),
        'doc_ids': data['ids'],
        'doc_model': data['model'],
        'end_date':end_date,
        'location_id':location_id.display_name,
        'season_id':season_id.name,
        'product_tmpl_ids':product_template_obj.mapped('name'),
        'ver_data' : ver_product_data,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: