from openerp.osv import osv, fields
from datetime import datetime, timedelta

class security_parking(osv.Model):
    _name = "hotel.security.parking"

    ''' def note_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def note_confirm(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'confirm'})
        return True
    
    def note_void(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'void'})
        return True
    '''
    def parking_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)
    
    def parking_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'confirmed'}, context=context)
    
    def parking_void(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'void'}, context=context)
    
    _columns = {
                'security_parking_id' : fields.char(string="Note Number", size=256, required=True, states={'draft':[('readonly', False)]}, help=''),
                'in_datetime' : fields.datetime(string="Incoming Date Time", states={'draft':[('readonly', False)]}, help=''),
                'out_datetime' : fields.datetime(string="Outgoing Date Time", states={'draft':[('readonly', False)]}, help=''),
                'type' : fields.selection([('guest','Guest'),
                                           ('taxi','Taxi'),
                                           ('intern','Intern'),
                                           ('parking','Parking')],required=True, string="Type", states={'draft':[('readonly', False)]}, help=''),
                'odo_in' : fields.integer('Odo Incoming', size=64, readonly=True, states={'draft':[('readonly', False)]}, help=''),
                'odo_out' : fields.integer('Odo Outgoing', size=64, readonly=True, states={'draft':[('readonly', False)]}, help=''),
                #'driver_id': fields.many2one('hr.employee', string="Driver", ondelete='set null', select=True, readonly=True, states={'draft':[('readonly', False)]}),
                #'driver_ids': fields.many2one('hr.employee', "Driver", required=True, select=True, readonly=True, states={'draft':[('readonly', False)]}),
                'driver_id': fields.many2one('hr.employee', 'Driver', select=True),
                'passengers': fields.text('Passengers', readonly=True, states={'draft':[('readonly', False)]}),
                'goods_memo': fields.text('Goods Memo', readonly=True, states={'draft':[('readonly', False)]}),
                'parking_money': fields.integer('Parking Money', size=64, readonly=True, states={'draft':[('readonly', False)]}, help=''),


                'user': fields.many2one('res.users', 'On Duty', select=True, readonly=True),
                'state' : fields.selection([('draft','Draft'),
                                            ('confirmed','Confirmed'),
                                            ('void','Void')], string="State", states={'draft':[('readonly', False)]}, help=''),
                }
    
    _sql_constraints = [
        ('security_parking_id_unique','UNIQUE(security_parking_id)','Security Parking ID is used!'),            
    ]
    
    _defaults = {
         'in_datetime' : fields.datetime.now,
         'out_datetime' : fields.datetime.now,
         'type': 'guest',
         'security_parking_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hotel.security.parking'),
         'user': lambda obj, cr, uid, context: uid,
         'state': 'draft'
    }