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
from openerp.osv import orm, fields
from openerp.tools import file_open


class ResCompany(orm.Model):
    _inherit = 'res.company'

    # def _get_wsdl_url(self, cr, uid, ids, field_name, arg, context=None):
    #     wsdl_file, wsdl_path = file_open(
    #         'delivery_carrier_label_postlogistics/data/barcode_v2_2_wsbc.wsdl',
    #         pathinfo=True)
    #     wsdl_url = 'file://' + wsdl_path
    #     res = dict.fromkeys(ids, wsdl_url)
    #     return res

    _columns = {
        # 'sigepweb_wsdl_url': fields.function(
        #     _get_wsdl_url,
        #     string='WSDL URL',
        #     type='char'),
        'sigepweb_username': fields.char('Username'),
        'sigepweb_password': fields.char('Password'),
        'sigepweb_contract_number': fields.char('Contract Number'),
        'sigepweb_post_card_number': fields.char('Post Card Number'),
        'sigepweb_enviroment': fields.select(),
        # 'sigepweb_license_ids': fields.one2many(
        #     'sigepweb.license',
        #     'company_id',
        #     'PostLogistics Frankling License'),
        'sigepweb_logo': fields.binary('Company logo for PostLogistics'),
        'sigepweb_office': fields.char('Post office'),

        # 'sigepweb_default_label_layout': fields.many2one(
        #     'delivery.carrier.template.option', 'Default label layout'),
        # 'sigepweb_default_output_format': fields.many2one(
        #     'delivery.carrier.template.option', 'Default output format'),
        # 'sigepweb_default_resolution': fields.many2one(
        #     'delivery.carrier.template.option', 'Default resolution'),
    }
