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

from openerp.osv import orm, fields
from pysigep_web.pysigepweb.webservice_atende_cliente import \
    WebserviceAtendeCliente
from pysigep_web.pysigepweb.dimensao import Dimensao

PRODUCAO = (WebserviceAtendeCliente.AMBIENTE_PRODUCAO, u'Produçao')
HOMOLOGACAO = (WebserviceAtendeCliente.AMBIENTE_HOMOLOGACAO, u'Homologação')

# Codigo para tipos de pacotes do correio
LETTER = (Dimensao.TIPO_ENVELOPE, 'Letter')
BOX = (Dimensao.TIPO_CAIXA, 'Box')
CILINDER = (Dimensao.TIPO_CILINDRO, 'Cilinder')


class ResCompany(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'sigepweb_client_cnpj': fields.char('Client CNPJ'),
        'sigepweb_username': fields.char('Username'),
        'sigepweb_password': fields.char('Password'),
        'sigepweb_carrier_id': fields.many2one('res.partner',
                                               'Partner Carrier'),
        'sigepweb_main_contract_number': fields.char('Main Contract'),
        'sigepweb_main_post_card_number': fields.char('Main Post Card'),
        'sigepweb_contract_ids': fields.one2many('sigepweb.contract',
                                                 'company_id',
                                                 string='Contract',
                                                 readonly=True,
                                                 ondelete="cascade"),
        'sigepweb_environment': fields.selection((HOMOLOGACAO, PRODUCAO),
                                                 string='Environment',
                                                 required=True),
        'shipping_response_ids': fields.one2many('shipping.response',
                                                 'company_id',
                                                 string='Shipping Response'),
        'sigepweb_plp_xml_path': fields.char('PLP XML Path'),

        'sigepweb_package_type': fields.selection((LETTER, BOX, CILINDER),
                                                  string='Package type'),
        'sigepweb_package_width': fields.integer('Package width'),
        'sigepweb_package_height': fields.integer('Package height'),
        'sigepweb_package_length': fields.integer('Package length'),
        'sigepweb_package_diameter': fields.integer('Package diameter'),
    }

    _defaults = {
        'sigepweb_environment': WebserviceAtendeCliente.AMBIENTE_HOMOLOGACAO,
        'sigepweb_package_type': BOX[0],
        'sigepweb_package_width': 11,
        'sigepweb_package_height': 2,
        'sigepweb_package_length': 16,
        'sigepweb_package_diameter': 5,
    }