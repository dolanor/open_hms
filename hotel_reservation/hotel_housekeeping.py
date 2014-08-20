# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from osv import fields
from osv import osv
import time
from mx import DateTime
import datetime
from tools.translate import _
import pooler
from tools import config
import netsvc

class rr_housekeeping(osv.osv):
    
    _name = 'rr.housekeeping'
    _description = 'test'
    _columns = {
                'name':fields.char('Req No',size=30,readonly=True,states={'draft':[('readonly',False)]}),
                'date':fields.datetime('Date Ordered', required=True,readonly=True,states={'draft':[('readonly',False)]}),
                'activity': fields.selection([('repair','Repair'),('replaced','Replace')], 'Activity', select=True, required=True,readonly=True,states={'draft':[('readonly',False)]}),
                'requested_by':fields.many2one('res.users','Requested By',readonly=True,states={'draft':[('readonly',False)]}),
                'requested_by_partner':fields.many2one('res.partner','Guest Name',readonly=True,states={'draft':[('readonly',False)]}),
                'source':fields.selection([('intern','Internal Observation'),('guest','Guest')], 'Source',required=True,readonly=True,states={'draft':[('readonly',False)]}),
                'assign_to':fields.selection([('intern','Internal'),('third_party','Third Party')], 'Assign Method',required=True,readonly=True,states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}),
                'assigned_third_party':fields.many2one('res.partner','Assigned To',readonly=True,states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}),
                'assigned_internal':fields.many2one('res.users','Assigned To',readonly=True,states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}),
                'room_no':fields.many2one('hotel.room','Room No',size=64,required=True,readonly=True,states={'draft':[('readonly',False)]}),
                'approved_by':fields.char('Approved By',size=20,),
                'rr_line_ids':fields.one2many('rr.housekeeping.line','rr_line_id','Repair / Replacement Info',required=True,readonly=True,states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}),
                'state': fields.selection([('draft','Draft'),('confirmed','Confirmed'),('assign','Assigned'),('done','Done'),('cancel','Cancel')], 'State', readonly=True,select=True),
                'complaint':fields.char('Complaint',size=250,readonly=True,states={'draft':[('readonly',False)]}),  
#                'shop_id':fields.many2one('sale.shop', 'Shop'),              
                'shop_id':fields.many2one('sale.shop', 'Shop', required=True, readonly=True, states={'draft':[('readonly',False)]}),      
                'company_id': fields.related('shop_id','company_id',type='many2one',relation='res.company',string='Company',store=True)       
                
                }
    _defaults = {
        
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), 
        'state':'draft',
        'assign_to':'intern',
        'source':'intern'
       }
    def create(self, cr, user, vals, context=None):
        now = datetime.datetime.now()
        if vals.has_key('rr_line_ids'):
            print vals['rr_line_ids']
            if vals['rr_line_ids']:
                print
            else:
                raise osv.except_osv(_('Warning !'),_('There are no product in requirement  line.'))
        
        if vals['activity'] == 'repair':
            temp= self.pool.get('ir.sequence').get(cr, user, 'rr.housekeeping.repair')
            temp1=temp[0:3]
            temp2=temp[3:]
            vals['name']=str(temp1)+'/'+str(now.year)+'/'+str(temp2)
        else:
            temp= self.pool.get('ir.sequence').get(cr, user, 'rr.housekeeping.replace')
            temp1=temp[0:3]
            temp2=temp[3:]
            vals['name']=str(temp1)+'/'+str(now.year)+'/'+str(temp2)
                 
        return super(rr_housekeeping,self).create(cr, user, vals, context)
    
    def confirm_request(self, cr, uid, ids, context=None):
        p=self.pool.get('res.users').browse(cr, uid, uid)
        print "--------------------------",p.id
        self.write(cr, uid, ids, {
            'approved_by':p.name,
            'state':'confirmed'
        })
        return True
    
    def assign_request(self, cr, uid, ids, context=None):
        print "----------------------------------",context
        print "ids------------------------------------------------->",ids
        obj=self.pool.get('rr.housekeeping').browse(cr, uid, ids[0])
        if obj.assign_to == 'intern':
            if not obj.assigned_internal:
                raise osv.except_osv(_('Warning !'),_('There is no  user selected'))
        elif obj.assign_to == 'third_party':
            if not obj.assigned_third_party:
                raise osv.except_osv(_('Warning !'),_('There is no Third party selected'))
        else:
            pass
        self.write(cr, uid, ids, {
            'state':'assign'
        })
        return True

