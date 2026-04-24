# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from collections import defaultdict
import io
import base64
import os



class TestCertificateentry(Document):
	def on_submit(self):
		self.update_inspection_qty() 
		self.update_customer_dc()


	def on_cancel(self):
		self.update_inspection_qty(is_canceled=1)
		self.update_customer_dc(is_canceled=1)
	
	def before_save(self):
		generate_hardness_graph(self)
	
	def validate(self):
		if not self.lab_inspection_id or not self.job_card_id:
			return
		existing = frappe.db.exists("Test Certificate entry",
		{
			"lab_inspection_id": self.lab_inspection_id,
			"job_card_id": self.job_card_id,
			"name": ["!=", self.name]
		})
		if existing:
			frappe.throw(
				f"Test Certificate Entry already exists for "
				f"Lab Inspection <b>{self.lab_inspection_id}</b> "
				f"and Job Card <b>{self.job_card_id}</b>"
			)

	def update_customer_dc(self, is_canceled=0):
		cd = frappe.get_doc("Customer DC", self.customer_dc_id)

		accepted_kgs = self.accepted_qty_in_kgs or 0
		accepted_nos = self.accepted_qty_in_nos or 0

		for d in cd.items:
			if d.part_no != self.part_no:
				continue

			current_kgs = d.balance_qty_kgs or 0
			current_nos = d.balance_qty_nos or 0

			if not is_canceled:
				d.db_set("balance_qty_kgs", current_kgs + accepted_kgs)
				d.db_set("balance_qty_nos", current_nos + accepted_nos)

			else:
				new_kgs = current_kgs - accepted_kgs
				new_nos = current_nos - accepted_nos

				if new_kgs < 0 or new_nos < 0:
					frappe.throw(
						f"Cannot cancel Test Certificate. "
						f"Delivery already made for Part No {self.part_no}"
					)

				d.db_set("balance_qty_kgs", new_kgs)
				d.db_set("balance_qty_nos", new_nos)

		# frappe.throw("yes")
	def update_inspection_qty(self,is_canceled=0):
		li = frappe.get_doc("Lab Inspection Entry", self.lab_inspection_id)

		certified = 0 if is_canceled == 1 else 1
		for d in li.inspection_qty_details:
			if d.job_card_id == self.job_card_id:
				d.db_set("test_certified", certified)

				


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
		self.check_qty_in_nos=0
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
				self.check_qty_in_nos=d.checked_qty_in_nos

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
				re.remarks=r.remarks
				re.reference_standard=self.get_standard(r.control_parameters)


		tested_qty_map = defaultdict(float)
		for r in self.test_results:
			if r.control_parameters:
				tested_qty_map[r.control_parameters] += (r.testing_qty or 0)

		for k in li.parameters:
			if self.job_card_id==k.job_card_id:
				row=self.append("test_parameters_details",{})
				row.test_parameters=k.control_parameter
				row.qty_checked = tested_qty_map.get(k.control_parameter, 0)

				row.reference_standard=self.get_standard(k.control_parameter)
				row.print_sequence_no = frappe.db.get_value('Internal Control Parameter', k.control_parameter, 'tc_order_no')


				row.acceptance_criteria_from=k.result_value_from
				row.acceptance_criteria_to=k.result_value_to
				row.remarks=k.remarks
				row.measurement_to=k.maximum_value
				row.measurement_from = k.minimum_value

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
        "start": start,
        "page_len": page_len,
        "txt": f"%{txt}%",
    }

    inspections = frappe.db.sql(
        """
        SELECT DISTINCT l.name,i.job_card_id
        FROM `tabLab Inspection Entry` l
        INNER JOIN `tabInspection Qty Details` i
            ON l.name = i.parent
        INNER JOIN `tabJob Card for process` p
            ON i.job_card_id = p.name
        WHERE
            i.test_certified = 0
            AND internal_process = 'FINAL INSPECTION'
            AND i.docstatus = 1
            AND l.docstatus = 1
            AND l.name LIKE %(txt)s
        LIMIT %(start)s, %(page_len)s
        """,
        args,
        as_dict=False,
    )

    return inspections

