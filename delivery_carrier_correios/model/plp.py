# -*- coding: utf-8 -*-
# #############################################################################
#
# Brazillian Carrier Correios Sigep WEB
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author: Rodolfo Bertozo <rodolfo.bertozo@kmee.com.br>
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


class Plp(orm.Model):
    _name = 'sigepweb.plp'

    _columns = {
        'contract': fields.char(u'Contrato'),
        'client_id': fields.many2one('res.company', u'Cliente'),
        'plp_number': fields.char(u'Num PLP'),
        # 'stock_picking_out_ids': fields.one2many('stock.picking.out', 'plp_id', u'Ordens de entrega'),
        'delivery_date': fields.date(u'Data de Entrega'),
        'x_barcode_id': fields.many2one('tr.barcode', u'BarCode'),
    }
