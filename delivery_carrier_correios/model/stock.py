# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author: Rodolfo Bertozo <rodolfo.bertozo@kmee.com.br
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

from openerp.osv import orm, fields, osv
from openerp.tools.translate import _

import re

from pysigep_web.pysigepweb.webservice_atende_cliente import \
    WebserviceAtendeCliente
from pysigep_web.pysigepweb.pysigep_exception import ErroConexaoComServidor
from pysigep_web.pysigepweb.resposta_busca_cliente import Cliente
from pysigep_web.pysigepweb.servico_postagem import ServicoPostagem
from pysigep_web.pysigepweb.endereco import Endereco
from company import LETTER, BOX, CILINDER


class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'idv': fields.selection([('51', 'Encomenda'),
                                 ('81', 'Malotes')],
                                string=u'Identificador de Dados Variaveis'),
        'invoice_ids': fields.many2one('account.invoice',
                                       string='Invoice',
                                       readonly=True),
    }

    _defaults = {
        'idv': '81',
    }

    def copy(self, cr, uid, id, default=None, context=None):

        if default is None:
            default = {}

        vals = {
            'sale_id': False,
            'invoice_ids': False,
            'shipping_response_id': False,
        }

        default.update(vals)
        return super(StockPickingOut, self).copy(
            cr, uid, id, default=default, context=context)

    def action_process(self, cr, uid, ids, context=None):
        res = super(StockPickingOut, self).action_process(cr, uid, ids,
                                                          context=context)

        for stock in self.browse(cr, uid, ids, context=context):

            if stock.carrier_id.type == 'sigepweb':

                company_id = stock.company_id

                try:
                    sv = WebserviceAtendeCliente(
                        company_id.sigepweb_environment)

                    if company_id.sigepweb_username == 'sigep':
                        company_id.cnpj_cpf = '34.028.316/0001-03'

                    cliente = Cliente(company_id.name,
                                      company_id.sigepweb_username,
                                      company_id.sigepweb_password,
                                      company_id.cnpj_cpf)

                    servico_postagem_id = \
                        stock.carrier_id.sigepweb_post_service_id

                    serv_post = ServicoPostagem(servico_postagem_id.code,
                                                descricao=servico_postagem_id.details,
                                                servico_id=servico_postagem_id.identifier)

                    tracking_packs = []
                    for line in stock.move_lines:

                        if line.tracking_id and line.tracking_id.id not in \
                                tracking_packs:
                            tracking_packs.append(line.tracking_id.id)

                    if not tracking_packs:
                        raise osv.except_osv(
                            _('Error!'), u'Embalagens sem código de referência')

                    etiquetas = sv.solicita_etiquetas(serv_post,
                                                      len(tracking_packs),
                                                      cliente)

                    sv.gera_digito_verificador_etiquetas(etiquetas,
                                                         cliente,
                                                         online=False)

                    obj_pack = self.pool.get('stock.tracking')

                    for index, etq in enumerate(etiquetas):
                        obj = obj_pack.browse(cr, uid, tracking_packs[index])
                        qr_code_id = self.create_qr_code(cr, uid, ids, etq)
                        barcode_id = self.create_barcode(cr, uid, ids, obj.name)

                        vals = {
                            'serial': etq.com_digito_verificador(),
                            'barcode_id': barcode_id,
                            'qr_code_id': qr_code_id
                        }

                        obj_pack.write(cr, uid, [obj.id], vals)

                    self.action_generate_carrier_label(cr, uid, ids)

                    if stock.sale_id and stock.sale_id.invoice_ids:

                        inv_ids = [(4, inv.id) for inv in stock.sale_id.invoice_ids]
                        self.write(cr, uid, ids, {
                            'invoice_ids': inv_ids})

                except ErroConexaoComServidor as e:
                    raise osv.except_osv(_('Error!'), e.message)

        return res

    def action_generate_carrier_label(self, cr, uid, ids, context=None):
        result = {
            'type': 'ir.actions.report.xml',
            'report_name': 'shipping.label.webkit'
        }

        return result

    def get_qr_string(self, cr, uid, id, etiqueta, context=None):
        qr_string = ''
        stock_obj = self.browse(cr, uid, id[0], context)
        company_obj = self.pool.get('res.company').browse(
            cr, uid, stock_obj.company_id.id, context)

        reg = re.compile('[0-9]*')
        zip_dest = ''.join(reg.findall(stock_obj.partner_id.zip))
        if len(zip_dest) != 8:
            raise osv.except_osv(_('Error!'), _(
                u'O CEP do destinatário fornecido não contém 8 números!'))
        else:
            qr_string += zip_dest  # CEP destinatario
        qr_string += '00000'  #complemente CEP destinatario

        zip_remet = ''.join(reg.findall(company_obj.zip))
        if len(zip_remet) != 8:
            raise osv.except_osv(_('Error!'), _(
                u'O CEP do remetente fornecido não contém 8 números!'))
        else:
            qr_string += zip_remet  # CEP remetente
        qr_string += '00000'  # complemento CEP remetente

        digito_validador_cep = str(Endereco.digito_validador_cep(zip_dest))
        qr_string += digito_validador_cep  # validador
        qr_string += stock_obj.idv  # idv

        qr_string += etiqueta.com_digito_verificador()  # Código da etiqueta

        # TODO: Implementar serviços adicionais, enquanto isso completar a string com 12 zeros
        qr_string += '250000000000'  #Serviçoes adicionais
        qr_string += stock_obj.carrier_id.sigepweb_post_card_id.number  # cartão de postagem
        qr_string += stock_obj.carrier_id.sigepweb_post_service_id.code  # Código de serviços
        qr_string += '00'  # TODO: Verificar o que é as informaçoes de agrupamento
        qr_string += stock_obj.partner_id.number.zfill(
            5)  # Número do logradouro
        qr_string += stock_obj.partner_id.street2 or ' ' * 20  # Complemento do logradouro
        qr_string += '00000'  # valor declarado

        if stock_obj.partner_id.phone:  # Telefone do destinatario
            phone = ''.join(reg.findall(stock_obj.partner_id.phone))
            phone = phone.zfill(12)
            if len(phone) != 12:
                raise osv.except_osv(_('Error!'),
                                     _('Size of partner phone number '
                                       'incorrect'))
            else:
                qr_string += phone
        else:
            qr_string += '0' * 12
        qr_string += '-00.000000'  # TODO: pegar a Longitude ou deixar preencido como padrão
        qr_string += '-00.000000'  # TODO: pegar a Latitude ou deixar preencido como padrão
        qr_string += '|'
        qr_string += ' ' * 30

        return qr_string

    def create_qr_code(self, cr, uid, id, etiqueta, context=None):

        barcode_vals = {
            'code': self.get_qr_string(cr, uid, id, etiqueta, context=context),
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

    def create_barcode(self, cr, uid, id, reference, context=None):

        barcode_vals = {
            'code': reference,
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
        'idv': fields.selection([('51', 'Encomenda'), ('81', 'Malotes')],
                                string=u'IDV'),
        'invoice_ids': fields.one2many('account.invoice',
                                       'stock_picking_id',
                                       string='Invoice',
                                       readonly=False),

    }

    _defaults = {
        'idv': '81',
    }

    def _invoice_hook(self, cursor, user, picking, invoice_id):

        self.write(cursor, user, [picking.id], {'invoice_ids': [(4,
                                                                 invoice_id)]})

        return super(StockPicking, self)._invoice_hook(
            cursor, user, picking, invoice_id)


class StockTracking(orm.Model):
    _inherit = "stock.tracking"

    _columns = {
        'shipping_response_id': fields.many2one('shipping.response',
                                                string='Shipping Group',
                                                readonly=True),
        'x_barcode_id': fields.many2one('tr.barcode',
                                        string=u'BarCode Label'),
        'barcode_id': fields.many2one('tr.barcode', string=u'Reference Code'),
        'qr_code_id': fields.many2one('tr.barcode', string=u'QR Code'),
        'package_type': fields.selection((LETTER, BOX, CILINDER),
                                         string='Package type',
                                         required=True),
        'package_width': fields.integer('Package width',
                                        help='Min value: 11 cm\n'
                                             'Max value: 105 cm'),
        'package_height': fields.integer('Package height',
                                         help='Min value: 2 cm\n'
                                              'Max value: 105 cm'),
        'package_length': fields.integer('Package length',
                                         help='Min value: 16 cm\n'
                                              'Max value: 105 cm'),
        'package_diameter': fields.integer('Package diameter',
                                           help='Min value: 5 cm\n'
                                                'Max value: 105 cm'),
    }

    _defaults = {
        'package_type': lambda self, cr, uid, c: self.pool.get(
            'res.users').browse(cr, uid, uid,
                                c).company_id.sigepweb_package_type,
        'package_width': lambda self, cr, uid, c: self.pool.get(
            'res.users').browse(cr, uid, uid,
                                c).company_id.sigepweb_package_width,
        'package_height': lambda self, cr, uid, c: self.pool.get(
            'res.users').browse(cr, uid, uid,
                                c).company_id.sigepweb_package_height,
        'package_length': lambda self, cr, uid, c: self.pool.get(
            'res.users').browse(cr, uid, uid,
                                c).company_id.sigepweb_package_length,
        'package_diameter': lambda self, cr, uid, c: self.pool.get(
            'res.users').browse(cr, uid, uid,
                                c).company_id.sigepweb_package_diameter,
    }

