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

{
    "name" : "Hotel Laundry",
    "version" : "1.0",
    "author" : "Riza and Friend",
    "category" : "Generic Modules/Hotel Laundry",
    "description": """
    Module for laundry management. You can manage:
    * Configure Property
    * Hotel Configuration
    * laundry services
    * Payment

    Different reports are also provided, mainly for hotel statistics.
    """,
    "depends" : ["base","hotel","hotel_reservation"],
    "init_xml" : [
                  ],
    "demo_xml" : [
    ],
    "update_xml" : [
                    "wizard/hotel_laundry_picking_view.xml",
                    "hotel_laundry_view.xml",
                    "laundry_sequence_view.xml",
                    "laundry_data.xml",
#                    'security/hotel_laundry_security.xml',
#                    "security/ir.model.access.csv",
                    ],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