# info source for house keeping
    def onchange_date_source(self, cr, uid, ids, date, source,sp_id):
        res={}
        if date and source and sp_id:
            if source == 'guest':
                main_obj_ids = self.pool.get('hotel.room.reservation.line').search(cr,uid,[('check_in','<=', date),('check_out','>=', date)])
                print main_obj_ids,"main_obj_ids"
                main_obj = self.pool.get('hotel.room.reservation.line').browse(cr,uid,main_obj_ids)
                new_ids = []
                for dest_line in main_obj:
                    if dest_line.room_id.product_id.shop_id.id == sp_id:
                        new_ids.append(dest_line.room_id.id)
                return {
                   'domain': {
                       'room_no': [('id', 'in', new_ids)],
                   } }
            else:
                new_ids = self.pool.get("hotel.room").search(cr, uid, [('product_id.shop_id.id', '=',sp_id)])
                return {
                   'domain': {
                       'room_no': [('id', 'in', new_ids)],
                   } }
        return {'value':res} 

# ------------------------------    

        
    def onchange_room(self, cr, uid, ids, date_order, room_no):
        res={}
        today=date_order
        booking_id=0
        history_obj=self.pool.get("hotel.room.reservation.line")
        folio_obj=self.pool.get("hotel.folio")
        if not room_no:
            return {'value':{'requested_by_partner': False}}
        obj = self.pool.get("hotel.room").browse(cr,uid,room_no)
        print ".>>>>>>>>>>>>>",obj.product_id.name
        for folio_hsry_id in history_obj.search(cr,uid,[('name','=',obj.product_id.name)]):
            hstry_line_id =history_obj.browse(cr,uid,folio_hsry_id)
            start_dt=hstry_line_id.check_in
            end_dt=hstry_line_id.check_out
            if (start_dt<=today) and (end_dt>=today):
                booking_id=hstry_line_id.booking_id.id
                folio_obj_id=folio_obj.search(cr,uid,[('reservation_id','=',booking_id)])
                res['requested_by_partner']=hstry_line_id.partner_id.id
            print ">>>>>>>>>>>>>>>>>>res : ",res
        return {'value':res} 
    
    
    
    def cancel_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state':'cancel'
        })
        return True
    
    def done_task(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state':'done'
        })
        return True
    
    
rr_housekeeping()

class rr_housekeeping_line(osv.osv):    
    _name = 'rr.housekeeping.line'
    _columns = {
                'rr_line_id':fields.many2one('rr.housekeeping','Housekeeping line id'),
                'product_id':fields.many2one('product.product','Product',required=True),
                'product_line_ids':fields.one2many('product.product.line','product_line_id','RICH----------'),                
                'qty':fields.float('Qty',size=10),
                'uom':fields.many2one('product.uom','UOM'), 
                'source_locatiion':fields.many2one('stock.location','Source Loaction'),
                'dest_locatiion':fields.many2one('stock.location','Destination Loaction'),
                'info_id':fields.many2one('issue.material.details','Matarial Id'),
                }
    def onchange_product(self, cr, uid, ids, product_id):
        if not product_id:
            return {'value': {'uom':'PCE'}}
        uom = self.pool.get('product.product').browse(cr, uid, product_id).uom_id.id
        return {'value': {'uom':uom}}
    
    def onchange_room_source(self, cr, uid, ids,source,room_no):
        
        return True
    
    def create(self, cr, user, vals, context=None):
        if vals.has_key('qty'):
            print "---------------------------------",vals['qty']
            if vals['qty'] <= 0.0:
                raise osv.except_osv(_('Warning !'),_('Product Quntity should not be 0 '))
        
        return super(rr_housekeeping_line,self).create(cr, user, vals, context)
    
rr_housekeeping_line()

class product_product_line(osv.osv):
    """Product of product"""
    _name = "product.product.line"
    _columns = {
            'product_line_id':fields.many2one('rr.housekeeping.line','Product line id'),
            'product_product_id':fields.many2one('product.product','Product',required=True),
            'qty':fields.float('Qty',size=10),
            'uom':fields.many2one('product.uom','UOM'),            
            }
    def onchange_product(self, cr, uid, ids, product_product_id):
        if not product_product_id:
            return {'value': {'uom':'PCE'}}
        uom = self.pool.get('product.product').browse(cr, uid, product_product_id).uom_id.id
        return {'value': {'uom':uom}}
    def create(self, cr, user, vals, context=None):
        if vals.has_key('qty'):
            print "---------------------------------",vals['qty']
            if vals['qty'] <= 0.0:
                raise osv.except_osv(_('Warning !'),_('Product Quntity should not be 0 '))
        return super(product_product_line,self).create(cr, user, vals, context)
