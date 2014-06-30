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
from tools.translate import _
import netsvc
from datetime import datetime

class hotel_laundry(osv.osv):
    """Hotel laundry is show in configuration and it will create supplier with service and items prices"""
    _name = 'hotel.laundry'
    _description = 'Hotel Laundry'
    
    def onchange_partner_id1(self, cr, uid, ids, partner_id):
        res1 = {}
        print partner_id,"partner_id"
        if partner_id:
#            addr = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery', 'invoice', 'contact'])
#            print addr,"addr"
#            if addr['invoice']:
#                res1['partner_address_id']=addr['invoice']
#                print res1,"res1"
#            else:
#                res_add=self.pool.get('res.partner.address').search(cr,uid,[('partner_id','=',partner_id)])
#                if res_add:
#                    res_browse=self.pool.get('res.partner.address').browse(cr,uid,res_add)
#                    res1['partner_address_id']=res_browse[0].id
            
            partner_ids =self.pool.get('res.partner').browse(cr,uid,partner_id)
            res1['name'] =partner_ids.name
            print res1,"res1"
#        else:
#            res1['partner_address']='/'
        return {'value': res1} 
    
    def confirm(self, cr, uid, ids, *args):
        for service in self.browse(cr, uid, ids):
            if service.laundry_service_ids == []:
                raise osv.except_osv('Warning!',"There is no services regarding to supplier ... !")
            else:
                for record in service.laundry_service_ids:
                    self.pool.get('hotel.laundry.services').write(cr,uid,record.id,{'supplier_id':service.partner_id.id})
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return  True
    
    def cancel_supplier(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'cancel'})
#        return super(hotel_laundry, self).unlink(cr, uid, ids, context = context)
        return True
    
    def update_record(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'edit'})
        return True
    
    _columns = {
                'name':fields.char('Name',size=30),
                'partner_id':fields.many2one('res.partner','Supplier Name',size=30,required=True,states={'confirmed':[('readonly',True)],'edit':[('readonly',True)]}, select=True),
#                'partner_address_id':fields.many2one('res.partner.address','Address',size=60,states={'confirmed':[('readonly',True)],'edit':[('readonly',True)]}, select=True),
                'laundry_service_ids':fields.one2many('hotel.laundry.services','hotel_laundry_service_id','Laundry Services',states={'confirmed':[('readonly',True)]}),
                'state': fields.selection([('draft', 'Draft'), ('edit', 'Edit'),('confirmed', 'Confirmed'), ('canceled', 'Cancel')], 'State', required=True, readonly=True),
                }
    _defaults = {
        'state': 'draft',
    }
hotel_laundry()

class hotel_laundry_service(osv.osv):
    """This class is used to create all the services which will be provide by the hotel management"""
    _name = 'hotel.laundry.services'
    _description = 'Laundry services in hotel'
    
    
    def onchange_services_id(self, cr, uid, ids, service_id):
        res1 = {}
        if service_id:
            service_ids =self.pool.get('product.product').browse(cr,uid,service_id)
            res1['name'] =service_ids.name
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.",res1
        return {'value': res1}
    
    def get_category_id(self, cr, uid, ids, context=None):
        obj=self.pool.get('product.category').search(cr,uid,[('name','=','Laundry')])
        print ">>>>>>>>..category id ",obj[0]
        return obj[0]
    
    _columns = {
                'name':fields.char('Name',size=30),
                'hotel_laundry_service_id':fields.many2one('hotel.laundry'),
                'supplier_id':fields.integer('Supplier Id',size=10),
                'laundry_services_id':fields.many2one('product.product','Service Name',size=30,required=True),
                'laundry_services_items_ids':fields.one2many('hotel.laundry.services.items','laundry_items_id','laundry service items'),
                'category_id':fields.integer('Category',size=20),
                }
    _defaults = {
        'category_id':get_category_id,
    }
hotel_laundry_service()

class hotel_laundry_service_items(osv.osv):
    """This class is used to create all the items which are related to hotel services"""
    _name = 'hotel.laundry.services.items'
    _description = 'Laundry services Items Details'
    
    def onchange_item_id(self, cr, uid, ids, item_id):
        res1 = {}
        if item_id:
            item_ids =self.pool.get('product.product').browse(cr,uid,item_id)
            res1['name'] =item_ids.name
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.",res1
        return {'value': res1}
    
    def get_category_id(self, cr, uid, ids, context=None):
        obj=self.pool.get('product.category').search(cr,uid,[('name','=','Clothes')])
        print ">>>>>>>>..category id ",obj[0]
        return obj[0]
    
    
    _columns = {
                'name':fields.char('Name',size=30),
                'laundry_items_id':fields.many2one('hotel.laundry.services'),
                'item_id':fields.many2one('product.product','Items',size=30,required=True),
                'cost_price':fields.float('Cost Price',size=30),
                'sale_price':fields.float('Sale Price',size=30),
                'category_id1':fields.integer('Category',size=20),
                }
    _defaults = {
        'category_id1':get_category_id,
    }
hotel_laundry_service_items()
    

