from openerp import models, fields, api, _

class SalaryRuleHistoryWizard(models.TransientModel):
    _name = 'salary.rule.history.wizard'

    @api.model
    def default_get(self, fields_list):
        res = super(SalaryRuleHistoryWizard, self).default_get(fields_list)
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        list_line = []
        admin_line = []
        if active_model == 'hr.salary.rule':
            for active_id in active_ids:
                active_id = self.env['hr.salary.rule'].browse(active_id)
                if active_id.related_type == 'pt':
                    for pt_line in active_id.professional_tax_line_ids:
                        list_line.append((0,0,{'witheffct_date':pt_line.witheffct_date,
                                               'range_from':pt_line.range_from,
                                               'range_to':pt_line.range_to,
                                               'tax_amount':pt_line.tax_amount}))
                    res.update({'salary_rule_history_line_ids': list_line})
                if active_id.related_type == 'pf':
                    for pt_line in active_id.contribution_line_ids:
                        list_line.append((0,0,{'witheffct_date':pt_line.witheffct_date,
                                               'celing_limit':pt_line.celing_limit,
                                               'epf_employee':pt_line.emloyee_ratio,
                                               'epf_employer':pt_line.emloyer_ratio,
                                               'eps_employer':pt_line.emloyer_eps_ratio}))
                    for admin in active_id.admin_charges_line_ids:
                        admin_line.append((0, 0, {'type': admin.type,
                                                 'name': admin.name,
                                                 'amount': admin.amount,
                                                 'witheffct_date': admin.witheffct_date,
                                                 }))


                    res.update({'pf_salary_rule_history_line_ids': list_line,
                                'salary_rule_history_admin_line_ids': admin_line
                                })
                if active_id.related_type == 'esi':
                    for pt_line in active_id.esi_contribution_line_ids:
                        list_line.append((0,0,{'witheffct_date':pt_line.witheffct_date,
                                               'celing_limit':pt_line.celing_limit,
                                               'employee_ratio_esi':pt_line.emloyee_ratio,
                                               'employer_esi':pt_line.emloyer_ratio,
                                              }))

                    res.update({'esi_salary_rule_history_line_ids': list_line,

                                })


                res.update({
                    'related_type':active_id.related_type,
                           })
        return res

    salary_rule_history_line_ids = fields.One2many('salary.rule.history.line','salary_rule_history_id',"Lines")
    pf_salary_rule_history_line_ids = fields.One2many('salary.rule.history.line', 'salary_rule_history_id', "Lines")
    esi_salary_rule_history_line_ids = fields.One2many('salary.rule.history.line', 'salary_rule_history_id', "Lines")
    related_type = fields.Selection([('basic', 'Basic'),
                                     ('canteen', 'canteen'),
                                     ('attendance', 'Attendance'),
                                     ('net', 'Net'),
                                     ('esi', 'ESI'),
                                     ('pf', 'PF'),
                                     ('labour_welfare', 'Labour Welfare'),
                                     ('insurance', 'Insurance'),
                                     ('welfare', 'Welfare Fund'),
                                     ('admin', 'Admin charges'),
                                     ('pt', 'Professional Tax')
                                     ], 'Related Process')
    salary_rule_history_admin_line_ids= fields.One2many('salary.rule.history.line.admin.charge','salary_rule_history_id',"Admin charges")
    @api.multi
    def action_submit(self):

        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        list_line = []
        new_list_line = []
        admin_line = []
        new_admin_line = []
        if active_model == 'hr.salary.rule':
            for active_id in active_ids:
                active_id = self.env['hr.salary.rule'].browse(active_id)
                if active_id.related_type == 'pt':
                    for pt_line in active_id.professional_tax_line_ids:
                        list_line.append((0, 0, {'witheffct_date': pt_line.witheffct_date,
                                                 'range_from': pt_line.range_from,
                                                 'range_to': pt_line.range_to,
                                                 'tax_amount': pt_line.tax_amount}))
                    for acti_line in self.salary_rule_history_line_ids:
                        new_list_line.append((0, 0, {'witheffct_date': acti_line.witheffct_date,
                                                 'range_from': acti_line.range_from,
                                                 'range_to': acti_line.range_to,
                                                 'tax_amount': acti_line.tax_amount}))
                    if active_id.professional_tax_line_ids:
                        active_id.professional_tax_line_ids.unlink()
                        active_id.update({'professional_tax_line_ids': new_list_line})
                    active_id.update({'salary_rule_history_ids': list_line})
                if active_id.related_type == 'pf':
                    for pt_line in active_id.contribution_line_ids:
                        list_line.append((0, 0, {'witheffct_date': pt_line.witheffct_date,
                                                 'celing_limit': pt_line.celing_limit,
                                                 'epf_employee': pt_line.emloyee_ratio,
                                                 'epf_employer': pt_line.emloyer_ratio,
                                                 'eps_employer': pt_line.emloyer_eps_ratio}))
                    for admin in active_id.admin_charges_line_ids:
                        admin_line.append((0, 0, {'type': admin.type,
                                                  'name': admin.name,
                                                  'amount': admin.amount,
                                                  'witheffct_date': admin.witheffct_date,
                                                  }))
                    for acti_line in self.pf_salary_rule_history_line_ids:
                        new_list_line.append((0, 0, {'witheffct_date': acti_line.witheffct_date,
                                                     'celing_limit': acti_line.celing_limit,
                                                     'emloyee_ratio': acti_line.epf_employee,
                                                     'emloyer_ratio': acti_line.epf_employer,
                                                     'emloyer_eps_ratio':acti_line.eps_employer}))

                    for adminn_line in self.salary_rule_history_admin_line_ids:
                        new_admin_line.append((0, 0, {'type': adminn_line.type,
                                                  'name': adminn_line.name,
                                                  'amount': adminn_line.amount,
                                                  'witheffct_date': adminn_line.witheffct_date,
                                                  }))
                    if active_id.contribution_line_ids:
                        active_id.contribution_line_ids.unlink()
                    if active_id.admin_charges_line_ids:
                        active_id.admin_charges_line_ids.unlink()

                    active_id.update({'contribution_line_ids': new_list_line,
                                      'admin_charges_line_ids':new_admin_line})
                    active_id.update({'salary_rule_history_ids': list_line,
                                  'admin_charges_line_history_ids':admin_line})
                if active_id.related_type == 'esi':

                    for esi_line in active_id.esi_contribution_line_ids:
                        list_line.append((0, 0, {'witheffct_date': esi_line.witheffct_date,
                                                 'celing_limit': esi_line.celing_limit,
                                                 'employee_esi': esi_line.emloyee_ratio,
                                                 'employer_esi': esi_line.emloyer_ratio}))
                    for acti__esi_line in self.salary_rule_history_line_ids:
                        new_list_line.append((0, 0, {'witheffct_date': acti__esi_line.witheffct_date,
                                                     'celing_limit': acti__esi_line.celing_limit,
                                                     'emloyee_ratio': acti__esi_line.employee_ratio_esi,
                                                     'emloyer_ratio': acti__esi_line.employer_esi}))
                    if active_id.esi_contribution_line_ids:
                        active_id.esi_contribution_line_ids.unlink()
                    active_id.update({'esi_contribution_line_ids': new_list_line})
                    active_id.update({'salary_rule_history_ids': list_line})


