from openerp import models, fields, api, _
from datetime import date


class sale_order(models.Model):
	_inherit = 'sale.order'


	@api.depends('amount_total','sale_advance')
	def compute_balance_amount(self):
		for rec in self:
			rec.balance_amount = rec.amount_total - rec.sale_advance

	customer_identify=fields.Char('Customer ID')
	show_visit_date = fields.Date('Showroom Visited Date')
	supply_date = fields.Date('Supply Date')

	sale_advance = fields.Float('Advance Amount')
	balance_amount = fields.Float('Balance Amount' ,readonly=True ,compute ='compute_balance_amount')
	bank_details = fields.Many2one('res.bank',string = 'Bank details')
	company = fields.Many2one('res.company',string = 'company')
	t_c_1 = fields.Boolean(string = 'Payment:advance must 50 per cent of the total cost')
	t_c_2 = fields.Boolean(string = 'Goods once sold can not be taken back')
	t_c_3 = fields.Boolean(string = 'Delivery:With in ..... from the date of order placed')
	days_within = fields.Float(string ='Days within')
	t_c_4 = fields.Boolean(string = 'Unloading charge should be beared ny customer of 50Ps/Piece')
	t_c_5 = fields.Boolean(string = 'Earth work charges should be given seperately by customer of rs 750/Head/day')
	t_c_6 = fields.Boolean(string = 'Laying Charge:excluded,it should be made by customer directly to laying crew')
	laying_charge = fields.Float('Rate per Sq.ft ')
	t_c_7 = fields.Boolean(string = 'Chips for laying should be provided by the customer')
	t_c_8 = fields.Boolean(string = 'Cement & M.dust for boarder concreting should be supplied by customer')
	t_c_9 = fields.Boolean(string = 'Transporting charge should given by the customer')
	t_c_10 = fields.Boolean(string = 'Mode of Payment : In addition to the advance amount,\
							the balance payment for each load should be made on the day of itself')
	t_c_11 = fields.Boolean(string = 'Wastage :3 percent is applicable')


class ResPartner(models.Model):

    _inherit = "res.partner"

    gst_no = fields.Char('GST No')

class product_template(models.Model):

	_inherit = "product.template"

	pro_color = fields.Char('Color')
	pro_design = fields.Char('Design')