class laundry_management(osv.osv):
    """This class is use to show all task related laundry management like washing, cleaning, iron and so on"""
    _name = 'laundry.management'
    _description = 'Laundry Management'
    
    def create(self, cr, uid, vals, context=None): 
        # function overwrites create method and auto generate request no.
        vals['name'] = self.pool.get('ir.sequence').get(cr,uid,'laundry.management')
        if vals.get('request_type')=='internal':
            pass
        elif vals.has_key("room_number"):
            room_no=vals.get('room_number')
            today=vals.get('date_order')
            history_obj=self.pool.get("hotel.room.booking.history")
            if not room_no:
                return {'value':{'partner_id': False}}
            obj = self.pool.get("hotel.room").browse(cr,uid,room_no)
            for folio_hsry_id in history_obj.search(cr,uid,[('name','=',obj.product_id.name)]):
                hstry_line_id =history_obj.browse(cr,uid,folio_hsry_id)
                start_dt=hstry_line_id.check_in
                end_dt=hstry_line_id.check_out
                if (start_dt<=today) and (end_dt>=today):
                    vals['partner_id']=hstry_line_id.partner_id.id
                    
        
        return super(laundry_management, self).create(cr, uid, vals, context=context)

    def write(self,cr, uid, ids,vals, context=None):
        if vals.get('request_type')=='internal':
            pass
        elif vals.has_key("room_number"):
            room_no=vals.get('room_number')
            today=vals.get('date_order')
            if not today:
                for self_obj in self.browse(cr,uid,ids):
                    today=self_obj.date_order
            history_obj=self.pool.get("hotel.room.booking.history")
            if not room_no:
                return {'value':{'partner_id': False}}
            obj = self.pool.get("hotel.room").browse(cr,uid,room_no)
            for folio_hsry_id in history_obj.search(cr,uid,[('name','=',obj.product_id.name)]):
                hstry_line_id =history_obj.browse(cr,uid,folio_hsry_id)
                start_dt=hstry_line_id.check_in
                end_dt=hstry_line_id.check_out
                if (start_dt<=today) and (end_dt>=today):
                    vals['partner_id']=hstry_line_id.partner_id.id
                    
        
        return super(laundry_management, self).write(cr, uid, ids, vals, context=context)
    
    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, order_lines, context={}):
        if (not pricelist_id) or (not order_lines):
            return {}
        warning = {
            'title': _('Pricelist Warning!'),
            'message' : _('If you change the pricelist of this order (and eventually the currency), prices of existing order lines will not be updated.')
        }
        return {'warning': warning}
    
    def on_change_shop_id(self,cr, uid, ids, shop_id, context=None):
        if not shop_id:
            return {'value':{}}
        temp=self.pool.get('sale.shop').browse(cr,uid,shop_id,context)
        return {'value':{'company_id':temp.company_id.id}}
 
    def onchange_partner_id(self, cr, uid, ids, partner_id):
        res1 = {}
        if partner_id:
            p_ids=self.pool.get('hotel.laundry').browse(cr,uid,partner_id)
#            res1['supplier_address_id']=p_ids.partner_address_id.id
            res1['supplier_id_temp']=p_ids.partner_id.id
        return {'value': res1}
    
    def get_folio_id(self,cr,uid,date_order,room_number,partner_id, context=None):
        id_val=0
        for folio_ids in self.pool.get('hotel.folio').search(cr,uid,[('checkin_date','<=',date_order) and ('checkout_date','>=',date_order) and ('partner_id','=',partner_id)]):
            if folio_ids:
                f_id=self.pool.get('hotel.folio').browse(cr,uid,folio_ids)
                for room_ids in self.pool.get('hotel.room').search(cr,uid,[('id','=',room_number)]):
                    room_id1=self.pool.get('hotel.room').browse(cr,uid,room_ids)
                    if folio_ids==room_id1.ref_folio_id.id:
                       id_val=f_id.order_id.id 
        
        return id_val
    
    
    def confirm(self, cr, uid, ids, context):
        journal_obj = self.pool.get('account.journal')
        for service in self.browse(cr, uid, ids):
            if service.laundry_service_product_ids == []:
                raise osv.except_osv('Warning!',"There is no services regarding to supplier ... !")
            if service.request_type == 'from_room':
                print "Picking generation>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>."
                #>>>>>>>>>>>>>>>#Calculation for getting folio id/ sale order id*****************************************************************************************
                sale_id=self.get_folio_id(cr,uid,service.date_order,service.room_number.id,service.partner_id.id,context=context)
                print ">>>>>>>>>>>>>>>>>>>>>>>>>>>.",sale_id
                #The working on creation of in-coming shipment
                picking_data={
                              'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
                              'origin':service.name,
#                              'address_id':service.supplier_address_id.id,
                              'min_date':service.deadline_date,
                              'type': 'in',
                              'sale_id':sale_id,
                              'state':'draft',
                            }
                # here we will perform calculation for find location id and location dest id from stock.warehouse and res.partner
                rec_id=self.pool.get('res.partner').browse(cr,uid,service.partner_id.id)
                customer_id=rec_id.property_stock_customer.id
                shop_obj=self.pool.get('sale.shop').browse(cr,uid,service.shop_id.id)
                warehouse_id=self.pool.get('stock.warehouse').browse(cr,uid,shop_obj.warehouse_id.id)
                add=warehouse_id.lot_stock_id.id
                
                picking_id=self.pool.get('stock.picking').create(cr,uid,picking_data)
                for service_line in service.laundry_service_product_ids:
                    for service_line_item in service_line.laundry_service_product_line_ids:
                        
                        move_data = {
                             'name': service.name + ': ' + (service_line_item.item_id.name or ''),          
                             'picking_id':picking_id,
                             'product_id':service_line_item.item_id.id,
                             'product_qty':service_line_item.qty,
                             'product_uom':service_line_item.qty_uom.id,
                             'location_id':customer_id,
                             'location_dest_id':add,
                             'state':'assigned',
                             }
                        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",move_data
                        picking_line=self.pool.get('stock.move').create(cr,uid,move_data)
                        
                        #for finding the picking id
                        pick_id=self.pool.get('stock.picking').browse(cr,uid,picking_id)
                        print ">>>>>>>>>>>>>>>>>>>>>>>>",pick_id.name
                        
                    #Here we create picking history according to laundry order                        
                      
                    message= _("Incoming picking id '%s' has been created.")%(pick_id.name,)
                    self.log(cr, uid, service.id, message)
                cr.execute('insert into laundry_order_picking_rel (laundry_order_id,picking_id) values (%s,%s)', (service.id, picking_id))
                #>>>>>>>>>>>>>>>#*****************************************************************************************
                #### The working on creation of customer invoice#####
                partner_id=service.partner_id.id
