from openerp import models, fields, api, _
from datetime import datetime,timedelta

class AbsenteesReport(models.TransientModel):
    _name = 'absentees.report'

    @api.model
    def get_attendance_days(self, start_date, end_date):
        # Find the list of days for which the report is to be generated
        delta = datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d");
        selected_days = [(datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day)).date() for
                         day in range(delta.days + 1)];

        '''
        Calculate all holidays including public holidays
        '''
        public_holidays = []
        public_holidays_recs = self.env['public.holiday'].search(
            [('date', '>=', (datetime.strptime(start_date, '%Y-%m-%d'))),
             ('date', '<=', (datetime.strptime(end_date, '%Y-%m-%d')))])
        for public_holidays_rec in public_holidays_recs:
            public_holidays.append(public_holidays_rec.date)

        employee_list = self.env['hr.employee'].search([])


        absent = []
        for emp in employee_list:
            absent_recs = self.env['hiworth.hr.attendance'].search(
                [('name', '=', emp.id), ('attendance', '=', 'absent'),
                 ('date', '>=', (datetime.strptime(start_date, '%Y-%m-%d'))),
                 ('date', '<=', (datetime.strptime(end_date, '%Y-%m-%d')))])
            for absent_rec in absent_recs:
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
            if datetime.strftime(day[0], "%Y-%m-%d") in public_holidays:
                selected_days_with_attendance[idx] += ("S",)

            elif day[0].isoweekday() in [7]:
                selected_days_with_attendance[idx] += ("S",)



            elif datetime.strftime(day[0], "%Y-%m-%d") in absent:
                selected_days_with_attendance[idx] += ("A",)

            elif day[0] > datetime.now().date():
                selected_days_with_attendance[idx] += ("S",)
            else:
                selected_days_with_attendance[idx] += ("A",)

        return selected_days_with_attendance

    @api.model
    def get_attendance_days_employee(self,employee_id, start_date, end_date):
        # Find the list of days for which the report is to be generated
        delta = datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d");
        selected_days = [(datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day)).date() for
                         day in range(delta.days + 1)];


        date_from = datetime.strptime(start_date, '%Y-%m-%d')
        to_date = datetime.strptime(end_date, '%Y-%m-%d')
        date_diff = to_date - date_from
        leaves = []

        public_holidays = []
        public_holidays_recs = self.env['public.holiday'].search(
            [('date', '>=', (datetime.strptime(start_date, '%Y-%m-%d'))),
             ('date', '<=', (datetime.strptime(end_date, '%Y-%m-%d')))])
        for public_holidays_rec in public_holidays_recs:
            public_holidays.append(public_holidays_rec.date)

        full_present = []
        full_present_recs = self.env['hiworth.hr.attendance'].search(
            [('name', '=', employee_id), ('attendance', '=', 'full'),
             ('date', '>=', (datetime.strptime(start_date, '%Y-%m-%d'))),
             ('date', '<=', (datetime.strptime(end_date, '%Y-%m-%d')))])
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
             ('date', '>=', (datetime.strptime(start_date, '%Y-%m-%d'))),
             ('date', '<=', (datetime.strptime(end_date, '%Y-%m-%d')))])
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
             ('date', '>=', (datetime.strptime(start_date, '%Y-%m-%d'))),
             ('date', '<=', (datetime.strptime(end_date, '%Y-%m-%d')))])
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
            if datetime.strftime(day[0], "%Y-%m-%d") in public_holidays:
                selected_days_with_attendance[idx] += ("H",)

            elif day[0].isoweekday() in [7]:
                selected_days_with_attendance[idx] += ("S",)

            elif datetime.strftime(day[0], "%Y-%m-%d") in full_present:
                selected_days_with_attendance[idx] += ("D",)

            elif datetime.strftime(day[0], "%Y-%m-%d") in half_present:
                selected_days_with_attendance[idx] += ("HP",)

            elif datetime.strftime(day[0], "%Y-%m-%d") in absent:
                selected_days_with_attendance[idx] += ("A",)

            elif datetime.strftime(day[0], "%Y-%m-%d") in leaves:
                selected_days_with_attendance[idx] += ("S",)

            elif day[0] > datetime.now().date():
                selected_days_with_attendance[idx] += ("D",)
            else:
                selected_days_with_attendance[idx] += ("A",)

        return selected_days_with_attendance;

    @api.multi
    def get_selected_users(self):
        new_list = []
        dom = []
        if self.attendance_category:
            if self.attendance_category != 'all':
                dom.append(('attendance_category','=',self.attendance_category))



        full_present = []

        for emp in  self.env['hr.employee'].search(dom):
            flag = []
            date_from = datetime.strptime(self.date_from, '%Y-%m-%d')
            to_date = datetime.strptime(self.date_to, '%Y-%m-%d')
            date_diff = to_date - date_from
            for rangeg in range(date_diff.days + 1):
                full_prsent_res = self.env['hiworth.hr.attendance'].search(
                    [('name', '=', emp.id), ('attendance', 'in', ['full','half']),
                     ('date', '=', date_from)])
                if full_prsent_res:
                    flag.append(1)
                else:
                    flag.append(0)
                from_date = date_from + timedelta(days=1)
                date_from = from_date

            flag = list(set(flag))

            if len(flag) ==1 and flag[0] == 0:
                new_list.append(emp)


        return self.env['hr.employee'].search(dom)

    date_from = fields.Date("From Date")
    date_to = fields.Date("To Date")
    attendance_category = fields.Selection([('all','All'),
                                            ('office_staff', 'Office Staff'),
                                            ('site_employee', 'Site Employee'),
                                            ], string='Attendance Category')


    @api.multi
    def action_submit(self):
        for rec in self:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'hiworth_hr_attendance.template_hiworth_hr_absentees_leave',
                'report_type': 'qweb-html'
            }