# @frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
# def lab_inspection(doctype, txt, searchfield, start, page_len, filters):
#     args = {
#         'start': start,
#         'page_len': page_len,
#         'txt': f'%{txt}%'
#     }

#     job_plans = frappe.db.sql("""
#         SELECT DISTINCT l.name
#         FROM `tabLab Inspection Entry` l
#         INNER JOIN `tabInspection Qty Details` i 
#             ON l.name = i.parent
#         INNER JOIN `tabJob Card for process` p 
#             ON i.job_card_id = p.name
#         INNER JOIN `tabSequence Lot wise Internal Process` c 
#             ON p.name = c.parent
#         WHERE 
#             c.certified = 0
# 			and l.internal_process='FINAL INSPECTION'
# 			and c.internal_process='FINAL INSPECTION'
#             AND i.docstatus = 1
#             AND l.docstatus = 1
#             AND l.name LIKE %(txt)s
#         LIMIT %(start)s, %(page_len)s
#     """, args, as_dict=False)

#     return job_plans

		
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def job_card_process(doctype, txt, searchfield, start, page_len, filters):
	lab_inspection = filters.get('lab_inspection')
	internal_process=frappe.db.get_value('Lab Inspection Entry',lab_inspection, 'internal_process')
	# frappe.errprint([internal_process,lab_inspection])
	args = {
		'start': start,
		'page_len': page_len,
		'lab_inspection':lab_inspection,
		'internal_process':internal_process,
		'txt': f'%{txt}%'
	}
	
	job_plans = frappe.db.sql("""
			select p.name,internal_process,i.parent  FROM `tabLab Inspection Entry`  l inner join
			`tabInspection Qty Details` i on i.parent=l.name inner join 
			`tabJob Card for process` p on p.name=i.job_card_id
	where (IFNULL(i.test_certified, 0) = 0) and internal_process= %(internal_process)s
  and  i.docstatus=1 and p.docstatus=1 and i.parent= %(lab_inspection)s and p.name LIKE %(txt)s
		LIMIT %(start)s, %(page_len)s
	""", args, as_dict=False)
	
	return job_plans


		
# @frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
# def job_card_process(doctype, txt, searchfield, start, page_len, filters):
# 	lab_inspection = filters.get('lab_inspection')
# 	internal_process=frappe.db.get_value('Lab Inspection Entry',lab_inspection, 'internal_process')
# 	# frappe.errprint([internal_process,lab_inspection])
# 	args = {
# 		'start': start,
# 		'page_len': page_len,
# 		'lab_inspection':lab_inspection,
# 		'internal_process':internal_process,
# 		'txt': f'%{txt}%'
# 	}
	
# 	job_plans = frappe.db.sql("""
# 			select p.name,internal_process,i.parent from `tabJob Card for process` p inner join 
# 	`tabSequence Lot wise Internal Process` c on p.name=c.parent  inner join
# 	`tabInspection Qty Details` i on i.job_card_id=p.name
# 	where (IFNULL(c.certified, 0) = 0) and internal_process= %(internal_process)s
#   and  i.docstatus=1 and i.parent= %(lab_inspection)s and p.name LIKE %(txt)s
# 		LIMIT %(start)s, %(page_len)s
# 	""", args, as_dict=False)
	
# 	return job_plans


