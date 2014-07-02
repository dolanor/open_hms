from osv import fields
from osv import osv
import time
#import ir
from mx import DateTime
import datetime
import pooler
from tools import config
import netsvc


class cancel_foilo_wizard(osv.osv_memory):
     _name = 'cancel.foilo.wizard'

     _description ='Cancel Wizard'
     
     _columns = {
                 'desc':fields.text('Description',readonly=True),
                 }
    
     def default_get(self, cr, uid, fields, context=None):
        print "default_get================="
        if context is None: context = {}
        # no call to super!
        res = {}
        move_ids = context.get('active_ids', [])
        print move_ids,"move_ids"
        print fields,"fields"
        if not move_ids or not context.get('active_model') == 'hotel.folio':
            return res
        move_ids = self.pool.get('hotel.folio').browse(cr, uid, move_ids, context=context)
        print move_ids,"move_ids============="
        for room in move_ids[0].room_lines:
            if move_ids[0].checkin_date != room.checkin_date or move_ids[0].checkout_date != room.checkout_date:
                raise osv.except_osv ('Error !','Checkin and Checkout at room line level should be same as that of main form !')
        today = time.strftime('%Y-%m-%d %H:%M:%S')
        if today > move_ids[0].checkin_date:
            desc = "Checkin time is Passed still want to cancel this folio."
        else:
            desc = "Do You want to continue ?"
        if 'desc' in fields:
            res.update(desc=desc)
        print "desc",desc
        return res
     
     def cancel_wizard(self, cr, uid, ids, data, context=None):
        print context,"context",data
        folio_object = self.browse(cr,uid,data['active_id'])
        cancel_data = self.pool.get('hotel.folio').action_cancel(cr, uid, data['active_ids'])
        print cancel_data,"cancel_data==============="
        return {'type': 'ir.actions.act_window_close'}
        
        
cancel_foilo_wizard()