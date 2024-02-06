from openerp import models, fields, api, _

class InsuranceRenewalWizard(models.TransientModel):
    _name = 'insurance.renewal.wizard'

    @api.model
    def default_get(self, fields_list):
        res = super(InsuranceRenewalWizard, self).default_get(fields_list)
        if self._context.get('active_model') == 'employee.insurance':
            res.update({'employee_insurance_ids':[(6,0,self._context.get('active_ids'))]})
        return res

    employee_insurance_ids = fields.Many2many('employee.insurance','employee_insurance_wizard_rel','employee_insurance_id','insurance_wizard_id',string="Employee insurances")

    @api.multi
    def action_submit(self):
        for rec in self:
            for insurance in rec.employee_insurance_ids:
                insurance.view_renewal()