#                if partner_id:
#                    addr = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery', 'invoice', 'contact'])
#                    print addr,"addr"
#                    if addr['invoice']:
#                        partner_add=addr['invoice']
#                    else:
#                        res_add=self.pool.get('res.partner.address').search(cr,uid,[('partner_id','=',partner_id)])
#                        if res_add:
#                            res_browse=self.pool.get('res.partner.address').browse(cr,uid,res_add)
#                            partner_add=res_browse[0].id
                print ">>>>>>>>>>>>>>>>>>>>>>",partner_id 
                if service.is_chargable:
                    account=self.pool.get('res.partner').browse(cr,uid,partner_id)
                    account_id=account.property_account_receivable.id
                    journal_ids = journal_obj.search(cr, uid, [('type', '=','sale')], limit=1)
                    
                    pricelist_obj=self.pool.get('product.pricelist').browse(cr,uid,service.pricelist_id.id)
                    cur_id=pricelist_obj.currency_id.id
                    #This currency is use in customer invoice
                        
                    invoice_data={
                                'name':service.name,
                                'origin': service.name,
                                'type':'out_invoice',
                                'reference': "Laundry Customer Invoice",
                                'currency_id': cur_id,
                                'partner_id':partner_id,
    #                            'address_invoice_id':partner_add,
                                'account_id':account_id,
                                'journal_id': len(journal_ids) and journal_ids[0] or False,
                                }
                    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> invoice_data",invoice_data
                    invoice_id=self.pool.get('account.invoice').create(cr,uid,invoice_data)
                    #find account id that is expenses account of product or product category
                    #create incovie in folio with respect to partner
                    cr.execute('insert into laundry_folio_invoice_rel (folio_id,invoice_id) values (%s,%s)', (sale_id, invoice_id))
                    for service_line in service.laundry_service_product_ids:
                        for service_line_item in service_line.laundry_service_product_line_ids:
                            
                            invoice_line_data={
                                               'invoice_id':invoice_id,
                                               'product_id':service_line.laundry_services_id.id,
                                               'name':service_line.laundry_services_id.name,
                                               'uos_id':service_line_item.qty_uom.id,
                                               'price_unit':service_line.sale_subtotal,
                                               'account_id':service_line_item.item_id.categ_id.property_account_income_categ.id
                                               }
                        print ">>>>>>>>>>>>>>>>>>>>>>>>>invoice_line_data",invoice_line_data
                        self.pool.get('account.invoice.line').create(cr, uid, invoice_line_data)
            else :
                print "not generate picking"
                
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return True
    
    def cancel_service(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'canceled'})
        return True
    
    def send_to_laundry(self, cr, uid, ids, context):
        journal_obj = self.pool.get('account.journal')
        for service in self.browse(cr, uid, ids):
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Working when request type is from room
            sale_id=self.get_folio_id(cr,uid,service.date_order,service.room_number.id,service.partner_id.id,context=context)
            if service.request_type == 'from_room':
                pick=self.pool.get('stock.picking').search(cr,uid,[('origin','=',service.name)])
                for pick_id in self.pool.get('stock.picking').browse(cr,uid,pick):
                    for move_line in pick_id.move_lines:
                        if pick_id.type=='in':
                            if move_line.state == 'done':
                                check=True
                            else:
                                raise osv.except_osv('Warning!',"Please process the in-coming shipment-%s first!"%(pick_id.name))
#                sale_id=self.get_folio_id(cr,uid,service.date_order,service.room_number.id,service.partner_id.id,context=context)
                if check:
                    picking_data={
                      'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out'),
                      'origin':service.name,
#                      'address_id':service.supplier_address_id.id,
                      'min_date':service.deadline_date,
                      'type': 'out',
                      'sale_id':sale_id,
                      'state':'draft',
                      }
