from openerp import fields, models, api
from lxml import etree
from datetime import datetime

class TyreModel(models.Model):
    _name = 'tyre.model'

    name=fields.Char("Name")

class TyrePosition(models.Model):
    _name='tyre.position'

    name=fields.Char("Name")

class TyreManufactuer(models.Model):
    _name = 'tyre.manufactuer'

    name=fields.Char("Name")

class TyreType(models.Model):
    _name = 'tyre.type'

    name=fields.Char("Name")

class RetreadingType(models.Model):
    _name = 'retreading.type'

    name=fields.Char("Name")



class VehicleTyre(models.Model):
    _name = 'vehicle.tyre'

    @api.model
    def create(self, vals):
        res = super(VehicleTyre, self).create(vals)
        if self._context.get('goods_receive_line'):

            self.env['goods.recieve.report.line'].browse(self._context.get('goods_receive_line')).tyre_id = res.id

        # retrading = self.env['retreading.tyre.line'].create({'vehicle_id':res.vehicle_id.id,
        #                                                      'manufacture_id':res.manufacture_id.id,
        #                                                      'retrading_cost':res.tyre_cost,
        #                                                      'purchase_km':res.purchase_mileage,
        #                                                      'tyre_id':res.id,
        #                                                      'purchase_type':res.purchase_type,
        #                                                      'retreading_date':res.purchase_date})
        return res

    @api.depends('retreading_ids')
    def compute_cum_km(self):
        cum_km = 0
        for record in self:
            for line in record.retreading_ids:
                if line.total_km >=0:
                    cum_km += line.total_km
            record.cum_km = cum_km

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(VehicleTyre, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'form':
            # Check if user is in group that allow creation
            doc = etree.XML(res['arch'])
            has_my_group = self.env.user.has_group('base.group_erp_manager')
            if has_my_group:
                if has_my_group:
                    root = etree.fromstring(res['arch'])
                    root.set('edit', 'true')
            res['arch'] = etree.tostring(root)
        return res

    @api.onchange('warranty_km','purchase_mileage')
    def onchange_warranty_km(self):
        for rec in self:
            rec.tread_warning = rec.warranty_km + rec.purchase_mileage

    name = fields.Char("Tyre ID/SN")
    purchase_type = fields.Selection([('new','New'),('secondary','Secondary')],"Purchase Type")
    purchase_date = fields.Datetime("Purchase Date")
    tyre_model_id = fields.Many2one('tyre.model',"Tyre Model")
    supplier = fields.Many2one('res.partner',"Supplier",domain="[('supplier','=',True)]")
    tyre_cost = fields.Float("Tyre Cost")
    projected_life = fields.Float("Projected Life (KM)")
    warranty_period=fields.Datetime("Warranty Period")
    warranty_km =fields.Float("Warranty KM")
    manufacture_id = fields.Many2one('tyre.manufactuer',"Tyre Manufactuer")
    tyre_type_id = fields.Many2one('tyre.type',"Tyre Type")
    purchase_mileage = fields.Float("Purchased @KM")
    position_id = fields.Many2one('tyre.position',"Tyre Position")
    is_remouldable = fields.Boolean("Is Remouldable")
    tread_warning=fields.Float("Tread/Retread Warning At Kms")
    # odometer_reading = fields.Float("Odometer Reading at Tyre Mount")
    vehicle_id = fields.Many2one('fleet.vehicle',"Vehicle")
    active = fields.Boolean("Active",default=True)
    cum_km = fields.Float("Cumulative KM",compute='compute_cum_km',store=True)
    retreading_ids = fields.One2many('retreading.tyre.line','tyre_id',"Tyre Retreading")
    start_odometer = fields.Float(string='Odometer')
    end_odometer = fields.Float(string="Last Odometer")

    _sql_constraints = [('name', 'unique(name)', 'Tyre Name Already Exists')]

    @api.multi
    def action_done(self):
        for rec in self:
            retreaing = self.env['retreading.tyre.line'].search([('tyre_id','=',rec.id)],limit=1,order='id desc')
            return {
                'name': 'Tyre Disposal',
                'view_type': 'form',
                'view_mode': 'form',

                'res_model': 'dispose.tyre',

                'type': 'ir.actions.act_window',
                'context': {'default_vehicle_id': rec.vehicle_id.id,
                            'default_tyre_id': rec.id,
                            'default_retreading_date': retreaing.retreading_date,
                            'default_retreading_km': retreaing.removing_km,
                            'default_total_km': rec.cum_km}

            }


class RetreadingTyreLine(models.Model):
    _name = 'retreading.tyre.line'

    @api.depends('vehicle_id')
    def compute_purchase_km(self):
        for rec in self:
            retreading = self.env['retreading.tyre.line'].search(
                [('retreading_date', '<', rec.retreading_date), ('tyre_id', '=', rec.tyre_id.id),
                 ('vehicle_id', '=', rec.vehicle_id.id)], order='id desc', limit=1)
            if retreading:
                 rec.retreading_km= rec.vehicle_id.odometer


    @api.depends('retreading_km','removing_km')
    def compute_total_km(self):
        for rec in self:
            retreading = self.env['retreading.tyre.line'].search([('retreading_date','<',rec.retreading_date),('tyre_id','=',rec.tyre_id.id),('vehicle_id','=',rec.vehicle_id.id)],order='id desc',limit=1)
            cum_retreading = self.env['retreading.tyre.line'].search([('retreading_date','<',rec.retreading_date),('tyre_id','=',rec.tyre_id.id)],order='id desc',limit=1)
            if retreading:
                if rec.removing_km >0:
                    rec.total_km =  rec.removing_km - rec.retreading_km
                    rec.cum_km = cum_retreading.cum_km + rec.total_km
          
            if not retreading:
                if rec.removing_km>0:
                    rec.total_km = rec.removing_km - rec.purchase_km
                    rec.cum_km = cum_retreading.cum_km + rec.total_km

    @api.model
    def create(self, vals):
        res = super(RetreadingTyreLine, self).create(vals)
        if self._context.get('goods_receive_line'):
            self.env['goods.recieve.report.line'].browse(self._context.get('goods_receive_line')).retread_tyre_id = res.id
        res.tyre_id.vehicle_id = res.vehicle_id.id
        return res

    # retreading_id = fields.Many2one('retreading.tyre')
    tyre_id = fields.Many2one('vehicle.tyre',"Tyre")
    manufacture_id = fields.Many2one('tyre.manufactuer', "Tyre Manufactuer")
    tyre_retrading_type = fields.Many2one('retreading.type',"Retreading Type")
    retreading_date = fields.Datetime("Retreading/Purchase Date")
    purchase_type = fields.Selection([('new', 'New'), ('secondary', 'Secondary')], "Purchase Type")
    estimated_life = fields.Float("Estimated Life ")
    retrading_cost = fields.Float("Purchase/Retreading Cost")
    retreading_km = fields.Float("Fitting/Refitting at KM")
    total_km= fields.Float("Total Mileage(KM) ",compute='compute_total_km')
    cum_km = fields.Float("Cum Mileage(KM)",compute='compute_total_km',store=True)
    tyre_name_id = fields.Many2one('retreading.tyre.name',"d")
    cum_km_2 = fields.Float('for exchange calc')
    vehicle_id = fields.Many2one('fleet.vehicle',"Vehicle")
    removing_km = fields.Float("Removing/Retrading KM")
    purchase_km = fields.Float("Purchase@KM")
    start_odometer = fields.Float(string='Odometer')
    end_odometer = fields.Float(string="Last Odometer")
    position_id = fields.Many2one('tyre.position', "Tyre Position", )


class RetreadingTyreName(models.Model):
    _name= 'retreading.tyre.name'

    @api.onchange('name')
    def onchange_name_id(self):
        tyre_list = []
        for rec in self:
            if rec.name:

                if not rec.retreading_ids:
                    retreading = self.env['retreading.tyre.line'].search(
                    [('tyre_id', '=', rec.name.id)],
                    order='id desc').ids

                    rec.retreading_ids = [(6, 0, retreading)]
            if self._context.get('vehicle_id'):

                mounting_tyre = self.env['vehicle.tyre'].search([('vehicle_id', '=', self._context.get('vehicle_id'))])
                for mount in mounting_tyre:
                    tyre_list.append(mount.id)

        return {'domain':{'name':[('id','in',tyre_list)]}}


    @api.one
    def compute_retread(self):
        for rec in self:
            rec.no_of_retread = len(rec.retreading_ids)

    name = fields.Many2one('vehicle.tyre', "Tyre")
    no_of_retread = fields.Float('No of Retreading',compute='compute_retread')
    retreading_ids = fields.One2many('retreading.tyre.line', 'tyre_name_id')
    retreading_tyre_id = fields.Many2one('retreading.tyre',"Retreading Tyre")

    _sql_constraints = [('name', 'unique(name)', 'Tyre Name Already Selected')]


class RetreadingTyre(models.Model):
    _name = 'retreading.tyre'
    _rec_name='vehicle_id'


    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        for rec in self:
            if rec.vehicle_id:

                tyre_list=[]
                mounting_tyre = self.env['vehicle.tyre'].search([('vehicle_id','=',rec.vehicle_id.id)])
                retreading=[]
                for mount in mounting_tyre:


                    retreading = self.env['retreading.tyre.line'].search(
                        [('tyre_id', '=', mount.id)],
                        order='id desc').ids

                    rec.retreading_tyre_name_ids = [(0,0,{'name':mount.id,
                                                                 'retreading_tyre_id':rec.id,
                                                              'retreading_ids'  :[(6,0,retreading)]})]


    vehicle_id = fields.Many2one('fleet.vehicle',"Vehicle")
    retreading_tyre_name_ids = fields.One2many('retreading.tyre.name','retreading_tyre_id')
    # comput_fields = fields.Float(compute='compute_field_line')


    _sql_constraints = [('name', 'unique(name)', 'Vehicle Name Already Exist')]







class MountingTyre(models.Model):
    _name = 'mounting.tyre'






    @api.onchange('name')
    def onchange_tyre(self):
        for rec in self:
            if rec.name:
                rec.cum_km = rec.name.cum_km
             
  
    name = fields.Many2one('vehicle.tyre', "Tyre ID/SN")
    cum_km = fields.Float('Cumiliative Kilometer')
    position_id = fields.Many2one('tyre.position', "Tyre Position", )
    manufacture_id = fields.Many2one('tyre.manufactuer', "Tyre Manufactuer")
    tyre_model_id = fields.Many2one('tyre.model', "Tyre Model")
    tyre_type_id = fields.Many2one('tyre.type', "Tyre Type")
    purchase_type = fields.Selection([('new', 'New'), ('secondary', 'Secondary')], "Purchase Type")
    vehicle_mount_id = fields.Many2one('vehicle.mount',"Vehicle Mount")
    refit_km = fields.Float('Refitting /Exchange KM')


class VehicleMountingTyre(models.Model):
    _name = 'vehicle.mount'





    vehicle_id = fields.Many2one('fleet.vehicle',"From Vehicle")
    to_vehicle_id = fields.Many2one('fleet.vehicle',"To Vehicle")
    exchange_date = fields.Date("Refitting/Exchange Date")
    mounting_tyre_ids = fields.One2many('mounting.tyre','vehicle_mount_id',"Tyre Details")
    refit_km = fields.Float('Refitting /Exchange KM')
    

class WarrantyTyre(models.Model):
    _name='warranty.tyre'

    @api.onchange('tyre_id')
    def onchange_tyre_id(self):
        for rec in self:
            rec.tyre_type_id = rec.tyre_id.tyre_type_id.id
            rec.amount= rec.tyre_id.tyre_cost
            rec.manufacture_id = rec.tyre_id.manufacture_id.id
            rec.insurer_id = rec.tyre_id.supplier.id
            rec.vehicle_id = rec.tyre_id.vehicle_id.id
            rec.closing_km = rec.tyre_id.cum_km

    @api.model
    def create(self,vals):
        res = super(WarrantyTyre, self).create(vals)


        self.env['dispose.tyre'].create({'tyre_id':res.tyre_id.id,
                                         'vehicle_id':res.vehicle_id.id,
                                         'retreading_date':datetime.now(),
                                         'total_km':res.tyre_id.cum_km,
                                         'retreading_km':res.tyre_id.vehicle_id.odometer})

        return res

    date = fields.Date("Claim submission date")
    tyre_id = fields.Many2one('vehicle.tyre',"Tyre ID/SN")
    tyre_type_id = fields.Many2one('tyre.type', "Tyre Type")
    amount = fields.Float("Claim Amount")
    claim_date = fields.Date("Claim Date")
    manufacture_id = fields.Many2one('tyre.manufactuer', "Tyre Manufactuer")
    insurer_id = fields.Many2one('res.partner',"Supplier",domain="[('is_insurer','=',True)]")
    is_account_entry = fields.Boolean("Claim approved")
    journal_id = fields.Many2one('account.journal',"Mode of Payment")
    account_id = fields.Many2one('account.account',"Debit Account")
    state = fields.Selection([('draft','Draft'),
                              ('paid','Paid')],default='draft',string="State")
    claim_rec_date= fields.Date("Claim Recived Date")
    amount_appr = fields.Float("Approved Amount")
    ref_det = fields.Char("Reference Details")
    vehicle_id = fields.Many2one('fleet.vehicle',"Vehicle")
    closing_km = fields.Float("Closing KM")
    not_approved = fields.Boolean("Claim Not Approved")


    @api.multi
    def action_done(self):
        for rec in self:

            tyre = self.env['dispose.tyre'].search([('tyre_id','=',rec.tyre_id.id)])
            if rec.is_account_entry:
                tyre.status = 'Claim Approved'
            if rec.not_approved:
                tyre.status = 'Claim Not Approved'


class DisposeTyre(models.Model):
    _name = 'dispose.tyre'



    @api.model
    def create(self,vals):
        res = super(DisposeTyre, self).create(vals)
        res.tyre_id.active = False;
        return res

    @api.multi
    def unlink(self):
        self.tyre_id.active = True
        res = super(DisposeTyre, self).unlink()

        return res

    retreading_date = fields.Datetime("Disposed Date")
    vehicle_id = fields.Many2one('fleet.vehicle',"Vehicle")
    tyre_id = fields.Many2one('vehicle.tyre',"Tyre",help="To See Tyre Running Details")
    retreading_km = fields.Float("Disposed at KM")
    total_km = fields.Float("Total KM ")
    status = fields.Char("Status")