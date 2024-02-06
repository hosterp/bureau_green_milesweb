from openerp import models, fields, api, _
from openerp.osv import osv

class StatutoryPaymentWizard(models.TransientModel):
    _name = 'statutory.payment.wizard'


    @api.model
    def default_get(self, fields_list):
        res = super(StatutoryPaymentWizard, self).default_get(fields_list)
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        if active_model == 'professional.tax':
            for active_id in active_ids:

                pt_record = self.env['professional.tax'].browse(active_id)
                professional_tax = self.env['hr.salary.rule'].search([('related_type', '=', 'pt')], order='id desc',
                                                                     limit=1)
                res.update({'account_id':professional_tax.common_account_id.id,
                            'paid_amount':pt_record.balance,
                            'contract_company_id':pt_record.company_contractor_id.id
                            })
        if active_model == 'hr.esi.payment':
            for active_id in active_ids:

                pt_record = self.env['hr.esi.payment'].browse(active_id)
                professional_tax = self.env['hr.salary.rule'].search([('related_type', '=', 'esi')], order='id desc',
                                                                     limit=1)
                res.update({'account_id':professional_tax.esi_account_id.id,
                            'paid_amount':pt_record.balance,
                            'contract_company_id':pt_record.company_contractor_id.id
                            })
        if active_model == 'pf.payment':
            for active_id in active_ids:

                pt_record = self.env['pf.payment'].browse(active_id)
                professional_tax = self.env['hr.salary.rule'].search([('related_type', '=', 'pf')], order='id desc',
                                                                     limit=1)
                res.update({'eps_account_id':professional_tax.eps_account.id,
                            'admin_charge_account_id':professional_tax.admin_charge_account_id.id,
                            'account_id':professional_tax.epf_account_id.id,
                            'paid_amount':pt_record.balance,
                            'contract_company_id':pt_record.company_contractor_id.id})


        return res

    @api.constrains('payable_amount')
    def check_payable_amount(self):
        for rec in self:
            if rec.payable_amount > rec.paid_amount:
                raise osv.except_osv(_('Warning!'), _("Payable amount should be less than or equal to the amount to be paid"))

    date = fields.Date("Date")
    journal_id = fields.Many2one('account.journal',"Mode of Payment")
    paid_amount = fields.Float("Amount to be Paid")
    payable_amount = fields.Float("Payable Amount")
    account_id = fields.Many2one('account.account',"Account")
    eps_account_id = fields.Many2one('account.account',"EPS Account")
    admin_charge_account_id = fields.Many2one('account.account',"Admin Charges Account")
    contract_company_id = fields.Many2one('res.partner',"Contract Company")


    @api.multi
    def action_submit(self):
        for rec in self:
            active_model = self._context.get('active_model')
            active_ids = self._context.get('active_ids')
            if active_model == 'professional.tax':
                for active_id in active_ids:
                    pt_record = self.env['professional.tax'].browse(active_id)
                    move = self.env['account.move']
                    move_line = self.env['account.move.line']

                    move_id = move.create({
                        'journal_id': rec.journal_id.id,
                        'date': rec.date,
                    })

                    line_id = move_line.create({
                        'account_id': rec.journal_id.default_credit_account_id.id,
                        'name': 'Professional Tax Amount',
                        'credit': rec.payable_amount,
                        'debit': 0,
                        'move_id': move_id.id,
                    })

                    line_id = move_line.create({
                        'account_id': rec.account_id.id,
                        'name': 'Professional Tax Amount',
                        'credit': 0,
                        'debit': rec.payable_amount,
                        'move_id': move_id.id,
                    })
                    move_id.button_validate()
                    pt_record.paid_amount = pt_record.paid_amount + rec.payable_amount
            if active_model == 'hr.esi.payment':
                for active_id in active_ids:
                    pt_record = self.env['hr.esi.payment'].browse(active_id)
                    move = self.env['account.move']
                    move_line = self.env['account.move.line']

                    move_id = move.create({
                        'journal_id': rec.journal_id.id,
                        'date': rec.date,
                    })

                    line_id = move_line.create({
                        'account_id': rec.journal_id.default_credit_account_id.id,
                        'name': 'ESI Amount',
                        'credit': rec.payable_amount,
                        'debit': 0,
                        'move_id': move_id.id,
                    })

                    line_id = move_line.create({
                        'account_id': rec.account_id.id,
                        'name': 'ESI Amount',
                        'credit': 0,
                        'debit': rec.payable_amount,
                        'move_id': move_id.id,
                    })
                    move_id.button_validate()
                    pt_record.paid_amount = pt_record.paid_amount + rec.payable_amount
            if active_model == 'pf.payment':
                for active_id in active_ids:
                    pt_record = self.env['pf.payment'].browse(active_id)
                    move = self.env['account.move']
                    move_line = self.env['account.move.line']

                    move_id = move.create({
                        'journal_id': rec.journal_id.id,
                        'date': rec.date,
                    })

                    line_id = move_line.create({
                        'account_id': rec.journal_id.default_credit_account_id.id,
                        'name': 'ESI Amount',
                        'credit': rec.payable_amount,
                        'debit': 0,
                        'move_id': move_id.id,
                    })

                    line_id = move_line.create({
                        'account_id': rec.account_id.id,
                        'name': 'ESI Amount',
                        'credit': 0,
                        'debit': rec.payable_amount,
                        'move_id': move_id.id,
                    })
                    move_id.button_validate()
                    pt_record.paid_amount = pt_record.paid_amount + rec.payable_amount
        return True