#                    # here we will perform calculation for find location id and location dest id from stock.warehouse and res.partner
                    rec_id=self.pool.get('res.partner').browse(cr,uid,service.partner_id.id)
                    supplier_id=rec_id.property_stock_supplier.id
                    shop_obj=self.pool.get('sale.shop').browse(cr,uid,service.shop_id.id)
                    warehouse_id=self.pool.get('stock.warehouse').browse(cr,uid,shop_obj.warehouse_id.id)
                    add=warehouse_id.lot_stock_id.id
                    picking_id=self.pool.get('stock.picking').create(cr,uid,picking_data)
                    
                    for service_line in service.laundry_service_product_ids:
                        for service_line_item in service_line.laundry_service_product_line_ids:
                            
                            move_data = {
                                 'name': service.name + ': ' + (service_line_item.item_id.name or ''),          
                                 'picking_id':picking_id,
                                 'product_id':service_line_item.item_id.id,
                                 'product_qty':service_line_item.qty,
                                 'product_uom':service_line_item.qty_uom.id,
                                 'location_id':add,
                                 'location_dest_id':supplier_id,
                                 'state':'assigned',
                                 }
                            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",move_data
                            picking_line=self.pool.get('stock.move').create(cr,uid,move_data)
                            
                            #for finding the picking id
                            pick_out_id=self.pool.get('stock.picking').browse(cr,uid,picking_id)
                            print ">>>>>>>>>>>>>>>>>>>>>>>>",pick_out_id.name
                            
                      
                        message=_("Outgoing picking id '%s' has been created.")%(pick_out_id.name,)
                        self.log(cr, uid, service.id, message)
                    cr.execute('insert into laundry_order_picking_rel (laundry_order_id,picking_id) values (%s,%s)', (service.id, picking_id))
                                        
                            
                
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Working when request type is internal                            
            elif service.request_type == 'internal':
                picking_data={
                                  'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out'),
                                  'origin':service.name,
#                                  'address_id':service.supplier_address_id.id,
                                  'min_date':service.deadline_date,
                                  'type': 'out',
                                  'state':'draft',
                                  }
                rec_id=self.pool.get('res.partner').browse(cr,uid,service.partner_id.id)
                supplier_id=rec_id.property_stock_supplier.id
                shop_obj=self.pool.get('sale.shop').browse(cr,uid,service.shop_id.id)
                warehouse_id=self.pool.get('stock.warehouse').browse(cr,uid,shop_obj.warehouse_id.id)
                add=warehouse_id.lot_stock_id.id
                picking_id=self.pool.get('stock.picking').create(cr,uid,picking_data)
                for service_line in service.laundry_service_product_ids:
                    for service_line_item in service_line.laundry_service_product_line_ids:
                                               
                        move_data = {
                                    'name': service.name + ': ' + (service_line_item.item_id.name or ''),          
                                    'picking_id':picking_id,
                                    'product_id':service_line_item.item_id.id,
                                    'product_qty':service_line_item.qty,
                                    'product_uom':service_line_item.qty_uom.id,
                                    'location_id':add,
                                    'location_dest_id':supplier_id,
                                    'state':'assigned',
                                    }
                        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",move_data
                        picking_line=self.pool.get('stock.move').create(cr,uid,move_data)
                                        
                                        #for finding the picking id
                        pick_out_id=self.pool.get('stock.picking').browse(cr,uid,picking_id)
                        print ">>>>>>>>>>>>>>>>>>>>>>>>",pick_out_id.name
                                        
                      
