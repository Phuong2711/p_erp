# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TimeLineType(models.Model):
    _name = "p.position"
    _order = "sequence"
    _description = "Position"

    name = fields.Char('Name', translate=True, required=True)
    sequence = fields.Integer('Sequence', required=True)
