# -*- coding: utf-8 -*-
# #############################################################################
#
#    Brazillian Carrier Correios Sigep WEB
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Mileo <mileo@kmee.com.br>
#    @author: Michell Stuttgart <michell.stuttgartx@kmee.com.br>
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
import logging

from openerp.osv import orm, fields
from openerp.tools.translate import _

from pysigep_web.pysigepweb.ambiente import FabricaAmbiente
from pysigep_web.pysigepweb.webservice_atende_cliente import \
    WebserviceAtendeCliente
from pysigep_web.pysigepweb.pysigep_exception import ErroConexaoComServidor

_logger = logging.getLogger(__name__)


class SigepWebConfigSettings(orm.TransientModel):
    _name = 'sigepweb.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'sigepweb_company_id': fields.many2one('res.company',
                                               'Company',
                                               required=True),

        'contract_ids': fields.related('sigepweb_company_id',
                                       'sigepweb_contract_ids',
                                       string=u'Contratos',
                                       type='one2many',
                                       relation='sigepweb.contract'),

        'username': fields.related('sigepweb_company_id', 'sigepweb_username',
                                   string=u'Login', type='char'),
        'password': fields.related('sigepweb_company_id', 'sigepweb_password',
                                   string=u'Senha', type='char'),
        'contract_number': fields.related(
            'sigepweb_company_id', 'sigepweb_main_contract_number',
            string=u'Número do Contrato', type='char'),
        'post_card_number': fields.related(
            'sigepweb_company_id', 'sigepweb_main_post_card_number',
            string=u'Número do Cartão de Postagem', type='char'),

        'environment': fields.selection(
            ((WebserviceAtendeCliente.AMBIENTE_PRODUCAO, u'Produçao'),
             (WebserviceAtendeCliente.AMBIENTE_HOMOLOGACAO, u'Homologação')),
            string='Environment'),
    }

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    _defaults = {
        'sigepweb_company_id': _default_company,
        'environment': FabricaAmbiente.AMBIENTE_HOMOLOGACAO,
    }

    def create(self, cr, uid, values, context=None):
        rec_id = super(SigepWebConfigSettings, self).create(
            cr, uid, values, context=context)
        # Hack: to avoid some nasty bug, related fields are not written
        # upon record creation.  Hence we write on those fields here.
        vals = {}
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.related) and fname in values:
                vals[fname] = values[fname]
        self.write(cr, uid, [rec_id], vals, context)
        return rec_id

    def onchange_company_id(self, cr, uid, ids, sigepweb_company_id, context=None):
        # update related fields
        values = {'currency_id': False}

        if not sigepweb_company_id:
            return {'value': values}

        company = self.pool.get('res.company').browse(
            cr, uid, sigepweb_company_id, context=context)

        values = {
            'username': company.sigepweb_username,
            'password': company.sigepweb_password,
            'contract_number': company.sigepweb_main_contract_number,
            'post_card_number': company.sigepweb_main_post_card_number,
            'contract_ids': [x.id for x in company.sigepweb_contract_ids],
        }
        return {'value': values}

    def update_sigepweb_webservice_options(self, cr, uid, ids, context=None):

        for config in self.browse(cr, uid, ids, context=context):

            username = config.sigepweb_company_id.sigepweb_username
            password = config.sigepweb_company_id.sigepweb_password
            contract_number = \
                config.sigepweb_company_id.sigepweb_main_contract_number
            post_card_number = \
                config.sigepweb_company_id.sigepweb_main_post_card_number

            try:
                print u'[INFO] Iniciando Serviço de Atendimento ao  Cliente'
                sv = WebserviceAtendeCliente(config.environment)

                print 'Cosultando dados do cliente'
                cliente = sv.busca_cliente(contract_number, post_card_number,
                                           username, password)

                print cliente.nome
                print cliente.login

                contratos = self._update_contract(
                    cr, uid, cliente.contratos, config.sigepweb_company_id.id,
                    context=context)

                vals = {
                    'sigepweb_contract_ids': contratos
                }

                pool = self.pool.get('res.company')
                pool.write(cr, uid, config.sigepweb_company_id.id, vals)

            except ErroConexaoComServidor as e:
                print e.message
                return

    def _update_post_services(self, cr, uid, services, context=None):

        res = []

        for serv in services.values():

            pool = self.pool.get('sigepweb.post.service')
            post_service_id = pool.search(cr, uid, [('code', '=', serv.codigo)])

            vals = {
                'name': serv.nome,
                'code': serv.codigo,
                'details': serv.descricao,
            }

            if not post_service_id:
                post_service_id = (0, 0, vals)
            else:
                post_service_id = (1, post_service_id[0], vals)

            res.append(post_service_id)

        return res

    def _update_post_card(self, cr, uid, cards, context=None):

        res = []

        for card in cards.values():

            post_service_ids = self._update_post_services(
                cr, uid, card.servicos_postagem, context=context)

            vals = {
                'number': card.numero,
                'admin_code': card.codigo_admin,
                'post_service_ids': post_service_ids,
            }

            pool = self.pool.get('sigepweb.post.card')
            post_card_id = pool.search(cr, uid, [('number', '=', card.numero)])

            if not post_card_id:
                post_card_id = (0, 0, vals)
            else:
                post_card_id = (1, post_card_id[0], vals)

            res.append(post_card_id)

        return res

    def _update_contract(self, cr, uid, contracts, company_id, context=None):

        res = []

        for contract in contracts.values():

            pool = self.pool.get('sigepweb.directorship')
            directorship_id = pool.search(
                cr, uid, [('code', '=', contract.diretoria.codigo)])

            vals = {
                'code': contract.diretoria.codigo,
                'acronym': contract.diretoria.sigla,
                'details': contract.diretoria.descricao,
            }

            if not directorship_id:
                directorship_id = pool.create(cr, uid, vals, context=context)
            else:
                directorship_id = directorship_id[0]
                pool.write(cr, uid, directorship_id, vals, context=context)

            pool = self.pool.get('sigepweb.contract')
            contract_id = pool.search(
                cr, uid, [('number', '=', contract.id_contrato)])

            post_card_ids = self._update_post_card(
                cr, uid, contract.cartoes_postagem, context=context)

            vals = {
                'number': contract.id_contrato,
                'post_card_ids': post_card_ids,
                'directorship_id': directorship_id,
                'rescompany_id': company_id,
            }

            if not contract_id:
                contract_id = (0, 0, vals)
            else:
                # pegamos o primeiro id porque o contract e sempre unico
                contract_id = (1, contract_id[0], vals)

            res.append(contract_id)

        return res