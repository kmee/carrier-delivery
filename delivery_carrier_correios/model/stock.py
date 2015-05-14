# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author: Rodolfo Bertozo <rodolfo.bertozo@kmee.com.br
#
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
from openerp.tools.translate import _


class StockPickingOut(orm.Model):
	_inherit = 'stock.picking.out'

	_columns = {
		"x_barcode_id": fields.many2one('tr.barcode', 'BarCode')
	}

	def action_generate_carrier_label(self, cr, uid, ids, context=None):
		result = {}
		result = {
			'type': 'ir.actions.report.xml',
			'report_name': 'shipping.label.webkit'
		}
		return result


class StockPicking(orm.Model):
	_inherit = 'stock.picking'

	_columns = {
		"x_barcode_id": fields.many2one('tr.barcode', 'BarCode')
	}
