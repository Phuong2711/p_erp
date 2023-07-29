# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import date
from pytz import timezone, utc

MONTHS = [("01", "January"),
          ("02", "February"),
          ("03", "March"),
          ("04", "April"),
          ("05", "May"),
          ("06", "June"),
          ("07", "July"),
          ("08", "August"),
          ("09", "September"),
          ("10", "October"),
          ("11", "November"),
          ("12", "December")]


class AttendaneXlsx(models.TransientModel):
    _name = 'report.p_attendance.attendance_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Generate Attendance Report'

    def _default_month(self):
        today_date = default_date = fields.Date.context_today(self)
        if today_date.day <= 10:
            default_date = fields.Date.context_today(self) - relativedelta.relativedelta(months=1)
        return default_date.strftime('%m')

    def _default_year(self):
        today_date = fields.Date.context_today(self)
        if today_date.day <= 10 and today_date.month == 1:
            return (fields.Date.context_today(self) - relativedelta.relativedelta(months=1)).strftime('%Y')
        return today_date.strftime('%Y')

    month = fields.Selection(selection=MONTHS, string='Month', default=_default_month, required=True)
    year = fields.Char(string='Year', default=_default_year, required=True)

    def generate_xlsx_report(self, workbook, data, partners):
        def generate_attendance_source_sheet(workbook, period):
            source_sheet = workbook.add_worksheet(_('Attendance Sources'))
            # Add format
            header_format = workbook.add_format(
                {'bold': True, 'font_name': 'Times New Roman', 'font_size': 11, 'align': 'center', 'valign': 'vcenter',
                 'text_wrap': True, 'border': 1})
            title_format = workbook.add_format(
                {'bold': True, 'font_name': 'Times New Roman', 'font_size': 12, 'align': 'center', 'valign': 'vcenter',
                 'text_wrap': True})
            date_format = workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11, 'num_format': 'dd/mm/yyyy', 'right': 1, 'bottom': 3})
            time_format = workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11, 'num_format': 'hh:mm', 'right': 1, 'bottom': 3})
            normal_format = workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11, 'num_format': '@', 'right': 1, 'bottom': 3})
            number_format = workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11, 'num_format': '#,##0.00', 'right': 1, 'bottom': 3})
            # Generate header
            ddmmyy = '%d/%m/%Y'
            source_sheet.merge_range('B1:J1', _('ATTENDANCE DETAILS'), title_format)
            source_sheet.merge_range('B2:J2', _('Period from %s to %s') % (period['from_date'].strftime(ddmmyy),
                                                                           period['to_date'].strftime(ddmmyy)),
                                     title_format)
            source_sheet.write('B3', _('Employee ID'), header_format)
            source_sheet.write('C3', _('Employee Name'), header_format)
            source_sheet.write('D3', _('Department Name'), header_format)
            source_sheet.write('E3', _('Department Code'), header_format)
            source_sheet.write('F3', _('Date'), header_format)
            source_sheet.write('G3', _('Check In'), header_format)
            source_sheet.write('H3', _('Check Out'), header_format)
            source_sheet.write('I3', _('Worked Days'), header_format)
            source_sheet.write('J3', _('Code'), header_format)
            # Generate Datas
            domains = [('p_attendance_date', '>=', period['from_date']), ('p_attendance_date', '<=', period['to_date'])]
            fields = ['employee_id', 'p_department_name',
                      'p_department_code', 'p_attendance_date',
                      'check_in', 'check_out', 'p_worked_days', 'p_code', 'p_tz']
            attendances = self.env['hr.attendance'].search_read(domains, fields)
            start_row_index = 4
            for attendance in attendances:
                tz = attendance['p_tz']
                if attendance['check_in']:
                    attendance['check_in'] = attendance['check_in'].replace(tzinfo=utc).astimezone(timezone(tz)).replace(tzinfo=None)
                if attendance['check_out']:
                    attendance['check_out'] = attendance['check_out'].replace(tzinfo=utc).astimezone(timezone(tz)).replace(tzinfo=None)
                source_sheet.write(f'B{start_row_index}', attendance['employee_id'][0], normal_format)
                source_sheet.write(f'C{start_row_index}', attendance['employee_id'][1], normal_format)
                source_sheet.write(f'D{start_row_index}', attendance['p_department_name'] or ' ', normal_format)
                source_sheet.write(f'E{start_row_index}', attendance['p_department_code'] or ' ', normal_format)
                source_sheet.write(f'F{start_row_index}', attendance['p_attendance_date'], date_format)
                source_sheet.write(f'G{start_row_index}', attendance['check_in'] or ' ', time_format)
                source_sheet.write(f'H{start_row_index}', attendance['check_out'] or ' ', time_format)
                source_sheet.write(f'I{start_row_index}', attendance['p_worked_days'], number_format)
                source_sheet.write(f'J{start_row_index}', attendance['p_code'], normal_format)

                start_row_index += 1
            # Format sheet
            source_sheet.set_column("B:B", None, None, {'hidden': True})
            source_sheet.set_column("C:F", 25)
            source_sheet.set_column("G:J", 14)
            source_sheet.freeze_panes("A4")



        from_date = date(int(partners.year), int(partners.month), 1)
        to_date = from_date + relativedelta(months=1, days=-1)
        period = {
            'from_date': from_date,
            'to_date': to_date
        }
        generate_attendance_source_sheet(workbook, period)

    def action_print_xlsx(self):
        return self.env.ref('p_attendance.attendance_xlsx_report').report_action(self)