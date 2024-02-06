from openerp import models, fields, api, _
from openerp import tools, _
from datetime import datetime, date, timedelta


# Individual Report

class IndividualAttendanceReportWizardNew1(models.TransientModel):
    _name = 'employee.attendance.individual.new1'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    employee_id = fields.Many2one('hr.employee','Employee Name')

    @api.multi
    def action_individual_attendance_open_window1(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Employees Individual Attendance Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_hr_attendance.report_employee_individual_attendance_template1',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    @api.multi
    def get_details_new(self):
        lst = []
        emp_attendance = self.env['hiworth.hr.attendance'].search(
            [('date', '>=', self.date_from), ('date', '<=', self.date_to),('name','=',self.employee_id.id)])
        if emp_attendance :
            for rec in emp_attendance:
                vals ={
                    'employee_id':rec.name,
                    'date':rec.date,
                    'attendance':rec.attendance

                }
                lst.append(vals)
            return lst



