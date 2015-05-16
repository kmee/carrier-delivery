# -*- coding: utf-8 -*-
# #############################################################################
#
# Brazillian Carrier Correios Sigep WEB
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
import time
import math
from pysigep_web.pysigepweb.webservice_calcula_preco_prazo import WebserviceCalculaPrecoPrazo
from pysigep_web.pysigepweb.pysigep_exception import ErroConexaoComServidor
from pysigep_web.pysigepweb.servico_postagem import ServicoPostagem
from pysigep_web.pysigepweb.dimensao import Dimensao, Caixa
from pysigep_web.pysigepweb.resposta_busca_cliente import Cliente


class DeliveryCarrier(orm.Model):
    """ Add service group """
    _inherit = 'delivery.carrier'

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        if context is None:
            context = {}
        order_id = context.get('order_id', False)
        if not order_id:
            res = super(DeliveryCarrier, self).name_get(cr, uid, ids,
                                                        context=context)
        else:
            order = self.pool.get('sale.order').browse(cr, uid, order_id,
                                                       context=context)
            currency = order.pricelist_id.currency_id.name or ''
            res = [(r['id'], r['name'] + ' (' + (str(r['price'])) + ' ' +
                    currency + ' ' + str(r['term']) + ' (s))') for r in
                   self.read(cr, uid, ids, ['name', 'price', 'term'], context)]
        return res

    def get_price(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        if context is None:
            context = {}
        sale_obj = self.pool.get('sale.order')
        grid_obj = self.pool.get('delivery.grid')

        for carrier in self.browse(cr, uid, ids, context=context):

            order_id = context.get('order_id', False)

            res[carrier.id] = {
                'price': 0.00,
                'term': 0.00,
            }

            if order_id:

                order = sale_obj.browse(cr, uid, order_id, context=context)

                carrier_grid = self.grid_get(cr, uid, [carrier.id],
                                             order.partner_shipping_id.id,
                                             context)
                if carrier_grid:
                    grid = grid_obj.browse(cr, uid, carrier_grid,
                                           context=context)
                    print grid.service

                    if grid.service == "correios":  #CHANGE
                        res[carrier.id]['price'], res[carrier.id][
                            'term'] = grid_obj.get_price_term(cr, uid, grid,
                                                              order, context)
                    else:
                        res[carrier.id]['price'] = grid_obj.get_price(
                            cr, uid, carrier_grid, order,
                            time.strftime('%Y-%m-%d'), context)
        return res

    def _get_carrier_type_selection(self, cr, uid, context=None):
        """ Add postlogistics carrier type """
        res = super(DeliveryCarrier, self)._get_carrier_type_selection(
            cr, uid, context=context)
        res.append(('sigepweb', 'Correios SigepWeb'))
        return res

    def onchange_sigepweb_post_service_ids(self, cr, uid, ids,
                                           sigepweb_post_service_ids,
                                           context=None):
        res = {'value': {}}

        if not sigepweb_post_service_ids:
            return res

        post_service = self.pool.get('sigepweb.post.service').browse(
            cr, uid, sigepweb_post_service_ids, context=context)

        values = {
            'code': post_service.code,
            'description': post_service.details,
        }

        res['value'].update(values)

        return res

    def _check_post_card(self, cr, uid, ids):

        for delivery in self.browse(cr, uid, ids):

            record_post_card = delivery.sigepweb_contract_ids.post_card_ids

            a = delivery.sigepweb_post_card_ids
            if a.id not in [c.id for c in record_post_card]:
                return False

        return True

    def _check_service_card(self, cr, uid, ids):

        # Garante que o record seja salvo com um servico que nao pertenca
        # cartao de postagem selecionado
        for delivery in self.browse(cr, uid, ids):

            post_service_ids = \
                delivery.sigepweb_post_card_ids.post_service_ids

            post_service = delivery.sigepweb_post_service_ids

            if post_service.id not in [s.id for s in post_service_ids]:
                return False

        return True

    _columns = {
        'sigepweb_contract_ids': fields.many2one('sigepweb.contract',
                                                 'Contract'),
        'sigepweb_post_card_ids': fields.many2one(
            'sigepweb.post.card', string='Post Cards',
            domain="[('contract_id', '=', sigepweb_contract_ids)]"),

        'sigepweb_post_service_ids': fields.many2one(
            'sigepweb.post.service', string='Post Services',
            domain="[('post_card_id', '=', sigepweb_post_card_ids)]"),

        'price': fields.function(get_price, string='Price', multi="sums"),
        'term': fields.function(get_price, string='Term', multi="sums"),
    }

    _constraints = [
        (_check_post_card,
         u'O numero de Cartão de Postagem fornecido não '
         u'esta presente no Contrato selecionado.',
         ['sigepweb_post_card_ids']),
        (_check_service_card,
         u'O numero de Servico de Postagem fornecido não '
         u'esta presente no Cartão de Postagem selecionado.',
         ['sigepweb_post_service_ids']),
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

        volume_cm = volume * 100000
        peso_volumetrico = 0

        if volume_cm > 60000:
            peso_volumetrico = math.ceil(volume_cm / 6000)

        peso_considerado = max(weight, peso_volumetrico)
        aresta = int(math.ceil(volume_cm**(1/3.0)))

        if order.carrier_id.type == 'sigepweb':

            post_serv = order.carrier_id.sigepweb_post_service_ids

            fields = {
                "codigo": int(post_serv.code),
                "descricao": post_serv.details,
                "indentificador": int(post_serv.identifier),
                "GOCEP": order.partner_shipping_id.zip,
                "HERECEP": order.shop_id.company_id.partner_id.zip,
                "peso": peso_considerado,
                "formato": "1",
                "comprimento": aresta,
                "altura": aresta,
                "largura": aresta,
                "diametro": "0",
                "nome": order.company_id.name,
                "login": order.company_id.sigepweb_username,
                "senha": order.company_id.sigepweb_password,
                "cnpj": order.company_id.cnpj_cpf,
                "contrato": order.company_id.sigepweb_main_contract_number,
                "cartao de postagem":
                    order.company_id.sigepweb_main_post_card_number,
                "cod_admin": order.carrier_id.sigepweb_post_card_ids.admin_code,
            }

            try:
                # response = Correios().frete(**fields)
                response = self._frete(fields)
            except Exception as exp:
                return (0.00, 0.00)
                raise osv.except_osv(_('Erro no calculo do frete!'),
                                     _('Nao foi possivel conectar'))
            return (float(response['Valor'].replace(",", ".")), response[
                'PrazoEntrega'] or 0.00)

        else:
            print u'[INFO] Tipo do Método de Entrega não é SigepWeb!'
            return (0.00, 0.00)


    def _frete(self, fields):

        # data = {'MsgErro',
        #         'Erro',
        #         'Codigo',
        #         'Valor',
        #         'PrazoEntrega',
        #              'ValorMaoPropria',
        #              'ValorValorDeclarado',
        #              'EntregaDomiciliar',
        #              'EntregaSabado',}

        #  self.codigo = returno_suds.Codigo
        # self.valor = returno_suds.Valor
        # self.prazo_entrega = returno_suds.PrazoEntrega
        # self.valor_mao_propria = returno_suds.ValorMaoPropria
        # self.valor_aviso_recebimento = returno_suds.ValorAvisoRecebimento
        # self.valor_declarado = returno_suds.ValorValorDeclarado
        # self.entrega_domiciliar = returno_suds.EntregaDomiciliar
        # self.entrega_sabado = returno_suds.EntregaSabado
        # self.erro = returno_suds.Erro
        # self.msg_erro = returno_suds.MsgErro
        # self.valor_sem_adicionais = returno_suds.ValorSemAdicionais
        # self.obs_fim = returno_suds.obsFim

        try:
            print '[INFO] Conectanco com webservice de calculo de prazo e preco'
            calc = WebserviceCalculaPrecoPrazo()

            service_post = [ServicoPostagem(fields['cod'])]

            dimensao = Dimensao(Caixa(fields['comprimento'],
                                      fields['altura'],
                                      fields['largura']))

            # nome, login, senha, cnpj, descricao_status_cliente=''):

            cliente = Cliente(fields['nome'], fields['login'],
                              fields['senha'], fields['cnpj'])

            retorno = calc.calcula_preco_prazo(service_post, fields['cod_admin'],
                                               fields['HERECEP'], fields['GOCEP'],
                                               fields['peso'], dimensao,
                                               False, 0, False, cliente)

            if retorno:

                data = {
                    'MsgErro': retorno[0].msg_erro,
                    'Erro': retorno[0].erro,
                    'Codigo': retorno[0].codigo,
                    'Valor': retorno[0].valor,
                    'PrazoEntrega': retorno[0].prazo_entrega,
                    'ValorMaoPropria': retorno[0].valor_mao_propria,
                    'ValorValorDeclarado': retorno[0].valor_declarado,
                    'EntregaDomiciliar': retorno[0].entrega_domiciliar,
                    'EntregaSabado': retorno[0].entrega_sabado
                }

                return data

        except ErroConexaoComServidor as e:
            raise osv.except_osv(_('Erro no calculo do frete!'),
                                 _('Nao foi possivel conectar.\n' + e.message))
