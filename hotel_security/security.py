from openerp.osv import osv, fields
from datetime import datetime, timedelta

class security_note(osv.Model):
    _name = "hotel.security_note"

    def action_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)
    
    def action_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'confirmed'}, context=context)
    
    def action_void(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'void'}, context=context)
    
    _columns = {
                'security_note_id' : fields.char(string="Note Number", size=256, required=True),
                'note_datetime' : fields.datetime(string="Date Time"),
                'category' : fields.selection([('routine','Routine'),
                                               ('case','Case')], string="Category"),
                'note' : fields.text(string='Note'),
                'state' : fields.selection([('draft','Draft'),
                                            ('confirm','Confirmed'),
                                            ('void', 'Void')], string="State"),
                }
    
    _sql_constraints = [
        ('security_note_id_unique','UNIQUE(security_note_id)','Security Note ID is used!'),            
    ]
    
    _defaults = {
         'note_datetime' : fields.datetime.now,
         'security_note_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hotel.security.note'),
         'state': 'draft'
    }