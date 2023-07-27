# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TimeLineType(models.Model):
    _name = "p.timeline.type"
    _order = "sequence"
    _description = "Timeline type"

    name = fields.Char('Name', translate=True, required=True)
    sequence = fields.Integer('Sequence', required=True)
