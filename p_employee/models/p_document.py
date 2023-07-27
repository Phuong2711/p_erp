# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Document(models.Model):
    _name = "p.document"
    _description = "Document"

    name = fields.Char(string='name', translate=True, required=True)
    document_line_ids = fields.One2many(comodel_name='p.document.line', inverse_name='document_id', string='Line ids')