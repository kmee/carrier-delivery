# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author: Michell Stuttgart <michell.stuttgart@kmee.com.br>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.report import report_sxw
from openerp import pooler


class PLPReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(PLPReport, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({'get_post_services': self._get_post_services})

    def _get_post_services(self, uid, ids, context=None):

        cr = self.cr
        pool = pooler.get_pool(self.cr.dbname)
        plp = pool.get('shipping.response').browse(cr, uid, ids, context=context)

        packs = plp.tracking_pack_line
        services = {}

        for p in packs:
            picking = p.move_ids[0].picking_id
            serv = picking.carrier_id.sigepweb_post_service_id

            if serv.id not in services:
                services[serv.id] = {}
                services[serv.id]['name'] = serv.name
                services[serv.id]['code'] = serv.code
                services[serv.id]['quant'] = 0

            services[serv.id]['quant'] += 1

        return services
        #
        # barcode_vals = {
        #     'code': plp.carrier_tracking_ref,
        #     'res_id': plp.id,
        #     'barcode_type': 'Code128',
        #     'width': 125,
        # }
        #
        # barcode_obj = self.pool.get('tr.barcode')
        # barcode_id = barcode_obj.create(cr, uid, barcode_vals, context=context)
        # barcode_obj.generate_image(cr, uid, [barcode_id], context=context)
        #
        # barcode_obj = self.pool.get('tr.barcode').browse(cr, uid, barcode_id)
        # return barcode_obj.image


    def _show_discount(self):

        return 'Hadouken'

report_sxw.report_sxw('report.plp.report.webkit',
                      'shipping.response',
                      'addons/delivery_carrier_correios/report/plp_report.mako',
                      parser=PLPReport)