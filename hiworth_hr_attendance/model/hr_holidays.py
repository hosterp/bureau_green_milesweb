from openerp import models, fields, api, _
from openerp.exceptions import except_orm, ValidationError
from datetime import datetime, date, timedelta
from openerp import tools
from dateutil.relativedelta import relativedelta

from openerp.osv import osv


class ApprovedPersons(models.Model):
    _name = 'approved.persons'

    name = fields.Many2one('res.users')
    app_id = fields.Many2one('hr.holidays')
    date_today = fields.Datetime('Date')


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'
    _order = 'id desc'

    @api.onchange('leave_id', 'employee_id')
    def onchange_leave_id(self):
        if self.leave_id:
            if self.employee_id:
                leave_obj = self.env['employee.leave'].search(
                    [('employee_id', '=', self.employee_id.id), ('state', '=', 'active'),
                     ('leave_id', '=', self.leave_id.id)])
                if leave_obj:
                    self.remaining = leave_obj.remaining
        if self.leave_id.name == 'CL':
            self.remaining = self.employee_id.casual_leave

    status = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')
    # admin = fields.Many2one('res.users','Admin')
    next_approver = fields.Many2one('res.users', readonly=True)
    approved_persons = fields.One2many('approved.persons', 'app_id', readonly=True)
    state = fields.Selection([('draft', 'To Submit'),

                              ('confirm', 'To Approve'),
                              ('validated', 'Second Approval'),

                              ('validate', 'Approved'),
                              ('refuse', 'Refuse'),
                              ('cancel', 'Cancelled'), ],
                             'Status', readonly=True, copy=False, default="draft")
    lop_emp = fields.Float(string="Loss Of Pay/Not")
    leave_ids = fields.One2many('employee.leave', 'holiday_id', 'Leaves')
    holiday_status_id = fields.Many2one("hr.holidays.status", "Leave Type", required=False)
    allocation_date_from = fields.Date('Date From')
    allocation_date_to = fields.Date('Date To')
    date_from = fields.Date('Start Date', readonly=True,
                            states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, select=True,
                            copy=False)
    date_to = fields.Date('End Date', readonly=True,
                          states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, copy=False)
    leave_id = fields.Many2one('hr.holidays.status', 'Leave Type')
    nos = fields.Float('No of Days', compute="_compute_no_days_new", store=True)
    remaining = fields.Float('Available Casual Leave', compute="_compute_remaining", store=True)
    attendance = fields.Selection([('full', 'Full'), ('half', 'Half')], default='full', string='Attendance')
    leave_credit_status = fields.Selection([('under', 'Under Process'), ('credited', 'Credited')], default='under',
                                           string="Leave Credit Status")
    employee_leave_status_ids = fields.One2many('employee.leave.request', 'leave_request_id', "Leave status")
    remaining_exgratia = fields.Float('Available Exgratia', compute="_compute_remaining", store=True)

    @api.multi
    @api.depends('date_from', 'date_to', 'employee_id', 'leave_id', 'attendance')
    def _compute_no_days_new(self):
        for record in self:
            if record.date_from and record.date_to:
                d1 = datetime.strptime(record.date_from, tools.DEFAULT_SERVER_DATE_FORMAT)
                d2 = datetime.strptime(record.date_to, tools.DEFAULT_SERVER_DATE_FORMAT)
                delta = d2 - d1
                if record.attendance == 'full':
                    record.nos = (delta.days) + 1
                elif record.attendance == 'half':
                    record.nos = (delta.days) + 0.5
                else:
                    pass

    @api.multi
    @api.depends('employee_id', 'leave_id')
    def _compute_remaining(self):
        for record in self:
            if record.leave_id and record.employee_id:
                #
                # leave_obj = self.env['employee.config.leave'].search(
                #     [('employee_id', '=', record.employee_id.id),
                #      ('leave_id', '=', record.leave_id.id)])
                # if leave_obj:
                #     record.remaining = leave_obj.remaining
                contract_obj = self.env['hr.contract'].search(
                    [('employee_id', '=', record.employee_id.id), ('state', '=', 'active')])
                if contract_obj:
                    record.remaining =contract_obj.employee_leave_ids.search([('id','in',contract_obj.employee_leave_ids.ids),],limit=1,order= 'id desc').remaining
                    # record.remaining_exgratia = contract_obj.remaining

    def _compute_number_of_days(self, cr, uid, ids, name, args, context=None):
        pass

    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        pass

    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        pass

    @api.model
    def create(self, vals):
        result = super(HrHolidays, self).create(vals)
        if result.type == 'remove':
            if result.employee_id.parent_id:
                user = self.env['res.users'].sudo().search([('employee_id', '=', result.employee_id.parent_id.id)])
                if user:
                    result.next_approver = user.id
        result.state = 'draft'
        return result

    @api.multi
    def write(self, vals):
        result = super(HrHolidays, self).write(vals)
        if vals.get('employee_id') and vals.get('type') == 'remove':
            if result['employee_id'].parent_id:
                user = self.env['res.users'].sudo().search([('employee_id', '=', result['employee_id'].parent_id.id)])
                if user:
                    result['next_approver'] = user.id

        return result

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.employee_leave_status_ids:
                rec.employee_leave_status_ids.unlink()
        result = super(HrHolidays, self).unlink()

        return result

    @api.multi
    def get_notifications(self):
        result = []
        for obj in self:
            result.append({
                # 'admin':obj.admin.name,
                'status': obj.status,
                'employee_id': obj.employee_id.name,
                'id': obj.id,
                'next_approver': obj.next_approver.name
            })
        return result

    @api.multi
    def approve_leave(self):
        view_id = self.env.ref('hiworth_hr_attendance.view_wizard_approve_lop').id
        return {
            'name': 'Loss Of Pay',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'loss.pay',
            'view_id': False,
            'views': [(view_id, 'form'), ],
            # 'view_id':view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_rec': self.id, 'default_name': self.number_of_days_temp},
        }

    @api.multi
    def confirm(self):
        self.state = 'confirm'
        date_diff = datetime.strptime(self.date_to, "%Y-%m-%d") - datetime.strptime(self.date_from, "%Y-%m-%d")
        if date_diff.days == 0:
            self.env['employee.leave.request'].create({'date': self.date_to,
                                                       'leave_id': self.leave_id.id,
                                                       'employee_id': self.employee_id.id,
                                                       'leave_request_id': self.id})
        else:
            date_from = datetime.strptime(self.date_from, "%Y-%m-%d")
            for r in range(date_diff.days + 1):
                self.env['employee.leave.request'].create({'date': date_from,
                                                           'leave_id': self.leave_id.id,
                                                           'employee_id': self.employee_id.id,
                                                           'leave_request_id': self.id})
                form_date = date_from + timedelta(days=1)
                date_from = form_date

    @api.multi
    def action_validate(self):
        self.state = 'validate'
        date_from = datetime.strptime(self.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(self.date_to, "%Y-%m-%d")
        date_diff = date_to - date_from
        from_date = date_from

        active_contract = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'active')])
        employee_leave_id = active_contract.employee_leave_ids.search([('id','in',active_contract.employee_leave_ids.ids),],limit=1,order= 'id desc')
        remaining = employee_leave_id.remaining
        for r in range(date_diff.days + 1):
            attendance = self.env['hiworth.hr.attendance'].search(
                [('name', '=', self.employee_id.id), ('date', '=', from_date)])
            if self.nos >= 1:
                if not attendance:
                    attendance = self.env['hiworth.hr.attendance'].create({
                        'name': self.employee_id.id,
                        'attendance': 'absent',
                        'attendance_category': self.employee_id.attendance_category,
                        'date': from_date.strftime("%Y-%m-%d")})

                if remaining>=1:
                    attendance.attendance = 'full'
                    attendance.compensatory_off = True
                    employee_leave_id.availed += 1

                elif remaining == 0.5:
                    attendance.attendance='half'
                    attendance.half_compensatory_off = True
                    employee_leave_id.availed += 0.5


            from_date = from_date + timedelta(days=1)
        # contract_config = self.env['employee.config.leave'].search([('employee_id', '=', self.employee_id.id),
        #                                                             ('leave_id', '=', self.leave_id.id)]) 
        # leave_request = self.env['employee.leave.request'].search(
        #     [('leave_credited', '=', False), ('leave_request_id', '=', self.id)])
        # active_contract = self.env['hr.contract'].search(
        #     [('employee_id', '=', self.employee_id.id), ('state', '=', 'active')])
        # contract_config = active_contract.employee_leave_ids.search([('id','in',active_contract.employee_leave_ids.ids),],limit=1,order= 'id desc')
        #
        # allowed_leave = contract_config.remaining
        # for leave in leave_request:
        #     leave_date = datetime.strptime(leave.date, "%Y-%m-%d")
        #     month_leave_status = self.env['month.leave.status'].search(
        #         [('status_id', '=', leave.employee_id.id), ('month_id', '=', leave_date.month),
        #          ('leave_id', '=', leave.leave_id.id)])
        #     prev_month = leave_date.month
        #     if not month_leave_status:
        #         if leave_date.month == 1:
        #             prev_month = 12
        #         else:
        #             prev_month = leave_date.month - 1
        #         prev_month_record = self.env['month.leave.status'].search([('status_id', '=', leave.employee_id.id),
        #                                                                    ('month_id', '=', prev_month),
        #                                                                    ('leave_id', '=', leave.leave_id.id),
        #                                                                    ])
        #         balance = prev_month_record.remaining or 0
        #
        #         month_leave_status = self.env['month.leave.status'].create({'status_id': leave.employee_id.id,
        #                                                                     'month_id': leave_date.month,
        #                                                                     'leave_id': leave.leave_id.id,
        #                                                                     'availed': 0,
        #                                                                     'available': balance,
        #                                                                     # 'exgratia': contract_config.availa_exgre,
        #                                                                     'month_leave_status_id': prev_month_record.id,
        #                                                                     })
        #     if allowed_leave > 0:
        #         if active_contract.remaining >= contract_config.remaining:
        #             exgratia_full_ids = self.env['exgratia.payment'].search([
        #                 ('employee_id', '=', self.employee_id.id), ('state', '=', 'new'),
        #                 ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'), ('estimated', '=', False)])
        #
        #             exgratia_half_ids = self.env['exgratia.payment'].search([
        #                 ('employee_id', '=', self.employee_id.id), ('state', '=', 'new'),
        #                 ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'half')])
        #
        #             exgratia_full_half_ids = self.env['exgratia.payment'].search([
        #                 ('employee_id', '=', self.employee_id.id), ('state', '=', 'new'),
        #                 ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
        #                 ('estimated', '=', 'half')])
        #
        #             exgratia = len(exgratia_full_ids) + (len(exgratia_half_ids) * .5) + (len(exgratia_full_half_ids) * 0.5)
        #             if exgratia > 0:
        #                 if allowed_leave < 1 or self.attendance == 'half':
        #                     leave.leave_credited = True
        #                     leave.adjusted_leave = 0.5
        #                     leave.lop_leave = 0.5
        #                     allowed_leave -= 0.5
        #                     contract_config.availed += 0.5
        #                     # contract_config.remaining -= 0.5
        #                     attendance = self.env['hiworth.hr.attendance'].search([('name', '=', self.employee_id.id),
        #                                                                            ('date', '=', leave.date),
        #                                                                            ])
        #                     if attendance:
        #                         attendance.attendance = 'half'
        #                         attendance.leave_id = leave
        #                         attendance.compensatory_off = True
        #
        #                     if exgratia_half_ids:
        #                         exgratia_half = self.env['exgratia.payment'].search([
        #                                     ('employee_id', '=', self.employee_id.id), ('state', '=', 'new'),
        #                                     ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'half')], limit=1)
        #
        #                         exgratia_half.state = 'paid'
        #                         leave.exgratia_id = exgratia_half.id
        #                         active_contract.availed_exgratia += 0.5
        #                         # contract_config.availa_exgre -= 0.5
        #
        #                     elif exgratia_full_half_ids and not exgratia_half_ids:
        #                         exgratia_full_half = self.env['exgratia.payment'].search([
        #                                         ('employee_id', '=', self.employee_id.id), ('state', '=', 'new'),
        #                                         ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
        #                                         ('estimated', '=', 'half')], limit=1)
        #                         exgratia_full_half.state = 'paid'
        #                         leave.exgratia_id = exgratia_full_half.id
        #                         active_contract.availed_exgratia += 0.5
        #                         # contract_config.availa_exgre -= 0.5
        #
        #                     else:
        #                         exgratia_full = self.env['exgratia.payment'].search([
        #                                     ('employee_id', '=', self.employee_id.id), ('state', '=', 'new'),
        #                                     ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
        #                                     ('estimated', '=', False)], limit=1)
        #                         exgratia_full.attendance = 'half'
        #                         exgratia_full.estimated = 'half'
        #                         active_contract.availed_exgratia += 0.5
        #                         # contract_config.availa_exgre -= 0.5
        #                         leave.exgratia_id = exgratia_full.id
        #
        #                     if month_leave_status:
        #                         month_leave_status.availed += .5
        #                         # next_month_avialble = self.env['month.leave.status'].search(
        #                         #     [('month_leave_status_id', '=', month_leave_status.id),
        #                         #      ])
        #                         # if next_month_avialble:
        #                         #     next_month_avialble.available -= .5
        #
        #                 else:
        #                     leave.leave_credited = True
        #                     leave.adjusted_leave = 1
        #                     allowed_leave -= 1
        #                     contract_config.availed += 1
        #                     # contract_config.remaining -= 1
        #                     attendance = self.env['hiworth.hr.attendance'].search([('name', '=', self.employee_id.id),
        #                                                                            ('date', '=', leave.date),
        #                                                                            ])
        #                     if attendance:
        #                         attendance.attendance = 'full'
        #                         attendance.compensatory_off = True
        #                         attendance.leave_id = leave
        #
        #                     exgratia_full = self.env['exgratia.payment'].search([
        #                         ('employee_id', '=', self.employee_id.id), ('state', '=', 'new'),
        #                         ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
        #                         ('estimated', '=', False)], limit=1)
        #                     exgratia_full_half = self.env['exgratia.payment'].search([
        #                         ('employee_id', '=', self.employee_id.id), ('state', '=', 'new'),
        #                         ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
        #                         ('estimated', '=', 'half')], limit=2)
        #                     exgratia_half = self.env['exgratia.payment'].search([
        #                         ('employee_id', '=', self.employee_id.id), ('state', '=', 'new'),
        #                         ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'half')], limit=2)
        #
        #                     if exgratia_full:
        #                         exgratia_full.state = 'paid'
        #                         leave.exgratia_id = exgratia_full.id
        #                         active_contract.availed_exgratia += 1
        #                         # contract_config.availa_exgre -= 1
        #
        #                     elif len(exgratia_full_half) == 2:
        #                             for exgratia_id in exgratia_full_half:
        #                                 exgratia_id.state = 'paid'
        #                             leave.exgratia_id = exgratia_full_half.ids[0]
        #                             leave.exgratia_id2 = exgratia_full_half.ids[1]
        #                             active_contract.availed_exgratia += 1
        #                             # contract_config.availa_exgre -= 1
        #
        #                     elif len(exgratia_half) == 2:
        #                             for exgratia_id in exgratia_half:
        #                                     exgratia_id.state = 'paid'
        #                             leave.exgratia_id = exgratia_half.ids[0]
        #                             leave.exgratia_id2 = exgratia_half.ids[1]
        #                             active_contract.availed_exgratia += 1
        #                             # contract_config.availa_exgre -= 1
        #                     else:
        #                         if exgratia_half_ids and exgratia_full_half_ids:
        #                             exgratia_half = self.env['exgratia.payment'].search([
        #                                 ('employee_id', '=', self.employee_id.id), ('state', '=', 'new'),
        #                                 ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'half')], limit=1)
        #
        #                             exgratia_full_half = self.env['exgratia.payment'].search([
        #                                 ('employee_id', '=', self.employee_id.id), ('state', '=', 'new'),
        #                                 ('exgratia_redeem', '=', 'leave'), ('attendance', '=', 'full'),
        #                                 ('estimated', '=', 'half')], limit=1)
        #
        #                             exgratia_half.state = 'paid'
        #                             exgratia_full_half.state = 'paid'
        #                             leave.exgratia_id1 = exgratia_half.id
        #                             leave.exgratia_id2 = exgratia_full_half.id
        #                             active_contract.availed_exgratia += 1
        #                             # contract_config.availa_exgre -= .5
        #
        #                     if month_leave_status:
        #                         month_leave_status.availed += 1
        #                         # next_month_avialble = self.env['month.leave.status'].search(
        #                         #     [('month_leave_status_id', '=', month_leave_status.id),
        #                         #      ])
        #                         # if next_month_avialble:
        #                         #     next_month_avialble.available -= 1
        #         else:
        #             if allowed_leave < 1 or self.attendance == 'half':
        #                 leave.leave_credited = True
        #                 leave.adjusted_leave = 0.5
        #                 leave.lop_leave = 0.5
        #                 allowed_leave -= 0.5
        #                 # contract_config.availed += 0.5
        #                 # contract_config.remaining -= .5
        #                 attendance = self.env['hiworth.hr.attendance'].search([('name', '=', self.employee_id.id),
        #                                                                        ('date', '=', leave.date),
        #                                                                        ])
        #                 if attendance:
        #                     attendance.attendance = 'half'
        #                     attendance.leave_id = leave
        #                     attendance.compensatory_off = True
        #
        #                 # active_contract.remaining -= .5
        #                 if month_leave_status:
        #                     month_leave_status.availed += .5
        #                     # next_month_avialble = self.env['month.leave.status'].search(
        #                     #     [('month_leave_status_id', '=', month_leave_status.id),
        #                     #      ])
        #                     # if next_month_avialble:
        #                     #     next_month_avialble.available -= .5
        #             else:
        #                 leave.leave_credited = True
        #                 leave.adjusted_leave = 1
        #                 allowed_leave -= 1
        #                 contract_config.availed += 1
        #                 # contract_config.remaining -= 1
        #                 attendance = self.env['hiworth.hr.attendance'].search([('name', '=', self.employee_id.id),
        #                                                                        ('date', '=', leave.date),
        #                                                                        ])
        #                 if attendance:
        #                     attendance.attendance = 'full'
        #                     attendance.compensatory_off = True
        #                     attendance.leave_id = leave
        #                 # active_contract.remaining -= 1
        #                 if month_leave_status:
        #                     month_leave_status.availed += 1
        #     #                 next_month_avialble = self.env['month.leave.status'].search(
        #     #                     [('month_leave_status_id', '=', month_leave_status.id),
        #     #                      ])
        #     #                 if next_month_avialble:
        #     #                     next_month_avialble.available -= 1
        #     else:
        #         leave.leave_credited = True
        #         leave.lop_leave = 1
        #         leave.adjusted_leave = 0
        #         attendance = self.env['hiworth.hr.attendance'].search([('name', '=', self.employee_id.id),
        #                                                                ('date', '=', leave.date),
        #                                                                ])
        #         if attendance:
        #             attendance.attendance = 'absent'
        #             attendance.leave_id = leave

    @api.multi
    def validate_leave(self):
        for rec in self:
            rec.state = 'validated'

    @api.multi
    def action_refuse(self):
        date_from = datetime.strptime(self.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(self.date_to, "%Y-%m-%d")
        if date_from.month != datetime.today().month:
            raise osv.except_osv(_('Warning!'),
                                 _('The leave request on the month %s could not be cancelled after the month') % (
                                     date_from.strftime("%B")))
        self.state = 'cancel'
        date_from = datetime.strptime(self.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(self.date_to, "%Y-%m-%d")
        date_diff = date_to - date_from
        for r in range(date_diff.days + 1):
            attendance = self.env['hiworth.hr.attendance'].search(
                [('name', '=', self.employee_id.id), ('date', '=', date_from)])
            if attendance:
                attendance.unlink()
            # if not attendance:
            # 	self.env['hiworth.hr.attendance'].create({'name': self.employee_id.id,
            # 											  'attendance': self.attendance,
            # 											  'attendance_category': self.employee_id.attendance_category,
            # 											  'date': date_from})
            # else:
            # 	attendance.attendance = 'self.attendance'

            from_date = date_from + timedelta(days=1)
            date_from = from_date
        contract_config = self.env['employee.config.leave'].search([('employee_id', '=', self.employee_id.id),
                                                                    ('leave_id', '=', self.leave_id.id)])
        leave_request = self.env['employee.leave.request'].search(
            [('leave_credited', '=', True), ('leave_request_id', '=', self.id)])

        contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                   ('state', '=', 'active')], limit=1, order='id desc')

        for leave in leave_request:
            if leave.adjusted_leave == 1:
                contract_config.availed -= 1

                if leave.exgratia_id:
                    if leave.exgratia_id.state == 'paid':
                        leave.exgratia_id.state = 'new'
                        if contract:
                            if leave.exgratia_id.attendance == 'half':
                                contract.availed_exgratia -= .5
                            else:
                                contract.availed_exgratia -= 1
                    else:
                        if leave.exgratia_id.estimated == 'half':
                            leave.exgratia_id.estimated = ''
                            contract.availed_exgratia -= .5

                if leave.exgratia_id2:
                    if leave.exgratia_id2.state == 'paid':
                        leave.exgratia_id2.state = 'new'
                        if contract:
                            if leave.exgratia_id2.attendance == 'half':
                                contract.availed_exgratia -= .5
                            else:
                                contract.availed_exgratia -= 1
                    else:
                        if leave.exgratia_id2.estimated == 'half':
                            leave.exgratia_id2.estimated = ''
                            contract.availed_exgratia -= .5

                month_date = datetime.strptime(leave.date, "%Y-%m-%d")
                month = month_date.month

                month_leave = self.env['month.leave.status'].search(
                    [('status_id', '=', leave.employee_id.id), ('month_id', '=', month),
                     ('leave_id', '=', leave.leave_id.id)])
                if month_leave:
                    month_leave.availed -= 1
            else:
                if leave.adjusted_leave == .5:
                    contract_config.availed -= .5
                    if leave.exgratia_id:
                        leave.exgratia_id.state = 'new'
                        leave.exgratia_id.estimated = ''
                        if contract:
                            contract.availed_exgratia -= 0.5
                    month_date = datetime.strptime(leave.date, "%Y-%m-%d")
                    month = month_date.month

                    month_leave = self.env['month.leave.status'].search(
                        [('status_id', '=', leave.employee_id.id), ('month_id', '=', month),
                         ('leave_id', '=', leave.leave_id.id)])
                    if month_leave:
                        month_leave.availed -= .5

            leave.leave_credited = False
            leave.adjusted_leave = 0
            leave.lop_leave = 0


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    effective_monthly_leave = fields.Integer('Effective Monthly Leave')


