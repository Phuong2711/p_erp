# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    p_code = fields.Char(string='Employee Code', copy=False)
    p_emergency_rela = fields.Char(string='Relationship', copy=False)
    p_emergency_address = fields.Char(string='Contact Address', copy=False)
    p_marital = fields.Selection(selection=[('single', 'Single'), ('married', 'Married')],
                                 string='Marital Status',
                                 tracking=True)
    p_issued_date = fields.Date(string='Issued Date', copy=False)
    p_issued_place = fields.Char(string='Issued Place', copy=False)
    p_timeline_ids = fields.One2many(comodel_name='p.timeline', inverse_name='employee_id', ondelete='cascade', copy=False)
    p_family_line_ids = fields.One2many(comodel_name='p.family.line', inverse_name='employee_id', ondelete='cascade', copy=False)
    p_document_line_ids = fields.One2many(comodel_name='p.document.line', inverse_name='employee_id', ondelete='cascade', copy=False)
    p_exists_document_ids = fields.Many2many(comodel_name='p.document', compute='_compute_p_exists_document_ids')

    @api.constrains('work_phone')
    def _check_work_phone(self):
        for employee in self:
            if employee.work_phone:
                pattern = '^0[0-9]{9}$'  # Phone number start with 0 and must have 10 digits
                if not re.match(pattern, employee.work_phone):
                    raise ValidationError(_('Work phone is not correct format!'))

    @api.constrains('p_code')
    def _check_p_code(self):
        for employee in self:
            if employee.p_code:
                domain = [('id', '!=', employee.id), ('p_code', '=', employee.p_code)]
                if self.search(domain):
                    raise ValidationError(_('Duplicating a employee code is not allowed!'))

    @api.depends('p_document_line_ids.document_id')
    def _compute_p_exists_document_ids(self):
        for employee in self:
            exists_document = employee.p_document_line_ids.mapped('document_id')
            employee.p_exists_document_ids = exists_document.ids



