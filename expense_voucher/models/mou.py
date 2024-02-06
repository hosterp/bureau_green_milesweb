from openerp import fields, models, api
from datetime import datetime
from openerp.exceptions import except_orm
from openerp.tools.translate import _

class Mou(models.Model):
    _name = 'mou.mou'
    _order = 'name desc'

    @api.model
    def create(self, vals):
       if vals.get('name', '/') == '/':
           vals['name'] = self.env['ir.sequence'].get('mou.sequence')+'/'+str(datetime.now().date().year) or '/'
        
       return super(Mou, self).create(vals)
   
   
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        address_list = []
        for mou in self:
            if mou.partner_id:
                if mou.partner_id.street:
                    address_list.append(mou.partner_id.street)
                if mou.partner_id.street2:
                    address_list.append(mou.partner_id.street2)
                if mou.partner_id.city:
                    address_list.append(mou.partner_id.city)
                if mou.partner_id.state_id:
                    address_list.append(mou.partner_id.state_id.name)
                if mou.partner_id.country_id:
                    address_list.append(mou.partner_id.country_id.name)

            address = ','.join(address_list)
            mou.address = address
            mou.account_name = mou.partner_id.account_name
            mou.bank_name = mou.partner_id.bank_name
            mou.ifsc_code = mou.partner_id.ifsc_code
            mou.gst_account = mou.partner_id.gst_account
            mou.branch = mou.partner_id.branch
            mou.gst_no = mou.partner_id.gst_no
            mou.pan = mou.partner_id.pan_no
            mou.acc_no = mou.partner_id.acc_no
#             return {'value':{'address':address}}


    @api.depends('cost','bata')
    def compute_total(self):
        for record in self:
           record.total = record.cost + record.bata
    
    name = fields.Char(string="MOU No.", copy=False)
    partner_id = fields.Many2one('res.partner', string="Name of Supplier/Owner", required=True, domain="['|','|',('other_mou_supplier','=', True),('is_rent_vehicle','=', True), ('is_rent_mach_owner','=', True)]")
    address = fields.Text(string="Address")
    agreement_date = fields.Date(string="Agreement Date", required=True)
    cost = fields.Float(string="Agreement Cost", )
    unit_of_meassure = fields.Many2one('mou.unit', 'Payment Unit', required=True)
    bata = fields.Float(string="Bata")
    starting_date = fields.Date(string="Start Date", required=True)
    finishing_date = fields.Date(string="End Date")
    amount = fields.Float(string="Amount")
    mode_of_payment = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], string="Mode of Payment")
    date_of_payment = fields.Date(string="Date of Payment")
    pan = fields.Char(string="PAN")
    gst_account= fields.Char(string="GST Account Name")
    gst_no = fields.Char(string="GST No.")
    account_name = fields.Char(string="Account Name")
    bank_name = fields.Char(string="Bank Name")
    branch = fields.Char(string="Branch")
    acc_no = fields.Char(string="A/C No.")
    ifsc_code = fields.Char(string="IFSC Code")
    site = fields.Many2one('stock.location', 'Site', required=True)
    supervisor = fields.Many2one('hr.employee', string="Supervisor", domain="[('user_category', 'in', ['supervisor','admin','interlocks','cheif_acc','sen_acc','jun_acc'])]", required=True)
    category_id = fields.Many2one('mou.category', string="Category", required=True)
    contractor_id = fields.Many2one('res.partner', string="Contractor",domain="[('company_contractor','=',True)]")
    type = fields.Many2one('vehicle.category.type', 'Vehicle Type', related='vehicle_number.vehicle_categ_id')
    vehicle_number = fields.Many2many('fleet.vehicle', string="Vehicle", domain="['|',('is_rent_mach', '=', True), ('rent_vehicle', '=', True)]")
    land_area = fields.Char(string="Land Area")
    with_operator = fields.Boolean(string="With Operator")
    total = fields.Float(string="Total", compute='compute_total', store=True)
    company_id = fields.Many2one('res.company', string="Company")
    terminate_date = fields.Date("Termination Date")
    active = fields.Boolean("Active",default=True)
    full_supply = fields.Boolean(default=False, string="Full Supply")
    full_supply_line = fields.One2many('fullsupply.line', 'mou_id')
    rate_per_km = fields.Float('Rate Per Km')
    per_day_rent = fields.Float('Rent Per Day')
    capacity = fields.Float('Capacity')
    state = fields.Selection([('draft','Draft'),
                              ('approved', 'Approved'),
                              ('rejected', 'Terminated')],default="draft", string="Status")
    
    mou_attach = fields.Binary("MOU Attachment")
    agreement_rate_details = fields.Text("Agreement Rate")
    bata_details = fields.Text("Bata")
    approved_by = fields.Many2one('res.users',"Approved By")
    detail = fields.Boolean("Detailed")
    bata_detail = fields.Boolean("Detailed")
    security_payment_mou = fields.Boolean("Security Payment Needed")
    other_conditions = fields.Boolean("Other Conditions")


    _defaults = {
        'name': lambda obj, cr, uid, context: '/',
    }

    @api.multi
    def get_vehicle_no(self):
        for rec in self:
            vehicle_name = ''
            for veh in rec.vehicle_number:
                vehicle_name = vehicle_name + veh.name + ','
            return vehicle_name
    
    
    @api.multi
    def action_approve(self):
        for mou in self:
            if not mou.mou_attach:
                raise except_orm(_('Warning'),
                                 _('Please Attach MOU Document'))

            mou.write({'state': 'approved',
                       'approved_by':self.env.user.id})
            
    @api.multi
    def action_reject(self):
        for mou in self:
            mou.active = False
            mou.terminate_date = datetime.now()
            mou.write({'state':'rejected'})

    @api.multi
    def action_reset(self):
        for rec in self:
            rec.active=True
            rec.state = 'draft'
            rec.terminate_date = False


    @api.multi
    def action_open_contract(self):
        return {
            'name': 'MOU Contract',
            'view_type': 'form',
            'view_mode': 'tree,form',

            'res_model': 'mou.contract',

            'type': 'ir.actions.act_window',
            #             'account_id':self.id,
            'domain':[('mou_id','=',self.id)],
            'context': {'default_mou_id': self.id,
                        'default_mou_category_id':self.category_id.id,
                        'default_partner_id':self.partner_id.id,
                        'default_contractor_id':self.contractor_id.id,
                        'default_amount':self.cost,
                        'default_start_date':self.starting_date,
                        'default_expiration_date':self.finishing_date
                        },
        }
            
            
