from openerp import models, fields, api, _
from openerp import tools, _
from datetime import datetime,timedelta


class ESIReport(models.Model):
    _name = 'esi.wizard'

    month = fields.Selection([('January', 'January'),
                              ('February', 'February'),
                              ('March', 'March'),
                              ('April', 'April'),
                              ('May', 'May'),
                              ('June', 'June'),
                              ('July', 'July'),
                              ('August', 'August'),
                              ('September', 'September'),
                              ('October', 'October'),
                              ('November', 'November'),
                              ('December', 'December')], 'Month')

    year = fields.Selection([(num, str(num)) for num in range(1900, 2080)], 'Year', default=(datetime.now().year))
    contract_company_id = fields.Many2one('res.partner',"Contract Company",domain="[('company_contractor','=',True)]")


    @api.multi
    def action_employee_pf_esi_open_window(self):
        print
        'a------------------------------------------------'

        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Employee Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_hr_attendance.report_employee_esi_template',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    @api.multi
    def action_employee_pf_esi_open_window1(self):
        print
        'b------------------------------------------------'

        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Employee Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_hr_attendance.report_employee_esi_template',
            'datas': datas,
            'report_type': 'qweb-html'
        }

    @api.multi
    def get_esi_pf_details(self):

        list = []
        basic = 0
        attendance = 0
        wages_due = 0
        employee_amount = 0
        employer_amount = 0
        pf_wages = 0
        edli = 0
        employer_epf = 0
        employee_epf = 0
        employer_eps = 0

        domain = []
        domain.append(('month', '=', self.month))
        domain.append(('year', '=', self.year))
        if self.contract_company_id:
            domain.append(('company_contractor_id', '=', self.contract_company_id.id))
        esi = self.env['hr.esi.payment'].search(domain)
        for empl_id in esi:

           for esi_line in empl_id.line_ids:
                    basic = esi_line.basic
                    attendance = esi_line.attendance
                    wages_due = esi_line.wages_due
                    employee_amount = esi_line.employee_amount
                    employer_amount = esi_line.employer_amount
                    list.append({
                        'employee_name': esi_line.employee_id.name,
                        'basic_pay': basic,
                        'attendance': attendance,
                        'wages_due': wages_due,
                        'employee_esi': employee_amount,
                        'employer_esi': employer_amount,
                        'pf_wages': pf_wages,
                        'edli': edli,
                        'employer_epf': employer_epf,
                        'employee_epf': employee_epf,
                        'eps': employer_eps,
                    })






        return list

    @api.multi
    def get_final_amount(self):

        list = []
        esi_employee_amount = 0
        esi_employer_amount = 0
        esi_amount_total = 0
        pf_employee_amount = 0
        pf_employer_amount = 0
        eps_amount = 0
        edli_amount = 0
        admin_amount = 0
        pf_amount_total = 0

        esi = self.env['hr.esi.payment'].search([('month', '=', self.month), ('year', '=', self.year)], limit=1)
        esi_employee_amount = esi.employee_amount
        esi_employer_amount = esi.employer_amount
        esi_amount_total = esi.amount_total

        pf = self.env['pf.payment'].search([('month', '=', self.month), ('year', '=', self.year)], limit=1)
        pf_employee_amount = pf.employee_amount
        pf_employer_amount = pf.employer_amount
        eps_amount = pf.eps_amount
        admin_amount = pf.admin_amount
        pf_amount_total = pf.amount_total
        list.append({
            'employee_esi': esi_employee_amount,
            'employer_esi': esi_employer_amount,
            'net_esi': esi_amount_total,
            'employee_epf': pf_employee_amount,
            'employer_epf': pf_employer_amount,
            'employer_eps': eps_amount,
            'edli': edli_amount,
            'admin_charge': admin_amount,
            'net_epf': pf_amount_total,
        })

        return list

    @api.multi
    def get_head(self):

        list = []
        esi_rule = self.env['hr.salary.rule'].search([('related_type', '=', 'esi')])
        pf_rule = self.env['hr.salary.rule'].search([('related_type', '=', 'pf')])
        for line in esi_rule.esi_contribution_line_ids:
            list.append({

                'employer_esi': line.emloyer_ratio,
                'employee_esi': line.emloyee_ratio,
            })

        return list
