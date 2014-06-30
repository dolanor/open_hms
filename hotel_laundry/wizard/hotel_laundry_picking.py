from osv import fields
from osv import osv
import time
from mx import DateTime
import datetime
import pooler
from tools import config
import netsvc
import decimal_precision as dp
from tools.translate import _

class hotel_laundry_picking(osv.osv_memory):
    """Hotel laundry picking is use to show all the product according to service in picking generation"""
    _name = 'hotel.laundry.picking'
    _description = 'Return Picking'
    
    _columns = {
        'product_return_moves' : fields.one2many('hotel.laundry.picking.memory', 'wizard_id', 'Moves'),
        'invoice_state': fields.selection([('2binvoiced', 'To be refunded/invoiced'), ('none', 'No invoicing')], 'Invoicing',required=True),
     }
    
    def default_get(self, cr, uid, fields, context=None):
        """
         To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary with default values for all field in ``fields``
        """
        result1 = []
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..",context
        if context is None:
            context = {}
        res = super(hotel_laundry_picking, self).default_get(cr, uid, fields, context=context)
        laundry_record_id = context and context.get('active_id', False) or False
        print ">>>>>>>>>>>>>>>>>>>>>>>>>..",laundry_record_id
        laundry_obj=self.pool.get('laundry.management')
        pick_obj = self.pool.get('stock.picking')
        laudnry_id=laundry_obj.browse(cr,uid,laundry_record_id)
        
        record_ids=pick_obj.search(cr,uid,[('origin','=',laudnry_id.name)])
        for rec in record_ids:
            records=pick_obj.browse(cr,uid,rec)
            if records.type=='out':
                record_id=records.id
            
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        if pick:
            return_history = self.get_return_history(cr, uid, record_id, context)       
            for line in pick.move_lines:
                qty = line.product_qty - return_history[line.id]
                if qty > 0:
                    result1.append({'product_id': line.product_id.id, 'quantity': qty,'move_id':line.id})
#                else:
##                    raise osv.except_osv(_('Warning !'), _("You have not sufficient product to return!"))
#                    laundry_obj.write(cr,uid,laundry_record_id,{'state':'laundry_returned'})
#                    return {'type': 'ir.actions.act_window_close'}
            
            if 'invoice_state' in fields:
                if pick.invoice_state=='invoiced':
                    res.update({'invoice_state': '2binvoiced'})
                else:
                    res.update({'invoice_state': 'none'})        
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': result1})
        return res
    
    def get_return_history(self, cr, uid, pick_id, context=None):
        """ 
         Get  return_history.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param pick_id: Picking id
         @param context: A standard dictionary
         @return: A dictionary which of values.
        """
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, pick_id, context=context)
        return_history = {}
        for m  in pick.move_lines:
            if m.state == 'done':
                return_history[m.id] = 0
                for rec in m.move_history_ids2:
                    return_history[m.id] += (rec.product_qty * rec.product_uom.factor)
            else:
                raise osv.except_osv(_('Warning !'), _("Please process the delivery order shipment-%s first!")%(pick.name)) 
        return return_history
    
    def do_method(self, cr, uid, ids, context=None):
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>this call when cancel button is hit"
        if context is None:
            context = {} 
        laundry_record_id = context and context.get('active_id', False) or False
        laundry_obj=self.pool.get('laundry.management')
        laundry_obj.write(cr,uid,laundry_record_id,{'state':'laundry_returned'})
        return {'type': 'ir.actions.act_window_close'}
    
    def create_returns(self, cr, uid, ids, context=None):
        """ 
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        count=0
        if context is None:
            context = {} 
        laundry_record_id = context and context.get('active_id', False) or False
        laundry_obj=self.pool.get('laundry.management')
        pick_obj = self.pool.get('stock.picking')
        laundry_id=laundry_obj.browse(cr,uid,laundry_record_id)
        
        if laundry_id.request_type=='from_room':
            count=-1
        
        record_ids=pick_obj.search(cr,uid,[('origin','=',laundry_id.name)])
        for rec in record_ids:
            records=pick_obj.browse(cr,uid,rec)
            count=count+1
            if records.type=='out':
                record_id=records.id
        
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('hotel.laundry.picking.memory')
        wf_service = netsvc.LocalService("workflow")
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        new_picking = None
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        set_invoice_state_to_none = True
        returned_lines = 0
        
#        Create new picking for returned products
        if pick.type=='out':
            new_type = 'in'
        elif pick.type=='in':
            new_type = 'out'
        else:
            new_type = 'internal'
        new_picking = pick_obj.copy(cr, uid, pick.id, {'name':'%s-return/%s' % (pick.name,count),
                'move_lines':[], 'state':'draft', 'type':new_type,
                'date':date_cur, 'invoice_state':data['invoice_state'],})
        
        val_id = data['product_return_moves']
        for v in val_id:
            data_get = data_obj.browse(cr, uid, v, context=context)
            mov_id = data_get.move_id.id
            new_qty = data_get.quantity
            move = move_obj.browse(cr, uid, mov_id, context=context)
            new_location = move.location_dest_id.id
            returned_qty = move.product_qty
            for rec in move.move_history_ids2:
                returned_qty -= rec.product_qty

            if returned_qty != new_qty:
                set_invoice_state_to_none = False
            if new_qty:
                returned_lines += 1
                new_move=move_obj.copy(cr, uid, move.id, {
                    'product_qty': new_qty,
                    'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id,
                        new_qty, move.product_uos.id),
                    'picking_id':new_picking, 'state':'draft',
                    'location_id':new_location, 'location_dest_id':move.location_id.id,
                    'date':date_cur,})
                move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4,new_move)]})
        if not returned_lines:
            laundry_obj.write(cr,uid,laundry_record_id,{'state':'laundry_returned'})
            raise osv.except_osv(_('Warning !'), _("Please specify at least one non-zero quantity!"))

        if set_invoice_state_to_none:
            pick_obj.write(cr, uid, [pick.id], {'invoice_state':'none'})
        wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
        pick_obj.force_assign(cr, uid, [new_picking], context)
        # Update view id in context, lp:702939
        view_list = {
                'out': 'view_picking_out_tree',
                'in': 'view_picking_in_tree',
                'internal': 'vpicktree',
            }
        data_obj = self.pool.get('ir.model.data')
        res = data_obj.get_object_reference(cr, uid, 'stock', view_list.get(new_type, 'vpicktree'))
        context.update({'view_id': res and res[1] or False})
        
        
        cr.execute('insert into laundry_order_picking_rel (laundry_order_id,picking_id) values (%s,%s)', (laundry_id.id, new_picking))
        return {
            'domain': "[('id', 'in', ["+str(new_picking)+"])]",
            'name': 'Picking List',
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'stock.picking',
            'type':'ir.actions.act_window',
            'context':context,
        }

class hotel_laundry_picking_memory(osv.osv_memory):
    _name = 'hotel.laundry.picking.memory'
    _description ='Hotel Laundry Picking Memory'
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True),
        'quantity' : fields.float("Quantity", required=True),
        'wizard_id' : fields.many2one('hotel.laundry.picking', string="Wizard"),
        'move_id' : fields.many2one('stock.move', "Move"),
    }
hotel_laundry_picking_memory()