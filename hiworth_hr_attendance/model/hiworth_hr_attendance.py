from openerp import models, fields, api
from datetime import datetime, timedelta,date
from openerp.tools.translate import _
from openerp.osv import osv
from lxml import etree




# 
class hr_attendance(osv.osv):
    _inherit = "hr.attendance"
     
    def _altern_si_so(self, cr, uid, ids, context=None):
        """ Alternance sign_in/sign_out check.
            Previous (if exists) must be of opposite action.
            Next (if exists) must be of opposite action.
        """
#         for att in self.browse(cr, uid, ids, context=context):
#             # search and browse for first previous and first next records
#             prev_att_ids = self.search(cr, uid, [('employee_id', '=', att.employee_id.id), ('name', '<', att.name), ('action', 'in', ('sign_in', 'sign_out'))], limit=1, order='name DESC')
#             next_add_ids = self.search(cr, uid, [('employee_id', '=', att.employee_id.id), ('name', '>', att.name), ('action', 'in', ('sign_in', 'sign_out'))], limit=1, order='name ASC')
#             prev_atts = self.browse(cr, uid, prev_att_ids, context=context)
#             next_atts = self.browse(cr, uid, next_add_ids, context=context)
#             # check for alternance, return False if at least one condition is not satisfied
#             if prev_atts and prev_atts[0].action == att.action: # previous exists and is same action
#                 return False
#             if next_atts and next_atts[0].action == att.action: # next exists and is same action
#                 return False
#             if (not prev_atts) and (not next_atts) and att.action != 'sign_in': # first attendance must be sign_in
#                 return False
        return True
         
         
    _constraints = [(_altern_si_so, 'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]
    

class HiworthHrAttendance(models.Model):
    _name='hiworth.hr.attendance'
    _order = "date desc"

    @api.model
    def _cron_attendance_entry_creation(self):
        today = datetime.today()
        # print 'v-----------------------------------------', today
        holiday = self.env['public.holiday'].search([('date','=',today)])
        if not holiday:
            # print 'hjkh--------------------------------'
            employees = self.env['hr.employee'].search([('cost_type','=','permanent')])
            for emp_id in employees:
                attendance = self.env['hiworth.hr.attendance'].search([('name','=', emp_id.id),('date','=',today)])
                # print 'attendance------------------', attendance
                from_date = datetime.now() - timedelta(days=6)
                to_date = datetime.now() - timedelta(days=1)
                present_work = 0
                vals = {}
                total_attendance = 0
                if datetime.now().weekday() == 6 and not attendance:
                    for i in range(6):
                        if from_date != to_date:
                            attendance = self.search([('date', '=', from_date), ('name', '=', vals.get('name'))])
            
                            if attendance.attendance == 'full':
                                present_work += 1
                            elif attendance.attendance == 'half':
                                present_work += .5
                            from_date = from_date + timedelta(days=1)
                            if attendance:
                                total_attendance += 1
    
                    if emp_id.casual_leave > 1:
                        present_work += 1
                        emp_id.casual_leave = emp_id.casual_leave - 1
                    if present_work >= 3:
                        vals.update({'name':emp_id.id,
                                     'date':datetime.now(),
                                     'attendance': 'full'})
                        self.env['hiworth.hr.attendance'].create(vals)
                    else:
                        if total_attendance == 6:
                            vals.update({'name':emp_id.id,
                                         'date':datetime.now(),
                                        'attendance': 'absent'})
                        self.env['hiworth.hr.attendance'].create(vals)

    @api.model
    def create(self, vals):
        date = vals.get('date')
        if isinstance(date, str):
            date = datetime.strptime(vals.get('date'), "%Y-%m-%d")
        from_date = date - timedelta(days=6)
        to_date = date - timedelta(days=1)

        # present_work = 0
        # if date.weekday() == 6:
        #     for i in range(6):
        #         if from_date != to_date:
        #             attendance = self.env['hiworth.hr.attendance'].search([('date','=',from_date),('name','=',vals.get('name'))])
        #             leave = self.env['employee.leave.request'].search([('employee_id','=',vals.get('name')),('date','=',from_date)])
        #             if not leave:
        #                 if attendance and attendance.attendance == 'full':
        #                     present_work +=1
        #                 elif attendance and  attendance.attendance == 'half':
        #                     present_work +=.5
        #             from_date = from_date + timedelta(days=1)
        #
        #     if present_work >= 3:
        #         vals.update({'attendance':'full',
        #                      'attendance_category':self.env['hr.employee'].browse(vals.get('name')).attendance_category})
        #     else:
        #         vals.update({'attendance': 'absent',
        #                      'attendance_category':self.env['hr.employee'].browse(vals.get('name')).attendance_category})
        #
        # public_holiday = self.env['public.holiday'].search([('date','=',vals['date'])])
        # if public_holiday:
        #     today_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d"),"%Y-%m-%d")
        #
        #     leave_request = self.env['hr.holidays'].search([('date_from','<=',vals['date']),('date_to','>=',vals['date']),('employee_id','=',vals['name'])])
        #     yesterday_date = datetime.strptime(vals['date'],"%Y-%m-%d") - timedelta(days=1)
        #
        #     public_attendance = self.search([('date','=',yesterday_date),('name','=',vals['name'])])
        #     if public_attendance and public_attendance.attendance == 'absent' or not public_attendance:
        #         vals.update({'attendance': 'absent'})
        #
        #     else:
        #         if leave_request:
        #
        #             vals.update({'attendance': 'absent'})
        #         else:
        #             vals.update({'attendance': 'full'})
        # vals.update({'attendance_category':self.env['hr.employee'].browse(vals.get('name')).attendance_category})
        #
        # attendance= self.search([('date','=',vals.get('date')),('name','=',vals.get('name'))])
        # if len(attendance) >0:
        #     raise osv.except_osv(_('Warning!'), _("Already Attendance Created"))
        # employee = self.env['hr.employee'].browse(vals['name'])
        #
        # if employee.joining_date:
        #     employee_joining_date = employee.joining_date
        #     if isinstance(employee.joining_date, str):
        #         employee_joining_date = datetime.strptime(employee.joining_date, "%Y-%m-%d")
        #     if date < employee_joining_date:
        #     # if vals['date']< employee.joining_date:
        #         raise osv.except_osv(('Error'), ('joining date of employee must be greater than Date'))
        # # else:
        # #     raise osv.except_osv(('Error'), ('Please fill up the joining date of employee in the emloyee details'))
        #
        res = super(HiworthHrAttendance, self).create(vals)
        # month_date = datetime.strptime(res.date, "%Y-%m-%d")
        # month = month_date.month
        # leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1, order='id asc')
        # month_leave = self.env['month.leave.status'].search(
        #     [('status_id', '=', res.name.id), ('month_id', '=', month), ('leave_id', '=', leave_type.id)])
        # if not month_leave:
        #     prev_month = month
        #     if month == 1:
        #         prev_month = 12
        #     else:
        #         prev_month -= 1
        #     prev_month_record = self.env['month.leave.status'].search([('status_id', '=', res.name.id),
        #                                                                ('month_id', '=', prev_month),
        #                                                                ('leave_id', '=', leave_type.id),
        #                                                                ])
        #
        #     balance = prev_month_record.remaining or 0
        #     prev_month_record_id = prev_month_record.id or False
        #     self.env['month.leave.status'].create({'status_id': res.name.id,
        #                                            'month_id': month,
        #                                            'leave_id': leave_type.id,
        #                                            'allowed': 0,
        #                                            'available': balance,
        #                                            'month_leave_status_id': prev_month_record_id,
        #                                            })
        #
        # date = datetime.strptime(res.date,"%Y-%m-%d")
        #
        # present_work = 0
        # if date.weekday()!=6:
        #
        #     diff = 6 - date.weekday()
        #
        #
        #
        #     sunday = date   + timedelta(diff)
        #     from_date = sunday - timedelta(days=6)
        #     to_date = sunday
        #     print "ggggggggggggggggggggggggggggggggggggggg", date,sunday,date.weekday(),diff
        #     total_attendance = 0
        #     for i in range(6):
        #         if from_date != to_date:
        #             attendance = self.env['hiworth.hr.attendance'].search(
        #                 [('date', '=', from_date), ('name', '=', vals.get('name'))])
        #             leave = self.env['employee.leave.request'].search(
        #                 [('employee_id', '=', vals.get('name')), ('date', '=', from_date)])
        #             if not leave:
        #                 if attendance and attendance.attendance == 'full':
        #
        #                     present_work += 1
        #                 elif attendance and attendance.attendance == 'half':
        #                     present_work += .5
        #             from_date = from_date + timedelta(days=1)
        #             if attendance:
        #                 total_attendance += 1
        #
        #     if present_work >= 3:
        #         sunday_att =  self.env['hiworth.hr.attendance'].search(
        #                 [('date', '=', sunday), ('name', '=', vals.get('name'))])
        #         if sunday_att:
        #             sunday_att.attendance = 'full'
        #         else:
        #             self.env['hiworth.hr.attendance'].create({'date':sunday.strftime("%Y-%m-%d"),
        #                                                       'name': vals.get('name'),
        #                                                       'attendance':'full'})
        #
        #     else:
        #         if total_attendance == 6:
        #
        #             sunday_att = self.env['hiworth.hr.attendance'].search(
        #                 [('date', '=', sunday), ('name', '=', vals.get('name'))])
        #             if sunday_att:
        #                 sunday_att.attendance = 'absent'
        #             else:
        #                 self.env['hiworth.hr.attendance'].create({'date': sunday.strftime("%Y-%m-%d"),
        #                                                       'name': vals.get('name'),
        #                                                       'attendance': 'absent'})
        #         print "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu", sunday.strftime("%Y-%m-%d")
        #
        # month_date = datetime.strptime(res.date,"%Y-%m-%d")
        # month = month_date.month
        # start_date = datetime(month_date.year, month_date.month, 1)
        # # end_date = datetime(month_date.year, month_date.month, 30)
        # if month == 2:
        #     if (month_date.year % 4 == 0):
        #         end_date = datetime(month_date.year, month_date.month, 29)
        #     else:
        #         end_date = datetime(month_date.year,month_date.month,28)
        # elif month in [1,3,5,7,8,10,12]:
        #     end_date = datetime(month_date.year, month_date.month, 31)
        # else:
        #     end_date = datetime(month_date.year, month_date.month, 30)
        # full_present = self.env['hiworth.hr.attendance'].search([('date','>=',start_date),('date','<=',end_date),('attendance','=','full'),('name','=',res.name.id), ('compensatory_off', '=', False),('half_compensatory_off', '=', False)])
        # half_prsent = self.env['hiworth.hr.attendance'].search([('date','>=',start_date),('date','<=',end_date),('attendance','=','half'),('name','=',res.name.id), ('compensatory_off', '=', False)])
        # half_compensatory = self.env['hiworth.hr.attendance'].search([('date','>=',start_date),('date','<=',end_date),('attendance','=','full'),('name','=',res.name.id), ('half_compensatory_off', '=', True)])
        # sundays = 0
        # date_start = start_date
        # date_end = end_date
        # for i in range(date_end.day-1):
        #     if date_start.weekday() == 6:
        #         sunday = self.env['hiworth.hr.attendance'].search(
        #             [('date', '=', date_start), ('attendance', '=', 'full'),
        #              ('name', '=', res.name.id)])
        #         if sunday:
        #             sundays += 1
        #     date_start += timedelta(days=1)
        #
        # public_holiday_total = 0
        # public_holidays = self.env['public.holiday'].search([('date','>=',start_date),('date','<=',end_date)])
        # for day in public_holidays:
        #     holiday_attendance = self.env['hiworth.hr.attendance'].search(
        #             [('date', '=', day.date), ('attendance', '=', 'full'),
        #              ('name', '=', res.name.id)])
        #     if holiday_attendance:
        #         public_holiday_total += 1
        #
        # attendance = len(full_present.ids) + (len(half_prsent.ids)*.5) + (len(half_compensatory.ids)*.5) - sundays - public_holiday_total
        #
        # leave_type = self.env['hr.holidays.status'].search([('limit','=',False)],limit=1,order='id asc')
        #
        # # if month == 2:
        # #     if attendance >= 14:
        # #         month_leave = self.env['month.leave.status'].search([('status_id','=',res.name.id),('month_id','=',month),('leave_id','=',leave_type.id)])
        # #         if not month_leave:
        # #             prev_month = month
        # #             if prev_month == 1:
        # #                 prev_month = 12
        # #             else:
        # #                 prev_month -= 1
        # #             prev_month_record = self.env['month.leave.status'].search([('status_id', '=', res.name.id),
        # #                                                                        ('month_id', '=', prev_month),
        # #                                                                        ('leave_id', '=', leave_type.id),
        # #                                                                        ])
        # #             balance = prev_month_record and prev_month_record.remaining or 0
        # #             self.env['month.leave.status'].create({'status_id':res.name.id,
        # #                                                    'month_id':month,
        # #                                                    'leave_id':leave_type.id,
        # #                                                    'allowed':1,
        # #                                                    'available':balance,
        # #                                                    'month_leave_status_id':prev_month_record and prev_month_record.id
        # #                                                    })
        # #         else:
        # #             if month_leave.allowed == 0:
        # #                 month_leave.allowed += 1
        # #
        # # else:
        #
        # if attendance >= 15:
        #     print "ggggggggggggggggggggggggggggggggggggggggggggggggggggggg"
        #     month_leave = self.env['month.leave.status'].search([('status_id','=',res.name.id),('month_id','=',month),('leave_id','=',leave_type.id)])
        #     contract_config = self.env['employee.config.leave'].search([('employee_id', '=', res.name.id),
        #                                                                 ('leave_id', '=', leave_type.id)])
        #     if not month_leave:
        #         prev_month = month
        #         if prev_month == 1:
        #             prev_month = 12
        #         else:
        #             prev_month -= 1
        #         prev_month_record = self.env['month.leave.status'].search([('status_id', '=', res.name.id),
        #                                                                    ('month_id', '=', prev_month),
        #                                                                    ('leave_id', '=', leave_type.id),
        #                                                                    ])
        #         balance = prev_month_record.remaining or 0
        #         self.env['month.leave.status'].create({'status_id': res.name.id,
        #                                                'month_id': month,
        #                                                'leave_id': leave_type.id,
        #                                                'allowed': 1,
        #                                                'available': balance,
        #                                                'month_leave_status_id': prev_month_record.id,
        #                                                })
        #         if contract_config:
        #             contract_config.nos += 1
        #
        #     else:
        #         if month_leave.allowed == 0:
        #             month_leave.allowed += 1
        #             if contract_config:
        #                 contract_config.nos += 1
        return res

    name = fields.Many2one('hr.employee')
    sign_in = fields.Datetime()
    sign_out = fields.Datetime()
    location = fields.Many2one('stock.location', 'Location')
    state = fields.Char()
    attendance_signin_id = fields.Integer()
    attendance_signout_id = fields.Integer()
    employee_type = fields.Char()
    attendance = fields.Selection([('full', 'Full Present'),('half','Half Present'),('absent','Absent')], default='full', string='Attendance')
    # attendance = fields.Selection([('full', 'Full'),('half','Half')], default='full', string='Attendance')
    date = fields.Date('Date')
    labour_category_account_id = fields.Many2one('account.account', domain="[('labour_categ','=',True)]",
                                                 string="Labour Account Category")
    labour = fields.Boolean("Labour")
    compensatory_off = fields.Boolean("Compensatory Off")
    half_compensatory_off = fields.Boolean("Compensatory Off")
    attendance_category = fields.Selection([('office_staff', 'Office Staff'),
                                            ('site_employee', 'Site Employee'),
                                            ('project_eng', 'Project Team')
                                            ], string='Attendance Category')
    leave_id = fields.Many2one('employee.leave.request')
    exgratia_id1 = fields.Many2one('exgratia.payment')
    exgratia_id2 = fields.Many2one('exgratia.payment')


    @api.multi
    def write(self,vals):
        res = super(HiworthHrAttendance, self).write(vals)
        for rec in self:
            month_date = datetime.strptime(rec.date, "%Y-%m-%d")
            month = month_date.month
            start_date = datetime(month_date.year, month_date.month, 1)
            # end_date = datetime(month_date.year, month_date.month, 30)
            if month == 2:
                if (month_date.year % 4 == 0):
                    end_date = datetime(month_date.year, month_date.month, 29)
                else:
                    end_date = datetime(month_date.year, month_date.month, 28)
            elif month in [1, 3, 5, 7, 8, 10, 12]:
                end_date = datetime(month_date.year, month_date.month, 31)
            else:
                end_date = datetime(month_date.year, month_date.month, 30)
            full_present = self.env['hiworth.hr.attendance'].search(
                [('date', '>=', start_date), ('date', '<=', end_date), ('attendance', '=', 'full'),
                 ('name', '=', rec.name.id), ('compensatory_off', '=', False),('half_compensatory_off', '=', False)])
            half_prsent = self.env['hiworth.hr.attendance'].search(
                [('date', '>=', start_date), ('date', '<=', end_date), ('attendance', '=', 'half'),
                 ('name', '=', rec.name.id), ('compensatory_off', '=', False)])
            half_compensatory = self.env['hiworth.hr.attendance'].search(
                [('date', '>=', start_date), ('date', '<=', end_date), ('attendance', '=', 'full'),
                 ('name', '=', rec.name.id), ('half_compensatory_off', '=', True)])

            sundays = 0
            date_start = start_date
            date_end = end_date
            for i in range(date_end.day - 1):
                if date_start.weekday() == 6:
                    sunday = self.env['hiworth.hr.attendance'].search(
                        [('date', '=', start_date), ('attendance', '=', 'full'),
                         ('name', '=', rec.name.id)])
                    if sunday:
                        sundays += 1
                date_start += timedelta(days=1)

            public_holiday_total = 0
            public_holidays = self.env['public.holiday'].search([('date', '>=', start_date), ('date', '<=', end_date)])
            for day in public_holidays:
                holiday_attendance = self.env['hiworth.hr.attendance'].search(
                    [('date', '=', day.date), ('attendance', '=', 'full'),
                     ('name', '=', rec.name.id)])
                if holiday_attendance:
                    public_holiday_total += 1

            attendance = len(full_present.ids) + (len(half_prsent.ids) * .5) + (
                        len(half_compensatory.ids) * .5) - sundays - public_holiday_total

            leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1, order='id asc')

            # if month == 2:
            #     if attendance >= 14:
            #         month_leave = self.env['month.leave.status'].search(
            #             [('status_id', '=', rec.name.id), ('month_id', '=', month),
            #              ('leave_id', '=', leave_type.id)])
            #         if not month_leave:
            #             prev_month = month
            #             if prev_month == 1:
            #                 prev_month = 12
            #             else:
            #                 prev_month -= 1
            #             prev_month_record = self.env['month.leave.status'].search(
            #                 [('status_id', '=', rec.name.id),
            #                  ('month_id', '=', prev_month),
            #                  ('leave_id', '=', leave_type.id),
            #                  ])
            #             balance = prev_month_record and prev_month_record.remaining or 0
            #             self.env['month.leave.status'].create({'status_id': rec.name.id,
            #                                                    'month_id': month,
            #                                                    'leave_id': leave_type.id,
            #                                                    'allowed': 1,
            #                                                    'available': balance,
            #                                                    'month_leave_status_id': prev_month_record and prev_month_record.id
            #                                                    })
            #         else:
            #             if month_leave.allowed == 0:
            #                 month_leave.allowed += 1
            #
            # else:

            if attendance >= 15:

                month_leave = self.env['month.leave.status'].search(
                    [('status_id', '=', rec.name.id), ('month_id', '=', month),
                     ('leave_id', '=', leave_type.id)])

                contract_config = self.env['employee.config.leave'].search([('employee_id', '=', rec.name.id),
                                                                            ('leave_id', '=',  leave_type.id)])
                if not month_leave:
                    prev_month = month
                    if prev_month == 1:
                        prev_month = 12
                    else:
                        prev_month -= 1
                    prev_month_record = self.env['month.leave.status'].search(
                        [('status_id', '=', rec.name.id),
                         ('month_id', '=', prev_month),
                         ('leave_id', '=', leave_type.id),
                         ])
                    balance = prev_month_record.remaining or 0
                    self.env['month.leave.status'].create({'status_id': rec.name.id,
                                                           'month_id': month,
                                                           'leave_id': leave_type.id,
                                                           'allowed': 1,
                                                           'available': balance,
                                                           'month_leave_status_id': prev_month_record.id,
                                                           })
                    if contract_config:
                        contract_config.nos += 1

                else:
                    if month_leave.allowed == 0:
                        month_leave.allowed += 1
                        if contract_config:
                            contract_config.nos += 1
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            month_date = datetime.strptime(rec.date, "%Y-%m-%d")
            # if month_date.month < datetime.today().month:
            #     raise osv.except_osv(_('Warning!'),
            #                          _('The attendance on the month %s could not be deleted after the month') % (
            #                              month_date.strftime("%B")))
            month = month_date.month
            start_date = datetime(month_date.year, month_date.month, 1)
            if month == 2:
                if (month_date.year % 4 == 0):
                    end_date = datetime(month_date.year, month_date.month, 29)
                else:
                    end_date = datetime(month_date.year, month_date.month, 28)
            elif month in [1, 3, 5, 7, 8, 10, 12]:
                end_date = datetime(month_date.year, month_date.month, 31)
            else:
                end_date = datetime(month_date.year, month_date.month, 30)

            leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1, order='id asc')


            month_leave_status = self.env['month.leave.status'].search([
                ('status_id', '=', rec.name.id),
                ('leave_id', '=', leave_type.id),
                ('month_id', '=', month_date.month)])
            contract = self.env['hr.contract'].search([('employee_id', '=', rec.name.id),
                                                       ('state', '=', 'active')], limit=1, order='id desc')

            full_present = self.env['hiworth.hr.attendance'].search(
                [('date', '>=', start_date), ('date', '<=', end_date), ('attendance', '=', 'full'),
                 ('name', '=', rec.name.id), ('compensatory_off', '=', False),('half_compensatory_off', '=', False)])
            half_prsent = self.env['hiworth.hr.attendance'].search(
                [('date', '>=', start_date), ('date', '<=', end_date), ('attendance', '=', 'half'),
                 ('name', '=', rec.name.id), ('compensatory_off', '=', False)])
            half_compensatory = self.env['hiworth.hr.attendance'].search(
                [('date', '>=', start_date), ('date', '<=', end_date), ('attendance', '=', 'full'),
                 ('name', '=', rec.name.id), ('half_compensatory_off', '=', True)])
            sundays = 0
            date_start = start_date
            date_end = end_date
            for i in range(date_end.day - 1):
                if date_start.weekday() == 6:
                    sunday = self.env['hiworth.hr.attendance'].search(
                        [('date', '=', start_date), ('attendance', '=', 'full'),
                         ('name', '=', rec.name.id)])
                    if sunday:
                        sundays += 1
                date_start += timedelta(days=1)

            public_holiday_total = 0
            public_holidays = self.env['public.holiday'].search([('date', '>=', start_date), ('date', '<=', end_date)])
            for day in public_holidays:
                holiday_attendance = self.env['hiworth.hr.attendance'].search(
                    [('date', '=', day.date), ('attendance', '=', 'full'),
                     ('name', '=', rec.name.id)])
                if holiday_attendance:
                    public_holiday_total += 1

            attendance = len(full_present.ids) + (len(half_prsent.ids) * .5) + (
                    len(half_compensatory.ids) * .5) - sundays - public_holiday_total
            # if month == 2:
            #     if len(attendance.ids) == 14:
            #         config_employee = self.env['employee.config.leave'].search([('employee_id', '=', rec.name.id),
            #                                                                     ('leave_id', '=', leave_type.id),
            #                                                                     ])
            #         config_employee.available -= 1
            #
            #         month_leave_status = self.env['month.leave.status'].search([
            #             ('status_id', '=', rec.name.id),
            #             ('leave_id', '=', leave_type.id),
            #             ('month_id', '=', month_date.month)])
            #         if month_leave_status:
            #             month_leave_status.allowed -= 1
            # else:
            if attendance < 15:
                if month_leave_status.allowed == 1:
                    month_leave_status.allowed -= 1
                    config_employee = self.env['employee.config.leave'].search([('employee_id', '=', rec.name.id),
                                                                                ('leave_id', '=', leave_type.id),
                                                                                ])
                    if config_employee:
                        config_employee.nos -= 1

            continue_function = False
            if rec.leave_id:
                if not rec.leave_id.adjusted_leave:
                    continue_function = True
            else:
                continue_function = True
            if continue_function:
                if rec.compensatory_off:
                    if rec.half_compensatory_off:
                        month_leave_status.availed -= .5
                        if rec.exgratia_id1:
                            if rec.exgratia_id1.state == 'paid':
                                rec.exgratia_id1.state = 'new'
                                if rec.exgratia_id1.attendance == 'half':
                                    if contract:
                                        contract.availed_exgratia -= 0.5
                                else:
                                    contract.availed_exgratia -= 1

                            else:
                                if rec.exgratia_id1.estimated == 'half':
                                    rec.exgratia_id1.estimated = ''
                                    contract.availed_exgratia -= .5

                    else:
                        month_leave_status.availed -= 1
                        if rec.exgratia_id1:
                            if rec.exgratia_id1.state == 'paid':
                                rec.exgratia_id1.state = 'new'
                                if rec.exgratia_id1.attendance == 'half':
                                    if contract:
                                        contract.availed_exgratia -= 0.5
                                else:
                                    contract.availed_exgratia -= 1
                            else:
                                if rec.exgratia_id1.estimated == 'half':
                                    rec.exgratia_id1.estimated = ''
                                    contract.availed_exgratia -= .5

                    if rec.exgratia_id2:
                        if rec.exgratia_id2.state == 'paid':
                            rec.exgratia_id1.state = 'new'
                            if rec.exgratia_id1.attendance == 'half':
                                if contract:
                                    contract.availed_exgratia -= 0.5
                            else:
                                contract.availed_exgratia -= 1
                        else:
                            if rec.exgratia_id1.estimated == 'half':
                                rec.exgratia_id1.estimated = ''
                                contract.availed_exgratia -= .5

        res = super(HiworthHrAttendance, self).unlink()
        return res