class MouCategory(models.Model):
    _name = 'mou.category'
    _rec_name = "name"

    name = fields.Char(string="Name")  

class MouUnit(models.Model):

    _name = "mou.unit"
    _rec_name = "name"

    name = fields.Char('Name')
    code = fields.Char('Code')

class ResPartner(models.Model):

    _inherit = "res.partner"

    other_mou_supplier = fields.Boolean('Other MOU Supplier/Owner')
    mou_contractor = fields.Boolean('MOU Contractor')
    tds_not_appicable = fields.Boolean("TDS Not Applicable")
    gst_account = fields.Char(string="GST Account Name")
    account_name1 = fields.Char(string="Account Number")
    account_name2 = fields.Char(string="Account Number")
    account_name3 = fields.Char(string="Account Number")
    i_ban_no1 = fields.Char(string="I Ban Number")
    i_ban_no2 = fields.Char(string="I Ban Number")
    i_ban_no3 = fields.Char(string="I Ban Number")
    bank_name1 = fields.Char(string="Bank Name")
    bank_name2 = fields.Char(string="Bank Name")
    bank_name3 = fields.Char(string="Bank Name")
    branch1 = fields.Char(string="Branch")
    branch2 = fields.Char(string="Branch")
    branch3 = fields.Char(string="Branch")
    acc_no = fields.Char(string="A/C No.")
    ifsc_code1 = fields.Char(string="IFSC Code")
    ifsc_code2 = fields.Char(string="IFSC Code")
    ifsc_code3 = fields.Char(string="IFSC Code")
    phone2 = fields.Char(string="Phone2")
    fax1 = fields.Char(string="Fax1")
    fax2 = fields.Char(string="Fax2")
    email2 = fields.Char(string="Email2")
    vat = fields.Char(string="VAT Number")
    co_tax_no = fields.Char(string="Cooperate Tax Number")



    # def create(self,vals):
    #     res = super(ResPartner, self).create(vals)
    #     if res.contractor or res.other_mou_supplier or res.is_rent_mach_owner or res.supplier:
    #         if not res.tds_applicable and not res.gst_no and not res.tds_not_appicable:
    #             raise except_orm(_('Warning'),
    #                              _('Please Fill the three Fields.'
    #                                '1.TDS Applicable'
    #                                '2. TDS Not Applicable'
    #                                '3. GST No'))
    #
    #     return res

    @api.multi
    def action_show_mou(self):

        view_tree = self.env.ref('expense_voucher.view_mou_tree')
        view_form = self.env.ref('expense_voucher.view_mou_form')
        return {
            'name': 'Related MOU Details',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mou.mou',
            'views': [(view_tree.id, 'tree'), (view_form.id, 'form')],
            'target': 'current',
            'domain': [('partner_id', '=', self.id)],
        }

