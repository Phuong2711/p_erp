# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _compute_last_attendance_id(self):
        wfh_code = self.env.company.p_wfh_code
        action_date = fields.Datetime.now()
        for employee in self:
            employee.last_attendance_id = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('p_attendance_date', '=', action_date),
                ('p_code', '=', wfh_code)
            ], limit=1)

    def _cron_update_last_attendance_id(self):
        wfh_code = self.env.company.p_wfh_code
        action_date = fields.Datetime.now()
        for employee in self.search([]):
            employee.last_attendance_id = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('p_attendance_date', '=', action_date),
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
        # Get latest Today work from home record
        domain = [('employee_id', '=', self.id), ('p_code', '=', wfh_code), ('p_attendance_date', '=', action_date)]
        today_wfh = self.env['hr.attendance'].search(domain, limit=1)

        if not today_wfh or today_wfh.check_out:
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'p_code': wfh_code,
            }
            return self.env['hr.attendance'].create(vals)

        today_wfh.check_out = action_date
        return today_wfh