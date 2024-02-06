from openerp import models, fields, api
import datetime, calendar, ast
import dateutil.parser
from datetime import timedelta


class HiworthHrLeave(models.Model):
    _name = 'hiworth.hr.leave'

    from_date = fields.Date(default=lambda self: self.default_time_range('from'))
    to_date = fields.Date(default=lambda self: self.default_time_range('to'))
    type_selection = fields.Selection([('approved', 'Approved'), ('confirm', 'Confirmed'), ('both', 'Both')],
                                      default='approved')
    attendance_type = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
                                       default='monthly')
    active_ids = fields.Char()
    attendance_category = fields.Selection([('office_staff', 'Office Employee '),
                                            ('site_employee', 'Site Employee'),
                                            ('project_eng', 'Project Team'),
                                            ], string='Attendance Category')

    @api.multi
    def get_employee_code(self, o):
        return self.env['hr.employee'].search([('id', '=', o.id)]).emp_code

    @api.multi
    def get_location_ml(self, o, day):
        rec = self.env['hiworth.hr.attendance'].search([('name', '=', o.id)])
        for r in rec:
            if dateutil.parser.parse(r.sign_in).date() == day[0]:
                return r.location.name

    @api.multi
    def get_employee_location(self, o, date):
        rec = self.env['hiworth.hr.attendance'].search([('name', '=', o.id)])
        # ,('sign_in','>=',date),('sign_out','<=',date)
        for r in rec:
            if str(dateutil.parser.parse(r.sign_in).date()) == date:
                return r.location.name

    @api.onchange('attendance_type')
    def _onchange_attendance_type(self):
        if self.attendance_type:
            if self.attendance_type == 'daily':
                self.from_date = fields.date.today()
                self.to_date = fields.date.today()

    # Calculate default time ranges
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

    @api.model
    def print_hiworth_hr_leave_summary(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Attendance report filter",
            "res_model": "hiworth.hr.leave",
            "context": {'active_ids': self.env.context.get('active_ids', [])},
            "views": [[False, "form"]],
            "target": "new",
        }

    @api.multi
    def print_hiworth_hr_leave_summary_confirmed(self):
        data = {}
        data['form'] = self.read(['from_date', 'end_date', 'type_selection'])
        return {'type': 'ir.actions.report.xml',
                'report_name': 'hiworth_hr_attendance.report_attendance_report.xlsx',
                'datas': data
                }

    @api.multi
    def view_hiworth_hr_leave_summary_confirmed(self):
        self.ensure_one()

        self.active_ids = self.env.context.get('active_ids', [])
        if self.attendance_type == 'monthly':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'hiworth_hr_attendance.template_hiworth_hr_leave_summary_view',
                'report_type': 'qweb-html'
            }
        if self.attendance_type == 'weekly':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'hiworth_hr_attendance.template_hiworth_hr_leave_summary_view',
                'report_type': 'qweb-html'
            }
        if self.attendance_type == 'daily':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'hiworth_hr_attendance.template_hiworth_hr_leave_summary_view1',
                'report_type': 'qweb-html'
            }

    def get_attendance_days(self, id, start_date, end_date):

        return self.env['hr.employee'].get_attendance_days(id, start_date, end_date)

    def get_selected_users(self, active_ids):
        dom = []
        if self.attendance_category:
            dom.append(('attendance_category', '=', self.attendance_category))
        else:
            dom.append(('attendance_category', 'in',
                        ['office_staff', 'site_employee', 'project_eng','taurus_driver', 'eicher_driver', 'pickup_driver',
                         'operators', 'cleaners']))
        return self.env['hr.employee'].search(dom)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def get_employee_location(self, o, date):
        rec = self.env['hiworth.hr.attendance'].search([('name', '=', o.id)])
        # ,('sign_in','>=',date),('sign_out','<=',date)
        for r in rec:
            if str(dateutil.parser.parse(r.sign_in).date()) == date:
                return r.location.name

    @api.model
    def get_prev_credit_days(self, employee_id, start_date, end_date):
        leave_balance = 0
        date_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        month = date_start.month
        acrued_month = self.env['month.leave.status'].search(
            [('status_id', '=', employee_id), ('month_id', '=', month)], limit=1, order='month_id desc')
        if acrued_month:
            leave_balance = acrued_month.available
        else:
            if month != 1:
                prev_month = month-1
                acrued_month = self.env['month.leave.status'].search(
                    [('status_id', '=', employee_id), ('month_id', '=', prev_month)], limit=1, order='month_id desc')
                if acrued_month:
                    leave_balance = acrued_month.remaining
            else:
                prev_month = 12
                acrued_month = self.env['month.leave.status'].search(
                    [('status_id', '=', employee_id), ('month_id', '=', prev_month)], limit=1, order='month_id desc')
                if acrued_month:
                    leave_balance = acrued_month.remaining
        if leave_balance < 0:
            leave_balance = 0
        return leave_balance

    @api.model
    def get_today_credit_days(self, employee_id, start_date, end_date):
        date_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        month = date_start.month
        current_credit = 0
        acrued_month = self.env['month.leave.status'].search(
            [('status_id', '=', employee_id), ('month_id', '=', month)])
        if acrued_month:
            current_credit = acrued_month.allowed
        return current_credit

    @api.model
    def get_lop(self, employee_id, start_date, end_date):
        date_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        month = date_start.month
        current_credit = 0
        acrued_month = self.env['month.leave.status'].search(
            [('status_id', '=', employee_id), ('month_id', '=', month)])
        if acrued_month:
            current_credit = acrued_month.remaining

        return current_credit

    @api.model
    def get_exgratia_days(self, employee_id, start_date, end_date):

        exgratia_full = self.env['exgratia.payment'].search(
            [('date', '>=', datetime.datetime.strptime(start_date, "%Y-%m-%d")),
             ('date', '<=', datetime.datetime.strptime(end_date, "%Y-%m-%d")),
             ('employee_id', '=', employee_id),
             ('state', '=', 'approved'),])

        exgratia_half = self.env['exgratia.payment'].search(
            [('date', '>=', datetime.datetime.strptime(start_date, "%Y-%m-%d")),
             ('date', '<=', datetime.datetime.strptime(end_date, "%Y-%m-%d")),
             ('employee_id', '=', employee_id), ('state', '=', 'approved'),
            ])

        exgratia_days = 0
        if exgratia_full:
            exgratia_days += len(exgratia_full.ids)
        if exgratia_half:
            exgratia_days += len(exgratia_half.ids) * .5
        return exgratia_days

    @api.model
    def get_sunday(self, employee_id, start_date, end_date):
        date_from = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        date_to = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        total_days = 0
        sunday = 0
        total_sun_days = 0
        employee = self.env['hr.employee'].browse(employee_id)
        public_holiday_present_count = 0

        date_diff = date_to - date_from

        for r in range((date_diff.days) + 1):
            public_holiday = self.env['public.holiday'].search([('date', '=', date_from)])

            if date_from.weekday() == 6 or public_holiday:
                if public_holiday:
                    if date_from.weekday() == 0:
                        week_start = date_from
                        week_end = date_from + timedelta(days=6)
                    if date_from.weekday() == 1:
                        week_start = date_from - timedelta(days=1)
                        week_end = date_from + timedelta(days=5)
                    if date_from.weekday() == 2:
                        week_start = date_from - timedelta(days=2)
                        week_end = date_from + timedelta(days=4)
                    if date_from.weekday() == 3:
                        week_start = date_from - timedelta(days=3)
                        week_end = date_from + timedelta(days=3)
                    if date_from.weekday() == 4:
                        week_start = date_from - timedelta(days=4)
                        week_end = date_from + timedelta(days=2)
                    if date_from.weekday() == 5:
                        week_start = date_from - timedelta(days=5)
                        week_end = date_from + timedelta(days=1)
                else:
                    week_start = date_from - timedelta(days=6)
                    week_end = date_from
                full_half = 0
                no_holidays = 0
                full = self.env['hiworth.hr.attendance'].search(
                    [('attendance', '=', 'full'), ('name', '=', employee_id), ('date', '>=', week_start),
                     ('date', '<', week_end), ('half_compensatory_off', '=', False), ('compensatory_off', '=', False)])

                half_compensatory = self.env['hiworth.hr.attendance'].search(
                    [('attendance', '=', 'full'), ('name', '=', employee_id), ('date', '>=', week_start),
                     ('date', '<', week_end), ('half_compensatory_off', '=', True)])

                half = self.env['hiworth.hr.attendance'].search(
                    [('attendance', '=', 'half'), ('name', '=', employee_id), ('date', '>=', week_start),
                     ('date', '<', week_end), ('compensatory_off', '=', False)])

                public_holidays = self.env['public.holiday'].search(
                    [('date', '>=', week_start), ('date', '<', week_end)])

                for holiday in public_holidays:
                    holiday_date = datetime.datetime.strptime(holiday.date, "%Y-%m-%d")
                    holiday_att_full = self.env['hiworth.hr.attendance'].search(
                        [('attendance', '=', 'full'), ('name', '=', employee_id), ('date', '=', holiday_date)])
                    if holiday_att_full:
                        no_holidays += 1
                    holiday_att_half = self.env['hiworth.hr.attendance'].search(
                        [('attendance', '=', 'half'), ('name', '=', employee_id), ('date', '=', holiday_date)])
                    if holiday_att_half:
                        no_holidays += .5

                full_half = len(full.ids) + (len(half.ids) * 0.5) - no_holidays + (len(half_compensatory)*.5)

                if full_half > 0:
                    if len(public_holidays) <= 3:
                        if full_half >= 3:
                            sunday_att = self.env['hiworth.hr.attendance'].search(
                                [('date', '=', date_from), ('name', '=', employee_id)])
                            if sunday_att:
                                if sunday_att.attendance == 'full':
                                    sunday += 1
                                    total_days += 1
                                elif sunday_att.attendance == 'half':
                                    sunday += .5
                                    total_days += .5
                                elif sunday_att.attendance == 'absent':
                                    sunday_att.attendance = 'full'
                                    sunday += 1
                            else:
                                vals = {
                                    'name': employee_id,
                                    'date': str(date_from.date()),
                                    'attendance': 'full',
                                    'attendance_category': employee.attendance_category,
                                }
                                sunday_att = self.env['hiworth.hr.attendance'].create(vals)
                                sunday_att.attendance = 'full'
                                if sunday_att:
                                    sunday += 1

                    elif len(public_holidays) == 4:
                        if full_half == 2:
                            sunday_att = self.env['hiworth.hr.attendance'].search(
                                [('date', '=', date_from), ('name', '=', employee_id)])
                            if sunday_att:
                                if sunday_att.attendance == 'full':
                                    sunday += 1
                                    total_days += 1
                                elif sunday_att.attendance == 'half':
                                    sunday += .5
                                    total_days += .5
                                elif sunday_att.attendance == 'absent':
                                    sunday_att.attendance = 'full'
                                    sunday += 1
                            else:

                                vals = {
                                    'name': employee_id,
                                    'date': str(date_from.date()),
                                    'attendance': 'full',
                                    'attendance_category': employee.attendance_category,
                                }
                                sunday_att = self.env['hiworth.hr.attendance'].create(vals)
                                sunday_att.attendance = 'full'
                                if sunday_att:
                                    sunday += 1

                    elif len(public_holidays) == 5:
                        if full_half == 1:
                            sunday_att = self.env['hiworth.hr.attendance'].search(
                                [('date', '=', date_from), ('name', '=', employee_id)])
                            if sunday_att:
                                if sunday_att.attendance == 'full':
                                    sunday += 1
                                    total_days += 1
                                elif sunday_att.attendance == 'half':
                                    sunday += .5
                                    total_days += .5
                                elif sunday_att.attendance == 'absent':
                                    sunday_att.attendance = 'full'
                                    sunday += 1
                            else:

                                vals = {
                                    'name': employee_id,
                                    'date': str(date_from.date()),
                                    'attendance': 'full',
                                    'attendance_category': employee.attendance_category,
                                }
                                sunday_att = self.env['hiworth.hr.attendance'].create(vals)
                                sunday_att.attendance = 'full'
                                if sunday_att:
                                    sunday += 1

                    elif len(public_holidays) == 6:
                        sunday_att = self.env['hiworth.hr.attendance'].search(
                            [('date', '=', date_from), ('name', '=', employee_id)])
                        if sunday_att:
                            if sunday_att.attendance == 'full':
                                sunday += 1
                                total_days += 1
                            elif sunday_att.attendance == 'half':
                                sunday += .5
                                total_days += .5
                            elif sunday_att.attendance == 'absent':
                                sunday_att.attendance = 'full'
                                sunday += 1
                        else:

                            vals = {
                                'name': employee_id,
                                'date': str(date_from.date()),
                                'attendance': 'full',
                                'attendance_category': employee.attendance_category,
                            }
                            sunday_att = self.env['hiworth.hr.attendance'].create(vals)
                            sunday_att.attendance = 'full'
                            if sunday_att:
                                sunday += 1

                    if sunday == 0:
                        sunday_att = self.env['hiworth.hr.attendance'].search(
                            [('date', '=', date_from), ('name', '=', employee_id), ('compensatory_off', '=', True)])
                        if sunday_att:
                            if sunday_att.attendance == 'full':
                                sunday += 1
                            elif sunday_att.attendance == 'half':
                                sunday += .5

                        full_week_att = self.env['hiworth.hr.attendance'].search([
                            ('name', '=', employee_id),
                            ('date', '>=', week_start),
                            ('date', '<', week_end)])
                        today_attendance = self.env['hiworth.hr.attendance'].search(
                            [('date', '=', date_from), ('name', '=', employee_id)])

                        len_full_week_att = len(full_week_att)
                        function_continue = True
                        if employee.joining_date:
                            joining_date = datetime.datetime.strptime(employee.joining_date, "%Y-%m-%d")
                            if joining_date.month == date_from.month:
                                if joining_date >= date_from - timedelta(days=6):
                                    function_continue = False
                                    no_days_before_joining = (joining_date - (date_from - timedelta(days=6))).days
                                    if len_full_week_att != (6 - no_days_before_joining):
                                        today_attendance.unlink()
                        if function_continue:
                            if len_full_week_att >= 6 and not len(public_holidays) == 0:
                                if not today_attendance:
                                    vals = {
                                        'name': employee_id,
                                        'date': str(date_from.date()),
                                        'attendance': 'absent',
                                        'attendance_category': employee.attendance_category,
                                    }
                                    today_attendance = self.env['hiworth.hr.attendance'].create(vals)
                                if today_attendance and not today_attendance.compensatory_off:
                                    today_attendance.attendance = 'absent'
                            elif len_full_week_att >= 5 and len(public_holidays) == 1:
                                if not today_attendance:
                                    vals = {
                                        'name': employee_id,
                                        'date': str(date_from.date()),
                                        'attendance': 'absent',
                                        'attendance_category': employee.attendance_category,
                                    }
                                    today_attendance = self.env['hiworth.hr.attendance'].create(vals)
                                if today_attendance and not today_attendance.compensatory_off:
                                    today_attendance.attendance = 'absent'
                            elif len_full_week_att >= 4 and len(public_holidays) == 2:
                                if not today_attendance:
                                    vals = {
                                        'name': employee_id,
                                        'date': str(date_from.date()),
                                        'attendance': 'absent',
                                        'attendance_category': employee.attendance_category,
                                    }
                                    today_attendance = self.env['hiworth.hr.attendance'].create(vals)
                                if today_attendance and not today_attendance.compensatory_off:
                                    today_attendance.attendance = 'absent'
                            elif len_full_week_att >= 3 and len(public_holidays) == 3:
                                if not today_attendance:
                                    vals = {
                                        'name': employee_id,
                                        'date': str(date_from.date()),
                                        'attendance': 'absent',
                                        'attendance_category': employee.attendance_category,
                                    }
                                    today_attendance = self.env['hiworth.hr.attendance'].create(vals)
                                if today_attendance and not today_attendance.compensatory_off:
                                    today_attendance.attendance = 'absent'

                            elif len_full_week_att >= 2 and len(public_holidays) == 4:
                                if not today_attendance:
                                    vals = {
                                        'name': employee_id,
                                        'date': str(date_from.date()),
                                        'attendance': 'absent',
                                        'attendance_category': employee.attendance_category,
                                    }
                                    today_attendance = self.env['hiworth.hr.attendance'].create(vals)
                                if today_attendance and not today_attendance.compensatory_off:
                                    today_attendance.attendance = 'absent'
                            elif len_full_week_att >= 1 and len(public_holidays) == 5:
                                if not today_attendance:
                                    vals = {
                                        'name': employee_id,
                                        'date': str(date_from.date()),
                                        'attendance': 'absent',
                                        'attendance_category': employee.attendance_category,
                                    }
                                    today_attendance = self.env['hiworth.hr.attendance'].create(vals)
                                if today_attendance and not today_attendance.compensatory_off:
                                    today_attendance.attendance = 'absent'

                            else:
                                if len_full_week_att < 5:
                                    today_attendance.unlink()

                    if employee.joining_date:
                        joining_date = datetime.datetime.strptime(employee.joining_date, "%Y-%m-%d")
                        if joining_date.month == date_from.month:
                            attendance = self.env['hiworth.hr.attendance'].search(
                                [('name', '=', employee_id), ('date', '=', date_from)])
                            if joining_date == date_from:
                                if joining_date.weekday() == 6:
                                    next_day_public_holiday = self.env['public.holiday'].search([('date', '=', date_from + timedelta(days=1))])
                                    if next_day_public_holiday:
                                        next_day = self.env['hiworth.hr.attendance'].search(
                                            [('name', '=', employee_id), ('date', '=', date_from + timedelta(days=2))])
                                    else:
                                        next_day = self.env['hiworth.hr.attendance'].search(
                                            [('name', '=', employee_id), ('date', '=', date_from + timedelta(days=1))])
                                    if next_day:
                                        if next_day.attendance == 'full':
                                            if attendance:
                                                attendance.attendance = 'full'
                                            else:
                                                vals = {
                                                    'name': employee_id,
                                                    'date': str(date_from.date()),
                                                    'attendance': 'full',
                                                    'attendance_category': employee.attendance_category,
                                                }
                                                attendance = self.env['hiworth.hr.attendance'].create(vals)
                                                attendance.attendance = 'full'
                                            sunday += 1
                                        else:
                                            if next_day.attendance != 'full':
                                                if attendance and not attendance.compensatory_off:
                                                    attendance.attendance = 'absent'
                                                else:
                                                    if not attendance:
                                                        vals = {
                                                            'name': employee_id,
                                                            'date': str(date_from.date()),
                                                            'attendance': 'absent',
                                                            'attendance_category': employee.attendance_category,
                                                        }
                                                        attendance = self.env['hiworth.hr.attendance'].create(vals)
                                                        attendance.attendance = 'absent'
                                elif public_holiday:
                                    if (date_from + timedelta(days=1)).weekday() == 6:
                                        next_day = self.env['hiworth.hr.attendance'].search(
                                            [('name', '=', employee_id), ('date', '=', date_from + timedelta(days=2))])
                                    else:
                                        next_day = self.env['hiworth.hr.attendance'].search(
                                            [('name', '=', employee_id), ('date', '=', date_from + timedelta(days=1))])
                                    if next_day:
                                        if next_day.attendance == 'full':
                                            if attendance:
                                                attendance.attendance = 'full'
                                            else:
                                                vals = {
                                                    'name': employee_id,
                                                    'date': str(date_from.date()),
                                                    'attendance': 'full',
                                                    'attendance_category': employee.attendance_category,
                                                }
                                                attendance = self.env['hiworth.hr.attendance'].create(vals)
                                                attendance.attendance = 'full'
                                            sunday += 1
                                        else:
                                            if next_day.attendance != 'full':
                                                if attendance and not attendance.compensatory_off:
                                                    attendance.attendance = 'absent'
                                                else:
                                                    if not attendance:
                                                        vals = {
                                                            'name': employee_id,
                                                            'date': str(date_from.date()),
                                                            'attendance': 'absent',
                                                            'attendance_category': employee.attendance_category,
                                                        }
                                                        attendance = self.env['hiworth.hr.attendance'].create(vals)
                                                        attendance.attendance = 'absent'
                            else:
                                if joining_date < date_from:
                                    if date_from - timedelta(days=2) <= joining_date:
                                        new_joining_full = self.env['hiworth.hr.attendance'].search(
                                            [('attendance', '=', 'full'), ('name', '=', employee_id),
                                             ('date', '>=', joining_date),
                                             ('date', '<', date_from), ('half_compensatory_off', '=', False), ('compensatory_off', '=', False)])

                                        new_joining_half = self.env['hiworth.hr.attendance'].search(
                                            [('attendance', '=', 'half'), ('name', '=', employee_id), ('date', '>=', joining_date),
                                             ('date', '<', date_from), ('half_compensatory_off', '=', False), ('compensatory_off', '=', False)])
                                        # joining_public_holidays = self.env['public.holiday'].search(
                                        #     [('date', '>=', joining_date),
                                        #      ('date', '<', date_from)])
                                        join_date_att = len(new_joining_full) + len(new_joining_half) * 0.5

                                        if joining_date == date_from - timedelta(days=2):
                                            days = self.env['hiworth.hr.attendance'].search(
                                                [('name', '=', employee_id),
                                                 ('date', '>=', joining_date),
                                                 ('date', '<', date_from),
                                                 ])
                                            if join_date_att == 2:
                                                sunday += 1
                                                if attendance:
                                                    if attendance.attendance != 'full':
                                                        attendance.attendance = 'full'
                                                else:
                                                    vals = {
                                                        'name': employee_id,
                                                        'date': str(date_from.date()),
                                                        'attendance': 'full',
                                                        'attendance_category': employee.attendance_category,
                                                    }
                                                    new_join_sun_att = self.env['hiworth.hr.attendance'].create(vals)
                                                    new_join_sun_att.attendance = 'full'
                                            else:
                                                if len(days) == 2:
                                                    if attendance and not attendance.compensatory_off:
                                                        attendance.attendance = 'absent'
                                                    else:
                                                        if not attendance:
                                                            vals = {
                                                                'name': employee_id,
                                                                'date': str(date_from.date()),
                                                                'attendance': 'absent',
                                                                'attendance_category': employee.attendance_category,
                                                            }
                                                            new_join_sun_att = self.env['hiworth.hr.attendance'].create(vals)
                                                            new_join_sun_att.attendance = 'absent'
                                                else:
                                                    if len(days) < 2:
                                                        attendance.unlink()

                                        if joining_date == date_from - timedelta(days=1):
                                            days = self.env['hiworth.hr.attendance'].search(
                                                [('name', '=', employee_id),
                                                 ('date', '>=', joining_date),
                                                 ('date', '<', date_from),
                                                 ])
                                            if join_date_att == 1:
                                                sunday += 1
                                                if attendance:
                                                    if attendance.attendance != 'full':
                                                        attendance.attendance = 'full'
                                                else:
                                                    if not attendance:
                                                        vals = {
                                                            'name': employee_id,
                                                            'date': str(date_from.date()),
                                                            'attendance': 'full',
                                                            'attendance_category': employee.attendance_category,
                                                        }
                                                        new_join_sun_att = self.env['hiworth.hr.attendance'].create(vals)
                                                        new_join_sun_att.attendance = 'full'
                                            else:
                                                if len(days) == 1:
                                                    if attendance and not attendance.compensatory_off:
                                                        attendance.attendance = 'absent'
                                                    else:
                                                        if not attendance:
                                                            vals = {
                                                                'name': employee_id,
                                                                'date': str(date_from.date()),
                                                                'attendance': 'absent',
                                                                'attendance_category': employee.attendance_category,
                                                            }
                                                            new_join_sun_att = self.env['hiworth.hr.attendance'].create(vals)
                                                            new_join_sun_att.attendance = 'absent'
                                                else:
                                                    if len(days) < 1:
                                                        attendance.unlink()

                total_sun_days = total_sun_days + sunday
                sunday = 0
            date_from = date_from + timedelta(days=1)

        return total_sun_days

    @api.model
    def get_attendance_days(self, employee_id, start_date, end_date):
        # Find the list of days for which the report is to be generated
        print "tttttttttttttttttttttttttttttt", start_date, end_date
        delta = datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.datetime.strptime(start_date, "%Y-%m-%d");
        selected_days = [(datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(days=day)).date() for
                         day in range(delta.days + 1)];

        '''
        Calculate all holidays including public holidays
        '''

        leaves = []

        public_holidays = []
        public_holidays_recs = self.env['public.holiday'].search(
            [('date', '>=', (datetime.datetime.strptime(start_date, '%Y-%m-%d'))),
             ('date', '<=', (datetime.datetime.strptime(end_date, '%Y-%m-%d')))])
        for public_holidays_rec in public_holidays_recs:
            public_holidays.append(public_holidays_rec.date)

        full_present = []
        full_present_recs = self.env['hiworth.hr.attendance'].search(
            [('name', '=', employee_id), ('attendance', '=', 'full'),
             ('date', '>=', (datetime.datetime.strptime(start_date, '%Y-%m-%d'))),
             ('date', '<=', (datetime.datetime.strptime(end_date, '%Y-%m-%d')))])
        for full_present_rec in full_present_recs:
            leave_recs = self.env['employee.leave.request'].search(
                [('employee_id', '=', employee_id), ('date', '=', full_present_rec.date), ('leave_credited', '=', True),
                 ('adjusted_leave', '=', 1)])
            if leave_recs:
                leaves.append(full_present_rec.date)
            else:
                full_present.append(full_present_rec.date)

        half_present = []
        half_present_recs = self.env['hiworth.hr.attendance'].search(
            [('name', '=', employee_id), ('attendance', '=', 'half'),
             ('date', '>=', (datetime.datetime.strptime(start_date, '%Y-%m-%d'))),
             ('date', '<=', (datetime.datetime.strptime(end_date, '%Y-%m-%d')))])
        for half_present_rec in half_present_recs:
            leave_recs = self.env['employee.leave.request'].search(
                [('employee_id', '=', employee_id), ('date', '=', half_present_rec.date), ('leave_credited', '=', True),
                 ('adjusted_leave', '=', 1)])
            if leave_recs:
                leaves.append(half_present_rec.date)
            else:
                half_present.append(half_present_rec.date)

        absent = []
        absent_recs = self.env['hiworth.hr.attendance'].search(
            [('name', '=', employee_id), ('attendance', '=', 'absent'),
             ('date', '>=', (datetime.datetime.strptime(start_date, '%Y-%m-%d'))),
             ('date', '<=', (datetime.datetime.strptime(end_date, '%Y-%m-%d')))])
        for absent_rec in absent_recs:
            leave_recs = self.env['employee.leave.request'].search(
                [('employee_id', '=', employee_id), ('date', '=', absent_rec.date), ('leave_credited', '=', True),
                 ('lop_leave', '=', 1)])
            if not leave_recs:
                absent.append(absent_rec.date)

        '''
        Calculate the attendance of the employee
        'FP' marks the day for employee was present
        'HP' marks the day for employee was present
        'A' marks the day for employee was absent
        'H' public holidays or paid leaves
        'D' marks the a normal day of the week (non working day)

        selected_days_with_attendance = [(datetime.date(2017, 5, 1),), (datetime.date(2017, 5, 2),), ...]
        '''
        selected_days_with_attendance = [(day,) for day in selected_days]
        for idx, day in enumerate(selected_days_with_attendance):
            # Check if day is sunday
            if datetime.datetime.strftime(day[0], "%Y-%m-%d") in public_holidays:
                selected_days_with_attendance[idx] += ("H",)

            elif day[0].isoweekday() in [7]:
                selected_days_with_attendance[idx] += ("S",)

            elif datetime.datetime.strftime(day[0], "%Y-%m-%d") in full_present:
                selected_days_with_attendance[idx] += ("FP",)

            elif datetime.datetime.strftime(day[0], "%Y-%m-%d") in half_present:
                selected_days_with_attendance[idx] += ("HP",)

            elif datetime.datetime.strftime(day[0], "%Y-%m-%d") in absent:
                selected_days_with_attendance[idx] += ("A",)

            elif datetime.datetime.strftime(day[0], "%Y-%m-%d") in leaves:
                selected_days_with_attendance[idx] += ("L",)

            elif day[0] > datetime.datetime.now().date():
                selected_days_with_attendance[idx] += ("D",)
            else:
                selected_days_with_attendance[idx] += ("A",)

        return selected_days_with_attendance;

    @api.model
    def get_total_public_holidays(self, selected_days_with_attendance):
        public_holidays = [day[0] for day in selected_days_with_attendance if day[1] == "H"]
        sundays = [day[0] for day in selected_days_with_attendance if day[1] == "S"]
        total_public_holidays = len(public_holidays) + len(sundays)
        return total_public_holidays

    @api.model
    def get_total_present_days1(self, selected_days_with_attendance, o, date):

        rec = self.env['hiworth.hr.attendance'].search(
            [('name', '=', o.id), ('sign_in', '>=', date), ('sign_out', '<=', date)])

        if rec:
            return datetime.datetime.strptime(rec.sign_in, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=5,
                                                                                                     minutes=30)
        else:
            return '---'

    @api.model
    def get_present_days(self, employee_id, from_date, to_date):
        date_from = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        date_to = datetime.datetime.strptime(to_date, "%Y-%m-%d")
        full_present = 0
        total_days = 0
        half_present = 0
        sunday = 0
        leave_adjusted_days = 0
        date_diff = date_to - date_from

        for r in range((date_diff.days) + 1):
            if date_from.weekday() != 6:
                # if date_from.weekday() == 6:

                #     week_start = date_from - timedelta(days=6)
                #     week_end = date_from
                #
                #     full_half = 0
                #
                #     full = self.env['hiworth.hr.attendance'].search(
                #         [('attendance', '=', 'full'), ('name', '=', employee_id), ('date', '>=', week_start),
                #          ('date', '<', week_end)])
                #     half = self.env['hiworth.hr.attendance'].search(
                #         [('attendance', '=', 'half'), ('name', '=', employee_id), ('date', '>=', week_start),
                #          ('date', '<', week_end)])
                #
                #     leave = self.env['employee.leave.request'].search(
                #         [('employee_id', '=', employee_id), ('leave_credited', '=', True), ('adjusted_leave', '=', 1),('date', '>=', week_start),
                #          ('date', '<', week_end)])
                #
                #
                #
                #
                #     full_half = len(full.ids) + len(half.ids) * 0.5
                #
                #     for leav in leave:
                #         att = self.env['hiworth.hr.attendance'].search(
                #         [('name', '=', employee_id), ('date', '=', leav.date)])
                #
                #         if att.attendance == 'full':
                #             full_half -= 1
                #         else:
                #             full_half -= .5
                #
                #     if full_half >= 3:
                #
                #         sunday += 1
                #
                # else:

                attendance = self.env['hiworth.hr.attendance'].search(
                    [('name', '=', employee_id), ('date', '=', date_from)])
                leave = self.env['employee.leave.request'].search(
                    [('employee_id', '=', employee_id), ('leave_credited', '=', True), ('adjusted_leave', '=', 1),
                     ('date', '=', date_from)])
                public_holiday = self.env['public.holiday'].search([('date', '=', date_from)])
                if not public_holiday:
                    if attendance:
                        if attendance.attendance == 'full':
                            total_days += 1
                        if attendance.attendance == 'half':
                            total_days += .5
                    # if attendance and attendance.compensatory_off:
                    #     if attendance.attendance == 'full':
                    #         leave_adjusted_days += 1
                    #     if attendance.attendance == 'half':
                    #         leave_adjusted_days += .5
            date_from = date_from + timedelta(days=1)

        return total_days

    @api.model
    def get_lop_days(self, employee_id, from_date, to_date):
        date_from = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        date_to = datetime.datetime.strptime(to_date, "%Y-%m-%d")
        leave = self.env['employee.leave.request'].search(
            [('employee_id', '=', employee_id), ('leave_credited', '=', True), ('lop_leave', '=', 1),
             ('date', '>=', date_from),
             ('date', '<=', date_to)])
        lop = 0
        if leave:
            lop = len(leave.ids)
        return lop

    @api.model
    def get_absent_days(self, employee_id, from_date, to_date):
        date_from = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        date_to = datetime.datetime.strptime(to_date, "%Y-%m-%d")
        full_present = 0
        total_days = 0
        half_present = 0
        date_diff = date_to - date_from
        sunday = 0

        att = self.env['hiworth.hr.attendance'].search(
            [('name', '=', employee_id), ('date', '>=', date_from), ('date', '<=', date_to),
             ('attendance', '=', 'absent')])

        half_att = self.env['hiworth.hr.attendance'].search(
            [('name', '=', employee_id), ('date', '>=', date_from), ('date', '<=', date_to),
             ('attendance', '=', 'half')])

        total_days = len(att.ids) + (len(half_att.ids) * .5)

        return total_days

    @api.model
    def get_total_present_days(self, selected_days_with_attendance):
        full_present_days = [day[0] for day in selected_days_with_attendance if day[1] == "FP"]
        half_present_days = [day[0] for day in selected_days_with_attendance if day[1] == "HP"]
        total_present_days = len(full_present_days) + float(len(half_present_days)) / 2
        total_public_holidays = self.get_total_public_holidays(selected_days_with_attendance)
        return total_present_days + total_public_holidays

    @api.model
    def get_total_leaves1(self, selected_days_with_attendance, o, date):
        rec = self.env['hiworth.hr.attendance'].search(
            [('name', '=', o.id), ('sign_in', '>=', date), ('sign_out', '<=', date)])

        if rec:
            return datetime.datetime.strptime(rec.sign_out, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=5,
                                                                                                      minutes=30)
        else:
            return '---'

    @api.model
    def get_total_leaves(self, selected_days_with_attendance):

        leave_days = [day[0] for day in selected_days_with_attendance if day[1] == "A"]
        total_leave_days = len(leave_days)
        return total_leave_days

    @api.model
    def get_previous_leaves(self, selected_days_with_attendance, employee_id, start_date, end_date):
        list = []

        pre_leaves = 0
        all_leaves = 0
        net_leaves = 0
        month = datetime.datetime.strptime(start_date, '%Y-%m-%d').month
        day = self.env['hr.employee'].search([('id', '=', employee_id)])
        for day1 in day.leave_ids:
            if day1.leave_id.effective_monthly_leave != 0:
                status = self.env['month.leave.status'].search(
                    [('status_id', '=', day.id), ('leave_id', '=', day1.leave_id.id), ('month_id', '=', month)],
                    limit=1)

                taken = 0
                holiday = self.env['hr.holidays'].search([('type', '=', 'remove'), ('employee_id', '=', day.id)])
                for hol_id in holiday:

                    if (start_date <= hol_id.date_from <= end_date) or (start_date <= hol_id.date_to <= end_date):
                        date_from1 = datetime.datetime.strptime(hol_id.date_from, '%Y-%m-%d').date()
                        date_to1 = datetime.datetime.strptime(hol_id.date_to, '%Y-%m-%d').date()
                        delta = date_to1 - date_from1

                        if hol_id.attendance == 'full':
                            for i in range(delta.days + 1):
                                if (date_from1 + timedelta(i)).month == month:
                                    taken += 1

                        elif hol_id.attendance == 'half':
                            for i in range(delta.days + 1):
                                if (date_from1 + timedelta(i)).month == month:
                                    taken += 0.5
                        else:
                            pass

                pre_leaves += status.allowed - day1.leave_id.effective_monthly_leave
                all_leaves += day1.leave_id.effective_monthly_leave
                net_leaves += status.allowed - taken
        list.append({
            'pre_leaves': pre_leaves,
            'all_leaves': all_leaves,
            'net_leaves': net_leaves,
        })

        return list