#                                        message = _("Laundry Order id '%s' has been Created.") % (service.name,)
                    message=_("Outgoing picking id '%s' has been created.")%(pick_out_id.name,)
                    self.log(cr, uid, service.id, message)
                cr.execute('insert into laundry_order_picking_rel (laundry_order_id,picking_id) values (%s,%s)', (service.id, picking_id))
                
            #################### Working on Supplier invoice generation#################################################################33333333
            if (service.request_type == 'from_room' and service.service_type == 'third_party') or (service.request_type == 'internal' and service.service_type == 'third_party' and service.is_chargable):
                supplier_id=service.supplier_id.id
                sup_id=self.pool.get('hotel.laundry').browse(cr,uid,supplier_id)
                sup_pid=sup_id.partner_id.id
    #            if sup_pid:
    #                addr = self.pool.get('res.partner').address_get(cr, uid, [sup_pid], ['delivery', 'invoice', 'contact'])
    #                print addr,"addr"
    #                if addr['invoice']:
    #                    supplier_add=addr['invoice']
    #                else:
    #                    res_add=self.pool.get('res.partner.address').search(cr,uid,[('partner_id','=',sup_pid)])
    #                    if res_add:
    #                        res_browse=self.pool.get('res.partner.address').browse(cr,uid,res_add)
    #                        supplier_add=res_browse[0].id
                
                part_obj=self.pool.get('res.partner').browse(cr,uid,sup_pid)
                account_id=part_obj.property_account_payable.id
                sup_pricelist=part_obj.property_product_pricelist.id
                pur_journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase')], limit=1)
                pricelist_obj=self.pool.get('product.pricelist').browse(cr,uid,sup_pricelist)
                cur_id=pricelist_obj.currency_id.id
                    
                invoice_data={
                            'name':service.name,
                            'origin': service.name,
                            'reference': "Laundry Supplier Invoice",
                            'type':'in_invoice',
                            'currency_id': cur_id,
                            'partner_id':sup_pid,
    #                        'address_invoice_id':supplier_add,
                            'account_id':account_id,
                            'journal_id': len(pur_journal_ids) and pur_journal_ids[0] or False,
                            }
                print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> invoice_data",invoice_data
                invoice_id=self.pool.get('account.invoice').create(cr,uid,invoice_data)
                #find account id that is expenses account of product or product category
                #create incovie in folio with respect to partner
    #            cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (sale_id, invoice_id))
                
                for service_lines in service.laundry_service_product_ids:
                    for service_line_item in service_lines.laundry_service_product_line_ids:
                        
                        sup_id=self.pool.get('hotel.laundry.services').browse(cr,uid,service_lines.laundry_services_id.id)
                        laundry_service_id=sup_id.laundry_services_id.id
                        laundry_service_name=sup_id.laundry_services_id.name
                        invoice_line_data={
                                           'invoice_id':invoice_id,
                                           'name':laundry_service_name,
                                           'product_id':laundry_service_id,
                                           'uos_id':service_line_item.qty_uom.id,
                                           'price_unit':service_lines.cost_subtotal,
                                           'account_id':service_line_item.item_id.categ_id.property_account_expense_categ.id
                                           }
                    print ">>>>>>>>>>>>>>>>>>>>>>>>>invoice_line_data",invoice_line_data
                    self.pool.get('account.invoice.line').create(cr, uid, invoice_line_data)
                    
                    print "This is internal request type so no need to create picking or return"
        
        self.write(cr, uid, ids, {'state': 'sent_to_laundry'})
        return True
    
    def customer_return(self, cr, uid, ids, context):
        wf_service = netsvc.LocalService("workflow")
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        picking_id = False
        for service in self.browse(cr, uid, ids):
            record_ids=self.pool.get('stock.picking').search(cr,uid,[('origin','=',service.name)])
            for pick_id in self.pool.get('stock.picking').browse(cr,uid,record_ids):
                for move_line in pick_id.move_lines:
                    if move_line.state == 'done':
                        cond=True
                        print "U can proceed >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                    else:
                        raise osv.except_osv('Warning!',"Please process all shipment related %s order!"%(service.name))
            
            for rec in record_ids:
                records=self.pool.get('stock.picking').browse(cr,uid,rec)
                if records.type=='in':
                    pick=records.id
                    break
            pick_id=self.pool.get('stock.picking').browse(cr,uid,pick)
#           creation picking entry in the hotel folio regarding guest id 
            sale_id=self.get_folio_id(cr,uid,service.date_order,service.room_number.id,service.partner_id.id,context=context)    
            if cond:
                picking_data={
                                  'name': pick_id.name+'-return',
                                  'origin':service.name,
#                                  'address_id':service.supplier_address_id.id,
                                  'min_date':service.deadline_date,
                                  'type': 'out',
                                  'date':date_cur,
                                  'sale_id':sale_id,
                                  'state':'draft',
                                }
                rec_id=self.pool.get('res.partner').browse(cr,uid,service.partner_id.id)
                customer_id=rec_id.property_stock_customer.id
                shop_obj=self.pool.get('sale.shop').browse(cr,uid,service.shop_id.id)
                warehouse_id=self.pool.get('stock.warehouse').browse(cr,uid,shop_obj.warehouse_id.id)
                add=warehouse_id.lot_stock_id.id
                
                    
                        
                picking_id=self.pool.get('stock.picking').create(cr,uid,picking_data)
                for service_line in service.laundry_service_product_ids:
                    for service_line_item in service_line.laundry_service_product_line_ids:
                                        
                        move_data = {
                                     'name': service.name + ': ' + (service_line_item.item_id.name or ''),          
                                     'picking_id':picking_id,
                                     'product_id':service_line_item.item_id.id,
                                     'product_qty':service_line_item.qty,
                                     'product_uom':service_line_item.qty_uom.id,
                                     'location_id':add,
                                     'location_dest_id':customer_id,
                                     'state':'draft',
                                     }
                        picking_line=self.pool.get('stock.move').create(cr,uid,move_data)
                            
                            #for finding the picking id
                        pick_id=self.pool.get('stock.picking').browse(cr,uid,picking_id)
                            
                            #Here we create picking history according to laundry order                        
                cr.execute('insert into laundry_order_picking_rel (laundry_order_id,picking_id) values (%s,%s)', (service.id, picking_id))  
