from openerp import models, fields, api
import datetime, calendar, ast
# from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx

from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')

# def get_col_widths(dataframe):
#     # First we find the maximum length of the index column
#     idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
#     # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
#     return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]


class AttendanceReport(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, lines):
        # We can recieve the data entered in the wizard here as data
        worksheet = workbook.add_worksheet("attendance_report.xlsx")
        boldc = workbook.add_format({'bold': True, 'align': 'center', 'text_wrap': True})
        holiday_regular = workbook.add_format(
            {'align': 'center', 'bold': False, 'text_wrap': True, 'bg_color': '#FFC7CE', })
        regular = workbook.add_format({'align': 'center', 'bold': False, 'text_wrap': True})

        worksheet.set_column('B:B',20)
        worksheet.set_column('C:D', 10)
        worksheet.set_row('2', boldc)
        worksheet.set_row(0,20)
        worksheet.set_row(1,20)
        worksheet.set_row(2, 50)

        start_date = datetime.datetime.strptime(lines.from_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(lines.to_date, "%Y-%m-%d")

        worksheet.merge_range('A1:Q1', "Attendance Report", boldc)
        worksheet.merge_range('A2:Q2', start_date.strftime("%B") + str(start_date.year), boldc)
        worksheet.write('A3', 'SL NO', regular)
        worksheet.write('B3', 'Employee Name', regular)
        worksheet.write('C3', 'Employee Code', regular)
        worksheet.write('D3', 'Date of Joining', regular)

        worksheet.set_column('E:AI', 2)

        comp_date = start_date
        day_first = start_date.day
        day_last = end_date.day

        col = 69
        new_col = 65
        next_col = 65

        # here we checking date (day_first < 23) because we need to get the cell address which is like A1,B2,..
        # so after Z the cell address going like AB1, AB2,.. so we have to get the cell character
        # so we are checking the condition (day_first < 23) because we have only 24 english alphabets

        for i in range(day_last):
            if day_first < 23:
                public_holiday = self.env['public.holiday'].search([('date', '=', comp_date.strftime("%Y-%m-%d"))])
                if not public_holiday and comp_date.weekday() != 6:
                    worksheet.write('%s3' % (chr(col)), day_first, regular)
                else:
                    worksheet.write('%s3' % (chr(col)), day_first, holiday_regular)

                day_first = day_first + 1
                comp_date = comp_date + timedelta(days=1)
                col += 1
            else:
                public_holiday = self.env['public.holiday'].search([('date', '=', comp_date.strftime("%Y-%m-%d"))])
                if not public_holiday and comp_date.weekday() != 6:
                    worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), day_first, regular)
                else:
                    worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), day_first, holiday_regular)
                day_first = day_first + 1
                comp_date = comp_date + timedelta(days=1)
                next_col += 1

        next_col = 74

        # worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Previous Attendance Credit", regular)
        # next_col += 1
        # worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Current Month Leave Credit", regular)
        # next_col += 1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Overtime Hours", regular)
        next_col += 1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Sundays/Holidays", regular)
        next_col += 1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Attendance", regular)
        next_col += 1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Leave", regular)
        next_col += 1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Absent", regular)
        next_col += 1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Non-Attendance Days", regular)
        next_col += 1
        # worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Total Attendance Payable", regular)
        # next_col += 1
        #
        # worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Leave Carry Forward", regular)

        domain = []
        if lines.attendance_category:
            domain=[('attendance_category','=',lines.attendance_category)]
        employees = self.env['hr.employee'].search(domain)

        row_no = 4
        sl_no = 1

        for emp in employees:
            worksheet.write('A%s' % (row_no), sl_no, regular)
            sl_no += 1
            worksheet.write('B%s' % (row_no), emp.name, regular)
            worksheet.write('C%s' % (row_no), emp.emp_code or '', regular)
            join_date = ''
            if emp.joining_date <= lines.to_date and emp.joining_date >= lines.from_date:
                join_date = emp.joining_date
            worksheet.write('D%s' % (row_no), join_date, regular)

            non_att_count = 0
            co_att_count = 0
            att_acount = 0
            absent_count = 0
            cmp_date = start_date
            attendance = ''
            col = 69
            new_col = 65
            next_col = 65
            sunday_holiday = 0

            for day in range(end_date.day):
                if cmp_date.day < 23:
                    attendance_id = self.env['employee.attendance'].search(
                        [('employee_id', '=', emp.id), ('date', '=', cmp_date)])
                    if not attendance_id.attendance:
                        attendance = ''
                        non_att_count += 1
                    if attendance_id.attendance == 'full':
                        if not attendance_id.compensatory_off:
                            attendance = 'FP'
                            att_acount +=1
                        else:
                            attendance = 'CO'
                            co_att_count += 1
                            if attendance_id.half_compensatory_off:
                                att_acount += 0.5
                    if attendance_id.attendance == 'half':
                        if attendance_id.compensatory_off:
                            attendance = 'HC'
                            co_att_count += 0.5
                        else:
                            att_acount = 0.5
                            attendance = 'HP'
                    attend_regular = workbook.add_format(
                        {'align': 'center', 'bold': False, 'font_color': 'green', 'text_wrap': True})
                    if attendance_id.attendance == 'absent':
                        attendance = 'AB'
                        absent_count += 1
                        attend_regular = workbook.add_format(
                            {'align': 'center', 'bold': False, 'font_color': 'red', 'text_wrap': True})
                    public_holiday = self.env['public.holiday'].search([('date', '=', cmp_date)])
                    if not public_holiday and cmp_date.weekday() != 6:
                        worksheet.write('%s%s' % (chr(col), row_no), attendance, attend_regular)
                    elif cmp_date.weekday() == 6:
                        worksheet.write('%s%s' % (chr(col), row_no), 'S', holiday_regular)
                        sunday_holiday+=1
                    else:
                        worksheet.write('%s%s' % (chr(col), row_no), 'H', holiday_regular)
                        sunday_holiday+=1
                    col += 1
                else:
                    attendance_id = self.env['employee.attendance'].search(
                        [('employee_id', '=', emp.id), ('date', '=', cmp_date)])
                    if not attendance_id.attendance:
                        attendance = ''
                        non_att_count += 1
                    if attendance_id.attendance == 'full':
                        if not attendance_id.compensatory_off:
                            attendance = 'FP'
                            att_acount +=1
                        else:
                            attendance = 'CO'
                            co_att_count += 1
                            if attendance_id.half_compensatory_off:
                                att_acount += 0.5
                    if attendance_id.attendance == 'half':
                        if attendance_id.compensatory_off:
                            attendance = 'HC'
                            co_att_count += 0.5
                        else:
                            att_acount = 0.5
                            attendance = 'HP'
                    attend_regular = workbook.add_format(
                        {'align': 'center', 'bold': False, 'font_color': 'green', 'text_wrap': True})
                    if attendance_id.attendance == 'absent':
                        attendance = 'AB'
                        absent_count += 1
                        attend_regular = workbook.add_format(
                            {'align': 'center', 'bold': False, 'font_color': 'red', 'text_wrap': True})
                    public_holiday = self.env['public.holiday'].search([('date', '=', cmp_date)])
                    if not public_holiday and cmp_date.weekday() != 6:
                        worksheet.write('%s%s%s' % (chr(new_col), chr(next_col),row_no), attendance, attend_regular)
                    elif cmp_date.weekday() == 6:
                        worksheet.write('%s%s%s' % (chr(new_col), chr(next_col),row_no), 'S', holiday_regular)
                        sunday_holiday+=1
                    else:
                        worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), 'H', holiday_regular)
                        sunday_holiday+=1
                    next_col += 1
                cmp_date = cmp_date + timedelta(days=1)

            next_col = 74
            # worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), prev_credit, regular)
            # next_col += 1            #
            # worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), current_credit, regular)            #
            # next_col += 1
            overtime_ids = self.env['over.time'].search([('employee_id', '=', emp.id),
                                                                ('date', '>=', lines.from_date),
                                                                ('date', '<=', lines.to_date)])
            overtime = sum(overtime_ids.mapped('hours'))
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), overtime, regular)
            next_col += 1
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), sunday_holiday, regular)
            next_col += 1
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), att_acount, regular)
            next_col += 1
            leaves_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id),
                                                                ('date_from', '>=', lines.from_date),
                                                                ('date_from', '<=', lines.to_date),
                                                                ('date_to', '>=', lines.from_date),
                                                                ('date_to', '<=', lines.to_date),
                                                                ('state', 'not in', ['cancel','refuse','draft'])])
            leaves = sum(leaves_ids.mapped('number_of_days_temp'))
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), leaves, regular)
            next_col += 1
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), absent_count, regular)
            next_col += 1
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), non_att_count, regular)
            next_col += 1
            # worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), carry_forward, regular)

            row_no+=1


