# -*- coding: utf-8 -*-

from openerp.osv import fields, orm

class shipping_response(orm.Model):
    _name = 'shipping.response'

    def generate_tracking_no(self, cr, uid, ids, context={}, error=True):
        pass

    def _compute_volume(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in ids:
            res[obj] = 0.00
        return res

    def _compute_weight(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in ids:
            res[obj] = 0.00
        return res

    def _compute_weight_net(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in ids:
            res[obj] = 0.00
        return res


    _columns = {
        'user_id': fields.many2one('res.users', 'Responsible',
            readonly=True, states={'draft': [('readonly', False)]}),
        'name': fields.char('Reference', required=True, readonly=True),
        'carrier_tracking_ref': fields.char('Tracking Ref.', readonly=True),

        'carrier_id': fields.many2one('res.partner',
              string='Carrier', readonly=True,
              states={'draft': [('readonly', False)]}),
        'carrier_responsible': fields.char('Carrier Responsible'),
        'date': fields.date('Date', require=True,
            readonly=True, states={'draft': [('readonly', False)]}
            ),
        'note': fields.text('Description / Remarks',
            readonly=True,
            states={'draft': [('readonly', False)]}),
        'state': fields.selection(
            [('draft', 'Draft'),
             ('confirmed', 'Confirmed'),
             ('in_transit', 'In Transit'),
             ('done', 'Done'),
             ('cancel', 'Cancel')
             ],
            required=True,
            ),
        'picking_line': fields.many2many(
            'stock.picking.out',
            'shipping_stock_picking_rel',
            'response_id',
            'picking_id',
            'Pickings',
            readonly=True,
            states={'draft': [('readonly', False)]},
            domain=[
                ('type', '=', 'out'),
                ('state', '=', 'done'),
                # ('carrier_id', '=', 'picking_line.carrier_id.partner_id'),
                # ('shipping_group', '=', False),
                ],
        ),
        # 'departure_picking_ids': fields.one2many('stock.picking.out',
        #                                          'shipping_response_id',
        #                                          'Departure Pickings',
        #     # readonly=True,
        #     # states={'draft': [('readonly', False)]}
        # ),
        'volume': fields.function(_compute_volume, type='float',
            string=u'Nº Volume',
            readonly=True, store=True,),
        'weight': fields.function(_compute_weight, type='float',
            string="Weight",
            readonly=True, store=True,),
        'weight_net': fields.function(_compute_weight_net, type='float',
            string="Net Weight",
            readonly=True, store=True,),
    }
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'state': 'draft',
        # 'selected': False,
        'name': '/',
    }


