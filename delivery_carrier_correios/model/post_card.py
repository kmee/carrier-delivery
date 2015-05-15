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


class PostCard(orm.Model):

    _name = 'sigepweb.post.card'

    _columns = {
        'number': fields.char(u'Número'),
        'admin_code': fields.char(u'Código Administrativo'),

        'post_service_ids': fields.many2many('sigepweb.post.service',
                                             'sigepweb_post_card_service_rel',
                                             'post_card_id', 'post_service_id',
                                             u'Serviços de Postagem'),
        'contract_id': fields.many2one('sigepweb.contract', u'Contrato'),
        'delivery_id': fields.one2many('delivery.carrier',
                                       'sigepweb_post_card_ids',
                                       'Carrier Delivery'),

    }

    _rec_name = 'number'