AttendanceReport('report.hiworth_hr_attendance.report_attendance_report.xlsx', 'hiworth.hr.leave')

class AttendanceReportWizard(models.TransientModel):
    _name = 'attendance.report.wizard'

    from_date = fields.Date(default=lambda self: self.default_time_range('from'))
    to_date = fields.Date(default=lambda self: self.default_time_range('to'))
    type_selection = fields.Selection([('approved', 'Approved'), ('confirm', 'Confirmed'), ('both', 'Both')],
                                      default='approved')
    attendance_type = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
                                       default='monthly')
    active_ids = fields.Char()
    attendance_category = fields.Selection([('office_staff', 'Office Staff'),
                                            ('site_employee', 'Site Employee'),
                                            ('taurus_driver', 'Taurus Driver'),
                                            ('eicher_driver', 'Eicher Driver'),
                                            ('pickup_driver', 'Pick Up Driver'),
                                            ('operators', 'Operators'),
                                            ('cleaners', 'Cleaners')
                                            ], string='Attendance Category')

    @api.multi
    def print_attendance_report(self):
        data = {'form': self.read(['from_date', 'end_date', 'type_selection','attendance_type','attendance_category'])}
        return {'type': 'ir.actions.report.xml',
                'report_name': 'cms_hr.excel_attendance_report.xlsx',
                'datas': data
                }

    @api.model
    def default_time_range(self, type):
        year = datetime.date.today().year
        month = datetime.date.today().month
        last_day = calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1]
        first_day = 1
        if type == 'from':
            return datetime.date(year, month, first_day)
        elif type == 'to':
            return datetime.date(year, month, last_day)
