# -*- coding: utf-8 -*-
# #############################################################################
#
#    Brazillian Carrier Correios Sigep WEB
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Mileo <mileo@kmee.com.br>
#    @author: Michell Stuttgart <michell.stuttgart@kmee.com.br>
#
#    Sponsored by Europestar www.europestar.com.br
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

import math
from pysigep_web.pysigepweb.webservice_calcula_preco_prazo import \
    WebserviceCalculaPrecoPrazo
from pysigep_web.pysigepweb.pysigep_exception import ErroConexaoComServidor
from pysigep_web.pysigepweb.servico_postagem import ServicoPostagem
from pysigep_web.pysigepweb.dimensao import Dimensao
from pysigep_web.pysigepweb.resposta_busca_cliente import Cliente


class DeliveryCarrier(orm.Model):

    _inherit = 'delivery.carrier'

    def _get_carrier_type_selection(self, cr, uid, context=None):
        res = super(DeliveryCarrier, self)._get_carrier_type_selection(
            cr, uid, context=context)
        res.append(('sigepweb', 'Correios SigepWeb'))
        return res

    def onchange_sigepweb_post_service_id(self, cr, uid, ids,
                                          sigepweb_post_service_id,
                                          context=None):
        res = {'value': {}}

        if not sigepweb_post_service_id:
            return res

        post_service = self.pool.get('sigepweb.post.service').browse(
            cr, uid, sigepweb_post_service_id, context=context)

        values = {
            'code': post_service.code,
            'description': post_service.details,
        }

        res['value'].update(values)

        return res

    def _check_post_card(self, cr, uid, ids):

        for delivery in self.browse(cr, uid, ids):

            if delivery.type == 'sigepweb':
                record_post_card = delivery.sigepweb_contract_id.post_card_ids

                a = delivery.sigepweb_post_card_id
                if a.id not in [c.id for c in record_post_card]:
                    return False

        return True

    def _check_service_card(self, cr, uid, ids):

        # Garante que o record seja salvo com um servico que nao pertenca
        # cartao de postagem selecionado
        for delivery in self.browse(cr, uid, ids):

            if delivery.type == 'sigepweb':

                post_service_ids = \
                    delivery.sigepweb_post_card_id.post_service_ids

                post_service = delivery.sigepweb_post_service_id

                if post_service.id not in [s.id for s in post_service_ids]:
                    return False

        return True

    _columns = {
        'sigepweb_contract_id': fields.many2one('sigepweb.contract',
                                                'Contract'),
        'sigepweb_post_card_id': fields.many2one(
            'sigepweb.post.card', string='Post Cards',
            domain="[('contract_id', '=', sigepweb_contract_id)]"),

        'sigepweb_post_service_id': fields.many2one(
            'sigepweb.post.service', string='Post Services',
            domain="[('post_card_id', '=', sigepweb_post_card_id)]"),

    }

    _constraints = [
        (_check_post_card,
         u'O numero de Cartão de Postagem fornecido não '
         u'esta presente no Contrato selecionado.',
         ['sigepweb_post_card_id']),
        (_check_service_card,
         u'O numero de Servico de Postagem fornecido não '
         u'esta presente no Cartão de Postagem selecionado.',
         ['sigepweb_post_service_id']),
    ]


class DeliveryGrid(orm.Model):
    _inherit = "delivery.grid"

    def get_price_term(self, cr, uid, grid, order, context):

        total = 0
        weight = 0
        volume = 0

        for line in order.order_line:
            if not line.product_id:
                continue
            total += line.price_subtotal or 0.0
            weight += (line.product_id.weight or 0.0) * line.product_uom_qty
            volume += (line.product_id.volume or 0.0) * line.product_uom_qty

        if not order.order_line:
            res = (0.00, 0.00)
            return res

        volume_cm = volume * 100000
        peso_volumetrico = 0

        if volume_cm > 60000:
            peso_volumetrico = math.ceil(volume_cm / 6000)

        peso_considerado = max(weight, peso_volumetrico)

        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)

        fields = {
            "cod": int(grid.service_type),
            "GOCEP": order.partner_shipping_id.zip,
            "HERECEP": order.shop_id.company_id.partner_id.zip,
            "peso": peso_considerado,
            "formato": user.company_id.sigepweb_package_type,
            "comprimento": user.company_id.sigepweb_package_length,
            "altura": user.company_id.sigepweb_package_height,
            "largura": user.company_id.sigepweb_package_width,
            "diametro": user.company_id.sigepweb_package_diameter,
            "nome": order.company_id.name,
            "login": order.company_id.sigepweb_username,
            "senha": order.company_id.sigepweb_password,
            "cnpj": order.company_id.cnpj_cpf,
            "cod_admin": grid.carrier_id.sigepweb_post_card_id.admin_code,
        }

        return self._frete(fields)

    def _frete(self, fields):

        try:
            calc = WebserviceCalculaPrecoPrazo()

            service_post = {fields['cod']: ServicoPostagem(fields['cod'])}

            dimensao = Dimensao(fields['formato'],
                                altura=fields['altura'],
                                largura=fields['largura'],
                                comprimento=fields['comprimento'],
                                diametro=fields['diametro'])

            cliente = Cliente(fields['nome'], fields['login'],
                              fields['senha'], fields['cnpj'])

            retorno = calc.calcula_preco_prazo(service_post,
                                               fields['cod_admin'],
                                               fields['HERECEP'],
                                               fields['GOCEP'],
                                               fields['peso'], dimensao,
                                               False, 0, False, cliente)

            if retorno:
                data = {
                    'MsgErro': retorno[0].msg_erro,
                    'Erro': retorno[0].erro,
                    'Codigo': retorno[0].codigo,
                    'Valor': retorno[0].valor.replace(",", "."),
                    'PrazoEntrega': retorno[0].prazo_entrega,
                    'ValorMaoPropria': retorno[0].valor_mao_propria,
                    'ValorValorDeclarado': retorno[0].valor_declarado,
                    'EntregaDomiciliar': retorno[0].entrega_domiciliar,
                    'EntregaSabado': retorno[0].entrega_sabado
                }

                # if data['MsgErro'] is not None:
                #     res = ('ERROR', data['MsgErro'])
                #     print data['MsgErro']
                # else:
                #     res = (float(data['Valor']), data['PrazoEntrega'] or 0.00)

                res = (float(data['Valor']), data['PrazoEntrega'] or 0.00)

                return res

        except ErroConexaoComServidor as e:
            raise osv.except_osv(('Erro no calculo do frete!'),
                                 'Nao foi possivel conectar.\n' + e.message)
