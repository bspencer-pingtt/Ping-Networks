from odoo import api, fields, models, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    bir_file_number = fields.Char('BIR File Number')
    paye_file_number = fields.Char('PAYE File Number')