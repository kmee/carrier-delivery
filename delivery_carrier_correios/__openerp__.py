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
{
    'name': 'Carrier Delivery Correios SigepWeb WebService',
    'version': '1.1',
    'author': "KMEE",
    'category': 'version',
    'complexity': 'normal',
    'depends': [
        'base_delivery_carrier_label',
        'tr_barcode_on_picking',
    ],
    'description': """
    Carrier Delivery Correios Sigepweb WebService
    """,
    'website': 'http://www.kmee.com.br/',
    'data': [
        'view/res_config_view.xml',
        'view/delivery_view.xml',
        'view/post_card_view.xml',
        'view/post_service_view.xml',
    ],
    'tests': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': True,
    'external_dependencies': {
        'python': ['suds'],
    }
}
