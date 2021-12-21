# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

import io
from datetime import datetime
from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ProductStockReport(models.TransientModel):
    _name = 'product.stock.report'

    end_date = fields.Datetime(string='End Date', required=True, default=datetime.now())
    location_id = fields.Many2one('stock.location', string="Location", required=True)
    category_id = fields.Many2one('product.category', string='Category', )
    season_id = fields.Many2one('res.season', string='Season', )
    product_tmpl_ids = fields.Many2many('product.template', string='Template',)
    vertical_id = fields.Many2one('product.attribute', string="Vertical")
    horizontal_id = fields.Many2one('product.attribute', string="Horizontal")

    # warning when select same variant
    @api.onchange('vertical_id', 'horizontal_id', 'category_id', 'product_tmpl_ids', 'season_id')
    def _onchange_product_var_id(self):
        if self.horizontal_id and self.vertical_id:
            if self.horizontal_id.id == self.vertical_id.id:
                raise UserError('Please Enter Different Variant.')

    def get_pdf_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'end_date': self.end_date,
                'location_id': self.location_id.id,
                'product_tmpl_ids': self.product_tmpl_ids.ids,
                'season_id':self.season_id.id,
                'category_id': self.category_id.id,
                'vertical_id': self.vertical_id.id,
                'horizontal_id': self.horizontal_id.id,
            }
        }
        return self.env.ref('bi_product_stocks_report.inventory_report').report_action(self, data=data)

    def _compute_quantities_product_quant_dic(self, lot_id, owner_id, package_id, from_date, to_date, product_obj):

        loc_list = []

        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_obj._get_domain_locations()
        custom_domain = []

        if self.location_id:
            custom_domain.append(('location_id', '=', self.location_id.id))

        domain_quant = [('product_id', 'in', product_obj.ids)] + domain_quant_loc + custom_domain

        dates_in_the_past = False


        if to_date.date() and to_date.date() < date.today():
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
        domain_move_in_todo = [('state', 'in',
                                ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
        domain_move_out_todo = [('state', 'in',
                                 ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in
                            Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'],
                                            orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in
                             Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'],
                                             orderby='id'))
        quants_res = dict((item['product_id'][0], item['quantity']) for item in
                          Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))

        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                     Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'],
                                                     orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                      Move.read_group(domain_move_out_done, ['product_id', 'product_qty'],
                                                      ['product_id'], orderby='id'))

        res = dict()
        for product in product_obj.with_context(prefetch_fields=False):
            product_id = product.id
            rounding = product.uom_id.rounding
            res[product_id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(product_id, 0.0) - moves_in_res_past.get(product_id,
                                                                                        0.0) + moves_out_res_past.get(
                    product_id, 0.0)
            else:
                qty_available = quants_res.get(product_id, 0.0)
            res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
            res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0),
                                                          precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0),
                                                          precision_rounding=rounding)
            res[product_id]['virtual_available'] = float_round(
                qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                precision_rounding=rounding)

        return res

    def generate_xls_report(self):
        filename = 'Product Stock Report.xls'
        workbook = xlwt.Workbook()
        stylePC = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        fontP = xlwt.Font()
        fontP.bold = True
        fontP.height = 200
        stylePC.font = fontP
        stylePC.num_format_str = '@'
        stylePC.alignment = alignment
        style_title = xlwt.easyxf(
            "font:height 300; font: name Liberation Sans, bold on; align: horiz center;pattern: pattern solid;")
        style_table_header = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
        style = xlwt.easyxf("font:height 200; font: name Liberation Sans,color black;")
        worksheet = workbook.add_sheet('Sheet 1')
        worksheet.write_merge(0, 1, 0, 12, "Product Stock Report", style_title)
        worksheet.write(3, 0, "End Date", style_table_header)
        worksheet.write(4, 0, self.end_date.strftime('%d-%m-%Y'))
        worksheet.write(3, 1, "Location", style_table_header)
        worksheet.write(4, 1, self.location_id.name)
        worksheet.write(3, 2, "Product Category", style_table_header)
        worksheet.write(4, 2, self.category_id.name)
        worksheet.write(3, 3, "Product Season", style_table_header)
        worksheet.write(4, 3, self.season_id.name)
        worksheet.write(6, 0, 'Product', style_table_header)

        c0 = 0
        c3 = 2
        c1 = 1
        r6 = 6
        v_r_7 = 7
        horizontal_list = []
        vertical_list = []
        header_val = []
        product_list = []
        template_dict = {}
        indexing_dict = {}
        pro_hor_list = []

        #  filter product with selected variant and category
        if self.season_id:
            product_template_obj = self.env['product.template'].search(
                [('attribute_line_ids.attribute_id', '=', self.horizontal_id.id),
                ('attribute_line_ids.attribute_id', '=', self.vertical_id.id), ('season_id', '=', self.season_id.id)])
        else:
            if not self.product_tmpl_ids:
                product_template_obj = self.env['product.template'].search(
                    [('attribute_line_ids.attribute_id', '=', self.horizontal_id.id),
                    ('attribute_line_ids.attribute_id', '=', self.vertical_id.id), ('categ_id', '=', self.category_id.id)])
            else:
                product_template_obj = self.product_tmpl_ids

        for p in product_template_obj:
            flag = True
            pro_ver_list = []
            for att_line in p.attribute_line_ids:
                for att_val in att_line.value_ids:

                    if att_val.attribute_id == self.horizontal_id:
                        if att_val.name not in header_val:
                            worksheet.write(r6, c3, att_val.name)
                            pro_hor_list.append((att_val.id, c3))
                            c3 = c3 + 1
                            horizontal_list.append(att_val.id)
                            header_val.append(att_val.name)
                    if att_val.attribute_id == self.vertical_id:
                        worksheet.write(v_r_7, c1, att_val.name)
                        pro_ver_list.append((att_val.id, v_r_7))
                        if att_val.id not in vertical_list:
                            vertical_list.append(att_val.id)
                        if flag == True:
                            worksheet.write(v_r_7, c0, p.name)
                            flag = False
                            product_list.append(p.id)
                        v_r_7 = v_r_7 + 1

            template_dict[p.id] = {'horizontal_list': horizontal_list, 'vertical_list': vertical_list}
            indexing_dict[p.id] = {'pro_ver_list': pro_ver_list}

        # template_dict for matched with variant and product in stock.quant
        for product in template_dict:

            for hor in template_dict[product]['horizontal_list']:

                for ver in template_dict[product]['vertical_list']:

                    att_final_val = [hor, ver]
                    varient = self.env['product.product'].search([('product_tmpl_id', '=', product)])

                    for pro_v in varient:

                        if hor in [i.product_attribute_value_id.id for i in pro_v.product_template_attribute_value_ids] and ver in [i.product_attribute_value_id.id for i in pro_v.product_template_attribute_value_ids]:
                            quant_obj = self.env['stock.quant'].search(
                                [('location_id', '=', self.location_id.id), ('product_id', '=', pro_v.id)])
                            total = 0
                            for quant in quant_obj:
                                total = total + quant.quantity
                            for r in indexing_dict[product]['pro_ver_list']:

                                if r[0] == ver:
                                    row_v = r[1]

                            for c in pro_hor_list:
                                if c[0] == hor:
                                    col_v = c[1]

                            quantity_p = self._compute_quantities_product_quant_dic(self._context.get('lot_id'),
                                                                                    self._context.get('owner_id'),
                                                                                    self._context.get('package_id'),
                                                                                    False, self.end_date, pro_v)

                            worksheet.write(row_v, col_v, quantity_p[pro_v.id]['qty_available'])

        fp = io.BytesIO()
        workbook.save(fp)

        export_id = self.env['stock.excel.report'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        res = {'view_mode': 'form',
               'res_id': export_id.id,
               'name': 'Stock Rotation Report',
               'res_model': 'stock.excel.report',
               'view_type': 'form',
               'type': 'ir.actions.act_window',
               'target': 'new'
               }
        return res


class StockExcelReport(models.TransientModel):
    _name = "stock.excel.report"

    excel_file = fields.Binary('Download Excel Report', readonly=True)
    file_name = fields.Char('File', readonly=True)

