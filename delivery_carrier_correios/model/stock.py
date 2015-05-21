# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author: Rodolfo Bertozo <rodolfo.bertozo@kmee.com.br
#
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
from bsddb.dbtables import _columns_key

from openerp.osv import orm, fields, osv
from openerp.tools.translate import _

from pysigep_web.pysigepweb.webservice_atende_cliente import \
    WebserviceAtendeCliente
from pysigep_web.pysigepweb.pysigep_exception import ErroConexaoComServidor
from pysigep_web.pysigepweb.resposta_busca_cliente import Cliente
from pysigep_web.pysigepweb.servico_postagem import ServicoPostagem


class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'x_barcode_id': fields.many2one('tr.barcode', string=u'BarCode'),
        'shipping_response_id': fields.many2one('shipping.response',
                                                string=u'Shipping Group',
                                                readonly=True),
        'barcode_id': fields.many2one('tr.barcode', string=u'QR Code'),
        'qr_code_id': fields.many2one('tr.barcode', string=u'Código de Barras'),
    }

    def action_process(self, cr, uid, ids, *args):
        res = super(StockPickingOut, self).action_process(cr, uid, ids, *args)

        for stock in self.browse(cr, uid, ids):

            if stock.carrier_id.type == 'sigepweb':

                company_id = stock.company_id

                try:
                    print u'[INFO] Iniciando Serviço de Atendimento ao  Cliente'
                    sv = WebserviceAtendeCliente(company_id.sigepweb_environment)

                    print u'[INFO] Consultando dados do cliente'

                    cliente = Cliente(company_id.name,
                                      company_id.sigepweb_username,
                                      company_id.sigepweb_password,
                                      company_id.cnpj_cpf)

                    servico_postagem_id = \
                        stock.carrier_id.sigepweb_post_service_id

                    serv_post = ServicoPostagem(servico_postagem_id.code,
                                                servico_postagem_id.details,
                                                servico_postagem_id.identifier)

                    etiquetas = sv.solicita_etiquetas(serv_post, 1, cliente)

                    sv.gera_digito_verificador_etiquetas(etiquetas,
                                                         cliente,
                                                         online=False)
                    # Adicionamos a etiqueta no campo carrier_tracking_ref
                    for etq in etiquetas:

                        vals = {
                            'carrier_tracking_ref': etq.com_digito_verificador(),
                        }
                        self.write(cr, uid, stock.id, vals, context=None)

                except ErroConexaoComServidor as e:
                    print e.message
                    raise osv.except_osv(_('Error!'), e.message)

        return res

    def action_generate_carrier_label(self, cr, uid, ids, context=None):
        result = {
            'type': 'ir.actions.report.xml',
            'report_name': 'shipping.label.webkit'
        }
        qr_code_id = self.create_qr_code(cr, uid, ids, context)
        barcode_id = self.create_barcode(cr, uid, ids, context)

        self.write(cr, uid, ids, {'barcode_id': barcode_id, 'qr_code_id': qr_code_id})

        return result

    def create_qr_code(self, cr, uid, id, context):

        barcode_vals = {
            'code': 'pypcrjycuhzvxbpcfwqjjarfmeyeewznfiyvdetokcxdbtfqyucizzsjskidnowshsdbqzgwnfwgdetzusxgrdtcosbwkgqyugvpzcmwfehmybjtgxveunjfbnizebaxtqskfkkqwc',
            'res_id': id[0],
            'barcode_type': 'qrcode',
            'hr_form': True,
            'width': 32,
            'height': 32,
        }

        barcode_obj = self.pool.get('tr.barcode')
        barcode_id = barcode_obj.create(cr, uid, barcode_vals, context=context)
        barcode_obj.generate_image(cr, uid, [barcode_id], context=context)

        return barcode_id

    def create_barcode(self, cr, uid, id, context):

        barcode_vals = {
            'code': self.browse(cr, uid, id, context)[0].name,
            'res_id': id[0],
            'barcode_type': 'Code128',
            'width': 125,
        }

        barcode_obj = self.pool.get('tr.barcode')
        barcode_id = barcode_obj.create(cr, uid, barcode_vals, context=context)
        barcode_obj.generate_image(cr, uid, [barcode_id], context=context)

        return barcode_id

class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        "x_barcode_id": fields.many2one('tr.barcode', string=u'BarCode'),
        'shipping_response_id': fields.many2one('shipping.response',
                                                string='Shipping Group',
                                                readonly=True),
        'barcode_id': fields.many2one('tr.barcode', string=u'QR Code'),
        'qr_code_id': fields.many2one('tr.barcode', string=u'Código de Barras'),
    }

#TODO: apagar campo carrier_tracking_ref quando duplicamos a ordem de entrega
