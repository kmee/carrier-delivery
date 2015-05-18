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

from openerp.osv import orm, fields


class Contract(orm.Model):
    _name = 'sigepweb.contract'

    _columns = {
        'number': fields.char(u'Número'),
        'post_card_ids': fields.one2many('sigepweb.post.card',
                                         'contract_id',
                                         u'Cartão de Postagem'),
        'directorship_id': fields.many2one('sigepweb.directorship',
                                           'Diretoria'),
        'delivery_id': fields.one2many('delivery.carrier',
                                       'sigepweb_contract_ids',
                                       'Carrier Delivery'),
        'company_id': fields.many2one('res.company', u'Empresa'),
        'shipping_response_ids': fields.one2many('shipping.response',
                                                 'contract_id',
                                                 string='Shipping Response')
    }

    _rec_name = 'number'


