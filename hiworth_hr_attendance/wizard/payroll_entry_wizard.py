from openerp import models, fields, api, _

class PayrollEntryWizard(models.TransientModel):
    _name = 'payroll.entry.wizard'


    @api.model
    def default_get(self, fields_list):
        res = super(PayrollEntryWizard, self).default_get(fields_list)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        employee_list = []
        if active_model == 'hr.employee':
            for active_id in active_ids:
                active = self.env['hr.contract'].search([('employee_id','=',active_id),
                                                         ('state','=','active')])

                employee_list.append((0,0,{'employee_id':active_id}))



        res.update({'payroll_entry_wizard_line_ids':employee_list})
        return res

    payroll_entry_wizard_line_ids = fields.One2many('payroll.entry.wizard.line','payroll_entry_wizard_id',"Payroll Lines")
    date_from = fields.Date("Date From")
    date_to = fields.Date("Date To")


    @api.onchange('date_from','date_to')
    def onchange_date_from_date_to(self):
        for rec in self:

            rule_list = []
            basic_rule = self.env['hr.salary.rule'].search([('related_type', '=', 'basic')], limit=1)
            attend_rule = self.env['hr.salary.rule'].search([('related_type', '=', 'attendance')], limit=1)
            print "tttttttttttttttttttttttttttttttttttttttttttttttt", basic_rule, attend_rule
            for emp in rec.payroll_entry_wizard_line_ids:
                rule_list = []
                contract_emp = self.env['hr.contract'].search([('employee_id','=',emp.employee_id.id),('state','=','active')])
                for rule in contract_emp.rule_lines:
                    if basic_rule.id == rule.rule_id.id:
                        print "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhurururururururururu"
                        rule_list.append((0, 0, {'name': rule.rule_id.name,
                                                 'code': rule.rule_id.code,
                                                 'category_id': rule.rule_id.category_id.id,
                                                 'amount': contract_emp.wage,
                                                 }))
                    if attend_rule.id == rule.rule_id.id:
                        #     (emp.get_present_days(emp.id, inv[0].from_date, inv[0].to_date) + emp.get_sunday(emp.id, inv[
                        #         0].from_date, inv[0].to_date))
                        attendance = self.env['hr.employee'].get_present_days(active_id, inv[0].from_date,
                                                                              inv[0].to_date)
                    #     rule_list.append((0, 0, {'name': rule.rule_id.name,
                    #                              'code': rule.rule_id.code,
                    #                              'category_id': rule.rule_id.category_id.id,
                    #
                    #                              'amount': active.wage,
                    #                              }))
                print "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",rule_list
                emp.payroll_entry_wizard_line_salary_ids = rule_list
                print "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",emp.payroll_entry_wizard_line_salary_ids
        print "ppppppppppppppppppppppppppppppppppp"


class PayrollEntryWizardLine(models.TransientModel):
    _name= 'payroll.entry.wizard.line'

    employee_id = fields.Many2one('hr.employee',"Employee")
    salary_rule_ids = fields.Many2many('hr.salary.rule',"Salary Rules")
    payroll_entry_wizard_id = fields.Many2one('payroll.entry.wizard')
    payroll_entry_wizard_line_salary_ids = fields.One2many('payroll.entry.wizard.line.salary','payroll_entry_wizard_line_id',"Lines ")

    @api.multi
    def view_deduction_summary(self):

        return {
                'name': 'Payroll',
                'view_type': 'form',
                'view_mode': 'form',
                'target':'new',
                'res_model': 'payroll.entry.wizard.line.salary',
                'view_id': 'payroll_entry_form_wizard_line',
                'type': 'ir.actions.act_window',
                 'domain':[('payroll_entry_wizard_line_id','=',rec.id)]


            }


class PayrollEntryWizardLineSalary(models.TransientModel):
    _name= 'payroll.entry.wizard.line.salary'

    @api.depends('amount','quantity')
    def compute_total(self):
        for rec in self:
            rec.total = rec.amount * rec.quantity


    name = fields.Char("Name")
    code = fields.Char("Code")
    category_id = fields.Many2one('hr.salary.rule.category',"Category")
    quantity = fields.Float("Quantity")
    amount = fields.Float("Amount")
    total = fields.Float("Total",compute='compute_total')
    payroll_entry_wizard_line_id = fields.Many2one('payroll.entry.wizard.line',)




