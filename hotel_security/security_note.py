from openerp.osv import osv, fields
from datetime import datetime, timedelta

class security_note(osv.Model):
    _name = "hotel.security.note"

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
    def note_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)
    
    def note_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'confirmed'}, context=context)
    
    def note_void(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'void'}, context=context)
    
    def action_set_to_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService('workflow')
        for id in ids:
            wf_service.trg_create(uid, self._name, id, cr)
        return True
    
    
    _columns = {
                'security_note_id' : fields.char(string="Note Number", size=256, required=True),
                'note_datetime' : fields.datetime(string="Date Time"),
                'category' : fields.selection([('routine','Routine'),
                                               ('case','Case')], string="Category"),
                'note' : fields.text(string='Note'),
                'user': fields.many2one('res.users', 'On Duty', select=True, readonly=True),
                'state' : fields.selection([('draft','Draft'),
                                            ('confirmed','Confirmed'),
                                            ('void', 'Void')], string="State"),
                }
    
    _sql_constraints = [
        ('security_note_id_unique','UNIQUE(security_note_id)','Security Note ID is used!'),            
    ]
    
    _defaults = {
         'note_datetime' : fields.datetime.now,
         'category' : 'routine',
         'security_note_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hotel.security.note'),
         'user': lambda obj, cr, uid, context: uid,
         'state': 'draft'
    }