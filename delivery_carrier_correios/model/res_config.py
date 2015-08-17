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
from openerp.tools.translate import _

from pysigep_web.pysigepweb.webservice_atende_cliente import \
    WebserviceAtendeCliente
from pysigep_web.pysigepweb.pysigep_exception import ErroConexaoComServidor
from company import PRODUCAO, HOMOLOGACAO, LETTER, BOX, CILINDER


class SigepWebConfigSettings(orm.TransientModel):

    _name = 'sigepweb.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'sigepweb_company_id': fields.many2one('res.company',
                                               'Empresa',
                                               required=True),

        'contract_ids': fields.related('sigepweb_company_id',
                                       'sigepweb_contract_ids',
                                       string='Contracts',
                                       type='one2many',
                                       relation='sigepweb.contract'),

        'username': fields.related(
            'sigepweb_company_id', 'sigepweb_username',
            string='Login', type='char', required=True),

        'password': fields.related(
            'sigepweb_company_id', 'sigepweb_password',
            string='Password', type='char', required=True),

        'carrier_id': fields.related(
            'sigepweb_company_id', 'sigepweb_carrier_id',
            string='Carrier correios', type='many2one', required=True,
            relation='res.partner'),

        'contract_number': fields.related(
            'sigepweb_company_id', 'sigepweb_main_contract_number',
            string='Contract Number', type='char', required=True, size=10),

        'post_card_number': fields.related(
            'sigepweb_company_id', 'sigepweb_main_post_card_number',
            string='Post Card Number', type='char',
            required=True, size=10),

        'environment': fields.related('sigepweb_company_id',
                                      'sigepweb_environment',
                                      string='Ambiente',
                                      type='selection',
                                      selection=[PRODUCAO, HOMOLOGACAO],
                                      store=True,
                                      required=True),

        'plp_xml_path': fields.related('sigepweb_company_id',
                                       'sigepweb_plp_xml_path',
                                       string='PLP XML Path',
                                       type='char'),

        'package_type': fields.related('sigepweb_company_id',
                                       'sigepweb_package_type',
                                       string='Package type',
                                       type='selection',
                                       selection=(LETTER, BOX, CILINDER),
                                       store=True,
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

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    def _check_package_width(self, cr, uid, ids):
        for config in self.browse(cr, uid, ids):
            if config.package_width not in xrange(11, 105):
                return False
        return True

    def _check_package_height(self, cr, uid, ids):
        for config in self.browse(cr, uid, ids):
            if config.package_height not in xrange(2, 105):
                return False
        return True

    def _check_package_length(self, cr, uid, ids):
        for config in self.browse(cr, uid, ids):
            if config.package_type != 'cilinder' and config.package_length not\
                    in xrange(16, 105):
                return False
            elif config.package_type == 'cilinder' and config.package_length \
                    not in xrange(18, 105):
                return False

        return True

    def _check_package_diameter(self, cr, uid, ids):
        for config in self.browse(cr, uid, ids):
            if config.package_diameter not in xrange(5, 105):
                return False
        return True

    _defaults = {
        'sigepweb_company_id': _default_company,
    }

    _constraints = [
        (_check_package_width,
         'Package width out of range. Value must be between 11 cm to 105 cm.',
         ['package_width']),
        (_check_package_height,
         'Package height out of range. Value must be between 2 cm to 105 cm.',
         ['package_height']),
        (_check_package_length,
         'Package lenght out of range. Value must be between 18 cm to 105 cm '
         'to cilinder and 16 cm to 105 cm to others packages type.',
         ['package_length']),
        (_check_package_diameter,
         'Package diameter out of range. Value must be between 5 cm to 105 '
         'cm.',
         ['package_length']),
    ]

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

        a = [x.id for x in company.sigepweb_contract_ids]

        values = {
            'username': company.sigepweb_username,
            'password': company.sigepweb_password,
            'contract_number': company.sigepweb_main_contract_number,
            'post_card_number': company.sigepweb_main_post_card_number,
            'carrier_id': company.sigepweb_carrier_id.id,
            'contract_ids': [(4, x) for x in a],
            'environment': company.sigepweb_environment,
            'plp_xml_path': company.sigepweb_plp_xml_path,
            'package_type': company.sigepweb_package_type,
            'package_width': company.sigepweb_package_width,
            'package_height': company.sigepweb_package_height,
            'package_length': company.sigepweb_package_length,
            'package_diameter': company.sigepweb_package_diameter,
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
                sv = WebserviceAtendeCliente(config.environment)

                client = sv.busca_cliente(contract_number, post_card_number,
                                          username, password)

                contracts = self._update_contract(
                    cr, uid, client.contratos, config.sigepweb_company_id.id,
                    context=context)

                vals = {
                    'sigepweb_contract_ids': contracts,
                    'sigepweb_client_cnpj': client.cnpj,
                }

                pool = self.pool.get('res.company')
                pool.write(cr, uid, config.sigepweb_company_id.id, vals,
                           context=context)

            except ErroConexaoComServidor as e:
                raise osv.except_osv(_('Error!'), e.message)

    def _update_post_services(self, cr, uid, services):

        res = []

        for serv in services.values():

            pool = self.pool.get('sigepweb.post.service')
            post_service_id = pool.search(cr, uid, [('code', '=', serv.codigo)])

            vals = {
                'name': serv.nome,
                'code': serv.codigo,
                'identifier': serv.identificador,
                'details': serv.descricao,
                'image_chancela': serv.chancela.base_64_str_imagem
            }

            if not post_service_id:
                post_service_id = pool.create(cr, uid, vals)
            else:
                post_service_id = post_service_id[0]

            res.append(post_service_id)

        res = [(6, 0, res)]

        return res

    def _update_post_card(self, cr, uid, cards):

        res = []

        for card in cards.values():

            pool = self.pool.get('sigepweb.post.card')
            post_card_id = pool.search(cr, uid, [('number', '=', card.numero)])

            post_service_ids = self._update_post_services(
                cr, uid, card.servicos_postagem)

            vals = {
                'number': card.numero,
                'admin_code': card.codigo_admin,
                'post_service_ids': post_service_ids,
            }

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
                cr, uid, [('number', '=', contract.id_contrato),
                          ('company_id', '=', company_id)])

            post_card_ids = self._update_post_card(
                cr, uid, contract.cartoes_postagem)

            obj_company_id = \
                self.pool.get('res.company').browse(cr, uid, company_id)

            vals = {
                'name': '[%s] %s' % (contract.id_contrato, obj_company_id.legal_name),
                'year': contract.data_inicio.year,
                'number': contract.id_contrato,
                'post_card_ids': post_card_ids,
                'directorship_id': directorship_id,
                'company_id': company_id,
            }

            if not contract_id:
                contract_id = (0, 0, vals)
            else:
                # pegamos o primeiro id porque o contract e sempre unico
                contract_id = (1, contract_id[0], vals)

            res.append(contract_id)

        return res