def generate_hardness_graph(doc):
	"""
	Fetch Lab inspection child rows matching job_card_id
	and parent lab_inspection_id, generate a Micro Hardness
	vs Case Depth graph, and attach to hardness_graph field.
	"""
	if not doc.job_card_id:
		frappe.msgprint(
			"Job Card ID is missing. Hardness graph not generated.",
			alert=True
		)
		return

	if not doc.lab_inspection_id:
		frappe.msgprint(
			"Lab Inspection ID is missing. Hardness graph not generated.",
			alert=True
		)
		return

	rows = frappe.db.get_all(
		"Lab inspection",
		filters={
			"parent": doc.lab_inspection_id,
			"job_card_id": doc.job_card_id,
		},
		fields=[
			"case_depth_1_1", "case_depth_1_2", "case_depth_1_3",
			"case_depth_1_4", "case_depth_1_5", "case_depth_1_6",
			"case_depth_1_7", "case_depth_1_8", "case_depth_1_9",
			"case_depth_1_10",
			"hardness_1_1", "hardness_1_2", "hardness_1_3",
			"hardness_1_4", "hardness_1_5", "hardness_1_6",
			"hardness_1_7", "hardness_1_8", "hardness_1_9",
			"hardness_1_10",
		],
		order_by="creation desc",
		limit=1
	)

	if not rows:
		frappe.msgprint(
			f"No Lab Inspection data found for Job Card ID: {doc.job_card_id} "
			f"in Lab Inspection Entry: {doc.lab_inspection_id}. "
			"Hardness graph not generated.",
			alert=True
		)
		return

	row = rows[0]

	case_depth_fields = [f"case_depth_1_{i}" for i in range(1, 11)]
	hardness_fields   = [f"hardness_1_{i}"   for i in range(1, 11)]

	points = []
	for cd_field, hv_field in zip(case_depth_fields, hardness_fields):
		cd_val = row.get(cd_field)
		hv_val = row.get(hv_field)
		if cd_val not in (None, "") and hv_val not in (None, ""):
			try:
				points.append((float(cd_val), float(hv_val)))
			except (ValueError, TypeError):
				continue

	if not points:
		frappe.msgprint(
			"Lab Inspection row found but no valid Case Depth / Hardness data. "
			"Graph not generated.",
			alert=True
		)
		return

	case_depths   = [p[0] for p in points]
	hardness_vals = [p[1] for p in points]

	try:
		import matplotlib
		matplotlib.use("Agg")
		import matplotlib.pyplot as plt
		import matplotlib.ticker as ticker
	except ImportError:
		frappe.throw(
			"matplotlib is not installed. Run: bench pip install matplotlib"
		)

	fig, ax = plt.subplots(figsize=(7, 4))

	ax.plot(
		case_depths, hardness_vals,
		marker="o", markersize=4,
		linestyle="--", linewidth=1.2,
		color="black"
	)

	ax.set_xlabel("Case Depth in mm", fontsize=9,fontweight='bold')
	ax.set_ylabel("Hardness\n(HV)", fontsize=9, rotation=0, labelpad=40,fontweight='bold')
	ax.set_title(
		"Case Depth(CD) by Micro Hardness(SH) Survey Method",
		fontsize=9, pad=8,fontweight='bold'	
	)

	y_min = max(0, min(hardness_vals) - 50)
	y_max = max(hardness_vals) + 100
	ax.set_ylim(y_min, y_max)
	ax.yaxis.set_major_locator(ticker.MultipleLocator(100))

	ax.set_xticks(case_depths)
	ax.tick_params(axis='both', labelsize=7)

	fig.canvas.draw()

	for label in ax.get_xticklabels() + ax.get_yticklabels():
		label.set_fontweight('bold')

	ax.grid(False)
	fig.tight_layout()

	buf = io.BytesIO()
	fig.savefig(buf, format="png", dpi=120)
	plt.close(fig)
	buf.seek(0)
	image_bytes = buf.read()

	file_name = f"hardness_graph_{doc.name}.png"

	if doc.hardness_graph:
		try:
			old_file = frappe.get_value(
				"File", {"file_url": doc.hardness_graph}, "name"
			)
			if old_file:
				frappe.delete_doc("File", old_file, force=True)
		except Exception:
			pass

	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_name": file_name,
		"attached_to_doctype": doc.doctype,
		"attached_to_name": doc.name,
		"attached_to_field": "hardness_graph",
		"is_private": 0,
		"content": image_bytes,
	})
	file_doc.save(ignore_permissions=True)

	doc.hardness_graph = file_doc.file_url
	frappe.msgprint("Hardness graph generated successfully.", alert=True)