class PublicHoliday(models.Model):
    _name = 'public.holiday'

    @api.multi
    def button_automatic_entry(self):
        for rec in self:
            for employee in self.env['hr.employee'].search([]):
                if employee.joining_date < rec.date:
                    self.env['hiworth.hr.attendance'].create({'name': employee.id,
                                                              'attendance': 'full',
                                                              'date': rec.date})

    name = fields.Char('Description')
    date = fields.Date('Date')


class EmployeeLeaveRequest(models.Model):
    _name = 'employee.leave.request'

    date = fields.Date("Date")
    leave_id = fields.Many2one('hr.holidays.status', "Leave Type")
    employee_id = fields.Many2one('hr.employee', "Employee")
    leave_credited = fields.Boolean(string="Leave Processed", default=False)
    adjusted_leave = fields.Float("Adjusted Leave")
    lop_leave = fields.Float("LOP")
    leave_request_id = fields.Many2one('hr.holidays', "Leave Request")
    exgratia_id = fields.Many2one('exgratia.payment')
    exgratia_id2 = fields.Many2one('exgratia.payment')


class MonthLeaveStatus(models.Model):
    _name = 'month.leave.status'

    @api.model
    def create(self, vals):
        res = super(MonthLeaveStatus, self).create(vals)
        totday = datetime.now()
        start_date = datetime(totday.year, res.month_id, 1)
        # end_date = datetime(totday.year, res.month_id, 30)
        if res.month_id == 2:
            if (totday.year % 4 == 0):
                end_date = datetime(totday.year, res.month_id, 29)
            else:
                end_date = datetime(totday.year, res.month_id, 28)
        elif res.month_id in [1, 3, 5, 7, 8, 10, 12]:
            end_date = datetime(totday.year, res.month_id, 31)
        else:
            end_date = datetime(totday.year, res.month_id, 30)
        leave_status = self.env['employee.leave.request'].search([('employee_id', '=', res.status_id.id),
                                                                  ('leave_id', '=', res.leave_id.id),
                                                                  ('date', '>=', start_date), ('date', '<=', end_date)],
                                                                 order='date asc')
        # allowed_leave = res.allowed
        config_employee = self.env['employee.config.leave'].search([('employee_id', '=', res.status_id.id),
                                                                    ('leave_id', '=', res.leave_id.id),
                                                                    ])
        contract = self.env['hr.contract'].search([('employee_id', '=', res.status_id.id),
                                                   ('state', '=', 'active')], limit=1, order='id desc')

        # if config_employee.remaining != res.remaining:
        # 	raise osv.except_osv(_('Warning!'), _(
        # 		"Employee's remainig leave credit in month leave status and leave details in contract are not equal"))
        # 	config_employee.available = res.available + res.allowed + contract.available_exgratia
        # else:
        # 	if res.allowed:
        # 		config_employee.available += res.allowed
        # allowed_leave = config_employee.remaining
        # for leave in leave_status:
        # 	if allowed_leave>0:
        # 		leave.leave_credited = True
        # 		leave.adjusted_leave = 1
        # 		allowed_leave -=1
        # 		config_employee.availed += 1
        # 		config_employee.remaining -= 1
        # 		attendance = self.env['hiworth.hr.attendance'].search([('name','=',res.status_id.id),
        # 															   ('date','=',leave.date),
        # 															   ])
        # 		if attendance:
        #
        # 			attendance.attendance = leave.leave_request_id.attendance
        #
        # 	else:
        # 		leave.leave_credited = True
        # 		leave.lop_leave = 1
        # 		attendance = self.env['hiworth.hr.attendance'].search([('name', '=', res.status_id.id),
        # 															   ('date', '=', leave.date),
        # 															   ])
        # 		if attendance:
        # 			attendance.attendance = 'absent'
        return res

    @api.depends('availed')
    def compute_balance(self):
        for rec in self:
            rec.remaining = (rec.available + rec.allowed + rec.exgratia) - rec.availed

    status_id = fields.Many2one('hr.employee')
    leave_id = fields.Many2one('hr.holidays.status')
    month_id = fields.Integer('Month')
    available = fields.Float("Available")
    exgratia = fields.Float("Exgratia")
    allowed = fields.Float(string="Accrued")
    availed = fields.Float(string="Availed")
    remaining = fields.Float(string="Remaining", compute='compute_balance')
    month_leave_status_id = fields.Many2one('month.leave.status', "Month Leave")
    active = fields.Boolean("Active", default=True)

    @api.model
    def _cron_monthly_status_entries(self):
        print '-----------------------------------------------------', self.env['hr.employee'].search(
            [('cost_type', '=', 'permanent')])

        for day in self.env['hr.employee'].search([('cost_type', '=', 'permanent')]):
            # for day in self.env['hr.holidays'].search([('type','=','add')]):
            for day1 in day.leave_ids:
                if day1.leave_id.effective_monthly_leave != 0:
                    status = self.env['month.leave.status'].search(
                        [('status_id', '=', day.id), ('leave_id', '=', day1.leave_id.id)], limit=1)
                    today = date.today()
                    d = today - relativedelta(months=1)
                    print 'month----------------------------', day.name, today.month, d.month
                    start = date(d.year, d.month, 1)
                    end = date(today.year, today.month, 1) - relativedelta(days=1)
                    taken = 0
                    holiday = self.env['hr.holidays'].search([('type', '=', 'remove'), ('employee_id', '=', day.id)])
                    for hol_id in holiday:
                        if (str(start) <= hol_id.date_from <= str(end)) or (str(start) <= hol_id.date_to <= str(end)):
                            date_from = datetime.strptime(hol_id.date_from, '%Y-%m-%d').date()
                            date_to = datetime.strptime(hol_id.date_to, '%Y-%m-%d').date()
                            delta = date_to - date_from

                            if hol_id.attendance == 'full':
                                for i in range(delta.days + 1):
                                    if (date_from + timedelta(i)).month == d.month:
                                        taken += 1

                            elif hol_id.attendance == 'half':
                                for i in range(delta.days + 1):
                                    if (date_from + timedelta(i)).month == d.month:
                                        taken += 0.5
                            else:
                                pass
                    bal_leave = 0
                    allowed = 0
                    print 'status---------------', status.allowed, taken
                    if status:
                        bal_leave = status.allowed - taken

                    if bal_leave > 0:
                        allowed = bal_leave + day1.leave_id.effective_monthly_leave
                    elif bal_leave < 0:
                        allowed = day1.leave_id.effective_monthly_leave
                    else:
                        allowed = day1.leave_id.effective_monthly_leave

                    status = self.env['month.leave.status'].create({
                        'status_id': day.id,
                        'leave_id': day1.leave_id.id,
                        'month_id': today.month,
                        'allowed': allowed,
                    })
                    config_employee = self.env['employee.config.leave'].search(
                        [('employee_id', '=', status.status_id.id),
                         ('leave_id', '=', status.leave_id.id),
                         ])
                    config_employee.nos += allowed

# @api.multi
# def write(self, vals):
# 	config_employee = self.env['employee.config.leave'].search([('employee_id', '=', self.status_id.id),
# 																('leave_id', '=', self.leave_id.id),
# 																])
# 	if config_employee.remaining != self.remaining:
# 		raise osv.except_osv(_('Warning!'), _(
# 			"Employee's remainig leave credit in month leave status and leave details in contract are not equal"))