product_product_line()


class issue_material_details(osv.osv):    
    _name = "issue.material.details"
    _description = 'Issue Material Details'
    _columns = {
            'name':fields.char('Issue Slip',size=20),
            'request_id':fields.many2one('rr.housekeeping','Request Number',required=True,readonly=True,states={'draft':[('readonly',False)]}),
            'repair_ids':fields.one2many('rr.housekeeping.line','info_id','Product Replacement info',readonly=True,states={'draft':[('readonly',False)]}),
            'complaint':fields.char('Complaint',size=250,readonly=True,states={'draft':[('readonly',False)]}),
            'shop_id':fields.many2one('sale.shop', 'Shop', required=True,readonly=True,states={'draft':[('readonly',False)]}),    
            'company_id': fields.related('shop_id','company_id',type='many2one',relation='res.company',string='Company',store=True),  
            'state': fields.selection([('draft','Draft'),('confirm','Confirm'),('done','Done')], 'State', readonly=True,select=True),
            }
    
    _defaults = {
        'state':'draft',
       }
    
    def create(self, cr, user, vals, context=None):
        vals['name'] = self.pool.get('ir.sequence').get(cr,user,'issue.material.details')
        return super(issue_material_details,self).create(cr, user, vals, context)
    
    def done_task(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state':'done' })
        return True
    
    def confirm_task(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids):
            print obj
            internal_move_id = self.pool.get('stock.picking').create(cr,uid,{'type':'internal', 'company_id':obj.company_id.id, 'origin':obj.name,}) 
            for line in obj.repair_ids:
                if not line.product_line_ids:
                    raise osv.except_osv(_('Warning !'),_('Product details is missing.'))    
                if not (line.source_locatiion and line.dest_locatiion):
                    raise osv.except_osv(_('Warning !'),_('Location is missing.'))        
                for product in line.product_line_ids:
                    print product
                    move_id = self.pool.get('stock.move').create(cr,uid,{'product_id':product.product_product_id.id, 'product_uom':product.uom.id, 'origin':obj.name, 'name':obj.name,'product_qty':product.qty,
                                                                         'location_id':line.source_locatiion.id, 'location_dest_id':line.dest_locatiion.id, 'picking_id':internal_move_id}) 
                                
        self.write(cr, uid, ids, { 'state':'confirm' })
        return True
    
    def on_change_request_id(self,cr,uid,ids,request_id):
        result = {}
        print request_id,"request_id"
        housekeeping_id = self.pool.get('rr.housekeeping').browse(cr,uid,request_id)
        print housekeeping_id,"housekeeping_id"
        result['complaint'] = housekeeping_id.complaint
        result['shop_id'] = housekeeping_id.shop_id.id
        source_location = housekeeping_id.shop_id.warehouse_id.lot_stock_id.id
        product_list = []
        for product in housekeeping_id.rr_line_ids:
            product_list.append(product.id)    
        print product_list,"product_list"
        line_ids = self.pool.get('rr.housekeeping.line').browse(cr,uid,product_list)
        for line in line_ids:
            self.pool.get('rr.housekeeping.line').write(cr, uid, [line.id], {'source_locatiion': source_location })
        result['repair_ids'] = product_list
        return {'value': result}
    
issue_material_details()

# class activity_type(osv.osv):
#     _name='activity.type'
#     _description='Activity Type'
#     _columns = {
#         'name':fields.char('Name',size=64,required=True),
#         'parent_id':fields.many2one('activity.type','Parent Category',),
#        }
# activity_type()
# 
# class activity_housekeeping(osv.osv):
#     _name='activity.housekeeping'
#     _description='Activity'
#     _columns = {
#         'name':fields.char('Name',size=64,required=True),
#         'categ_id':fields.many2one('activity.type','Category',required=True),
#        }
# activity_housekeeping()

# class hotel_housekeeping_activities(osv.osv):
#     _inherit = "hotel.housekeeping.activities"
#     _description = "Housekeeping Activities "
#     _columns = {
#         'activity_id':fields.many2one('activity.housekeeping','Housekeeping Activity',required=True),
#         }
# hotel_housekeeping_activities()
