# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TimeLine(models.Model):
    _name = "p.timeline"

    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    type_id = fields.Many2one(comodel_name='p.timeline.type', string='Type', ondelete='restrict')
    sequence = fields.Integer(string='Sequence', related='type_id.sequence')
    employee_id = fields.Many2one(comodel_name='hr.employee')
