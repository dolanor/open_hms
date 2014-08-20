from openerp.osv import osv, fields
class Partner(osv.Model):
    """Inherited res.partner"""
    _inherit = 'res.partner'
    _columns = {
    # We just add a new column in res.partner model
        'instructor' : fields.boolean("Instructor"),
    }
    _defaults = {
    # By default, no partner is an instructor
        'instructor' : False,
    }