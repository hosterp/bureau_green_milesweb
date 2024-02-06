from openerp import models, fields, api, _
from openerp import tools, _
from datetime import datetime, date, timedelta


class FleetDocumentRetread(models.TransientModel):
	_name = 'fleet.documents.retread'

	vehicle_id = fields.Many2one('fleet.vehicle',"Vehicle")
	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')
	tyre_id = fields.Many2one('vehicle.tyre',"Tyre")
	tyre_warranty = fields.Boolean("Tyre Warranty")
	tyre_retread = fields.Boolean("Tyre Retread")


	@api.onchange('tyre_retread')
	def onchange_tyre_retread(self):
		for rec in self:
			rec.tyre_warranty = False

	@api.onchange('tyre_warranty')
	def onchange_tyre_warranty(self):
		for rec in self:
			rec.tyre_retread = False



	@api.onchange('vehicle_id')
	def onchange_vehicle_id(self):
		for rec in self:
			if rec.tyre_retread:
				return {'domain': {'tyre_id': [('vehicle_id', '=', rec.vehicle_id.id)]}}
			else:
				return{'domain':{'tyre_id':[('vehicle_id','=',rec.vehicle_id.id),('active','=',False)]}}

	@api.multi
	def action_fleet_documents_open_window(self):
		if not self.tyre_warranty:
			datas = {
				'ids': self._ids,
				'model': self._name,
				'form': self.read(),
				'context': self._context,
			}

			return {
				'name': 'Documents Renewal Report',
				'type': 'ir.actions.report.xml',
				'report_name': 'hiworth_tms.report_fleet_vehicle_retrading_template',
				'datas': datas,
				'report_type': 'qweb-pdf'
			}
		else:
			datas = {
				'ids': self._ids,
				'model': self._name,
				'form': self.read(),
				'context': self._context,
			}

			return {
				'name': 'Tyre warrenty report',
				'type': 'ir.actions.report.xml',
				'report_name': 'hiworth_tms.tyre_warranty_report_template',
				'datas': datas,
				'report_type': 'qweb-pdf'
			}

	@api.multi
	def action_fleet_documents_open_window1(self):
		if not self.tyre_warranty:
			datas = {
				'ids': self._ids,
				'model': self._name,
				'form': self.read(),
				'context': self._context,
			}

			return {
				'name': 'Documents Renewal Report',
				'type': 'ir.actions.report.xml',
				'report_name': 'hiworth_tms.report_fleet_vehicle_retrading_template',
				'datas': datas,
				'report_type': 'qweb-html'
			}
		else:
			datas = {
				'ids': self._ids,
				'model': self._name,
				'form': self.read(),
				'context': self._context,
			}

			return {
				'name': 'Tyre warrenty report',
				'type': 'ir.actions.report.xml',
				'report_name': 'hiworth_tms.tyre_warranty_report_template',
				'datas': datas,
				'report_type': 'qweb-html'
			}


	@api.multi
	def get_details(self):
		if not self.tyre_warranty:
			list = []
			dom = []
			date_from = datetime.strptime(self.date_from,"%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
			date_to = datetime.strptime(self.date_to,"%Y-%m-%d").strftime("%Y-%m-%d 23:59:59")
			if self.vehicle_id:
				dom.append(('id', '=', self.vehicle_id.id))

			vehicles = self.env['fleet.vehicle'].search(dom)
			for veh_id in vehicles:
				for detail in veh_id.tyre_detials_ids:
					if self.tyre_id:

						if detail.id == self.tyre_id.id:
							for tyre_in in detail.retreading_ids:

								if tyre_in.retreading_date >= date_from and tyre_in.retreading_date <= date_to:
									list.append({
										# 'vehicle_name': veh_id.name,
										'tyre_name': detail.name,
										'date':tyre_in.retreading_date,
										'vendor':tyre_in.manufacture_id.name,
										'purchase_type':tyre_in.purchase_type,
										'type':tyre_in.tyre_retrading_type.name,

										'retreading_cost':tyre_in.retrading_cost,
										'purchase_km':tyre_in.purchase_km,
										'retreading_km':tyre_in.retreading_km,
										'removing_km':tyre_in.removing_km,
										'total_km':tyre_in.total_km,

									})
					else:
						for tyre_in in detail.retreading_ids:
							if tyre_in.retreading_date >= date_from and tyre_in.retreading_date <= date_to:
								list.append({
									# 'vehicle_name': veh_id.name,
									'tyre_name': detail.name.name,
									'date': tyre_in.retreading_date,
									'vendor': tyre_in.manufacture_id.name,
									'type': tyre_in.tyre_retrading_type.name,
									'estimated_life': tyre_in.estimated_life,
									'retreading_cost': tyre_in.retrading_cost,
									'retreading_km': tyre_in.retreading_km,
									'total_km': tyre_in.total_km,
									'cum_km': tyre_in.cum_km
								})
		else:
			list = []
			tyre = self.env['warranty.tyre'].search([('tyre_id', '=', self.tyre_id.id)])

			for ty_id in tyre:
				if ty_id.date <= self.date_to and ty_id.date >= self.date_from:
					status = ''
					if ty_id.is_account_entry:
						status = 'Claim Approved'
					if ty_id.not_approved:
						status = 'Claim Not Approved'
					list.append({
						# 'vehicle_name': veh_id.name,
						'tyre_no': ty_id.tyre_id.name,
						'tyre_type': ty_id.tyre_type_id.name,
						'tyre_man': ty_id.manufacture_id.name,
						'sup_name': ty_id.tyre_type_id.name,
						'c_s_d': ty_id.date and datetime.strptime(ty_id.date,"%Y-%m-%d").strftime("%d-%m-%Y") or '',
						'claim_amt': ty_id.amount,
						'claim_amt_rec': ty_id.amount_appr,
						'claim_amt_rec_date': ty_id.claim_rec_date and datetime.strptime(ty_id.claim_rec_date,"%Y-%m-%d").strftime("%d-%m-%Y") or '',
						'difference': ty_id.amount - ty_id.amount_appr,
						'dif_and_ref_det': ty_id.ref_det,
						'status':status,
					})

		return list



		return list


class FleetTyreWarrenty(models.TransientModel):
	_name='fleet.tyre.warrenty'

	tyre_id=fields.Many2one('vehicle.tyre','Tyre')
	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')
	@api.multi
	def action_fleet_documents_open_window(self):

		datas = {
			'ids': self._ids,
			'model': self._name,
			'form': self.read(),
			'context': self._context,
		}

		return {
			'name': 'Tyre warrenty report',
			'type': 'ir.actions.report.xml',
			'report_name': 'hiworth_tms.tyre_warranty_report_template',
			'datas': datas,
			'report_type': 'qweb-pdf'
		}

	@api.multi
	def action_fleet_documents_open_window1(self):

		datas = {
			'ids': self._ids,
			'model': self._name,
			'form': self.read(),
			'context': self._context,
		}

		return {
			'name': 'Tyre warrenty report',
			'type': 'ir.actions.report.xml',
			'report_name': 'hiworth_tms.tyre_warranty_report_template',
			'datas': datas,
			'report_type': 'qweb-html'
		}

	@api.multi
	def get_details(self):
		list = []
		tyre = self.env['warranty.tyre'].search([('tyre_id', '=', self.tyre_id.id)])

		for ty_id in tyre:
			if ty_id.claim_date<=self.date_to and ty_id.claim_date>=self.date_from:
				list.append({
					# 'vehicle_name': veh_id.name,
					'tyre_no': ty_id.tyre_id.name,
					'tyre_type':ty_id.tyre_type_id.name,
					'tyre_man':ty_id.manufacture_id.name,
					'sup_name':ty_id.tyre_type_id.name,
					'c_s_d':ty_id.date,
					'claim_amt':ty_id.amount,
					'claim_amt_rec':ty_id.amount,
					'claim_amt_rec_date':ty_id.claim_date,
					'dif_and_ref_det':ty_id.claim_date
				})



		return list


class FleetDocumentWizard(models.TransientModel):
	_name = 'fleet.documents.wizard'

 
	document_type = fields.Selection([('pollution','Pollution'),
									('road_tax','Road Tax'),
									('fitness','Fitness'),
									('insurance','Insurance'),
									('permit','Permit'),
									], string="Document Type")
	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')
		


	@api.multi
	def action_fleet_documents_open_window(self):

			datas = {
				 'ids': self._ids,
				 'model': self._name,
				 'form': self.read(),
				 'context':self._context,
			}
		 
			return{
				 'name' : 'Documents Renewal Report',
				 'type' : 'ir.actions.report.xml',
				 'report_name' : 'hiworth_tms.report_fleet_documents_renewal_template',
				 'datas': datas,
				 'report_type': 'qweb-pdf'
			}

	@api.multi
	def action_fleet_documents_open_window1(self):

			datas = {
				 'ids': self._ids,
				 'model': self._name,
				 'form': self.read(),
				 'context':self._context,
			}
		 
			return{
				 'name' : 'Documents Renewal Report',
				 'type' : 'ir.actions.report.xml',
				 'report_name' : 'hiworth_tms.report_fleet_documents_renewal_template',
				 'datas': datas,
				 'report_type': 'qweb-html'
			}

 

	@api.multi
	def get_details123(self):
		list = []
		doc_renewal = ''
		vehicles = self.env['fleet.vehicle'].search([])
		for veh_id in vehicles:

			if self.document_type == 'pollution':
				if self.date_from <= veh_id.pollution_date and self.date_to >= veh_id.pollution_date:
					list.append({
						'vehicle_name': veh_id.name,
						'start_date':veh_id.pollution_start_date,
						'end_date':veh_id.pollution_end_date,
						'renewal_date': datetime.strptime(veh_id.pollution_date, '%Y-%m-%d').strftime('%d-%m-%Y'),
					})

			elif self.document_type == 'road_tax':
				if self.date_from <= veh_id.roadtax_date and self.date_to >= veh_id.roadtax_date:
					list.append({
						'vehicle_name': veh_id.name,
						'start_date': veh_id.road_tax_start_date,
						'end_date': veh_id.road_tax_end_date,
						'renewal_date': datetime.strptime(veh_id.roadtax_date, '%Y-%m-%d').strftime('%d-%m-%Y'),
					})
			elif self.document_type == 'fitness':
				if self.date_from <= veh_id.fitness_date and self.date_to >= veh_id.fitness_date:
					list.append({
						'vehicle_name': veh_id.name,
						'start_date': veh_id.fitness_start_date,
						'end_date': veh_id.fitness_end_date,
						'renewal_date': datetime.strptime(veh_id.fitness_date, '%Y-%m-%d').strftime('%d-%m-%Y'),
					})

			elif self.document_type == 'insurance':
				if self.date_from <= veh_id.insurance_date and self.date_to >= veh_id.insurance_date:
					list.append({
						'vehicle_name': veh_id.name,
						'start_date':veh_id.insu_start_date,
						'end_date':veh_id.next_payment_date_ins,
						'renewal_date': datetime.strptime(veh_id.insurance_date, '%Y-%m-%d').strftime('%d-%m-%Y'),
					})

			elif self.document_type == 'permit':
				if self.date_from <= veh_id.permit_date and self.date_to >= veh_id.permit_date:
					list.append({
						'vehicle_name': veh_id.name,
						'start_date': veh_id.permit_start_date,
						'end_date': veh_id.permit_end_date,
						'renewal_date': datetime.strptime(veh_id.permit_date, '%Y-%m-%d').strftime('%d-%m-%Y'),
					})
			else:

				pass



		
		list_new  = sorted(list, key = lambda i: datetime.strptime(i['renewal_date'], '%d-%m-%Y'))
		return list_new



class FleetDocumentsAll(models.Model):
	_name = 'fleet.documents.all'

 
	document_ids = fields.One2many('fleet.documents.all.line', 'line_id')

	@api.multi
	def open_report_documents_all(self):
		return self.env['report'].get_action(self, 'hiworth_tms.report_fleet_documents_all')

	@api.model
	def default_get(self, default_fields):
		vals = super(FleetDocumentsAll, self).default_get(default_fields)
		list=[]
		vehicles = self.env['fleet.vehicle'].search([('rent_vehicle','!=',True)])
		for veh_id in vehicles:

			list.append([0, 0, {'vehicle_id':veh_id.id,
								'pollution_date':veh_id.pollution_date,
								'road_tax_date':veh_id.roadtax_date,
								'fitness_date':veh_id.fitness_date,
								'insurance_date':veh_id.insurance_date,
								'permit_date':veh_id.permit_date,
								'customer':True,
								'customer1':1,
								}])
			vals['document_ids'] = list
		return vals


class FleetDocumentsAll1(models.Model):
	_name = 'fleet.documents.all.line'

	line_id = fields.Many2one('fleet.documents.all')
	vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
	pollution_date = fields.Date('Pollution Renewal Date')
	road_tax_date = fields.Date('Road Tax Renewal Date')
	fitness_date = fields.Date('Fitness Renewal Date')
	insurance_date = fields.Date('Insurance Renewal Date')
	permit_date = fields.Date('Permit Renewal Date')


class VehicleMileageWizard(models.TransientModel):
	_name = 'vehicle.mileage.wizard'

 
	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')
		


	@api.multi
	def action_vehicle_mileage_open_window(self):

			datas = {
				 'ids': self._ids,
				 'model': self._name,
				 'form': self.read(),
				 'context':self._context,
			}
		 
			return{
				 'name' : 'Mileage Report',
				 'type' : 'ir.actions.report.xml',
				 'report_name' : 'hiworth_tms.report_fleet_vehicle_mileage_template',
				 'datas': datas,
				 'report_type': 'qweb-pdf'
			}

	@api.multi
	def action_vehicle_mileage_open_window1(self):

			datas = {
				 'ids': self._ids,
				 'model': self._name,
				 'form': self.read(),
				 'context':self._context,
			}
		 
			return{
				 'name' : 'Mileage Report',
				 'type' : 'ir.actions.report.xml',
				 'report_name' : 'hiworth_tms.report_fleet_vehicle_mileage_template',
				 'datas': datas,
				 'report_type': 'qweb-html'
			}

 

	@api.multi
	def get_details(self):
		list = []
		mileage = 0
		vehicles = self.env['fleet.vehicle'].search([])
		for veh_id in vehicles:
			# line1 = self.env['diesel.pump.line'].search([('vehicle_id','=', veh_id.id),('date','>=',self.date_from),('date','<=',self.date_to)], order="date asc", limit=1)
			# line2 = self.env['diesel.pump.line'].search([('vehicle_id','=', veh_id.id),('date','>=',self.date_from),('date','<=',self.date_to)], order="date desc", limit=1)
			
			# if line1.date != self.date_from:
   #          	raise osv.except_osv(('Error'), ('Please configure journal and account for this payment'));
   			


   			vals2 = 0
			vals1 = 0
			km2 = 0
			km1 = 0
			km = 0
			litre = 0
			first_km = self.env['diesel.pump.line'].search(
				[('is_full_tank', '=', True), ('vehicle_id', '=', veh_id.id), ('date', '>=', self.date_from),
				 ('date', '<=', self.date_to)], order='date asc', limit=1)
			close_km = self.env['diesel.pump.line'].search(
				[('is_full_tank', '=', True), ('vehicle_id', '=', veh_id.id), ('date', '>=', self.date_from),
				 ('date', '<=', self.date_to)], order='date desc', limit=1)
			lines = self.env['diesel.pump.line'].search([('vehicle_id','=', veh_id.id),('date','>=',self.date_from),('date','<=',self.date_to)],order='date asc')
			if lines:
				full_tank = False
				temp_litre = 0
				for line_id in lines:
					if not first_km.date >= line_id.date:
						temp_litre += line_id.litre
						if line_id.is_full_tank:
							full_tank = True
						if full_tank:
							litre += temp_litre
							temp_litre = 0
							full_tank = False


				km = close_km.odometer - first_km.odometer


				if litre == 0:
					mileage = 0
				else:
					mileage = km / litre


				list.append({
								'vehicle_name': veh_id.name,
								'km': km,
								'litre': litre,
								'mileage': mileage,
								})

		return list


class VehicleDetailReportWizard(models.TransientModel):
	_name = 'vehicle.detail.report.wizard'

	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')


	@api.multi
	def get_details(self):
		for rec in self:
			data_list = []
			data_dict = {}
			vehicles = self.env['fleet.vehicle'].search([('acquisition_date','>=',rec.date_from),('acquisition_date','<=',rec.date_to)])
			for veh in vehicles:
				data_list.append({'reg_no':veh.name,
								  'brand':veh.brand_id.name,
								  'model':veh.model_id.name,
								  'purchase_date':veh.acquisition_date and datetime.strptime(veh.acquisition_date,"%Y-%m-%d").strftime("%d-%m-%Y") or '',
								  'reg_owner':veh.vehicle_under.name,
								  'presnt_insu_comp':veh.agent_id.name,
								  'insu_renewal_date':veh.insurance_date and datetime.strptime(veh.insurance_date,"%Y-%m-%d").strftime("%d-%m-%Y") or '',
								  'road_tax_renewal_date':veh.roadtax_date and datetime.strptime(veh.roadtax_date,"%Y-%m-%d").strftime("%d-%m-%Y") or '',
								  'fitness_renewal_date':veh.fitness_date and datetime.strptime(veh.fitness_date,"%Y-%m-%d").strftime("%d-%m-%Y") or '',
								  'permit_renewal_date':veh.permit_date and datetime.strptime(veh.permit_date,"%Y-%m-%d").strftime("%d-%m-%Y") or '',
								  'pollu_renewal_date':veh.pollution_date and datetime.strptime(veh.pollution_date,"%Y-%m-%d").strftime("%d-%m-%Y") or ''})
		return  data_list


	@api.multi
	def action_fleet_documents_open_window(self):
		datas = {
			'ids': self._ids,
			'model': self._name,
			'form': self.read(),
			'context': self._context,
		}

		return {
			'name': 'Vehicle Detail Report',
			'type': 'ir.actions.report.xml',
			'report_name': 'hiworth_tms.vehicle_detail_report_template',
			'datas': datas,
			'report_type': 'qweb-pdf'
		}

	@api.multi
	def action_fleet_documents_open_window1(self):
		datas = {
			'ids': self._ids,
			'model': self._name,
			'form': self.read(),
			'context': self._context,
		}

		return {
			'name': 'Vehicle Detail Report',
			'type': 'ir.actions.report.xml',
			'report_name': 'hiworth_tms.vehicle_detail_report_template',
			'datas': datas,
			'report_type': 'qweb-html'
		}
