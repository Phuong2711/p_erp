# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    parent_id = fields.Many2one('hr.department', tracking=True)
    p_code = fields.Char(string='Department Code', tracking=True, copy=False)

    @api.constrains('p_code')
    def _check_p_code(self):
        """
        Check p_code is in use by other department
        """
        for department in self:
            if department.p_code:
                check_p_code_domain = [('id', '!=', department.id), ('p_code', '=', department.p_code)]
                if self.search(check_p_code_domain):
                    raise ValidationError(_('Duplicating a department code is not allowed!'))


