from openerp import fields, models, api
from datetime import datetime,timedelta
from dateutil.relativedelta import *
from openerp.exceptions import except_orm
from openerp.tools.translate import _

class MouContract(models.Model):
    _name = 'mou.contract'
    _order = 'id desc'

    @api.model
    def create(self,vals):
        res = super(MouContract, self).create(vals)
        res.mou_id.cost = res.amount
        res.mou_id.starting_date = res.start_date
        res.mou_id.finishing_date = res.expiration_date
        return res

    mou_id = fields.Many2one('mou.mou',"Mou")
    mou_category_id = fields.Many2one('mou.category',"Category")
    start_date = fields.Date("Contract Start Date")
    expiration_date = fields.Date("Contract End Date")
    amount = fields.Float("Agreement Amount")
    partner_id = fields.Many2one('res.partner',"Name of Supplier/Owner")
    contractor_id = fields.Many2one('res.partner',string="Contractor",domain="[('company_contractor','=',True)]")
    contract_ref = fields.Char("Contractor Reference")
    terms_cond = fields.Text("Terms and Conditions")
    state = fields.Selection([('open',"In Progress"),
                              ('toclose',"To Close"),
                              ('terminate',"Terminated")],default='open',string="Status")

    @api.multi
    def contract_close(self):
        for rec in self:
            rec.state = 'terminate'

    @api.multi
    def contract_renew(self):
        for rec in self:
            today_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d"),"%Y-%m-%d")
            date = datetime.strptime(rec.expiration_date,"%Y-%m-%d")
            diff_date = date - today_date
            if diff_date.days <15:
                rec.state = 'terminate'
                return {
                    'name': 'MOU Contract',
                    'view_type': 'form',
                    'view_mode': 'tree,form',

                    'res_model': 'mou.contract',

                    'type': 'ir.actions.act_window',
                    #             'account_id':self.id,
                    'domain': [('mou_id', '=', self.mou_id.id)],
                    'context': {'default_mou_id': self.mou_id.id,
                                'default_mou_category_id': self.mou_category_id.id,
                                'default_partner_id': self.partner_id.id,
                                'default_contractor_id': self.contractor_id.id,
                                'default_amount': self.amount,
                                'default_start_date': date + timedelta(days=1),
                                'default_expiration_date': date + timedelta(days=1) + relativedelta(years=+1)
                                },
                }



            else:
                raise except_orm(_('Warning'),
                                 _("You can't renew a contract which is in force."
                                   " Advance renewal could be done 15 days before the contract expiry date"))