#                        message = _("Laundry Order id '%s' has been Created.\n") % (service.name,)
                message= _("Incoming picking id '%s' has been created.")%(pick_id.name,)
                self.log(cr, uid, service.id, message)
                    
        wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        self.pool.get('stock.picking').force_assign(cr, uid, [picking_id], context)    
             
        self.write(cr, uid, ids, {'state': 'customer_returned'})
        return True
    
    def done_from_room(self, cr, uid, ids, context):
        for service in self.browse(cr, uid, ids):
            pick=self.pool.get('stock.picking').search(cr,uid,[('origin','=',service.name)])
            for pick_id in self.pool.get('stock.picking').browse(cr,uid,pick):
                for move_line in pick_id.move_lines:
                    if move_line.state == 'done':
                        print "U can proceed >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                    else:
                        raise osv.except_osv('Warning!',"Please process the return shipment-%s first!"%(pick_id.name))
        
        
        self.write(cr, uid, ids, {'state': 'done'})
        return True
    
    def done_internal(self, cr, uid, ids, context):
        for service in self.browse(cr, uid, ids):
            pick=self.pool.get('stock.picking').search(cr,uid,[('origin','=',service.name)])
            for pick_id in self.pool.get('stock.picking').browse(cr,uid,pick):
                for move_line in pick_id.move_lines:
                    if move_line.state == 'done':
                        print "U can proceed >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                    else:
                        raise osv.except_osv('Warning!',"Please process the return shipment-%s first!"%(pick_id.name))
        
        self.write(cr, uid, ids, {'state': 'done'})
        return True
    
    def onchange_room_no(self, cr, uid, ids, room_no,date_order):
        print "onchange_room_no",room_no
        res={}
        today=date_order
        history_obj=self.pool.get("hotel.room.booking.history")
        if not room_no:
            return {'value':{'partner_id': False}}
        obj = self.pool.get("hotel.room").browse(cr,uid,int(room_no))
        print "obj",obj
        print ".>>>>>>>>>>>>>",obj.product_id.name
        for folio_hsry_id in history_obj.search(cr,uid,[('name','=',obj.product_id.name)]):
            print folio_hsry_id,"folio_hsry_id"
            hstry_line_id =history_obj.browse(cr,uid,folio_hsry_id)
            start_dt=hstry_line_id.check_in
            end_dt=hstry_line_id.check_out
            if (start_dt<=today) and (end_dt>=today):
                print "rrrrrrrrrrrr"
                res['partner_id']=hstry_line_id.partner_id.id
        return {'value':res}        
            
#        return {'value':{'partner_id': obj.ref_partner_id.id,'folio_id': obj.ref_folio_id.id}}
    
    def get_rooms(self, cr, uid, ids,request_type,date_order):
        res=[]
        val={}
        print "Today date ...............",time.strftime('%Y-%m-%d %H:%M:%S')
        today=date_order
        print ">>>>>>>>>>>>>>>>>>>>> today",today
        if request_type=='from_room':
            print ">>>>>>>>>>>>>>>>>>>>> ddddddddddddddddddddtoday"
            for folio_ids in self.pool.get('hotel.folio').search(cr,uid,[('checkin_date','<=',today),('checkout_date','>=',today)]):
                print folio_ids,"folio_ids"
                folio_id1 = self.pool.get('hotel.folio').browse(cr,uid,folio_ids)
                for folio_line in folio_id1.room_lines:
                    start_dt=folio_line.checkin_date
                    end_dt=folio_line.checkout_date
                    room_id=folio_line.product_id.id
                    if (start_dt<=today) and (end_dt>=today):
                        print ".>>>>>>>.>>>True",room_id
                        print ">>>>>>>>>",self.pool.get('hotel.room').search(cr,uid,[('product_id','=',room_id)])
                        product_id=self.pool.get('hotel.room').search(cr,uid,[('product_id','=',room_id)])
#                        res.append((str(product_id[0]),str(folio_line.product_id.name)),)
                        res.append(product_id[0])
#       
        print "REssssss",res            
        return {
            'domain': {
                'room_number': [('id', 'in', res)],
            } }

#    def get_room_numbers(self, cr, uid, context={}):
#        res=[]
#        today=time.strftime('%Y-%m-%d %H:%M:%S')
#        for folio_ids in self.pool.get('hotel.folio').search(cr,uid,[('checkin_date','<=',today),('checkout_date','>=',today)]):
#            print folio_ids,"folio_ids"
#            folio_id1 = self.pool.get('hotel.folio').browse(cr,uid,folio_ids)
#            for folio_line in folio_id1.room_lines:
#                start_dt=folio_line.checkin_date
#                end_dt=folio_line.checkout_date
#                room_id=folio_line.product_id.id
#                if (start_dt<=today) and (end_dt>=today):
#                    print ".>>>>>>>.>>>True",room_id
#                    print ">>>>>>>>>",self.pool.get('hotel.room').search(cr,uid,[('product_id','=',room_id)])
#                    product_id=self.pool.get('hotel.room').search(cr,uid,[('product_id','=',room_id),('state','=','sellable')])
#                    res.append((str(product_id[0]),str(folio_line.product_id.name)),)
#        print "REs",res
#        return res

        
        
    _columns = {
        'name': fields.char('Order Reference', size=64,readonly=True),
        'user_id':  fields.many2one('res.users', 'Responsible',states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]}),
        'date_order':fields.datetime('Request Date', required=True, states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]}, select=True),
        'deadline_date':fields.datetime('Request Deadline',states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]},size=30),
        'shop_id': fields.many2one('sale.shop', 'Shop Name', states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]}, select=True,help="Will show list of shop that belongs to allowed companies of logged-in user."),
