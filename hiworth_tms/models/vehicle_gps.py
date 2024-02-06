from openerp import fields, models, api


class GpsModel(models.Model):
    _name = 'gps.model'

    name = fields.Char("Name")

class GpsManufacturer(models.Model):
    _name = 'gps.manufacturer'

    name = fields.Char("Name")


class VehicleGps(models.Model):
    _name = 'vehicle.gps'

    @api.model
    def create(self, vals):
        res = super(VehicleGps, self).create(vals)
        if self._context.get('goods_receive_line'):
            self.env['goods.recieve.report.line'].browse(self._context.get('goods_receive_line')).gps_id = res.id
        return res

    name = fields.Char("Name")
    vehicle_id = fields.Many2one('fleet.vehicle',"Vehicle")
    purchase_type  = fields.Selection([('new','New'),
                                       ('secondary','Secondary')],default='new',string="Purchase Type")
    purchase_date = fields.Datetime("Purchase Date")
    gps_model_id = fields.Many2one('gps.model',string="GPS Model")
    notes = fields.Text("Description")
    supplier_id = fields.Many2one('res.partner',"Supplier")
    manufacturer_id = fields.Many2one('gps.manufacturer',"Manufacturer")
    gps_cost = fields.Float("GPS Cost")

