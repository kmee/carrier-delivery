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
        'x_barcode_id': fields.many2one('tr.barcode', 'BarCode'),
        'shipping_response_id': fields.many2one('shipping.response',
                                                string='Shipping Group',
                                                readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice',
                                      readonly=True),
    }

    def copy(self, cr, uid, id, default=None, context=None):

        if default is None:
            default = {}

        vals = {
            'carrier_tracking_ref': '',
            'invoice_id': False,
        }

        default.update(vals)
        return super(StockPickingOut, self).copy(
            cr, uid, id, default=default, context=context)

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
        return result


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        "x_barcode_id": fields.many2one('tr.barcode', u'BarCode'),
        'shipping_response_id': fields.many2one('shipping.response',
                                                string='Shipping Group',
                                                readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice',
                                      readonly=True),
    }

    def _invoice_hook(self, cursor, user, picking, invoice_id):

        self.write(cursor, user, [picking.id],
                   {'invoice_id': invoice_id})

        return super(StockPicking, self)._invoice_hook(
            cursor, user, picking, invoice_id)
