from openerp import models, fields, api, _
from openerp.osv import osv
from datetime import datetime,timedelta


class AttendanceRequest(models.Model):
	_name = 'attendance.request'
	_order = 'date desc'

	date = fields.Date('Requested Date',default=fields.Date.today(), readonly=True)
	attendance_date = fields.Date('Date of Attendance',default=fields.Date.today(),required=True)
	# sign_in = fields.Datetime('Requested Sign In',required=True)
	# sign_out = fields.Datetime('Requested Sign Out',required=True)
	user = fields.Many2one('res.users', 'Employee Name')
	attendance = fields.Selection([('full', 'Full Present'),
								('half','Half Present'),
								# ('absent','Absent')
								], default='full', string='Attendance')
	state = fields.Selection([('draft',"Pending"),
							  ('first_approve',"First Approval"),
							  ('second_approve',"Second Approval"),
							  ('rejected', 'Rejected')],default='draft',string="Status")
	remarks = fields.Char("Remarks")
	approved_date = fields.Date("Approved Date", default=lambda self: fields.datetime.now())
	rejected_date = fields.Date("Rejected Date", default=lambda self: fields.datetime.now())

	_defaults = {
		'user':lambda obj, cr, uid, ctx=None: uid,
		}

	@api.model
	def create(self, vals):
		attendance_date = datetime.strptime(vals['attendance_date'], "%Y-%m-%d")
		requested_date = datetime.strptime(vals['date'], "%Y-%m-%d")
		if attendance_date.month != requested_date.month:
			raise osv.except_osv(_('Warning!'), _(
				'The attendance of the month %s should be requested with in the month') % (
				attendance_date.strftime("%B")))
		employee = self.env['res.users'].browse(vals['user']).employee_id
		attendance_rec = self.env['hiworth.hr.attendance'].search(
			[('name', '=', employee.id), ('date', '=', attendance_date)])
		if not attendance_rec:
			raise osv.except_osv(
				_('Warning!'), _('The attendance requested date is not marked as absent or present for the requested employee %s')% employee.name)
		if attendance_rec.attendance == 'full':
			raise osv.except_osv(
				_('Warning!'), _('The attendance requested date is marked as present for the requested employee  %s')% employee.name)
		return super(AttendanceRequest, self).create(vals)

	@api.multi
	def unlink(self):
		# if self.state != 'draft':
		# 	raise osv.except_osv(_('Warning!'), _('Processed attendance request can not be deleted'))
		#
		return super(AttendanceRequest, self).unlink()

	@api.multi
	def button_first_approve(self):
		for rec in self:
			rec.state = 'second_approve'
			entry = self.env['hiworth.hr.attendance'].search([('name', '=', self.user.employee_id.id), ('date', '=', self.attendance_date)])
			date = datetime.strptime(rec.attendance_date, "%Y-%m-%d")
			if entry:
				if entry.compensatory_off == True:
					leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1,
																	   order='id asc')
					config_employee = self.env['employee.config.leave'].search([('employee_id', '=', self.user.employee_id.id),
																				('leave_id', '=', leave_type.id),
																				])
					if config_employee:
						config_employee.available += 1
					entry.compensatory_off = False
					month_leave = self.env['month.leave.status'].search(
						[('status_id', '=', self.user.employee_id.id), ('month_id', '=', date.month), ('leave_id', '=', leave_type.id)])
					if month_leave:
						month_leave.available += 1
				entry.write({'attendance': self.attendance})
			# raise osv.except_osv(_('Warning!'), _("Already entered attendance for employee '%s'") % (lines.employee_id.name,))

			else:
				self.env['hiworth.hr.attendance'].with_context(default_name=self.user.employee_id.id, default_check=1).create({
					'name': self.user.employee_id.id,
					'attendance': self.attendance,
					'date': self.attendance_date,

				})
			# date = datetime.strptime(rec.attendance_date, "%Y-%m-%d")
			present_work = 0
			if date.weekday() != 6:

				diff = 6 - date.weekday()
				if diff >3 and diff <6:
					diff = date.weekday()
				sunday = date + timedelta(diff)
				from_date = sunday - timedelta(days=6)
				to_date = sunday

				for i in range(6):
					if from_date != to_date:
						attendance = self.env['hiworth.hr.attendance'].search(
							[('date', '=', from_date), ('name', '=', rec.user.employee_id.id)])
						leave = self.env['employee.leave.request'].search(
							[('employee_id', '=', rec.user.employee_id.id), ('date', '=', from_date)])
						if not leave:
							if attendance and attendance.attendance == 'full':

								present_work += 1
							elif attendance and attendance.attendance == 'half':
								present_work += .5
						from_date = from_date + timedelta(days=1)

				if present_work >= 3:
					sunday_att = self.env['hiworth.hr.attendance'].search(
						[('date', '=', sunday), ('name', '=', rec.user.employee_id.id)])
					if sunday_att:
						sunday_att.attendance = 'full'

				else:
					sunday_att = self.env['hiworth.hr.attendance'].search(
						[('date', '=', sunday), ('name', '=', rec.user.employee_id.id)])
					if sunday_att:
						sunday_att.attendance = 'absent'



	@api.multi
	def request_attendance(self):
		for rec in self:
			rec.state = 'first_approve'

	@api.multi
	def button_reject(self):
		for rec in self:
			rec.state = 'rejected'


class PendingRequests(models.Model):
	_name = 'pending.attendance.request'

	date = fields.Date('Requested Date')
	attendance_date = fields.Date('Date of Attendance',default=fields.Date.today())
	# sign_in = fields.Datetime('Sign In')
	# sign_out = fields.Datetime('Sign Out')
	user1 = fields.Many2one('hr.employee','Logged User')
	state = fields.Selection([('pending','Pending'),('approved','Approved')],default="pending")
	attendance = fields.Selection([('full', 'Full Present'),
								('half','Half Present'),
								# ('absent','Absent')
								], default='full', string='Attendance')


	@api.multi
	def approve_attendance(self):
		self.state = 'approved'
		entry = self.env['hiworth.hr.attendance'].search([('name','=',self.user1.id),('date','=',self.date)])

		if len(entry) != 0:
			entry[-1].write({'attendance':self.attendance})
			# raise osv.except_osv(_('Warning!'), _("Already entered attendance for employee '%s'") % (lines.employee_id.name,))

		else:
			self.env['hiworth.hr.attendance'].with_context(default_name=self.user1.id,default_check=1).create({
												  'name':self.user1.id,
												  'attendance':self.attendance,
												  'date':self.attendance_date,

												  })



