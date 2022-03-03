from odoo import api, fields, models, _

class YearPeriods(models.Model):
    _name = 'year.periods'
    _description = 'Periods'

    name = fields.Char('Periods')
