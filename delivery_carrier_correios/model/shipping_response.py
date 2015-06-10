# -*- coding: utf-8 -*-
# #############################################################################
#
#    Brazillian Carrier Correios Sigep WEB
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
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
import os
import math

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
from pysigep_web.pysigepweb.pysigep_exception import ErroConexaoComServidor, ErroValidacaoXML
from pysigep_web.pysigepweb.etiqueta import Etiqueta
from pysigep_web.pysigepweb.resposta_busca_cliente import Cliente


class ShippingResponse(orm.Model):
    _name = 'shipping.response'

    def copy(self, cr, uid, ids, default=None, context=None):

        if default is None:
            default = {}

        vals = {
            'picking_line': False,
            'carrier_tracking_ref': '',
            'name': '/',
        }

        default.update(vals)
        return super(ShippingResponse, self).copy(
            cr, uid, ids, default=default, context=context)

    def _compute_volume(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in ids:
            obj_ship = self.browse(cr, uid, obj, context=context)
            res[obj] = len(obj_ship.picking_line)

        return res

    def _compute_weight(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in ids:
            res[obj] = 0.00

            obj_ship = self.browse(cr, uid, obj, context=context)
            for picking in obj_ship.picking_line:
                res[obj] += picking.weight * int(picking.quantity_of_volumes)

        return res

    def _compute_weight_net(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in ids:
            res[obj] = 0.00

            obj_ship = self.browse(cr, uid, obj, context=context)
            for picking in obj_ship.picking_line:
                res[obj] += picking.weight_net * int(picking.quantity_of_volumes)

        return res

    def action_shipment_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def action_shipment_confirm(self, cr, uid, ids, context=None):
        if self.generate_tracking_no(cr, uid, ids, context=context):
            self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
            return True
        return False

    def action_shipment_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def action_shipment_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def generate_tracking_no(self, cr, uid, ids, context=None):

        for ship in self.browse(cr, uid, ids):

            company_id = ship.company_id
            contract_id = ship.contract_id
            post_card_id = ship.post_card_id

            # Expressao regular para buscar apenas numeros no numero de endereco
            reg = re.compile('[0-9]*')
            numero = ''.join(reg.findall(company_id.number))

            # Endereco do remetente
            obj_endereco = Endereco(logradouro=company_id.street,
                                    numero=int(numero),
                                    bairro=company_id.district,
                                    cep=int(company_id.zip.replace('-', '')),
                                    cidade=company_id.l10n_br_city_id.name,
                                    uf=company_id.state_id.code,
                                    complemento=company_id.street2)

            # Primeira tag do XML
            obj_tag_plp = TagPLP(post_card_id.number)

            # Criamos o cliente que sera usado para consultar o webservice
            cliente = Cliente(company_id.name,
                              company_id.sigepweb_username,
                              company_id.sigepweb_password,
                              company_id.cnpj_cpf)

            # Criamos a tag remetente do xml
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

            if not ship.tracking_pack_line:
                msg = "A PLP deve possuir pelo menos uma Ordem de Entrega. " \
                      "Por favor adicione uma Ordem de Entrega!"
                raise osv.except_osv(_('Error!'), msg)

            for tracking_pack in ship.tracking_pack_line:

                # O stock.picking e o mesmo para todas as linhas
                picking = tracking_pack.move_ids[0].picking_id
                partner_id = picking.partner_id
                numero = ''.join(reg.findall(partner_id.number))

                # Endereco do destinatario
                obj_endereco = Endereco(logradouro=partner_id.street,
                                        numero=int(numero),
                                        bairro=partner_id.district,
                                        cep=partner_id.zip.replace('-', ''),
                                        cidade=partner_id.l10n_br_city_id.name,
                                        uf=partner_id.state_id.code,
                                        complemento=partner_id.street2)

                # Criamos a tag com os dados do destinatario
                obj_destinatario = TagDestinatario(partner_id.name,
                                                   obj_endereco,
                                                   telefone=partner_id.phone
                                                            or False)

                # Para encomendas do tip PAC41068, devemos fornecer a série
                # e o numero da fatura
                if picking.carrier_id.sigepweb_post_service_id.code == '41068':

                    nfe_number = picking.invoice_id.internal_number
                    nfe_serie = picking.invoice_id.document_serie_id.code

                    if nfe_number == '':
                        msg = "A ordem de entrega deve estar faturada antes " \
                              "de entrar na PLP!"
                        raise osv.except_osv(_('Error!'), msg)

                    obj_nacional = TagNacionalPAC41068(obj_endereco,
                                                       nfe_number,
                                                       nfe_serie)
                else:
                    obj_nacional = TagNacional(obj_endereco)

                # Criamos a tag de servico adicional
                obj_servico_adicional = TagServicoAdicional()

                # Calculamos dimensoes do pacote a partir do seu volume
                weight = 0
                volume = 0

                for line in tracking_pack.move_ids:
                    if not line.product_id:
                        continue
                    weight += (line.product_id.weight or 0.0) * line.product_qty
                    volume += (line.product_id.volume or 0.0) * line.product_qty

                volume_cm = volume * 100000
                peso_volumetrico = 0

                if volume_cm > 60000:
                    peso_volumetrico = math.ceil(volume_cm / 6000)

                # Calculamos o peso considerado. O OpenERP fornece peso em
                # kilogramas
                peso_considerado = max(weight, peso_volumetrico) * 1000
                aresta = int(math.ceil(volume_cm ** (1 / 3.0)))

                # Criamos um objeto dimensao
                obj_dimensao_objeto = TagDimensaoObjeto(Caixa(aresta, aresta,
                                                              aresta))

                # Criamos um servico postagem que representa o servico a ser
                # utilizado
                sv_postagem = ServicoPostagem(
                    picking.carrier_id.sigepweb_post_service_id.code)

                etq = Etiqueta(tracking_pack.serial)
                lista_etiqueta += [Etiqueta(tracking_pack.serial)]

                obj_postal = TagObjetoPostal(
                    obj_destinatario=obj_destinatario,
                    obj_nacional=obj_nacional,
                    obj_dimensao_objeto=obj_dimensao_objeto,
                    obj_servico_adicional=obj_servico_adicional,
                    obj_servico_postagem=sv_postagem,
                    obj_etiqueta=etq,
                    peso=float(peso_considerado),
                    status_processamento=0)

                lista_obj_postal.append(obj_postal)

            # Finalmente criamos a tag root do xml
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
                    'name': 'PLP/' + str(plp.id_plp_cliente),
                    'carrier_tracking_ref': plp.id_plp_cliente,
                }

                # Definimos o path para salvar o xml da PLP
                path = company_id.sigepweb_plp_xml_path + \
                    company_id.sigepweb_environment + '/'

                if not os.path.exists(path):
                    #Criando diretorio homlogacao ou producao
                    os.mkdir(path)

                path += 'PLP' + str(plp.id_plp_cliente)

                # Salvando xml da PLP em disco
                plp.salvar_xml(path)

                return self.write(cr, uid, ship.id, vals, context=context)

            except IOError as e:
                print e.message
                raise osv.except_osv(_('Error!'), e.strerror)
            except ErroConexaoComServidor as e:
                print e.message
                raise osv.except_osv(_('Error!'), e.message)
            except ErroValidacaoXML as e:
                print e.message
                raise osv.except_osv(_('Error!'), e.message)

        return False

    def onchange_company_id(self, cr, uid, ids, sigepweb_company_id, context=None):

        res = {'value': {}}

        if sigepweb_company_id:
            company = self.pool.get('res.company').browse(
                cr, uid, sigepweb_company_id, context=context)

            values = {'carrier_id': company.sigepweb_carrier_id.id}

            res['value'].update(values)

        return res

    _columns = {

        'company_id': fields.many2one('res.company',
                                      string='Company',
                                      required=True,
                                      readonly=True,
                                      states={'draft': [('readonly', False)]}),

        'user_id': fields.many2one('res.users',
                                   'Responsible',
                                   readonly=True,
                                   states={'draft': [('readonly', False)]}),

        'name': fields.char('Reference', required=True, readonly=True),

        'carrier_tracking_ref': fields.char('Tracking Ref.', readonly=True),

        'carrier_id': fields.related('company_id',
                                     'sigepweb_carrier_id',
                                     string='Carrier',
                                     type='many2one',
                                     relation='res.partner',
                                     readonly=True),

        'carrier_responsible': fields.many2one('res.partner',
                                               string='Carrier Responsible',
                                               readonly=True,
                                               states={'draft': [('readonly', False)]}),

        'date': fields.date('Date', require=True, readonly=True,
                            states={'draft': [('readonly', False)]}),

        'note': fields.text('Description / Remarks', readonly=True,
                            states={'draft': [('readonly', False)]}),

        'contract_id': fields.many2one('sigepweb.contract',
                                       string='Contract',
                                       required=True,
                                       readonly=True,
                                       states={'draft': [('readonly', False)]},
                                       domain="[('company_id', '=',"
                                              "company_id)]",
                                       ),

        'post_card_id': fields.many2one('sigepweb.post.card',
                                        string='Post Cards',
                                        required=True,
                                        readonly=True,
                                        states={'draft': [('readonly',
                                                           False)]},
                                        domain="[('contract_id', '=', "
                                               "contract_id)]"),

        'picking_line': fields.one2many('stock.picking.out',
                                        'shipping_response_id',
                                        string='Pickings',
                                        readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        domain=[
                                            ('type', '=', 'out'),
                                            ('state', '=', 'done'),
                                        ]),

        'tracking_pack_line': fields.one2many('stock.tracking',
                                              'shipping_response_id',
                                              string='Tracking Packs',
                                              readonly=True,
                                              required=True,
                                              states={
                                                  'draft': [('readonly', False)]
                                              }),

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

        'state': fields.selection([('draft', 'Draft'),
                                   ('confirmed', 'Confirmed'),
                                   ('done', 'Done'),
                                   ('cancel', 'Cancel'),
                                   ], required=True, string=u'Situation'),
    }
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'state': 'draft',
        'name': '/',
    }


