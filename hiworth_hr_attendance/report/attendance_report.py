from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import timedelta
import logging
import datetime
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class AttendanceReport(ReportXlsx):

    # def generate_xlsx_report(self, workbook, data, lines):
    #     # We can recieve the data entered in the wizard here as data
    #     worksheet = workbook.add_worksheet("attendance_report.xlsx")
    # 
    #     boldc = workbook.add_format({'bold': True, 'align': 'center', 'text_wrap': True})
    #     heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
    #     bold = workbook.add_format({'bold': True})
    #     rightb = workbook.add_format({'align': 'right', 'bold': True})
    # 
    #     holiday_regular = workbook.add_format(
    #         {'align': 'center', 'bold': False, 'text_wrap': True, 'bg_color': '#FFC7CE', })
    #     regular = workbook.add_format({'align': 'center', 'bold': False, 'text_wrap': True})
    #     attend_regular = workbook.add_format(
    #         {'align': 'center', 'bold': False, 'font_color': 'brown', 'text_wrap': True})
    #     centerb = workbook.add_format({'align': 'center', 'bold': True})
    #     center = workbook.add_format({'align': 'center'})
    #     right = workbook.add_format({'align': 'right'})
    #     bolde = workbook.add_format({'bold': True, 'font_color': 'brown'})
    #     merge_format = workbook.add_format({
    #         'bold': 1,
    #         'border': 1,
    #         'align': 'center',
    #         'valign': 'vcenter',
    #         'bg_color': '#D3D3D3',
    #         'font_color': '#000000',
    #     })
    #     format_hidden = workbook.add_format({
    #         'hidden': True
    #     })
    #     align_format = workbook.add_format({
    #         'align': 'right',
    #     })
    # 
    #     row = 7
    #     col = 0
    #     new_row = row
    #     inv = lines
    #     print
    #     "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr", inv
    #     worksheet.set_column('B:B', 20)
    #     worksheet.set_column('D:D', 20)
    #     worksheet.set_row('2', boldc)
    #     worksheet.set_row(2, 50)
    #     month = datetime.strptime(inv[0].from_date, "%Y-%m-%d").month
    #     if month == 2:
    #         if (datetime.strptime(inv[0].from_date, "%Y-%m-%d").year % 4 == 0):
    #             worksheet.set_column('D:AF', 2)
    #         else:
    #             worksheet.set_column('D:AE', 2)
    # 
    #     elif month in [1, 3, 5, 7, 8, 10, 12]:
    #         worksheet.set_column('D:AH', 2)
    # 
    #     else:
    #         worksheet.set_column('D:AG', 2)
    # 
    #     worksheet.merge_range('A1:Q1', "Attendance Report", boldc)
    # 
    #     month = datetime.strptime(inv[0].from_date, "%Y-%m-%d").month
    #     mauonth = datetime.strptime(inv[0].from_date, "%Y-%m-%d").month
    #     if month == 1:
    # 
    #         month = "January" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     elif month == 2:
    # 
    #         month = "Febuary" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     elif month == 3:
    #         month = "March" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     elif month == 4:
    #         month = "April" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     elif month == 5:
    #         month = "May" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     elif month == 6:
    #         month = "June" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     elif month == 7:
    #         month = "July" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     elif month == 8:
    #         month = "August" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     elif month == 9:
    #         month = "Septemper" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     elif month == 10:
    #         month = "October" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     elif month == 11:
    #         month = "November" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     else:
    #         month = "December" + str(datetime.strptime(inv[0].from_date, "%Y-%m-%d").year)
    #     worksheet.merge_range('A2:Q2', month, boldc)
    #     worksheet.write('A3', 'SL NO:', regular)
    #     worksheet.write('B3', 'Employee Name', regular)
    #     worksheet.write('C3', 'Employee Code', regular)
    #     worksheet.write('D3', 'Date of Joining', regular)
    #     comp_date = datetime.strptime(inv[0].from_date, "%Y-%m-%d")
    #     day_first = datetime.strptime(inv[0].from_date, "%Y-%m-%d").day
    #     day_last = datetime.strptime(inv[0].to_date, "%Y-%m-%d").day
    #     col = 69
    #     new_col = 65
    #     next_col = 65
    #     for i in range(day_last):
    #         if day_first < 23:
    #             public_holiday = self.env['public.holiday'].search([('date', '=', comp_date.strftime("%Y-%m-%d"))])
    #             if not public_holiday and comp_date.weekday() != 6:
    #                 worksheet.write('%s3' % (chr(col)), day_first, regular)
    #             else:
    #                 worksheet.write('%s3' % (chr(col)), day_first, holiday_regular)
    # 
    #             day_first = day_first + 1
    #             comp_date = comp_date + timedelta(days=1)
    #             col += 1
    #         else:
    #             public_holiday = self.env['public.holiday'].search([('date', '=', comp_date.strftime("%Y-%m-%d"))])
    #             if not public_holiday and comp_date.weekday() != 6:
    #                 worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), day_first, regular)
    #             else:
    #                 worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), day_first, holiday_regular)
    #             day_first = day_first + 1
    #             comp_date = comp_date + timedelta(days=1)
    #             next_col += 1
    #     # worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Previous Attendance Credit", regular)
    #     # next_col += 1
    #     # worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Current Month Attendance Credit", regular)
    #     # next_col += 1
    #     # worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Exgratia", regular)
    #     worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Overtime Hours", regular)
    #     next_col += 1
    #     worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Sunday/Holiday Working Hours", regular)
    #     next_col += 1
    #     worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Attendance", regular)
    #     next_col += 1
    #     worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Leave", regular)
    #     next_col += 1
    # 
    #     worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Absent", regular)
    #     next_col += 1
    #     worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Non-Attendance Days", regular)
    #     next_col += 1
    #     # worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Total Attendance Payable", regular)
    # 
    #     # next_col += 1
    #     # worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Leave Carry Forward", regular)
    # 
    #     row_no = 4
    #     sl_no = 1
    # 
    #     active_ids = inv[0].get_selected_users(inv[0].active_ids)
    # 
    #     for emp in active_ids:
    #         carry_forward = (emp.get_lop(emp.id, inv[0].from_date, inv[0].to_date))
    #         print
    #         "carryyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", carry_forward
    #         sunday_days = emp.get_sunday(emp.id, inv[0].from_date, inv[0].to_date)
    #         for abs_att in self.env['hiworth.hr.attendance'].search(
    #                 [('name', '=', emp.id), ('date', '>=', inv[0].from_date), ('date', '<=', inv[0].to_date),
    #                  ('attendance', 'in', ['absent', 'half'])], order='date asc'):
    #             abs_att_date = datetime.strptime(abs_att.date, "%Y-%m-%d")
    #             if carry_forward > 0:
    #                 public_holiday = self.env['public.holiday'].search([('date', '=', abs_att_date)])
    #                 if abs_att_date.weekday() == 6 or public_holiday:
    #                     if public_holiday:
    #                         if abs_att_date.weekday() == 0:
    #                             week_start = abs_att_date
    #                             week_end = abs_att_date + timedelta(days=6)
    #                         if abs_att_date.weekday() == 1:
    #                             week_start = abs_att_date - timedelta(days=1)
    #                             week_end = abs_att_date + timedelta(days=5)
    #                         if abs_att_date.weekday() == 2:
    #                             week_start = abs_att_date - timedelta(days=2)
    #                             week_end = abs_att_date + timedelta(days=4)
    #                         if abs_att_date.weekday() == 3:
    #                             week_start = abs_att_date - timedelta(days=3)
    #                             week_end = abs_att_date + timedelta(days=3)
    #                         if abs_att_date.weekday() == 4:
    #                             week_start = abs_att_date - timedelta(days=4)
    #                             week_end = abs_att_date + timedelta(days=2)
    #                         if abs_att_date.weekday() == 5:
    #                             week_start = abs_att_date - timedelta(days=5)
    #                             week_end = abs_att_date + timedelta(days=1)
    #                         previous_days = self.env['hiworth.hr.attendance'].search([
    #                             ('name', '=', emp.id), ('date', '>=', week_start),
    #                             ('date', '<', week_end)])
    #                         previous_days_len = len(previous_days)
    #                         no_days = 5
    #                     else:
    #                         previous_days = self.env['hiworth.hr.attendance'].search([
    #                             ('name', '=', emp.id), ('date', '>=', abs_att_date - timedelta(days=6)),
    #                             ('date', '<', abs_att_date)])
    #                         previous_days_len = len(previous_days)
    #                         no_days = 6
    #                     if emp.joining_date:
    #                         joining_date = datetime.strptime(emp.joining_date, "%Y-%m-%d")
    #                         if joining_date.month == abs_att_date.month:
    #                             if joining_date > abs_att_date - timedelta(days=6):
    #                                 no_days_before_joining = (joining_date - (abs_att_date - timedelta(days=6))).days
    #                                 attendance_days = self.env['hiworth.hr.attendance'].search([
    #                                     ('name', '=', emp.id), ('date', '>=', emp.joining_date),
    #                                     ('date', '<', abs_att_date)])
    #                                 if len(attendance_days) == (6 - no_days_before_joining):
    #                                     if public_holiday:
    #                                         previous_days_len = 5
    #                                     else:
    #                                         previous_days_len = 6
    #                     if previous_days_len == no_days:
    #                         if abs_att.attendance == 'half':
    #                             abs_att.compensatory_off = True
    #                             abs_att.attendance = 'full'
    #                             abs_att.half_compensatory_off = True
    #                             carry_forward -= 0.5
    #                             leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1,
    #                                                                                order='id asc')
    #                             config_employee = self.env['employee.config.leave'].search([
    #                                 ('employee_id', '=', emp.id), ('leave_id', '=', leave_type.id), ])
    #                             if config_employee:
    #                                 config_employee.availed += 0.5
    #                             month_leave = self.env['month.leave.status'].search(
    #                                 [('status_id', '=', emp.id), ('month_id', '=', mauonth),
    #                                  ('leave_id', '=', leave_type.id)])
    #                             contract = self.env['hr.contract'].search(
    #                                 [('employee_id', '=', emp.id),
    #                                  ('state', '=', 'active')], limit=1, order='id desc')
    #                             if month_leave:
    #                                 if month_leave.exgratia >= month_leave.remaining:
    #                                     exgratia_full_ids = self.env['exgratia.payment'].search([
    #                                         ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                         ('exgratia_redeem', '=', 'leave'),
    #                                         ('estimated', '=', False)], limit=1)
    #                                     exgratia_half_ids = self.env['exgratia.payment'].search([
    #                                         ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                         ('exgratia_redeem', '=', 'leave'), ], limit=1)
    #                                     exgratia_full_half_ids = self.env['exgratia.payment'].search([
    #                                         ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                         ('exgratia_redeem', '=', 'leave'), ('estimated', '=', 'half')], limit=1)
    # 
    #                                     exgratia = len(exgratia_full_ids) + (len(exgratia_half_ids) * .5) + (
    #                                                 len(exgratia_full_half_ids) * 0.5)
    #                                     if exgratia > 0:
    #                                         if exgratia_half_ids:
    #                                             exgratia_half = exgratia_half_ids
    #                                             exgratia_half.state = 'paid'
    #                                             abs_att.exgratia_id1 = exgratia_half.id
    # 
    #                                         elif not exgratia_half_ids and exgratia_full_half_ids:
    #                                             exgratia_half = exgratia_full_half_ids
    #                                             exgratia_half.state = 'paid'
    #                                             abs_att.exgratia_id1 = exgratia_half.id
    # 
    #                                         else:
    #                                             exgratia_full = exgratia_full_ids
    #                                             # exgratia_full.attendance = 'half'
    #                                             exgratia_full.estimated = 'half'
    #                                             abs_att.exgratia_id1 = exgratia_full.id
    # 
    #                                         if contract:
    #                                             contract.availed_exgratia += 0.5
    #                                 month_leave.availed += 0.5
    # 
    #                         else:
    #                             if carry_forward < 1:
    #                                 abs_att.compensatory_off = True
    #                                 abs_att.attendance = 'half'
    #                                 carry_forward -= 0.5
    #                                 leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1,
    #                                                                                    order='id asc')
    #                                 config_employee = self.env['employee.config.leave'].search(
    #                                     [('employee_id', '=', emp.id),
    #                                      (
    #                                          'leave_id', '=', leave_type.id),
    #                                      ])
    #                                 if config_employee:
    #                                     config_employee.availed += 0.5
    #                                 month_leave = self.env['month.leave.status'].search(
    #                                     [('status_id', '=', emp.id), ('month_id', '=', mauonth),
    #                                      ('leave_id', '=', leave_type.id)])
    #                                 if month_leave:
    #                                     if month_leave.exgratia >= month_leave.remaining:
    # 
    #                                         exgratia_half_ids = self.env['exgratia.payment'].search([
    #                                             ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                             ('exgratia_redeem', '=', 'leave'), ], limit=1)
    # 
    #                                         exgratia_full_half_ids = self.env['exgratia.payment'].search([
    #                                             ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                             ('exgratia_redeem', '=', 'leave'),
    #                                             ('estimated', '=', 'half')], limit=1)
    #                                         exgratia = (len(exgratia_full_half_ids) * .5) + (
    #                                                     len(exgratia_half_ids) * .5)
    # 
    #                                         if exgratia > 0:
    #                                             contract = self.env['hr.contract'].search(
    #                                                 [('employee_id', '=', emp.id),
    #                                                  ('state', '=', 'active')], limit=1, order='id desc')
    #                                             if exgratia_half_ids:
    #                                                 exgratia_half = exgratia_half_ids
    #                                                 exgratia_half.state = 'paid'
    #                                                 abs_att.exgratia_id1 = exgratia_half.id
    #                                             else:
    #                                                 if exgratia_full_half_ids:
    #                                                     exgratia_half = exgratia_full_half_ids
    #                                                     exgratia_half.state = 'paid'
    #                                                     abs_att.exgratia_id1 = exgratia_half.id
    #                                             if contract:
    #                                                 contract.availed_exgratia += 0.5
    #                                     month_leave.availed += 0.5
    # 
    #                             else:
    #                                 abs_att.compensatory_off = True
    #                                 abs_att.attendance = 'full'
    #                                 carry_forward -= 1
    #                                 leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1,
    #                                                                                    order='id asc')
    #                                 config_employee = self.env['employee.config.leave'].search(
    #                                     [('employee_id', '=', emp.id),
    #                                      ('leave_id', '=', leave_type.id),
    #                                      ])
    #                                 if config_employee:
    #                                     config_employee.availed += 1
    #                                 month_leave = self.env['month.leave.status'].search(
    #                                     [('status_id', '=', emp.id), ('month_id', '=', mauonth),
    #                                      ('leave_id', '=', leave_type.id)])
    #                                 if month_leave:
    #                                     if month_leave.exgratia >= month_leave.remaining:
    #                                         exgratia_full_ids = self.env['exgratia.payment'].search([
    #                                             ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                             ('exgratia_redeem', '=', 'leave'),
    #                                             ('estimated', '=', False)], limit=1)
    #                                         exgratia_half_ids = self.env['exgratia.payment'].search([
    #                                             ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                             ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'half')],
    #                                             limit=2)
    #                                         exgratia_full_half_ids = self.env['exgratia.payment'].search([
    #                                             ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                             ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
    #                                             ('estimated', '=', 'half')], limit=2)
    #                                         exgratia = len(exgratia_full_ids) + (len(exgratia_half_ids) * 0.5) + (
    #                                                     len(exgratia_full_half_ids) * 0.5)
    # 
    #                                         if exgratia > 0:
    #                                             if exgratia_full_ids:
    #                                                 exgratia_full = exgratia_full_ids
    #                                                 exgratia_full.state = 'paid'
    #                                                 abs_att.exgratia_id1 = exgratia_full.id
    # 
    #                                             elif len(exgratia_full_half_ids) >= 2:
    #                                                 exgratia_full_half = exgratia_full_half_ids
    #                                                 for exgratia_id in exgratia_full_half:
    #                                                     exgratia_id.state = 'paid'
    #                                                 abs_att.exgratia_id1 = exgratia_full_half.ids[0]
    #                                                 abs_att.exgratia_id2 = exgratia_full_half.ids[1]
    # 
    #                                             elif len(exgratia_half_ids) >= 2:
    #                                                 exgratia_half = exgratia_half_ids
    #                                                 for exgratia_id in exgratia_half:
    #                                                     exgratia_id.state = 'paid'
    #                                                 abs_att.exgratia_id1 = exgratia_half.ids[0]
    #                                                 abs_att.exgratia_id2 = exgratia_half.ids[1]
    #                                             else:
    #                                                 if exgratia_full_half_ids and exgratia_half_ids:
    #                                                     exgratia_half = self.env['exgratia.payment'].search([
    #                                                         ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                                         ('exgratia_redeem', '=', 'leave'),
    #                                                         ('attendance', '=', 'half')], limit=1)
    # 
    #                                                     exgratia_full_half = self.env['exgratia.payment'].search([
    #                                                         ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                                         ('exgratia_redeem', '=', 'leave'),
    #                                                         ('attendance', '=', 'full'),
    #                                                         ('estimated', '=', 'half')], limit=1)
    #                                                     exgratia_half.state = 'paid'
    #                                                     exgratia_full_half.state = 'paid'
    #                                                     abs_att.exgratia_id1 = exgratia_half.id
    #                                                     abs_att.exgratia_id2 = exgratia_full_half.id
    # 
    #                                             contract = self.env['hr.contract'].search(
    #                                                 [('employee_id', '=', emp.id),
    #                                                  ('state', '=', 'active')], limit=1, order='id desc')
    # 
    #                                             if contract:
    #                                                 contract.availed_exgratia += 1
    #                                     month_leave.availed += 1
    # 
    #                 else:
    #                     if abs_att.attendance == 'half':
    #                         abs_att.half_compensatory_off = True
    #                         abs_att.compensatory_off = True
    #                         abs_att.attendance = 'full'
    #                         carry_forward -= .5
    #                         leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1,
    #                                                                            order='id asc')
    #                         config_employee = self.env['employee.config.leave'].search([
    #                             ('employee_id', '=', emp.id), ('leave_id', '=', leave_type.id), ])
    #                         if config_employee:
    #                             config_employee.availed += .5
    #                         month_leave = self.env['month.leave.status'].search(
    #                             [('status_id', '=', emp.id), ('month_id', '=', mauonth),
    #                              ('leave_id', '=', leave_type.id)])
    #                         if month_leave:
    #                             if month_leave.exgratia >= month_leave.remaining:
    #                                 exgratia_full_ids = self.env['exgratia.payment'].search([
    #                                     ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                     ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
    #                                     ('estimated', '=', False)], limit=1)
    #                                 exgratia_half_ids = self.env['exgratia.payment'].search([
    #                                     ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                     ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'half')], limit=1)
    #                                 exgratia_full_half_ids = self.env['exgratia.payment'].search([
    #                                     ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                     ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
    #                                     ('estimated', '=', 'half')], limit=1)
    #                                 exgratia = len(exgratia_full_ids) + (len(exgratia_half_ids) * .5) + (
    #                                         len(exgratia_full_half_ids) * .5)
    #                                 if exgratia > 0:
    #                                     if exgratia_half_ids:
    #                                         exgratia_half = exgratia_half_ids
    #                                         exgratia_half.state = 'paid'
    #                                         abs_att.exgratia_id1 = exgratia_half.id
    # 
    #                                     elif not exgratia_half_ids and exgratia_full_half_ids:
    #                                         exgratia_half = exgratia_full_half_ids
    #                                         exgratia_half.state = 'paid'
    #                                         abs_att.exgratia_id1 = exgratia_half.id
    # 
    #                                     else:
    #                                         exgratia_full = exgratia_full_ids
    #                                         exgratia_full.estimated = 'half'
    #                                         abs_att.exgratia_id1 = exgratia_full.id
    # 
    #                                     contract = self.env['hr.contract'].search(
    #                                         [('employee_id', '=', emp.id),
    #                                          ('state', '=', 'active')], limit=1, order='id desc')
    # 
    #                                     if contract:
    #                                         contract.availed_exgratia += 0.5
    #                             month_leave.availed += 0.5
    # 
    # 
    #                     else:
    #                         if carry_forward < 1:
    #                             abs_att.compensatory_off = True
    #                             abs_att.attendance = 'half'
    #                             carry_forward -= .5
    #                             leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1,
    #                                                                                order='id asc')
    #                             config_employee = self.env['employee.config.leave'].search(
    #                                 [('employee_id', '=', emp.id),
    #                                  (
    #                                      'leave_id', '=', leave_type.id),
    #                                  ])
    #                             if config_employee:
    #                                 config_employee.availed += .5
    #                             month_leave = self.env['month.leave.status'].search(
    #                                 [('status_id', '=', emp.id), ('month_id', '=', mauonth),
    #                                  ('leave_id', '=', leave_type.id)])
    #                             if month_leave:
    #                                 if month_leave.exgratia >= month_leave.remaining:
    #                                     exgratia_half_ids = self.env['exgratia.payment'].search([
    #                                         ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                         ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'half')], limit=1)
    # 
    #                                     exgratia_full_half_ids = self.env['exgratia.payment'].search([
    #                                         ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                         ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
    #                                         ('estimated', '=', 'half')], limit=1)
    # 
    #                                     if exgratia_half_ids:
    #                                         exgratia_half = exgratia_half_ids
    #                                         exgratia_half.state = 'paid'
    #                                         abs_att.exgratia_id1 = exgratia_half.id
    #                                     else:
    #                                         if exgratia_full_half_ids:
    #                                             exgratia_half = exgratia_full_half_ids
    #                                             exgratia_half.state = 'paid'
    #                                             abs_att.exgratia_id1 = exgratia_half.id
    # 
    #                                     contract = self.env['hr.contract'].search(
    #                                         [('employee_id', '=', emp.id),
    #                                          ('state', '=', 'active')], limit=1, order='id desc')
    # 
    #                                     if contract:
    #                                         contract.availed_exgratia += 0.5
    # 
    #                                 month_leave.availed += 0.5
    # 
    #                         else:
    #                             abs_att.compensatory_off = True
    #                             abs_att.attendance = 'full'
    #                             carry_forward -= 1
    #                             leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1,
    #                                                                                order='id asc')
    #                             config_employee = self.env['employee.config.leave'].search(
    #                                 [('employee_id', '=', emp.id),
    #                                  ('leave_id', '=', leave_type.id),
    #                                  ])
    #                             if config_employee:
    #                                 config_employee.availed += 1
    #                             month_leave = self.env['month.leave.status'].search(
    #                                 [('status_id', '=', emp.id), ('month_id', '=', mauonth),
    #                                  ('leave_id', '=', leave_type.id)])
    #                             if month_leave:
    #                                 if month_leave.exgratia >= month_leave.remaining:
    #                                     exgratia_full_ids = self.env['exgratia.payment'].search([
    #                                         ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                         ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
    #                                         ('estimated', '=', False)], limit=1)
    # 
    #                                     exgratia_half_ids = self.env['exgratia.payment'].search([
    #                                         ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                         ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'half')], limit=2)
    # 
    #                                     exgratia_full_half_ids = self.env['exgratia.payment'].search([
    #                                         ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                         ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
    #                                         ('estimated', '=', 'half')], limit=2)
    # 
    #                                     exgratia = len(exgratia_full_ids) + (len(exgratia_half_ids) * 0.5) + (
    #                                             len(exgratia_full_half_ids) * 0.5)
    # 
    #                                     if exgratia > 0:
    #                                         if exgratia_full_ids:
    #                                             exgratia_full = exgratia_full_ids
    #                                             exgratia_full.state = 'paid'
    #                                             abs_att.exgratia_id1 = exgratia_full.id
    # 
    #                                         elif len(exgratia_full_half_ids) >= 2:
    #                                             exgratia_full_half = exgratia_full_half_ids
    #                                             for exgratia_id in exgratia_full_half:
    #                                                 exgratia_id.state = 'paid'
    #                                             abs_att.exgratia_id1 = exgratia_full_half.ids[0]
    #                                             abs_att.exgratia_id2 = exgratia_full_half.ids[1]
    # 
    #                                         elif len(exgratia_half_ids) >= 2:
    #                                             exgratia_half = exgratia_half_ids
    #                                             for exgratia_id in exgratia_half:
    #                                                 exgratia_id.state = 'paid'
    #                                             abs_att.exgratia_id1 = exgratia_half.ids[0]
    #                                             abs_att.exgratia_id2 = exgratia_half.ids[1]
    # 
    #                                         else:
    #                                             if exgratia_full_half_ids and exgratia_half_ids:
    #                                                 exgratia_half = self.env['exgratia.payment'].search([
    #                                                     ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                                     ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'half')],
    #                                                     limit=1)
    #                                                 exgratia_full_half = self.env['exgratia.payment'].search([
    #                                                     ('employee_id', '=', emp.id), ('state', '=', 'new'),
    #                                                     ('exgratia_redeem', '=', 'leave'),
    #                                                     ('estimated', '=', 'half')], limit=1)
    # 
    #                                                 exgratia_half.state = 'paid'
    #                                                 exgratia_full_half.state = 'paid'
    #                                                 abs_att.exgratia_id1 = exgratia_half.id
    #                                                 abs_att.exgratia_id2 = exgratia_full_half.id
    # 
    #                                     contract = self.env['hr.contract'].search(
    #                                         [('employee_id', '=', emp.id),
    #                                          ('state', '=', 'active')], limit=1, order='id desc')
    # 
    #                                     if contract:
    #                                         contract.availed_exgratia += 1
    #                                 month_leave.availed += 1
    # 
    #         print
    #         "carry forwardhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh", carry_forward
    # 
    #         total_att = 0
    #         worksheet.write('A%s' % (row_no), sl_no, regular)
    #         sl_no += 1
    #         worksheet.write('B%s' % (row_no), emp.name, regular)
    #         worksheet.write('C%s' % (row_no), emp.emp_code, regular)
    #         print
    #         "hhhhhhhhhhhhh", emp.joining_date
    #         join_date = ''
    #         if emp.joining_date <= inv[0].to_date and emp.joining_date >= inv[0].from_date:
    #             join_date = emp.joining_date
    #         worksheet.write('D%s' % (row_no), join_date, regular)
    #         day_first = datetime.strptime(inv[0].from_date, "%Y-%m-%d")
    #         day_first_day = datetime.strptime(inv[0].from_date, "%Y-%m-%d").day
    #         day_last = datetime.strptime(inv[0].to_date, "%Y-%m-%d")
    #         day_last_day = datetime.strptime(inv[0].to_date, "%Y-%m-%d").day
    #         no_of_days = day_last - day_first
    #         col = 69
    #         new_col = 65
    #         next_col = 65
    #         attendan = ''
    #         no_absent_days = 0
    #         non_att_days = 0
    #         co_att_count = 0
    #         for i in range(day_last_day):
    #             if day_first_day < 23:
    #                 attendance = self.env['hiworth.hr.attendance'].search(
    #                     [('name', '=', emp.id), ('date', '=', day_first)])
    #                 att = 0
    #                 if not attendance.attendance:
    #                     attendan = ''
    #                     non_att_days += 1
    #                 if attendance.attendance == 'full':
    #                     if not attendance.compensatory_off:
    #                         attendan = 'FP'
    #                         att = 1
    #                     else:
    #                         attendan = 'CO'
    #                         co_att_count += co_att_count
    #                         if attendance.half_compensatory_off:
    #                             att = .5
    #                     attend_regular = workbook.add_format(
    #                         {'align': 'center', 'bold': False, 'font_color': 'green', 'text_wrap': True})
    #                 if attendance.attendance == 'half':
    #                     if attendance.compensatory_off:
    #                         attendan = 'HC'
    #                     else:
    #                         att = .5
    #                         attendan = 'HP'
    #                     attend_regular = workbook.add_format(
    #                         {'align': 'center', 'bold': False, 'font_color': 'green', 'text_wrap': True})
    #                 if attendance.attendance == 'absent':
    #                     attendan = 'AB'
    #                     no_absent_days += 1
    #                     attend_regular = workbook.add_format(
    #                         {'align': 'center', 'bold': False, 'font_color': 'red', 'text_wrap': True})
    #                 public_holiday = self.env['public.holiday'].search([('date', '=', day_first)])
    #                 if not public_holiday and day_first.weekday() != 6:
    #                     worksheet.write('%s%s' % (chr(col), row_no), attendan, attend_regular)
    #                 elif day_first.weekday() == 6:
    #                     sunday_attendance = self.env['hiworth.hr.attendance'].search(
    #                         [('name', '=', emp.id), ('date', '=', day_first)])
    # 
    #                     print
    #                     "hhhhhhhhhhhhhhhhhhhhhhhhhh", sunday_attendance
    # 
    #                     if not sunday_attendance.compensatory_off:
    #                         worksheet.write('%s%s' % (chr(col), row_no), 'S', holiday_regular)
    #                         att = 0
    #                     else:
    #                         if sunday_attendance.attendance == 'full':
    #                             worksheet.write('%s%s' % (chr(col), row_no), 'CO', holiday_regular)
    #                         else:
    #                             worksheet.write('%s%s' % (chr(col), row_no), 'HC', holiday_regular)
    #                 else:
    #                     if public_holiday:
    #                         att = 0
    #                         holiday_attendance = self.env['hiworth.hr.attendance'].search(
    #                             [('name', '=', emp.id), ('date', '=', day_first)])
    #                         if not holiday_attendance.compensatory_off:
    #                             worksheet.write('%s%s' % (chr(col), row_no), 'H', holiday_regular)
    #                         else:
    #                             if holiday_attendance.attendance == 'full':
    #                                 worksheet.write('%s%s' % (chr(col), row_no), 'CO', holiday_regular)
    #                             else:
    #                                 worksheet.write('%s%s' % (chr(col), row_no), 'HC', holiday_regular)
    #                 total_att += att
    #                 day_first = day_first + timedelta(days=1)
    #                 day_first_day = day_first_day + 1
    #                 col += 1
    #             else:
    #                 attendance = self.env['hiworth.hr.attendance'].search(
    #                     [('name', '=', emp.id), ('date', '=', day_first)])
    # 
    #                 att = 0
    #                 if not attendance.attendance:
    #                     attendan = ''
    #                     non_att_days += 1
    #                 if attendance.attendance == 'full':
    #                     if not attendance.compensatory_off:
    #                         attendan = 'FP'
    #                         att = 1
    #                     else:
    #                         attendan = 'CO'
    #                         co_att_count += co_att_count
    #                         if attendance.half_compensatory_off:
    #                             att = .5
    #                     attend_regular = workbook.add_format(
    #                         {'align': 'center', 'bold': False, 'font_color': 'green', 'text_wrap': True})
    #                 if attendance.attendance == 'half':
    #                     if attendance.compensatory_off:
    #                         attendan = 'HC'
    #                     else:
    #                         att = .5
    #                         attendan = 'HP'
    #                     attend_regular = workbook.add_format(
    #                         {'align': 'center', 'bold': False, 'font_color': 'green', 'text_wrap': True})
    #                 if attendance.attendance == 'absent':
    #                     attendan = 'AB'
    #                     no_absent_days += 1
    #                     attend_regular = workbook.add_format(
    #                         {'align': 'center', 'bold': False, 'font_color': 'red', 'text_wrap': True})
    #                 public_holiday = self.env['public.holiday'].search([('date', '=', day_first)])
    #                 if not public_holiday and day_first.weekday() != 6:
    #                     worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), attendan, attend_regular)
    #                 elif day_first.weekday() == 6:
    #                     att = 0
    #                     sunday_attendance = self.env['hiworth.hr.attendance'].search(
    #                         [('name', '=', emp.id), ('date', '=', day_first)])
    #                     if not sunday_attendance.compensatory_off:
    #                         worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), 'S', holiday_regular)
    #                     else:
    #                         worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), 'CO', holiday_regular)
    #                 else:
    #                     att = 0
    #                     worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), 'H', holiday_regular)
    #                 total_att += att
    #                 day_first = day_first + timedelta(days=1)
    #                 day_first_day = day_first_day + 1
    #                 next_col += 1
    # 
    #         # prev_credit = emp.get_prev_credit_days(emp.id, inv[0].from_date, inv[0].to_date)
    #         # worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), prev_credit, regular)
    #         # next_col += 1
    #         # current_credit = 0
    #         # if total_att >= 15:
    #         #     current_credit = emp.get_today_credit_days(emp.id, inv[0].from_date, inv[0].to_date)
    #         #     worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), current_credit, regular)
    #         # else:
    #         #     worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), '0', regular)
    #         # next_col += 1
    # 
    #         # Triangle Customisation
    # 
    #         exgratia = self.env['exgratia.payment']
    #         exgratia_days = exgratia.search(
    #             [('date', '>=', datetime.strptime(inv[0].from_date, "%Y-%m-%d")),
    #              ('date', '<=', datetime.strptime(inv[0].to_date, "%Y-%m-%d")),
    #              ('employee_id', '=', emp.id),
    #              ('state', '!=', 'cancel'),])
    #         holiday = 0
    #         week_day = 0
    #         public_holiday = self.env['public.holiday']
    #         for number in exgratia_days.ids:
    #             day = exgratia.browse(number)
    #             public_holidays = public_holiday.search([('date', '=', day.date)])
    #             if datetime.strptime(day.date, "%Y-%m-%d").weekday() == 6 or public_holidays:
    #                 holiday += day.hours
    #             else:
    #                 week_day += day.hours
    # 
    #         #############################################################
    # 
    #         # exgratia_days = emp.get_exgratia_days(emp.id, inv[0].from_date, inv[0].to_date)
    #         # sunday_days = emp.get_sunday(emp.id, inv[0].from_date, inv[0].to_date)
    #         absent_days = emp.get_absent_days(emp.id, inv[0].from_date, inv[0].to_date)
    #         present_days = emp.get_present_days(emp.id, inv[0].from_date, inv[0].to_date)
    # 
    #         worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), week_day, regular)
    #         # worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), exgratia_days, regular)
    #         next_col += 1
    #         worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), holiday, regular)
    #         # worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), sunday_days, regular)
    #         next_col += 1
    #         worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), present_days, regular)
    # 
    #         next_col += 1
    #         leaves = self.env['employee.leave.request'].search([('employee_id', '=', emp.id),
    #                                                             ('date', '>=', inv[0].from_date),
    #                                                             ('date', '<=', inv[0].to_date),
    #                                                             ('leave_request_id.state', '!=', 'cancel')])
    # 
    #         worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), len(leaves.ids), regular)
    # 
    #         next_col += 1
    #         worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), absent_days, regular)
    # 
    #         next_col += 1
    #         non_attendance_days = ((no_of_days.days) + 1) - (present_days + sunday_days + absent_days)
    #         if non_attendance_days < 0:
    #             non_attendance_days = 0
    #         worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), non_attendance_days, regular)
    # 
    #         next_col += 1
    #         # total_payable_days = present_days + sunday_days
    #         # worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no),total_payable_days
    #         #                   , regular)
    #         #
    #         # next_col += 1
    #         # if carry_forward < 0:
    #         #     carry_forward = 0
    #         # end_date = datetime.strptime(inv[0].to_date, "%Y-%m-%d")
    #         #
    #         # current_month_latest_leave = self.env['month.leave.status'].search(
    #         #     [('status_id', '=', emp.id), ('month_id', '=', end_date.month)], limit=1, order='month_id desc')
    #         #
    #         # if current_month_latest_leave:
    #         #     carry_forward = current_month_latest_leave.remaining
    #         # if not current_month_latest_leave:
    #         #     latest_leave = self.env['month.leave.status'].search(
    #         #         [('status_id', '=', emp.id), ('month_id', '=', end_date.month-1)], limit=1, order='month_id desc')
    #         #     carry_forward = latest_leave.remaining
    #         # if not carry_forward:
    #         #     carry_forward = 0
    #         #
    #         # worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), carry_forward, regular)
    #         row_no += 1
    # 
    #         print("Non attendanceeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", non_att_days)
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
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Comp:Attendance", regular)
        next_col += 1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Total Attendance Payable", regular)
        next_col += 1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Leave", regular)
        next_col += 1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Absent", regular)
        next_col += 1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Non-Attendance Days", regular)
        next_col += 1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Balance Leave", regular)

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

            sunday_holiday_att,sun_hol_att = emp.employee_attendance_regulise(start_date,end_date,emp)

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
                    attendance_id = self.env['hiworth.hr.attendance'].search(
                        [('name', '=', emp.id), ('date', '=', cmp_date)])
                    if not attendance_id:
                        attendance = ''
                        non_att_count += 1
                    if attendance_id.attendance == 'full':
                        if not attendance_id.compensatory_off:
                            attendance = 'FP'
                            att_acount += 1
                        else:
                            attendance = 'CO'
                            if attendance_id.compensatory_off:
                                co_att_count += 1
                            elif attendance_id.half_compensatory_off:
                                att_acount += 0.5
                                co_att_count += 0.5
                    if attendance_id.attendance == 'half':
                        if attendance_id.compensatory_off:
                            attendance = 'HC'
                            co_att_count += 0.5
                        else:
                            att_acount += 0.5
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
                        if attendance == '':
                            values = {'date': cmp_date,
                                      'name': emp.id,
                                      'user_id': self.env.user.id,
                                      'attendance': 'full'}
                            new_sun_att = self.env['hiworth.hr.attendance'].create(values)
                            non_att_count = non_att_count - 1
                        sunday_holiday+=1
                        worksheet.write('%s%s' % (chr(col), row_no), 'S', holiday_regular)
                    else:
                        worksheet.write('%s%s' % (chr(col), row_no), 'H', holiday_regular)
                        sunday_holiday+=1
                    col += 1
                else:
                    attendance_id = self.env['hiworth.hr.attendance'].search(
                        [('name', '=', emp.id), ('date', '=', cmp_date)])
                    if not attendance_id:
                        attendance = ''
                        non_att_count += 1
                    if attendance_id.attendance == 'full':
                        if not attendance_id.compensatory_off:
                            attendance = 'FP'
                            att_acount += 1
                        else:
                            attendance = 'CO'
                            if attendance_id.compensatory_off:
                                co_att_count += 1
                            elif attendance_id.half_compensatory_off:
                                att_acount += 0.5
                                co_att_count += 0.5
                    if attendance_id.attendance == 'half':
                        if attendance_id.compensatory_off:
                            attendance = 'HC'
                            co_att_count += 0.5
                        else:
                            att_acount += 0.5
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
                        if attendance == '':
                            values = {'date': cmp_date,
                                      'name': emp.id,
                                      'user_id': self.env.user.id,
                                      'attendance': 'full'}
                            new_sun_att = self.env['hiworth.hr.attendance'].create(values)
                            non_att_count = non_att_count - 1
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

            exgratia = self.env['exgratia.payment']

            over_time_ids = exgratia.search([('date', '>=', start_date),
                                                  ('date', '<=', end_date),
                                                  ('employee_id', '=', emp.id),
                                                  ('state', '=', 'approved'),
                                                  ('attendance', 'not in', ['full', 'half'])],)

            over_time = sum(over_time_ids.mapped('hours'))

            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), over_time, regular)
            next_col += 1
            
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), sunday_holiday_att, regular)
            # worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), sunday_holiday, regular)
            next_col += 1
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), att_acount, regular)
            next_col += 1
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), co_att_count, regular)
            next_col += 1
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), att_acount+co_att_count, regular)
            # worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), att_acount+co_att_count+sun_hol_att, regular)
            next_col += 1
            leaves_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id),
                                                                ('date_from', '>=', lines.from_date),
                                                                ('date_from', '<=', lines.to_date),
                                                                ('date_to', '>=', lines.from_date),
                                                                ('date_to', '<=', lines.to_date),
                                                                ('state', 'not in', ['cancel','refuse','draft'])])
            leaves = sum(leaves_ids.mapped('nos'))
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), leaves, regular)
            next_col += 1
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), absent_count, regular)
            next_col += 1
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), non_att_count, regular)
            next_col += 1
            active_contract = self.env['hr.contract'].search(
                [('employee_id', '=', emp.id), ('state', '=', 'active')])

            employee_leave_id = active_contract.employee_leave_ids.search(
                [('id', 'in', active_contract.employee_leave_ids.ids), ], limit=1, order='id desc')
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col), row_no), employee_leave_id.remaining, regular)
            row_no+=1



AttendanceReport('report.hiworth_hr_attendance.report_attendance_report.xlsx', 'hiworth.hr.leave')