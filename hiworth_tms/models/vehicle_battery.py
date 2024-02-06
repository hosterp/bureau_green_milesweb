from openerp import fields, models, api
from openerp.exceptions import except_orm
from lxml import etree
from openerp.tools.translate import _


class VehicleBattery(models.Model):
    _name = 'vehicle.battery'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(VehicleBattery, self).fields_view_get(
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

    @api.model
    def create(self,vals):

        res = super(VehicleBattery, self).create(vals)

        if self._context.get('goods_receive_line'):
            self.env['goods.recieve.report.line'].browse(self._context.get('goods_receive_line')).battery_id = res.id
        return res

    name= fields.Char("ID/SN")
    vehicle_id = fields.Many2one('fleet.vehicle',"Vehicle")
    warranty_period_from = fields.Date("Warranty Period From")
    warranty_to = fields.Date("To")
    extended_warranty_period_from = fields.Date("Extended Warranty Period From")
    extended_warranty_to = fields.Date("To")
    supplier_id = fields.Many2one('res.partner',string="Supplier",domain="[('supplier','=',True)]")
    amount = fields.Float("Amount")
    active = fields.Boolean("Active",default=True)
    disposed_date = fields.Date("Disposed Date")

    @api.constrains('warranty_to')
    def check_warranty_warranty_to(self):
        for rec in self:
            if rec.warranty_to < rec.warranty_period_from:
                raise except_orm(_('Warning!'),
                                     _('Warranty Period To must be less than or equal to Warranty Period From'))

    @api.constrains('extended_warranty_to')
    def check_warranty_date(self):
        for rec in self:
            if rec.extended_warranty_to < rec.extended_warranty_period_from:
                raise except_orm(_('Warning!'), _('Extended Warranty Period To must be less than or equal to Extended Warranty Period From'))

    @api.constrains('extended_warranty_period_from')
    def check_warranty_extended_warranty_period_from(self):
        for rec in self:
            if rec.extended_warranty_period_from < rec.warranty_to:
                raise except_orm(_('Warning!'),
                                 _('Extended Warranty Period From must be less than or equal to Warranty Period To'))
