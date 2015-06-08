# -*- coding: utf-8 -*-
# #############################################################################
#
# Copyright (C) 2015 KMEE (http://www.kmee.com.br)
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

from PIL import Image, ImageDraw, ImageFont
from StringIO import StringIO
import io
import base64
import re

from pysigep_web.pysigepweb.webservice_atende_cliente import \
    WebserviceAtendeCliente
from pysigep_web.pysigepweb.pysigep_exception import ErroConexaoComServidor
from pysigep_web.pysigepweb.resposta_busca_cliente import Cliente
from pysigep_web.pysigepweb.servico_postagem import ServicoPostagem
from pysigep_web.pysigepweb.endereco import Endereco


class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'x_barcode_id': fields.many2one('tr.barcode',
                                        string=u'BarCode'),
        'shipping_response_id': fields.many2one('shipping.response',
                                                string=u'Shipping Group',
                                                readonly=True),
        'barcode_id': fields.many2one('tr.barcode', string=u'QR Code'),
        'qr_code_id': fields.many2one('tr.barcode', string=u'Código de Barras'),
        'idv': fields.selection([('51', 'Encomenda'),
                                 ('81', 'Malotes')],
                                string=u'IDV'),
        'image_chancela': fields.binary('Chancela Correios',
                                        filters='*.png, *.jpg',
                                        readonly=True),
        'invoice_id': fields.many2one('account.invoice',
                                      string='Invoice',
                                      readonly=True),
        'carrier_tracking_ref': fields.text('Ref Rastreamento de Carga',
                                            readonly=True),
    }

    _defaults = {
        'idv': '81',
    }

    def copy(self, cr, uid, id, default=None, context=None):

        if default is None:
            default = {}

        vals = {
            'carrier_tracking_ref': '',
            'invoice_id': False,
            'shipping_response_id': False,
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
                    sv = WebserviceAtendeCliente(
                        company_id.sigepweb_environment)

                    print u'[INFO] Consultando dados do cliente'

                    if company_id.sigepweb_username == 'sigep':
                        company_id.cnpj_cpf = '34.028.316/0001-03'

                    cliente = Cliente(company_id.name,
                                      company_id.sigepweb_username,
                                      company_id.sigepweb_password,
                                      company_id.cnpj_cpf)

                    servico_postagem_id = \
                        stock.carrier_id.sigepweb_post_service_id

                    serv_post = ServicoPostagem(servico_postagem_id.code,
                                                servico_postagem_id.details,
                                                servico_postagem_id.identifier)

                    tracking_packs = []
                    for line in stock.move_lines:

                        if line.tracking_id.name not in tracking_packs:
                            tracking_packs.append(line.tracking_id.id)

                    etiquetas = sv.solicita_etiquetas(serv_post,
                                                      len(tracking_packs),
                                                      cliente)

                    sv.gera_digito_verificador_etiquetas(etiquetas,
                                                         cliente,
                                                         online=False)

                    for index, etq in enumerate(etiquetas):
                        vals = {
                            'serial': etq.com_digito_verificador()
                        }
                        obj_pack = self.pool.get('stock.tracking')
                        obj_pack.write(cr, uid, tracking_packs[index], vals)

                        #
                        # if line.tracking_id.name in tracking_packs:
                        #     tracking_packs += 1

                    # etq_str = ''
                    # last_index = len(etiquetas) - 1
                    #
                    # for index, etq in enumerate(etiquetas):
                    #     dig = '' if index == last_index else ', '
                    #     etq_str += etq.com_digito_verificador() + dig
                    #
                    # vals = {
                    #     'carrier_tracking_ref': etq_str,
                    # }
                    # self.write(cr, uid, stock.id, vals, context=None)

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
        image_chancela = self.create_chancela(cr, uid, ids, context)
        self.write(cr, uid, ids,
                   {'barcode_id': barcode_id, 'qr_code_id': qr_code_id,
                    'image_chancela': image_chancela})

        id_barcode_default = self.browse(cr, uid, ids, context)[
            0].x_barcode_id.id
        self.pool.get('tr.barcode').write(cr, uid, id_barcode_default,
                                          {'hr_form': True, 'width': 350})

        return result

    def create_chancela(self, cr, uid, ids, context):
        obj_stock = self.browse(cr, uid, ids[0], context)
        # company = self.pool('res.company').browse(cr, uid, ids[0], context)
        company = self.pool.get('res.company').browse(cr, uid,
                                                      obj_stock.company_id.id,
                                                      context)
        imagem = obj_stock.carrier_id.image_chancela
        texto1 = "0000/2002 - DR/XX/YY"
        texto2 = company.name
        imagem = Image.open(StringIO(imagem.decode('base64')))
        img = imagem.convert("RGB")
        write = Image.new("RGB", (img.size[0], img.size[1]))
        draw = ImageDraw.ImageDraw(img)

        FONT = "../static/src/fonts/arial.ttf"
        font = ImageFont.truetype(FONT, 8)
        draw.setfont(font)
        tamanho_texto = draw.textsize(texto1)
        h_position = (img.size[0] - tamanho_texto[0]) / 2
        v_position = img.size[1] / 2
        draw.text((h_position, v_position), texto1, fill=(0, 0, 0))

        FONT = "../static/src/fonts/arial_negrito.ttf"
        font = ImageFont.truetype(FONT, 11)
        draw.setfont(font)
        tamanho_texto = draw.textsize(texto2)
        h_position = (img.size[0] - tamanho_texto[0]) / 2
        v_position = img.size[1] / 2 + 8
        draw.text((h_position, v_position), texto2, fill=(0, 0, 0))
        tmp = io.BytesIO()
        img.save(tmp, 'png')
        img = base64.b64encode(tmp.getvalue())
        # Image.open(StringIO(img.decode('base64'))).convert('RGB').show()

        return img

    def get_qr_string(self, cr, uid, id, context):
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
        if stock_obj.carrier_tracking_ref:
            qr_string += stock_obj.carrier_tracking_ref  # Código da etiqueta
        else:
            qr_string += '0' * 13
        # TODO: Implementar serviços adicionais, enquanto isso completar a string com 12 zeros
        qr_string += '000000000000'  #Serviçoes adicionais
        qr_string += stock_obj.carrier_id.sigepweb_post_card_id.number  # cartão de postagem
        qr_string += stock_obj.carrier_id.sigepweb_post_service_id.code  # Código de serviços
        qr_string += '00'  # TODO: Verificar o que é as informaçoes de agrupamento
        qr_string += stock_obj.partner_id.number.zfill(5)  # Número do logradouro
        qr_string += stock_obj.partner_id.street2 or ' ' * 20  # Complemento do logradouro
        qr_string += '00000'  # valor declarado
        if stock_obj.partner_id.phone:  # Telefone do destinatario
            phone = ''.join(reg.findall(stock_obj.partner_id.phone.zfill(12)))
            if len(phone) != 12:
                raise osv.except_osv(_('Error!'),
                                     _(u'O Telefone do destinatário incorreto'))
            else:
                qr_string += phone
        else:
            qr_string += '0' * 12
        qr_string += '-00.000000'  # TODO: pegar a Longitude ou deixar preencido como padrão
        qr_string += '-00.000000'  # TODO: pegar a Latitude ou deixar preencido como padrão
        qr_string += '|'
        qr_string += ' ' * 30
        print len(qr_string)

        return qr_string

    def create_qr_code(self, cr, uid, id, context):

        barcode_vals = {
            'code': self.get_qr_string(cr, uid, id, context),
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
        'idv': fields.selection([('51', 'Encomenda'), ('81', 'Malotes')],
                                string=u'IDV'),
        'image_chancela': fields.binary('Chancela Correios',
                                        filters='*.png, *.jpg',
                                        readonly=True),
        'invoice_id': fields.many2one('account.invoice',
                                      string='Invoice',
                                      readonly=True),
        'carrier_tracking_ref': fields.text(string='Ref Rastreamento de Carga',
                                            readonly=True),
    }

    def _invoice_hook(self, cursor, user, picking, invoice_id):
        self.write(cursor, user, [picking.id], {'invoice_id': invoice_id})

        return super(StockPicking, self)._invoice_hook(
            cursor, user, picking, invoice_id)
