from openerp import models, fields, api, _
from datetime import datetime,timedelta
from openerp.osv import osv

class ExgratiaPayment(models.Model):
    _name = 'exgratia.payment'

    contract_id = fields.Many2one('hr.contract')

    # @api.onchange('employee_id')
    # def onchange_employee_id(self):
    #     active_contract = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id)],limit=1)
    #     self.payment_amt = (active_contract.wage /30)

    # @api.depends('employee_id')
    # def compute_lop(self):
    #     for rec in self:
    #         if rec.date and rec.employee_id:
    #             month_date = datetime.strptime(rec.date, "%Y-%m-%d")
    #             start_date = datetime(month_date.year, month_date.month, 1)
    #             if month_date.month == 2:
    #                 if month_date.month % 4 == 0:
    #                     end_date = datetime(month_date.year, month_date.month, 29)
    #                 else:
    #                     end_date = datetime(month_date.year, month_date.month, 28)
    #             elif month_date.month in [1, 3, 5, 7, 8, 10, 12]:
    #                 end_date = datetime(month_date.year, month_date.month, 31)
    #             else:
    #                 end_date = datetime(month_date.year, month_date.month, 30)
    #             leave_request = self.env['employee.leave.request'].search([('employee_id','=',rec.employee_id.id),
    #                                                             ('leave_id','=',rec.leave_type_id.id),
    #                                                             ('leave_credited','=',True),
    #                                                             ('lop_leave','!=',0.0),
    #                                                              ('date','>=',start_date),
    #                                                              ('date','<=',end_date)],limit=1,order='date asc')
    #             rec.lop = len(leave_request.ids)
    #         else:
    #             rec.lop = 0

    # @api.model
    # def create(self,vals):
    #     if 'contract_id' in vals:
    #         contract_id = self.env['hr.contract'].browse([(vals.get('contract_id'))])
    #         vals.update({'employee_id': contract_id.employee_id.id})
    #     prev_record = self.env['exgratia.payment'].search([('date','=',vals['date']),('employee_id','=',vals['employee_id'])])
    #     if prev_record:
    #         raise osv.except_osv(('Error'), ('Already Entered this Attendance'))
    #     employee = self.env['hr.employee'].browse(vals['employee_id'])
    #     if vals['date'] < employee.joining_date:
    #         raise osv.except_osv(('Error'), ('joining date of employee must be greater than Date'))
    #     month_date = datetime.strptime(vals['date'], "%Y-%m-%d")
    #
    #     if month_date > datetime.today():
    #         raise osv.except_osv('Error', 'Date of Exgratia can not be future date')
    #     if vals.get('exgratia_redeem') == 'leave':
    #         vals.update({'credit': True})
    #     res = super(ExgratiaPayment, self).create(vals)
    #     # if res.exgratia_redeem == 'leave' and res.credit:
    #     #     # start_date = datetime(month_date.year, month_date.month, 1)
    #     #     # if month_date.month == 2:
    #     #     #     if month_date.month % 4 == 0:
    #     #     #         end_date = datetime(month_date.year, month_date.month, 29)
    #     #     #     else:
    #     #     #         end_date = datetime(month_date.year, month_date.month, 28)
    #     #     # elif month_date.month in [1, 3, 5, 7, 8, 10, 12]:
    #     #     #     end_date = datetime(month_date.year, month_date.month, 31)
    #     #     # else:
    #     #     #     end_date = datetime(month_date.year, month_date.month, 30)
    #     #     month_leave_status = self.env['month.leave.status'].search([('status_id', '=', res.employee_id.id),
    #     #                                                                 ('month_id', '=', month_date.month)])
    #     #     if month_leave_status:
    #     #         if res.attendance == 'full':
    #     #             month_leave_status.exgratia += 1
    #     #         else:
    #     #             month_leave_status.exgratia += .5
    #     #
    #     #     else:
    #     #         leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1, order='id asc')
    #     #         if res.attendance == 'full':
    #     #             self.env['month.leave.status'].create({'status_id': res.employee_id.id,
    #     #                                                    'month_id': month_date.month,
    #     #                                                    'exgratia': 1,
    #     #                                                    'leave_id': leave_type.id,
    #     #                                                    })
    #     #         else:
    #     #             self.env['month.leave.status'].create({'status_id': res.employee_id.id,
    #     #                                                    'month_id': month_date.month,
    #     #                                                    'exgratia': .5,
    #     #                                                    'leave_id': leave_type.id,
    #     #                                                    })
    #     #     contract = self.env['hr.contract'].search([('employee_id', '=', res.employee_id.id),
    #     #                                                       ('state', '=', 'active')], limit=1, order='id desc')
    #     #     if contract:
    #     #         if res.attendance == 'full':
    #     #             contract.available_exgratia += 1
    #     #         else:
    #     #             contract.available_exgratia += 0.5
    #     #     contract_config = self.env['employee.config.leave'].search([('employee_id', '=', res.employee_id.id)],
    #     #                                                                limit=1, order='id desc')
    #     #     if contract_config:
    #     #         if res.attendance == 'full':
    #     #             contract_config.availa_exgre += 1
    #     #         else:
    #     #             contract_config.availa_exgre += 0.5
    #     res.state = 'new'
    #     return res

    employee_id = fields.Many2one('hr.employee',"Employee", required=True)
    date = fields.Date("Date", required=True)
    hours = fields.Float()
    attendance = fields.Selection([('full','Full Present'),
                                   ('half','Half Present')],string="Attendance")
    payment_amt = fields.Float("Amount/Hour")
    total_amt = fields.Float("Overtime Salary")
    journal_id = fields.Many2one('account.journal',"Mode of Payment")
    debit_account_id = fields.Many2one('account.account',"Debit Account",domain="[('type','!=','view')]")
    credit_account_id = fields.Many2one('account.account',"Credit Account",domain="[('type','!=','view')]")
    state = fields.Selection([('draft','Draft'),('requested', 'Requested'),
                              ('approved',"Approved"),('cancel','Cancel')],default='draft',string="Status")
    move_id = fields.Many2one('account.move',"Account Entry")
    leave_type_id = fields.Many2one('hr.holidays.status',"Leave Type")
    # lop = fields.Float("Lop",compute='compute_lop',store=True)
    remarks = fields.Char("Remarks")
    estimated = fields.Selection([('full','Full Present'),
                                   ('half','Half Present')], readonly=True)
    exgratia_redeem = fields.Selection([('leave', 'Adjust to leave'),
                                   ('payment', 'Cash Payment')], string="Please choose an option to redeem ",)
    credit = fields.Boolean()

    @api.depends('payment_amt','hours')
    def compute_overtime_amount(self):
        for rec in self:
            rec.total_amt = rec.payment_amt * rec.hours

    @api.multi
    def action_request_method(self):
        self.state = 'requested'

    @api.multi
    def action_approve(self):
        self.state = 'approved'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_set_draft(self):
        self.state = 'draft'

    # @api.multi
    # def write(self, vals):
    #     previous_date = self.date
    #     res = super(ExgratiaPayment, self).write(vals)
    #     if vals.get('exgratia_redeem'):
    #         if self.exgratia_redeem == 'leave':
    #             if not self.credit:
    #                 month_date = datetime.strptime(self.date, "%Y-%m-%d")
    #                 month_leave_status = self.env['month.leave.status'].search([('status_id', '=', self.employee_id.id),
    #                                                                             ('month_id', '=', month_date.month)])
    #                 if month_leave_status:
    #                     if self.attendance == 'full':
    #                         month_leave_status.exgratia += 1
    #                     else:
    #                         month_leave_status.exgratia += 0.5
    #
    #                 else:
    #                     leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1,
    #                                                                        order='id asc')
    #                     if self.attendance == 'full':
    #                         self.env['month.leave.status'].create({'status_id': self.employee_id.id,
    #                                                                'month_id': month_date.month,
    #                                                                'exgratia': 1,
    #                                                                'leave_id': leave_type.id,
    #                                                                })
    #                     else:
    #                         self.env['month.leave.status'].create({'status_id': self.employee_id.id,
    #                                                                'month_id': month_date.month,
    #                                                                'exgratia': .5,
    #                                                                'leave_id': leave_type.id,
    #                                                                })
    #
    #                 contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
    #                                                                   ('state', '=', 'active')], limit=1, order='id desc')
    #
    #                 if contract:
    #                     if self.attendance == 'full':
    #                         contract.available_exgratia += 1
    #                     else:
    #                         contract.available_exgratia += 0.5
    #                 contract_config = self.env['employee.config.leave'].search([('employee_id', '=', self.employee_id.id)],
    #                                                                            limit=1, order='id desc')
    #                 if contract_config:
    #                     if self.attendance == 'full':
    #                         contract_config.availa_exgre += 1
    #                     else:
    #                         contract_config.availa_exgre += 0.5
    #
    #                 self.credit = True
    #         else:
    #             if self.exgratia_redeem != 'leave':
    #                 if self.credit:
    #                     month_date = datetime.strptime(self.date, "%Y-%m-%d")
    #                     month_leave_status = self.env['month.leave.status'].search([('status_id', '=', self.employee_id.id),
    #                                                                                 ('month_id', '=', month_date.month)])
    #                     if month_leave_status:
    #                         if self.attendance == 'full':
    #                             month_leave_status.exgratia -= 1
    #                         else:
    #                             month_leave_status.exgratia -= 0.5
    #
    #                     contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
    #                                                                ('state', '=', 'active')], limit=1, order='id desc')
    #
    #                     if contract:
    #                         if self.attendance == 'full':
    #                             contract.available_exgratia -= 1
    #                         else:
    #                             contract.available_exgratia -= 0.5
    #
    #                     contract_config = self.env['employee.config.leave'].search(
    #                         [('employee_id', '=', self.employee_id.id)],
    #                         limit=1, order='id desc')
    #                     if contract_config:
    #                         if self.attendance == 'full':
    #                             contract_config.availa_exgre -= 1
    #                         else:
    #                             contract_config.availa_exgre -= 0.5
    #                     self.credit = False
    #     return res


    # @api.multi
    # def action_payment(self):
    #     for rec in self:
    #         if rec.exgratia_redeem =='payment':
    #
    #             move_line_list = []
    #
    #             move_line_list.append((0, 0, {'name': 'Exgratia '+ rec.employee_id.name ,
    #                                           'account_id': rec.debit_account_id.id,
    #                                           'debit': rec.payment_amt,
    #                                           'credit': 0,
    #                                           }))
    #
    #             move_line_list.append((0, 0, {'name': 'Exgratia '+ rec.employee_id.name,
    #                                           'account_id': rec.credit_account_id.id,
    #                                           'debit': 0,
    #                                           'credit': rec.payment_amt}))
    #
    #             move_vals = {'journal_id': rec.journal_id.id,
    #                          'company_id': self.env.user.company_id.id,
    #                          'date': rec.date,
    #                          'line_id': move_line_list,
    #                          }
    #
    #             move_id = self.env['account.move'].create(move_vals)
    #             rec.move_id = move_id.id
    #             rec.state = 'paid'
    #         else:
    #             raise osv.except_osv(_('Warning!'), _('The selected exgratia is already redeemed as a leave credit'))
    #     return True
    #
    #
    #
    # @api.multi
    # def action_adjust_leave(self):
    #     for rec in self:
    #         month_date = datetime.strptime(rec.date,"%Y-%m-%d")
    #         start_date = datetime(month_date.year,month_date.month,1)
    #         if month_date.month == 2:
    #             if month_date.month % 4 == 0:
    #                 end_date = datetime(month_date.year,month_date.month,29)
    #             else:
    #                 end_date = datetime(month_date.year,month_date.month,28)
    #         elif month_date.month in [1, 3, 5, 7, 8, 10, 12]:
    #             end_date = datetime(month_date.year, month_date.month, 31)
    #         else:
    #             end_date = datetime(month_date.year, month_date.month, 30)
    #         month_leave_status = self.env['month.leave.status'].search([('status_id', '=', rec.employee_id.id),
    #                                                                         ('month_id', '=', month_date.month)])
    #         # if month_leave_status:
    #         #     if rec.attendance == 'full':
    #         #         month_leave_status.exgratia +=1
    #         #     else:
    #         #         month_leave_status.exgratia += .5
    #         #
    #         # else:
    #         #     if rec.attendance == 'full':
    #         #         self.env['month.leave.status'].create({'status_id':rec.employee_id.id,
    #         #                                                'month_id':month_date.month,
    #         #                                                'exgratia':1,
    #         #                                                })
    #         #     else:
    #         #         self.env['month.leave.status'].create({'status_id': rec.employee_id.id,
    #         #                                                'month_id': month_date.month,
    #         #                                                'exgratia': .5,
    #         #                                                })
    #         # contract_config = self.env['hr.contract'].search([('employee_id', '=', lop.employee_id.id),
    #         #                                                   ('state', '=', 'active')], limit=1, order='id desc')
    #         #
    #         # if contract_config:
    #         #     if rec.attendance == 'full':
    #         #         contract_config.available_exgratia +=1
    #         #     else:
    #         #         contract_config.available_exgratia += .5
    #         lop = self.env['employee.leave.request'].search([('employee_id','=',rec.employee_id.id),
    #                                                         ('leave_id','=',rec.leave_type_id.id),
    #                                                         ('leave_credited','=',True),
    #                                                         ('lop_leave','!=',0.0),
    #                                                          ('date','>=',start_date),
    #                                                          ('date','<=',end_date)],limit=1,order='date asc')
    #         if lop:
    #             lop.adjusted_leave = 1
    #             lop.lop_leave = 0
    #             attendance = self.env['hiworth.hr.attendance'].search([('date','=',lop.date),
    #                                                                    ('name','=',lop.employee_id.id)])
    #             attendance.attendance = lop.leave_request_id.attendance
    #             contract_config = self.env['hr.contract'].search([('employee_id','=',lop.employee_id.id),
    #                                                                         ('state','=','active')],limit=1,order='id desc')
    #             if rec.attendance == 'full':
    #                 contract_config.availed_exgratia += 1
    #
    #             else:
    #                 contract_config.availed_exgratia += .5
    #             if month_leave_status:
    #                 if rec.attendance == 'full':
    #                     month_leave_status.availed += 1
    #
    #                 else:
    #                     month_leave_status.availed += .5
    #
    #         # if not lop:
    #         #     absent_attendance = self.env['hiworth.hr.attendance'].search([('date', '>=', start_date),
    #         #                                                                   ('date', '<=', end_date),
    #         #                                                            ('name', '=', rec.employee_id.id),
    #         #                                                                   ('attendance','=','absent')],order='date asc',limit=1)
    #         #
    #         #     half_day_attendance = self.env['hiworth.hr.attendance'].search([('date', '>=', start_date),
    #         #                                                                   ('date', '<=', end_date),
    #         #                                                            ('name', '=', rec.employee_id.id),
    #         #                                                                   ('attendance','=','half')],order='date asc',limit=1)
    #         #     contract_config = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
    #         #                                                       ('state', '=', 'active')], limit=1,
    #         #                                                      order='id desc')
    #         #     if self.attendance == 'full':
    #         #         if absent_attendance:
    #         #             for abs in absent_attendance:
    #         #                 abs.attendance = 'full'
    #         #                 abs.compensatory_off = True
    #         #                 contract_config.availed_exgratia += 1
    #         #                 contract_config.available_exgratia += 1
    #         #             if month_leave_status:
    #         #                 month_leave_status.availed += 1
    #         #         else:
    #         #
    #         #             contract_config.available_exgratia += 1
    #         #     if self.attendance == 'half':
    #         #         if half_day_attendance:
    #         #             for abs in half_day_attendance:
    #         #                 abs.attendance = 'full'
    #         #                 abs.compensatory_off = True
    #         #                 contract_config.availed_exgratia += .5
    #         #                 contract_config.available_exgratia += .5
    #         #             if month_leave_status:
    #         #                 month_leave_status.availed += .5
    #         #         else:
    #         #
    #         #             contract_config.available_exgratia += .5
    #
    #             rec.state = 'paid'
    #         else:
    #             raise osv.except_osv(('Error'), ('No LOP found for  %s to adjust in the exgratia') % rec.employee_id.name)
    #
    # @api.multi
    # def action_cancel(self):
    #     for rec in self:
    #         if rec.state == 'paid' or rec.estimated == 'half':
    #             raise osv.except_osv(_('Warning!'), _(
    #                 'The Exgratia on Processing can not be cancelled' ))
    #         date = datetime.strptime(rec.date, "%Y-%m-%d")
    #         if date.month != datetime.today().month:
    #             raise osv.except_osv(_('Warning!'), _(
    #                 'The Exgratia on the month %s can not be cancelled/deleted after the month') % (
    #                                      date.strftime("%B")))
    #         rec.state = 'cancel'
    #         if rec.exgratia_redeem == 'leave':
    #             if rec.estimated == 'half':
    #                 month_leave_status = self.env['month.leave.status'].search([('status_id', '=', rec.employee_id.id),
    #                                                                             ('month_id', '=', date.month)])
    #                 if month_leave_status:
    #                     if rec.attendance == 'full':
    #                         month_leave_status.exgratia -= 1
    #                     else:
    #                         month_leave_status.exgratia -= .5
    #
    #                 contract_config = self.env['employee.config.leave'].search([('employee_id', '=', rec.employee_id.id)], limit=1, order='id desc')
    #                 if contract_config:
    #                     if rec.attendance == 'full':
    #                         contract_config.availa_exgre -= 1
    #                     else:
    #                         contract_config.availa_exgre -= .5
    #
    #                 contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
    #                                                            ('state', '=', 'active')], limit=1, order='id desc')
    #                 if contract:
    #                     if rec.attendance == 'full':
    #                         contract.available_exgratia -= 1
    #                     else:
    #                         contract.available_exgratia -= .5
    #                 rec.credit = False
    #         return rec
    #
    # @api.multi
    # def action_set_draft(self):
    #     for rec in self:
    #         month_date = datetime.strptime(rec.date, "%Y-%m-%d")
    #         if month_date.month != datetime.today().month:
    #             raise osv.except_osv(_('Warning!'), _(
    #                 'The Exgratia on the month %s can not be cancelled/deleted after the month') % (
    #                                      month_date.strftime("%B")))
    #         rec.state = 'new'
    #         if rec.exgratia_redeem == 'leave':
    #             # start_date = datetime(month_date.year, month_date.month, 1)
    #             # if month_date.month == 2:
    #             #     if month_date.month % 4 == 0:
    #             #         end_date = datetime(month_date.year, month_date.month, 29)
    #             #     else:
    #             #         end_date = datetime(month_date.year, month_date.month, 28)
    #             # elif month_date.month in [1, 3, 5, 7, 8, 10, 12]:
    #             #     end_date = datetime(month_date.year, month_date.month, 31)
    #             # else:
    #             #     end_date = datetime(month_date.year, month_date.month, 30)
    #             month_leave_status = self.env['month.leave.status'].search([('status_id', '=', rec.employee_id.id),
    #                                                                         ('month_id', '=', month_date.month)])
    #             if month_leave_status:
    #                 if rec.attendance == 'full':
    #                     month_leave_status.exgratia += 1
    #                 else:
    #                     month_leave_status.exgratia += .5
    #             else:
    #                 if rec.attendance == 'full':
    #                     self.env['month.leave.status'].create({'status_id': rec.employee_id.id,
    #                                                            'month_id': month_date.month,
    #                                                            'exgratia': 1,
    #                                                            })
    #                 else:
    #                     self.env['month.leave.status'].create({'status_id': rec.employee_id.id,
    #                                                            'month_id': month_date.month,
    #                                                            'exgratia': .5,
    #                                                            })
    #
    #             contract_config = self.env['employee.config.leave'].search([
    #                 ('employee_id', '=', rec.employee_id.id)], limit=1, order='id desc')
    #             if contract_config:
    #                 if rec.attendance == 'full':
    #                     contract_config.availa_exgre += 1
    #                 else:
    #                     contract_config.availa_exgre += .5
    #             contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
    #                                                               ('state', '=', 'active')], limit=1, order='id desc')
    #             if contract:
    #                 if rec.attendance == 'full':
    #                     contract.available_exgratia += 1
    #                 else:
    #                     contract.available_exgratia += .5
    #             rec.credit = True
    #         return rec

    @api.multi
    def unlink(self):
        for rec in self:

            if rec.state == 'paid':
                raise osv.except_osv(('Warning'), ('Exgratia in the paid state can not be deleted'))
            if rec.state != 'cancel':
                raise osv.except_osv(('Warning'), ('Please cancel the Exgratia and try again!'))
            # if rec.state == 'draft':
            #     contract_config = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
            #                                                       ('state', '=', 'active')], limit=1, order='id desc')
            #     if contract_config:
            #         if rec.attendance == 'full':
            #             contract_config.available_exgratia -= 1
            #         else:
            #             contract_config.available_exgratia -= .5
            #
            #     month_date = datetime.strptime(rec.date,"%Y-%m-%d")
            #     month_leave_status = self.env['month.leave.status'].search([('status_id', '=', rec.employee_id.id),
            #                                                                 ('month_id', '=', month_date.month)])
            #     if month_leave_status:
            #         if rec.attendance == 'full':
            #             month_leave_status.exgratia -= 1
            #         else:
            #             month_leave_status.exgratia -= .5
            return super(ExgratiaPayment, self).unlink()