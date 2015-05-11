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
from pysigep_web.pysigepweb.usuario import Usuario
from pysigep_web.pysigepweb.webservice_atende_cliente import \
    WebserviceAtendeCliente


_logger = logging.getLogger(__name__)


class SigepWebConfigSettings(orm.TransientModel):
    _name = 'sigepweb.config.settings'
    _inherit = 'res.config.settings'

    def _get_selection(self, cursor, user_id, context=None):
        return ((FabricaAmbiente.AMBIENTE_PRODUCAO, u'Produçao'),
                (FabricaAmbiente.AMBIENTE_HOMOLOGACAO, u'Homologação'))

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        # 'wsdl_url': fields.related(
        #     'company_id', 'postlogistics_wsdl_url',
        #     string='WSDL URL', type='char'),
        'username': fields.related('company_id', 'pysigepweb_username',
                                   string='Username', type='char'),
        'password': fields.related('company_id', 'pysigepweb_password',
                                   string='Password', type='char'),
        'admin_code': fields.related(
            'company_id', 'sigepweb_admin_code',
            string='Contract Number', type='char'),
        'contract_number': fields.related(
            'company_id', 'sigepweb_contract_number',
            string='Contract Number', type='char'),
        'post_card_number': fields.related(
            'company_id', 'sigepweb_post_card_number',
            string='Post Card Number', type='char'),
        'post_card_status': fields.char('Post Card Status'),

        'environment': fields.selection(
            ((WebserviceAtendeCliente.AMBIENTE_PRODUCAO, u'Produçao'),
             (WebserviceAtendeCliente.AMBIENTE_HOMOLOGACAO, u'Homologação')),
            string='Environment'),

        'logo': fields.related(
            'company_id', 'pysigepweb_logo',
            string='Company Logo on Post labels', type='binary',
            help="Optional company logo to show on label.\n"
                 "If using an image / logo, please note the following:\n"
                 "– Image width: 47 mm\n"
                 "– Image height: 25 mm\n"
                 "– File size: max. 30 kb\n"
                 "– File format: GIF or PNG\n"
                 "– Colour table: indexed colours, max. 200 colours\n"
                 "– The logo will be printed rotated counter-clockwise by 90°"
                 "\n"
                 "We recommend using a black and white logo for printing in "
                 " the ZPL2 format."
        ),
        'office': fields.related(
            'company_id', 'pysigepweb_office',
            string='Domicile Post office', type='char',
            help="Post office which will receive the shipped goods"),
    }

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    _defaults = {
        'company_id': _default_company,
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

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        # update related fields
        values = {'currency_id': False}
        if not company_id:
            return {'value': values}
        company = self.pool.get('res.company').browse(
            cr, uid, company_id, context=context)

        values = {
            'username': company.sigepweb_username,
            'password': company.sigepweb_password,
            'contract_number': company.sigepweb_contract_number,
            'post_card_number': company.sigepweb_office,
            'sigepweb_admin_code': company.sigepweb_admin_code,
            'logo': company.sigepweb_logo,
            'office': company.sigepweb_office,
        }
        return {'value': values}





