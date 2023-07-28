# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DocumentLine(models.Model):
    _name = "p.document.line"
    _description = "Document line"

    document_id = fields.Many2one(comodel_name='p.document', string='Document name', ondelete='restrict')
    document_attachment = fields.Binary(string='Attachment')
    document_attachment_name = fields.Char(string='Attachment name')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')