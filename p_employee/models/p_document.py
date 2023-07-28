# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import json


class Document(models.Model):
    _name = "p.document"
    _description = "Document"

    name = fields.Char(string='Name', translate=True, required=True)
    document_line_ids = fields.One2many(comodel_name='p.document.line', inverse_name='document_id', string='Line ids')
    employee_ids = fields.Char(string='Employee', compute='_compute_employee')
    submitted_employee_count = fields.Integer(string='Submitted Employee Count', compute='_compute_employee')
    not_submitted_employee_count = fields.Integer(string='Not Submitted Employee Count', compute='_compute_employee')

    @api.depends('document_line_ids')
    def _compute_employee(self):
        for document in self:
            submitted_employee = document.document_line_ids.filtered(lambda l: l.employee_id.active).mapped('employee_id')
            document.employee_ids = json.dumps(submitted_employee.ids)
            document.submitted_employee_count = len(submitted_employee)
            document.not_submitted_employee_count = self.env['hr.employee'].search_count([]) - document.submitted_employee_count

    def action_submitted_employees(self):
        self.ensure_one()
        return {
            'name': _("Submitted"),
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'hr.employee',
            'domain': [('id', 'in', json.loads(self.employee_ids))]
        }

    def action_not_submitted_employees(self):
        self.ensure_one()
        return {
            'name': _("Not Submitted"),
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'hr.employee',
            'domain': [('id', 'not in', json.loads(self.employee_ids))]
        }