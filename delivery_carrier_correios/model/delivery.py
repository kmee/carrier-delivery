# -*- coding: utf-8 -*-
# #############################################################################
#
# Brazillian Carrier Correios Sigep WEB
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


class DeliveryCarrier(orm.Model):
    """ Add service group """
    _inherit = 'delivery.carrier'

    _columns = {

        'sigepweb_contract_ids': fields.many2one('sigepweb.contract',
                                                 'Contract'),
        'sigepweb_post_card_ids': fields.related(
            'sigepweb_contract_ids', 'post_card_ids', type='many2one',
            relation='sigepweb.post.card', string='Post Cards',
            domain="[('contract_id', '=', sigepweb_contract_ids)]"),

        'sigepweb_post_service_ids': fields.related(
            'sigepweb_post_card_ids', 'post_service_ids', type='many2one',
            relation='sigepweb.post.service', string='Post Services',
            domain="[('post_card_id', '=', sigepweb_post_card_ids)]"),
    }

    def _get_carrier_type_selection(self, cr, uid, context=None):
        """ Add postlogistics carrier type """
        res = super(DeliveryCarrier, self)._get_carrier_type_selection(
            cr, uid, context=context)
        res.append(('sigepweb', 'Correios SigepWeb'))
        return res

    def onchange_sigepweb_post_service_ids(self, cr, uid, ids,
                                           sigepweb_post_service_ids,
                                           context=None):
        res = {'value': {}}

        if not sigepweb_post_service_ids:
            return res

        post_service = self.pool.get('sigepweb.post.service').browse(
            cr, uid, sigepweb_post_service_ids, context=context)

        values = {
            'code': post_service.code,
            'description': post_service.details,
        }

        res['value'].update(values)

        return res