#        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]}, select=True),
        'company_id': fields.many2one('res.company','Company',states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]},required=True,select=1),
        'request_type':fields.selection([('internal','Internal'),('from_room','From Room')],'Request Type', states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]},size=30),
        'room_number':fields.many2one('hotel.room','Room No',states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]},size=64, help="Will show list of currently occupied room no that belongs to selected shop."),
        'partner_id':fields.many2one('res.partner', 'Guest Name',states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]}),
        'supplier_id':fields.many2one('hotel.laundry','Supplier',states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]}),
#        'supplier_address_id':fields.many2one('res.partner.address','Address',states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]},size=60),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled'),('sent_to_laundry', 'Sent to Laundry'),('laundry_returned', 'Laundry Returned'),('customer_returned', 'Customer Returned'),('done', 'Done')], 'State',readonly=True),
        'laundry_service_product_ids':fields.one2many('laundry.service.product','laundry_service_id','Laundry Service Product',states={'confirmed':[('readonly',True)], 'laundry_returned':[('readonly',True)],'sent_to_laundry':[('readonly',True)],'customer_returned':[('readonly',True)],'done':[('readonly',True)]}),
        'supplier_id_temp':fields.integer('Supplier Temp Id',size=30),
        'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'invoice_ids': fields.many2many('stock.picking', 'laundry_order_picking_rel', 'laundry_order_id', 'picking_id', 'Invoice Lines', readonly=True),
#        'room_number_selection':fields.selection(get_room_numbers, 'room number'),
        'service_type': fields.selection([('internal','Internal'),('third_party','Third Party')],'Service Type',),
        'is_chargable' : fields.boolean('Is Chargable'), 
    }
    _defaults = {
        'date_order': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.order', context=c),
        }
laundry_management()


class laundry_service_product(osv.osv):
    """This class is used to show all the services according to supplier means all services of the supplier will be show here"""
    _name = 'laundry.service.product'
    _description = 'Laundry Service Product'
    
    def get_cost_value(self, cr, uid, ids, name, args, context={}):
        res={}
        cost_subtotal=0.0
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>.get cost values"
        for records in self.browse(cr,uid,ids):
            for records1 in records.laundry_service_product_line_ids:
                cost_subtotal+=records1.cost_subtotal
#            qty=records.product_uom_qty
            res[records.id]=cost_subtotal
#            res['cost_subtotal']=cost_subtotal*qty
        return res
    
    def get_sales_value(self, cr, uid, ids, name, args, context={}):
        res={}
        sale_subtotal=0.0
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>.get sale values"
        for records in self.browse(cr,uid,ids):
            for records1 in records.laundry_service_product_line_ids:
                sale_subtotal+=records1.sale_subtotal
#            qty=records.product_uom_qty
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>",sale_subtotal 
            res[records.id]=sale_subtotal
#            res['sale_subtotal']=sale_subtotal*qty
        return res
    
    def get_cost_subtotal_value(self, cr, uid, ids, name, args, context={}):
        res={}
        cost_price=0.0
        for records in self.browse(cr,uid,ids):
            for records1 in records.laundry_service_product_line_ids:
                cost_price+=records1.cost_subtotal
            res[records.id]=cost_price
        return res
        
    def get_sales_subtotal_values(self, cr, uid, ids, name, args, context={}):
        res={}
        sale_price=0.0
        for records in self.browse(cr,uid,ids):
            for records1 in records.laundry_service_product_line_ids:
                sale_price+=records1.sale_subtotal
            res[records.id]=sale_price
        return res
    
    
    def on_change_service_ids(self,cr,uid,ids,pricelist,supplier):
        res={}
        print '>>>>>>>>>parent pricelist',pricelist
        if pricelist:
            res['pricelist_id']=pricelist
            res['supplier_id']=supplier
        print ">>>>>>.res",res
        return {'value': res}
        
        
    def _get_currency(self, cr, uid, ctx):
        comp = self.pool.get('res.users').browse(cr,uid,uid).company_id
        if not comp:
            comp_id = self.pool.get('res.company').search(cr, uid, [])[0]
            comp = self.pool.get('res.company').browse(cr, uid, comp_id)
        return comp.currency_id.id
    
        
    _columns = {
            'laundry_service_id':fields.many2one('laundry.management'),
            'laundry_services_id':fields.many2one('hotel.laundry.services','Service Name',size=30,required=True),
            'pricelist_id':fields.many2one('product.pricelist', 'Pricelist'),
            'supplier_id':fields.many2one('res.partner','supplier'),
#            'currency_id' : fields.many2one('res.currency','Currency',size=30),
#            'product_uom_qty':fields.float('Quantity',size=30),
#            'qty_uom':fields.many2one('product.uom','UOM',size=30),
            'cost_rate':fields.function(get_cost_value, method=True, string='Cost Rate', type="float", store=True, help="This column will compute cost price based on the pricelist linked to selected supplier"),
            'sales_rate':fields.function(get_sales_value, method=True, string='Sales Rate', type="float", store=True, help="This column will compute cost price based on the pricelist selected at header part"),
            'cost_subtotal':fields.function(get_cost_subtotal_value, method=True, string='Cost Sub Total', type="float", store=True),
            'sale_subtotal':fields.function(get_sales_subtotal_values, method=True, string='Sales Sub Total', type="float", store=True),
            'laundry_service_product_line_ids':fields.one2many('laundry.service.product.line','laundry_service_line_id','Laundry Product Service Line'),
            }
