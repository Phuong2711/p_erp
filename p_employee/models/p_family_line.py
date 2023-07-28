# -*- coding: utf-8 -*-
from odoo import api, fields, models


class FamilyLine(models.Model):
    _name = 'p.family.line'
    _description = 'Family line'

    name = fields.Char(string='Relative Name')
    date_of_birth = fields.Date(string='Date of Birth')
    phone = fields.Char(string='Phone Number')
    relationship = fields.Char(string='Relationship')
    employee_id = fields.Many2one(comodel_name='hr.employee')