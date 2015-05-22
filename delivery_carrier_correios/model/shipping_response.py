# -*- coding: utf-8 -*-
# #############################################################################
#
# Brazillian Carrier Correios Sigep WEB
# Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Mileo <mileo@kmee.com.br>
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

from openerp.osv import fields, orm, osv
from openerp.tools.translate import _

import re

from pysigep_web.pysigepweb.webservice_atende_cliente import \
    WebserviceAtendeCliente
from pysigep_web.pysigepweb.tag_nacional import TagNacionalPAC41068
from pysigep_web.pysigepweb.tag_plp import TagPLP
from pysigep_web.pysigepweb.tag_remetente import TagRemetente
from pysigep_web.pysigepweb.tag_dimensao_objeto import *
from pysigep_web.pysigepweb.tag_objeto_postal import *
from pysigep_web.pysigepweb.tag_correios_log import TagCorreiosLog
from pysigep_web.pysigepweb.diretoria import Diretoria
from pysigep_web.pysigepweb.endereco import Endereco
from pysigep_web.pysigepweb.pysigep_exception import ErroConexaoComServidor
from pysigep_web.pysigepweb.etiqueta import Etiqueta
from pysigep_web.pysigepweb.resposta_busca_cliente import Cliente


class ShippingResponse(orm.Model):
    _name = 'shipping.response'

    def generate_tracking_no(self, cr, uid, ids, context={}, error=True):
        pass

    def _compute_volume(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in ids:
            res[obj] = 0

            obj_ship = self.browse(cr, uid, obj, context=context)
            for picking in obj_ship.picking_line:
                res[obj] += int(picking.quantity_of_volumes)

        return res

    def _compute_weight(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in ids:
            res[obj] = 0.00

            obj_ship = self.browse(cr, uid, obj, context=context)
            for picking in obj_ship.picking_line:
                res[obj] += picking.weight

        return res

    def _compute_weight_net(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in ids:
            res[obj] = 0.00

            obj_ship = self.browse(cr, uid, obj, context=context)
            for picking in obj_ship.picking_line:
                res[obj] += picking.weight_net

        return res

    def shipment_confirm(self, cr, uid, ids, context=None):

        for ship in self.browse(cr, uid, ids):

            weight = 0.0
            weight_net = 0.0

            company_id = ship.company_id
            contract_id = ship.contract_id
            post_card_id = ship.post_card_id

            reg = re.compile('[0-9]*')
            numero = ''.join(reg.findall(company_id.number))

            obj_endereco = Endereco(logradouro=company_id.street,
                                    numero=int(numero),
                                    bairro=company_id.district,
                                    cep=int(company_id.zip.replace('-', '')),
                                    cidade=company_id.l10n_br_city_id.name,
                                    uf=company_id.state_id.code,
                                    complemento=company_id.street2)

            obj_tag_plp = TagPLP(post_card_id.number)

            cliente = Cliente(company_id.name,
                              company_id.sigepweb_username,
                              company_id.sigepweb_password,
                              company_id.cnpj_cpf)

            obj_remetente = TagRemetente(cliente.nome,
                                         contract_id.number,
                                         post_card_id.admin_code,
                                         obj_endereco,
                                         Diretoria(
                                             contract_id.directorship_id.code),
                                         telefone=company_id.phone or False,
                                         email=company_id.email,
                                         fax=company_id.fax)

            lista_obj_postal = []
            lista_etiqueta = []

            for picking in ship.picking_line:

                weight += picking.weight
                weight_net += picking.weight_net

                partner_id = picking.partner_id

                reg = re.compile('[0-9]*')
                numero = ''.join(reg.findall(partner_id.number))

                obj_endereco = Endereco(logradouro=partner_id.street,
                                        numero=int(numero),
                                        bairro=partner_id.district,
                                        cep=partner_id.zip.replace('-', ''),
                                        cidade=partner_id.l10n_br_city_id.name,
                                        uf=partner_id.state_id.code,
                                        complemento=partner_id.street2)

                obj_destinatario = TagDestinatario(partner_id.name,
                                                   obj_endereco,
                                                   telefone=partner_id.phone
                                                            or False)

                # obj_nacional = TagNacionalPAC41068(obj_endereco,
                #                                    102030, '1')
                #TODO: Implementar para PAC41068.
                #TODO: Buscar numero e serie da fatura a partir da invoice
                obj_nacional = TagNacional(obj_endereco)

                if picking.carrier_id.sigepweb_post_service_id.code == '41068':
                    print "[Warnig] service PAC41068 need nfe number and serie"

                obj_servico_adicional = TagServicoAdicional()

                #TODO: Inserir campos de dimensao do objeto em cada
                #TODO: Ordem de Entrega
                obj_dimensao_objeto = TagDimensaoObjeto(Caixa())

                sv_postagem = ServicoPostagem(
                    picking.carrier_id.sigepweb_post_service_id.code)

                etq = Etiqueta(picking.carrier_tracking_ref)
                lista_etiqueta.append(etq)

                obj_postal = TagObjetoPostal(obj_destinatario=obj_destinatario,
                                             obj_nacional=obj_nacional,
                                             obj_dimensao_objeto=obj_dimensao_objeto,
                                             obj_servico_adicional=obj_servico_adicional,
                                             obj_servico_postagem=sv_postagem,
                                             ob_etiqueta=etq,
                                             peso=picking.weight,
                                             status_processamento=0)

                lista_obj_postal.append(obj_postal)

            obj_correios_log = TagCorreiosLog('2.3', obj_tag_plp,
                                              obj_remetente, lista_obj_postal)

            try:
                print u'[INFO] Iniciando Serviço de Atendimento ao  Cliente'
                sv = WebserviceAtendeCliente(company_id.sigepweb_environment)

                plp = sv.fecha_plp_varios_servicos(obj_correios_log,
                                                   long(ship.id),
                                                   lista_etiqueta,
                                                   post_card_id.number,
                                                   cliente)

                print u'[INFO] Id PLP: ', plp.id_plp_cliente

                vals = {
                    'name': 'SP' + str(plp.id_plp_cliente),
                    'carrier_tracking_ref': plp.id_plp_cliente,
                }

                self.write(cr, uid, ship.id, vals, context=context)

            except ErroConexaoComServidor as e:
                print e.message
                raise osv.except_osv(_('Error!'), e.message)

    _columns = {
        'user_id': fields.many2one('res.users',
                                   'Responsible',
                                   readonly=True,
                                   states={'draft': [('readonly', False)]}),

        'name': fields.char('Reference', required=True, readonly=True),

        'carrier_tracking_ref': fields.char('Tracking Ref.', readonly=True),

        'carrier_id': fields.many2one('res.partner', string='Carrier',
                                      required=True, readonly=True,
                                      states={'draft': [('readonly', False)]}),

        'carrier_responsible': fields.many2one('res.partner',
                                               string='Carrier Responsible',
                                               states={'draft': [('readonly', False)]}),

        'date': fields.date('Date', require=True, readonly=True,
                            states={'draft': [('readonly', False)]}),

        'note': fields.text('Description / Remarks', readonly=True,
                            states={'draft': [('readonly', False)]}),

        'company_id': fields.many2one('res.company',
                                      string='Company',
                                      required=True,
                                      readonly=True,
                                      states={'draft': [('readonly', False)]}),

        'contract_id': fields.many2one('sigepweb.contract',
                                       string='Contract',
                                       required=True,
                                       readonly=True,
                                       states={'draft': [('readonly', False)]},
                                       domain="[('company_id', '=',"
                                              "company_id)]",
                                       ),
        # postagem fornecido
        'post_card_id': fields.many2one('sigepweb.post.card',
                                        string='Post Cards',
                                        required=True,
                                        readonly=True,
                                        states={'draft': [('readonly',
                                                           False)]},
                                        domain="[('contract_id', '=', "
                                               "contract_id)]"),

        'state': fields.selection([('draft', 'Draft'),
                                   ('confirmed', 'Confirmed'),
                                   ('in_transit', 'In Transit'),
                                   ('done', 'Done'),
                                   ('cancel', 'Cancel'),
                                   ], required=True, ),

        'picking_line': fields.one2many('stock.picking.out',
                                        'shipping_response_id',
                                        string='Pickings',
                                        readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        domain=[
                                            ('type', '=', 'out'),
                                            ('state', '=', 'done'),
                                        ]),

        'volume': fields.function(_compute_volume,
                                  type='float',
                                  string=u'Nº Volume',
                                  readonly=True,
                                  store=True, ),
        'weight': fields.function(_compute_weight,
                                  type='float',
                                  string=u'Weight',
                                  readonly=True, store=True, ),
        'weight_net': fields.function(_compute_weight_net,
                                      type='float',
                                      string=u'Net Weight',
                                      readonly=True, store=True,
                                      method=True),
    }
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'state': 'draft',
        'name': '/',
    }


