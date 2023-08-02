# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date
from pytz import timezone, utc
import calendar

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


attendance_column_names = ['G', 'H', 'I', 'J', 'K', 'L',
                           'M', 'N', 'O', 'P', 'Q', 'R',
                           'S', 'T', 'U', 'V', 'W', 'X',
                           'Y', 'Z', 'AA', 'AB', 'AC', 'AD',
                           'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK']


class AttendanceXlsx(models.TransientModel):
    _name = 'report.p_attendance.attendance_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Generate Attendance Report'

    def _default_month(self):
        today_date = default_date = fields.Date.context_today(self)
        if today_date.day <= 10:
            default_date = fields.Date.context_today(self) - relativedelta(months=1)
        return default_date.strftime('%m')

    def _default_year(self):
        today_date = fields.Date.context_today(self)
        if today_date.day <= 10 and today_date.month == 1:
            return (fields.Date.context_today(self) - relativedelta(months=1)).strftime('%Y')
        return today_date.strftime('%Y')

    month = fields.Selection(selection=MONTHS, string='Month', default=_default_month, required=True)
    year = fields.Char(string='Year', default=_default_year, required=True)

    def generate_xlsx_report(self, workbook, data, partners):
        def get_selected_period(partners):
            from_date = date(year=int(partners.year), month=int(partners.month), day=1)
            to_date = from_date + relativedelta(months=1, days=-1)
            return {
                'from_date': from_date,
                'to_date': to_date
            }

        def generate_attendance_source_sheet(workbook, period):
            work_sheet = workbook.add_worksheet(_('Attendance Sources'))
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
            work_sheet.merge_range('A1:I1', _('ATTENDANCE DETAILS'), title_format)
            work_sheet.merge_range('A2:I2', _('Period from %s to %s') % (period['from_date'].strftime(ddmmyy),
                                                                           period['to_date'].strftime(ddmmyy)),
                                     title_format)
            work_sheet.write('A3', _('Employee ID'), header_format)
            work_sheet.write('B3', _('Employee Name'), header_format)
            work_sheet.write('C3', _('Department Name'), header_format)
            work_sheet.write('D3', _('Department Code'), header_format)
            work_sheet.write('E3', _('Date'), header_format)
            work_sheet.write('F3', _('Check In'), header_format)
            work_sheet.write('G3', _('Check Out'), header_format)
            work_sheet.write('H3', _('Worked Days'), header_format)
            work_sheet.write('I3', _('Code'), header_format)
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
                work_sheet.write(f'A{start_row_index}', attendance['employee_id'][0], normal_format)
                work_sheet.write(f'B{start_row_index}', attendance['employee_id'][1], normal_format)
                work_sheet.write(f'C{start_row_index}', attendance['p_department_name'] or ' ', normal_format)
                work_sheet.write(f'D{start_row_index}', attendance['p_department_code'] or ' ', normal_format)
                work_sheet.write(f'E{start_row_index}', attendance['p_attendance_date'], date_format)
                work_sheet.write(f'F{start_row_index}', attendance['check_in'] or ' ', time_format)
                work_sheet.write(f'G{start_row_index}', attendance['check_out'] or ' ', time_format)
                work_sheet.write(f'H{start_row_index}', attendance['p_worked_days'], number_format)
                work_sheet.write(f'I{start_row_index}', attendance['p_code'], normal_format)

                start_row_index += 1
            # Format sheet
            work_sheet.set_column("A:A", None, None, {'hidden': True})
            work_sheet.set_column("B:E", 25)
            work_sheet.set_column("F:I", 14)
            work_sheet.freeze_panes("A4")

        def generate_sumary_sheet(workbook, period):
            work_sheet = workbook.add_worksheet(_('Monthly Attendances'))
            WEEKDAYS = {0: _("Mon"), 1: _("Tue"),
                        2: _("Wed"), 3: _("Thu"),
                        4: _("Fri"), 5: _("Sat"),
                        6: _("Sun")}
            # Unpacking period
            start_date, end_date = period.values()
            # Add Format
            header_format = workbook.add_format(
                {'bold': True, 'font_name': 'Times New Roman', 'font_size': 11, 'align': 'center', 'valign': 'vcenter',
                 'text_wrap': True, 'border': 1})
            title_format = workbook.add_format(
                {'bold': True, 'font_name': 'Times New Roman', 'font_size': 12, 'align': 'center', 'valign': 'vcenter',
                 'text_wrap': True})
            date_format = workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11, 'align': 'center', 'num_format': 'dd', 'right': 1,
                 'bottom': 1, 'top': 1})
            normal_format = workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11, 'num_format': '@', 'right': 1, 'bottom': 1})
            index_format = workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11, 'align': 'center', 'num_format': '@', 'right': 1,
                 'bottom': 1})
            number_format = workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11,
                 'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'right': 1, 'bottom': 1})

            # Generate Header
            work_sheet.merge_range('A1:AK1', _('MONTHLY ATTENDANCE REPORT'), title_format)
            work_sheet.write('T2', _('Month:'))
            work_sheet.write('V2', _('Year:'))
            work_sheet.merge_range('A3:A4', _('No'), header_format)
            work_sheet.merge_range('B3:B4', _('ID'), header_format)
            work_sheet.merge_range('C3:C4', _('Employee code'), header_format)
            work_sheet.merge_range('D3:D4', _('Employee name'), header_format)
            work_sheet.merge_range('E3:E4', _('Department'), header_format)
            work_sheet.merge_range('F3:F4', _('Total worked days'), header_format)

            month_calendar = calendar.Calendar().itermonthdays2(start_date.year, start_date.month)
            CALENDAR_DATE_ROW_INDEX = 2
            CALENDAR_NAME_ROW_INDEX = CALENDAR_DATE_ROW_INDEX + 1
            CALENDAR_START_COL_INDEX = 6
            for day, week_day in month_calendar:
                if not day:
                    continue
                work_sheet.write_formula(CALENDAR_DATE_ROW_INDEX, CALENDAR_START_COL_INDEX, F"=DATE($W$2,$U$2,{day})", date_format)
                work_sheet.write(CALENDAR_NAME_ROW_INDEX, CALENDAR_START_COL_INDEX, WEEKDAYS.get(week_day), normal_format)
                CALENDAR_START_COL_INDEX += 1

            # Generate Data
            work_sheet.write('U2', start_date.month)
            work_sheet.write('W2', start_date.year)

            count = 1
            start_row_index = 4
            for employee in self.env['hr.employee'].search([]):
                real_row_index = start_row_index + 1
                work_sheet.write(start_row_index, 0, count, index_format)
                work_sheet.write(start_row_index, 1, employee.id, normal_format)
                work_sheet.write(start_row_index, 2, employee.p_code or ' ', normal_format)
                work_sheet.write(start_row_index, 3, employee.name, normal_format)
                work_sheet.write(start_row_index, 4, employee.department_id.name or ' ', normal_format)
                work_sheet.write_formula(start_row_index, 5, F"=SUM($G{real_row_index}:$AK{real_row_index})", number_format)
                for column_name in attendance_column_names:
                    work_sheet.write_formula(F'{column_name}{real_row_index}', F"""=SUMIFS('{_('Attendance Sources')}'!$H$4:$H$100000,'{_('Attendance Sources')}'!$A$4:$A$100000,'{_('Monthly Attendances')}'!$B{real_row_index},'{_('Attendance Sources')}'!$E$4:$E$100000,'{_('Monthly Attendances')}'!{column_name}$3)""", number_format)

                start_row_index += 1
                count += 1

            # Format Sheet
            work_sheet.set_row(3, 45)
            work_sheet.set_column('B:C', None, None, {'hidden': True})
            work_sheet.set_column('A:A', 5)
            work_sheet.set_column('D:E', 25)
            work_sheet.set_column('F:F', 9)
            work_sheet.set_column('G:AK', 7)
            work_sheet.freeze_panes('G5')





        period = get_selected_period(partners)
        generate_sumary_sheet(workbook, period)
        generate_attendance_source_sheet(workbook, period)


    def action_print_xlsx(self):
        return self.env.ref('p_attendance.attendance_xlsx_report').report_action(self)

    @api.constrains('year')
    def _check_year(self):
        if self.year and len(self.year) != 4 or not self.year.isnumeric():
            raise ValidationError(_(f'The value [%s] should be year') % self.year)