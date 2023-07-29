# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _compute_last_attendance_id(self):
        wfh_code = self.env.company.p_wfh_code
        for employee in self:
            employee.last_attendance_id = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('p_code', '=', wfh_code)
            ], limit=1)

    def _attendance_action_change(self):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        self.ensure_one()
        wfh_code = self.env.company.p_wfh_code
        action_date = fields.Datetime.now()

        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'p_code': wfh_code,
            }
            return self.env['hr.attendance'].create(vals)
        attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False), ('p_code', '=', wfh_code)], limit=1)
        if attendance:
            attendance.check_out = action_date
        else:
            raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.sudo().name, })
        return attendance