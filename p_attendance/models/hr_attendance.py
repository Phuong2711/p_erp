# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from pytz import timezone, utc


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    def _default_p_code(self):
        return self.env.company.p_wfo_code

    p_code = fields.Char(string='Code', default=_default_p_code)
    p_worked_days = fields.Float(string='Worked Days', compute='_compute_worked_hours', store=True, readonly=True, digits=(16, 2))
    p_attendance_date = fields.Date(string='Attendance Date', compute='_compute_attendance_date', store=True)
    p_department_name = fields.Char(string='Department Name', compute='_compute_department')
    p_department_code = fields.Char(string='Department Code', compute='_compute_department', store=True)
    p_tz = fields.Char(string='Timezone', compute='_compute_tz')
    check_in = fields.Datetime(default=False, required=False)

    def init(self):
        self.env.cr.execute("""
        CREATE INDEX IF NOT EXISTS hr_attendance_employee_id_p_attendance_date_p_code_index 
        ON hr_attendance (employee_id, p_attendance_date, p_code)
        """)

    def _check_validity(self):
        pass

    @api.constrains('check_in', 'check_out')
    def _check_check_in_check_out(self):
        for attendance in self:
            if not (attendance.check_in or attendance.check_out):
                raise ValidationError(_('To avoid junk data, "Check In" and "Check out" cannot empty at the same time!'))
            if attendance.check_in and attendance.check_out:
                tz = attendance.employee_id.tz
                check_in_date = attendance.check_in.replace(tzinfo=utc).astimezone(timezone(tz)).date()
                check_out_date = attendance.check_out.replace(tzinfo=utc).astimezone(timezone(tz)).date()
                if check_in_date != check_out_date:
                    raise ValidationError(_('Check in and Check out must be in a same date!'))

    @api.depends('check_in', 'check_out', 'employee_id', 'employee_id.resource_calendar_id')
    def _compute_worked_hours(self):
        def get_delta(check_in, check_out, calendar=None):
            """
            Get duration of an attendance
            :param check_in: Checkin of an attendance
            :param check_out: Checkout of an attendance
            :param calendar: Calendar (Default=None)
            :return: a dict {'days': n, 'hours': h} containing the
            quantity of working time expressed as days and as hours.
            """
            if check_in > check_out:
                [check_in, check_out] = [check_out, check_in]
            if calendar:
                return calendar.get_work_duration_data(check_in, check_out, compute_leaves=True)

            delta = attendance.check_out - attendance.check_in
            SECOND_PER_HOUR = 3600.0
            worked_hours = delta.total_seconds() / SECOND_PER_HOUR
            worked_days = worked_hours / self.env.company.p_work_hour_day
            return {'hours': worked_hours, 'days': round(worked_days, 2)}

        company = self.env.company
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                if company.p_worked_hours_base == 'flexible':
                    calendar = None
                elif company.p_worked_hours_base == 'employee':
                    calendar = attendance.employee_id.resource_calendar_id
                elif company.p_worked_hours_base == 'company':
                    calendar = company.resource_calendar_id

                delta = get_delta(attendance.check_in, attendance.check_out, calendar)
                attendance.worked_hours = delta.get('hours', False)
                attendance.p_worked_days = delta.get('days', False)
            else:
                attendance.worked_hours = False
                attendance.p_worked_days = False

    @api.depends('employee_id', 'check_in', 'check_out')
    def _compute_attendance_date(self):
        for attendance in self:
            tz = attendance.employee_id.tz
            check_in_date = check_out_date = None
            if attendance.check_in:
                check_in_date = attendance.check_in.replace(tzinfo=utc).astimezone(timezone(tz)).date()
            if attendance.check_out:
                check_out_date = attendance.check_out.replace(tzinfo=utc).astimezone(timezone(tz)).date()

            attendance.p_attendance_date = check_in_date or check_out_date

    @api.depends('employee_id')
    def _compute_department(self):
        for attendance in self:
            department = attendance.employee_id.department_id
            attendance.p_department_name = department.name
            attendance.p_department_code = department.p_code

    @api.depends('employee_id')
    def _compute_tz(self):
        for attendance in self:
            attendance.p_tz = attendance.employee_id.tz