class SalaryRuleHistoryLine(models.TransientModel):
    _name = 'salary.rule.history.line'

    range_from = fields.Float('HALF YEARLY Income Range From')
    range_to = fields.Float('To')
    tax_amount = fields.Float('HALF YEARLY Professional Tax')
    celing_limit = fields.Float("Celing Limit")
    epf_employee = fields.Float("Employee Contribution EPF (%)")
    epf_employer = fields.Float("Employer Contribution EPF(%)")
    eps_employer = fields.Float("Employer Contribution EPS (%)")
    name = fields.Char("Name")
    type = fields.Selection([('per','%'),('lump','Lumpsum')],default='per',string="Type")
    amount = fields.Float("Amount")
    witheffct_date = fields.Date("With Effect From")
    salary_rule_history_id = fields.Many2one('salary.rule.history.wizard')
    employee_ratio_esi = fields.Float("Employee ESI")
    employer_esi = fields.Float("Employer ESI")

class SalaryRuleHistoryLineAdminCharge(models.TransientModel):
    _name = 'salary.rule.history.line.admin.charge'

    type = fields.Selection([('per', '%'), ('lump', 'Lumpsum')], default='per', string="Type")
    name = fields.Char("Name")
    amount = fields.Float("Percentage/Amount")
    witheffct_date = fields.Date("With Effect From")
    salary_rule_history_id = fields.Many2one('salary.rule.history.wizard')