#    _defaults = {
#        'currency_id':_get_currency,
#        }
laundry_service_product()

class laundry_service_product_line(osv.osv):
    """This class will show all the items according to service selection by the hotel manager"""
    _name = 'laundry.service.product.line'
    _description = 'Product Line show all items details'
    
    def get_price(self,cr, uid, ids, pricelist_ids,price,context=None):
        price_amt=0.0
        pricelist_version_ids=[]
        if context is None:
            context = {}

        date = time.strftime('%Y-%m-%d')
        if 'date' in context:
            date = context['date']
                        
        currency_obj = self.pool.get('res.currency')
        product_pricelist_version_obj = self.pool.get('product.pricelist.version')
        user_browse = self.pool.get('res.users').browse(cr,uid,uid)
        company_obj = self.pool.get('res.company')
        company_id = company_obj.browse(cr,uid,user_browse.company_id.id)
        pricelist_obj=self.pool.get('product.pricelist').browse(cr,uid,pricelist_ids)
        if pricelist_ids:
            pricelist_version_ids.append(pricelist_ids)
            pricelist_obj=self.pool.get('product.pricelist').browse(cr,uid,pricelist_ids)
            
        pricelist_version_ids=list(set(pricelist_version_ids))
        plversions_search_args = [
            ('pricelist_id', 'in', pricelist_version_ids),
            '|',
            ('date_start', '=', False),
            ('date_start', '<=', date),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', date),
        ]

        plversion_ids = product_pricelist_version_obj.search(cr, uid, plversions_search_args)
        print "plverson ids",plversion_ids 
        if len(pricelist_version_ids) != len(plversion_ids):
            msg = "At least one pricelist has no active version !\nPlease create or activate one."
            raise osv.except_osv(_('Warning !'), _(msg))
        
        cr.execute(
                    'SELECT i.*, pl.currency_id '
                    'FROM product_pricelist_item AS i, '
                        'product_pricelist_version AS v, product_pricelist AS pl '
                    'WHERE price_version_id = '+str(plversion_ids[0])+''
                        'AND i.price_version_id = v.id AND v.pricelist_id = pl.id ')
                    
        print ">>>>>>>>>>>>>..cr ..",cr
        
        res1 = cr.dictfetchall()
        if pricelist_obj:
            price=currency_obj.compute(cr, uid, company_id.currency_id.id, pricelist_obj.currency_id.id, price, round=False)
        
        for res in res1:
            if res:
                price_limit = price
                price = price * (1.0+(res['price_discount'] or 0.0))
#                price = rounding(price, res['price_round'])
                price += (res['price_surcharge'] or 0.0)
                if res['price_min_margin']:
                    price = max(price, price_limit+res['price_min_margin'])
                if res['price_max_margin']:
                    price = min(price, price_limit+res['price_max_margin'])
                break
    
        price_amt=price
        return price_amt
    
    def _get_uom_id(self, cr, uid, *args):
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
            return result[1]
        except Exception, ex:
            return False  
        
    def onchange_itemid(self,cr,uid,ids,itemid,pricelist,supplier_id):
        print ">>>>>..onchange item id"
        partner_obj=self.pool.get('res.partner').browse(cr,uid,supplier_id)
        sup_pricelist=partner_obj.property_product_pricelist.id
        cost=0
        sale=0
        res={}
        if itemid:
            record_id = self.pool.get('hotel.laundry.services.items').browse(cr,uid,itemid)
            cost=self.get_price(cr,uid,ids,sup_pricelist,record_id.cost_price)
            sale=self.get_price(cr,uid,ids,pricelist,record_id.sale_price)
            res['item_id']=record_id.item_id.id
            res['cost_price']=cost
            res['sales_price']=sale
            res['cost_subtotal']=cost
            res['sale_subtotal']=sale
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>...",res
        return {'value': res}
    
    def onchange_quantity(self,cr,uid,ids,qty,cost_p,sale_p):
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.quantity"
        res={}
       
        if qty:
            res['cost_subtotal']=qty*cost_p
            res['sale_subtotal']=qty*sale_p
            
        return {'value': res}
    
    
    _columns = {
            'laundry_service_line_id':fields.many2one('laundry.service.product'),
            'item_id':fields.many2one('product.product','Item',size=30),
            'item_id_ref':fields.many2one('hotel.laundry.services.items','Items',size=30,required=True),
            'qty_uom':fields.many2one('product.uom','UOM',size=30),
            'qty':fields.float('Quantity',size=30),
            'cost_price':fields.float('Cost Price',size=30, help="This column will compute cost price based on the pricelist linked to selected supplier"),
            'sales_price':fields.float('Sales Price',size=30, help="This column will compute cost price based on the pricelist selected at header part"),
            'cost_subtotal':fields.float('Cost Sub Total',size=30),
            'sale_subtotal':fields.float('Sale Sub Total',size=30),
            }
    _defaults = {
               'qty_uom' : _get_uom_id,
               'qty': 1,
               }
laundry_service_product() 
    
    





