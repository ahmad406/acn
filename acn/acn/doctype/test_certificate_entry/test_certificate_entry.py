# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TestCertificateentry(Document):
	def on_submit(self):
		self.update_inspection_qty() 
		self.update_customer_dc()


	def on_cancel(self):
		self.update_inspection_qty(is_canceled=1)
		self.update_customer_dc(is_canceled=1)

	def update_customer_dc(self,is_canceled=0):
		cd=frappe.get_doc("Customer DC",self.customer_dc_id)
		for d in cd.items:
			if d.part_no==self.part_no:
				if is_canceled:
					d.db_set("balance_qty_kgs",d.balance_qty_kgs+self.accepted_qty_in_kgs)
					d.db_set("balance_qty_nos",d.balance_qty_nos+self.accepted_qty_in_nos)

				else:
					d.db_set("balance_qty_kgs",d.balance_qty_kgs+self.accepted_qty_in_kgs)
					d.db_set("balance_qty_nos",d.balance_qty_nos+self.accepted_qty_in_nos)
		# frappe.throw("yes")

	def update_inspection_qty(self, is_canceled=0):
		li = frappe.get_doc("Lab Inspection Entry", self.lab_inspection_id)
		job = frappe.get_doc("Job Card for process", self.job_card_id)

		for d in job.sequence_lot_wise_internal_process:
			if d.internal_process == li.internal_process:
				# Deduct on submit, add on cancel
				qty_change = -self.accepted_qty_in_nos if is_canceled else self.accepted_qty_in_nos
				new_qty = (d.inspection_qty or 0) + qty_change
				d.db_set("inspection_qty", new_qty)


	# def update_certifed_status(self,is_canceled=0):
		# status=1
		# if is_canceled:
		# 	status=0
		# li=frappe.get_doc("Lab Inspection Entry",self.lab_inspection_id)
		# for d in li.inspection_qty_details:
		# 	if d.job_card_id==self.job_card_id:
		# 		d.db_set("test_certified",status)
		# 		break

	@frappe.whitelist()
	def get_details(self):
		if not self.lab_inspection_id:
			frappe.throw("Select Lab Inspection Id")
		if not self.job_card_id:
			frappe.throw("Select Job Card Id")

		self.set("test_parameters_details",[])
		self.set("test_results",[])

		self.customer_dc_id=""
		self.customer=""
		self.item=""
		self.part_no=""
		self.material=""
		self.accepted_qty_in_nos=""
		self.accepted_qty_in_kgs=""
		li=frappe.get_doc("Lab Inspection Entry",self.lab_inspection_id)
		for d in li.inspection_qty_details:
			if d.job_card_id==self.job_card_id:
				self.customer_dc_id=d.customer_dc_id
				self.customer=d.customer_name
				self.item=d.item_name
				self.part_no=d.part_no
				self.material=d.material
				self.accepted_qty_in_nos=d.accepted_qty_in_nos
				self.accepted_qty_in_kgs=d.accepted_qty_in_kgs

				break
		for r in li.test_results:
			if r.job_card_id==self.job_card_id:
				re=self.append("test_results",{})
				re.job_card_id=r.job_card_id
				re.control_parameters=r.control_parameters
				re.minimum_value=r.minimum_value
				re.maximum_value=r.maximum_value
				re.scale=r.scale
				re.testing_time=r.testing_time
				re.result_vaule=r.result_vaule
				re.testing_qty=r.testing_qty



		for k in li.parameters:
			if self.job_card_id==k.job_card_id:
				row=self.append("test_parameters_details",{})
				row.test_parameters=k.control_parameter
				row.qty_checked=self.accepted_qty_in_nos
				frappe.errprint("in")

				row.reference_standard=self.get_standard(k.control_parameter)
				row.print_sequence_no = frappe.db.get_value('Internal Control Parameter', k.control_parameter, 'tc_order_no')


				row.acceptance_criteria_from=k.result_value_from
				row.acceptance_criteria_to=k.result_value_to
				row.scale=k.scale
				self.other_detail_1=k.other_detail_1
				self.other_detail_2=k.other_detail_2
				self.other_detail_3=k.other_detail_3
				self.other_detail_4=k.other_detail_4
				self.other_detail_5=k.other_detail_5
				self.other_detail_6=k.other_detail_6
				self.other_detail_7=k.other_detail_7
				self.other_detail_8=k.other_detail_8
				self.other_detail_9=k.other_detail_9
				self.ref_standard=k.ref_standard


				self.core=k.core
				self.case=k.case


				self.case_depth_1_1=k.case_depth_1_1
				self.case_depth_1_2=k.case_depth_1_2
				self.case_depth_1_3=k.case_depth_1_3
				self.case_depth_1_4=k.case_depth_1_4
				self.case_depth_1_5=k.case_depth_1_5
				self.case_depth_1_6=k.case_depth_1_6
				self.case_depth_1_6=k.case_depth_1_6
				self.case_depth_1_7=k.case_depth_1_7
				self.case_depth_1_8=k.case_depth_1_8
				self.case_depth_1_9=k.case_depth_1_9
				self.case_depth_1_10=k.case_depth_1_10

				self.hardness_1_1=k.hardness_1_1
				self.hardness_1_2=k.hardness_1_2
				self.hardness_1_3=k.hardness_1_3
				self.hardness_1_4=k.hardness_1_4
				self.hardness_1_5=k.hardness_1_5
				self.hardness_1_6=k.hardness_1_6
				self.hardness_1_7=k.hardness_1_7
				self.hardness_1_8=k.hardness_1_8
				self.hardness_1_9=k.hardness_1_9
				self.hardness_1_10=k.hardness_1_10


				self.case_depth_2_1=k.case_depth_2_1
				self.case_depth_2_2=k.case_depth_2_2
				self.case_depth_2_3=k.case_depth_2_3
				self.case_depth_2_4=k.case_depth_2_4
				self.case_depth_2_5=k.case_depth_2_5
				self.case_depth_2_6=k.case_depth_2_6
				self.case_depth_2_7=k.case_depth_2_7
				self.case_depth_2_8=k.case_depth_2_8
				self.case_depth_2_9=k.case_depth_2_9
				self.case_depth_2_10=k.case_depth_2_10


				self.hardness_2_1=k.hardness_2_1
				self.hardness_2_2=k.hardness_2_2
				self.hardness_2_3=k.hardness_2_3
				self.hardness_2_4=k.hardness_2_4
				self.hardness_2_5=k.hardness_2_5
				self.hardness_2_6=k.hardness_2_6
				self.hardness_2_7=k.hardness_2_7
				self.hardness_2_8=k.hardness_2_8
				self.hardness_2_9=k.hardness_2_9
				self.hardness_2_10=k.hardness_2_10


				row.lab_entry_no=k.lab_entry_no
		jb=frappe.get_doc("Job Card for process",self.job_card_id)
		for f in jb.parameters_with_acceptance_criteria:
			rw=self.append("parameters",{})
			rw.internal_process=f.internal_process
			rw.process_parameter=f.control_parameter
			rw.minimum_value=f.minimum_value
			rw.maximum_value=f.maximum_value
			rw.scale=f.scale
			rw.microstructure_cutoff=f.microstructure_cutoff
			rw.information=f.information


		



			# row.measurement_from=
			# row.measurement_to=
		return True

	def get_standard(self,para):
		doc=frappe.get_doc("Internal Control Parameter",para)
		if doc.ref_std:
			if doc.ref_std[0].reference_standard:
				return  doc.ref_std[0].reference_standard
			else:
				return ""
		else:
			return ""
		
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def lab_inspection(doctype, txt, searchfield, start, page_len, filters):
    args = {
        'start': start,
        'page_len': page_len,
        'txt': f'%{txt}%'
    }

    job_plans = frappe.db.sql("""
        SELECT DISTINCT l.name
        FROM `tabLab Inspection Entry` l
        INNER JOIN `tabInspection Qty Details` i 
            ON l.name = i.parent
        INNER JOIN `tabJob Card for process` p 
            ON i.job_card_id = p.name
        INNER JOIN `tabSequence Lot wise Internal Process` c 
            ON p.name = c.parent
        WHERE 
            c.inspection_qty > 0
            AND i.docstatus = 1
            AND l.docstatus = 1
            AND l.name LIKE %(txt)s
        LIMIT %(start)s, %(page_len)s
    """, args, as_dict=False)

    return job_plans


		
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def job_card_process(doctype, txt, searchfield, start, page_len, filters):
	lab_inspection = filters.get('lab_inspection')
	args = {
		'start': start,
		'page_len': page_len,
		'lab_inspection':lab_inspection,
		'txt': f'%{txt}%'
	}
	
	job_plans = frappe.db.sql("""
			select p.name,internal_process,i.parent from `tabJob Card for process` p inner join 
	`tabSequence Lot wise Internal Process` c on p.name=c.parent  inner join
	`tabInspection Qty Details` i on i.job_card_id=p.name
	where c.inspection_qty >0  and  i.docstatus=1 and i.parent= %(lab_inspection)s and p.name LIKE %(txt)s
		LIMIT %(start)s, %(page_len)s
	""", args, as_dict=False)
	
	return job_plans
