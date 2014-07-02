# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import osv, fields
from tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from osv import fields, osv
from tools.translate import _
import netsvc
import tools
from tools import float_compare
import decimal_precision as dp
import logging

class rr_housekeeping_wizard(osv.osv_memory):
    _name = 'rr.housekeeping.wizard'
    _description = 'rr_housekeeping_wizard'
    _columns = {
                'rr_line_ids':fields.one2many('rr.housekeeping.line.wizard','rr_line_id','Repair / Replacement Info',required=True),
    }
rr_housekeeping_wizard()

class rr_housekeeping_line_wizard(osv.osv_memory):
    _name = 'rr.housekeeping.line.wizard'
    _description = 'rr_housekeeping_line_wizard'
    _columns = {
                'rr_line_id':fields.many2one('rr.housekeeping.wizard','Housekeeping line id'),
    }
rr_housekeeping_line_wizard()

class issue_material(osv.osv_memory):
    _name = 'issue.material'
    _description = 'Issue Material'
    _columns = {
        'location_id': fields.many2one('stock.location', 'Source Location', required=True),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location',required=True),
        'rr_line_ids':fields.one2many('rr.housekeeping.line.wizard','rr_line_id','Repair / Replacement Info',required=True),
    }

    def check_stock(self, cr, uid, ids, context=None):
        
#        print "ids",ids
#        print "zankar"
#        print "context",context
        wizard_obj = self.browse(cr, uid, ids[0], context=context)
#        house_obj = self.pool.get('rr.housekeeping').browse(cr,uid,context['active_id'])
#        for line in house_obj.rr_line_ids:
#            context['product_id']= line.product_id.id
#            arg = None
#            real_stock_on_location = self.pool.get('stock.location')._product_value(cr, uid, [wizard_obj.location_id.id], ['stock_real'], arg, context)
#            print "-------------",line.product_id.name,"--->",real_stock_on_location
#-------------------------------------------------------------------------------------------------------------------------            
            
        field_names=['stock_real']
        res = self.browse(cr, uid, ids, context=context)
        line_obj = self.pool.get('rr.housekeeping.line').search(cr, uid, [('rr_line_id','=',context['active_id'])])
        list1=[]
        list2=[]
        for obj in line_obj:
            line_line_obj = self.pool.get('product.product.line').search(cr,uid,[('product_line_id','=',obj)])
            if line_line_obj:
                for obj1 in line_line_obj:
                    p1 = self.pool.get('product.product.line').browse(cr, uid, obj1)
                    list1.append(p1.product_product_id.id)
                    list2.append(p1.id)
                    p=self.pool.get('product.product').browse(cr, uid, p1.product_product_id.id)
            else:
                print 
        new_list = list(set(list1))
        for i in new_list:
            sum=0
            for j in list2:
                get_ids=self.pool.get('product.product.line').search(cr,uid,[('product_product_id','=',i),('id','=',j)])
                for k in get_ids:
                    p=self.pool.get('product.product.line').browse(cr, uid, k, context=None)
                    sum=sum+p.qty
            product_obj=self.pool.get('product.product').browse(cr, uid, i, context=None)
            stock_obj1=self.pool.get('stock.location')
            if context is None:
                context = {}
            ctx = context.copy()
            ctx.update({'product_id':product_obj.id})
            arg = None
            total_sum = self.pool.get('stock.location')._product_value(cr, uid, [wizard_obj.location_id.id], ['stock_real'], arg, ctx)
#            print "product_product_name------------------",product_obj.id
#            print "ids------------->",i
#            print"total sum--------------------------",total_sum
            for item in total_sum.itervalues():
                print "--------------------------------------",item
                item1=item
                for value in item1.itervalues():
#                    print  "valuse--------------",value
                    test_sum=value
#            print "product Avb qnty",product_obj.qty_available
#            print "test_sum---------------->",test_sum
            if test_sum <= sum:
                raise osv.except_osv(_('Warning !'),_('There is only  %s qty for product %s products.')% (product_obj.qty_available,product_obj.name))
        
        return {'type': 'ir.actions.act_window_close'}

issue_material()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
