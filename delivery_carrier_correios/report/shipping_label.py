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
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp import pooler

from openerp.addons.delivery_carrier_correios.model.pysigep_web.pysigepweb.chancela import Chancela


class ShippingLabelReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ShippingLabelReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'get_chancela': self._get_chancela})

    def _get_chancela(self, uid, ids, context=None):

        cr = self.cr
        pool = pooler.get_pool(self.cr.dbname)
        obj_stock = pool.get('stock.picking.out').browse(cr, uid, ids, context=context)

        carrier = obj_stock.carrier_id

        if obj_stock.state != 'done' or not carrier or carrier.type != \
                'sigepweb':
            # msg = 'Ordem de Entrega deve estar como \"Entregue\" para que a ' \
            #       'etiqueta seja impressa. O tipo da transportadora tambem ' \
            #       'deve estar como \"Correios SigepWep\".'
            # raise osv.except_osv(_('Error!'), _(msg))
            return None

        chancela = Chancela(carrier.sigepweb_post_service_id.image_chancela, '')

        company = obj_stock.company_id
        contract = carrier.sigepweb_contract_id

        chancela.nome_cliente = company.name
        chancela.num_contrato = contract.number
        chancela.ano_assinatura = contract.year
        chancela.dr_origem = company.state_id.code
        chancela.dr_postagem = obj_stock.partner_id.state_id.code

        try:
            img = chancela.get_image_base64
        except IOError as excp:
            raise osv.except_osv(_('Error!'), _(excp.message))

        return img

report_sxw.report_sxw('report.shipping.label.webkit',
                      'stock.picking.out',
                      'addons/delivery_carrier_correios/report/shipping_label.mako',
                      parser=ShippingLabelReport)