# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class CustomerDC(Document):
	def validate(self):
		for d in self.items:
			d.balance_qty_nos=d.qty_kgs
			d.balance_qty_kgs=d.qty_nos

	def on_submit(self):
		self.update_qty_in_sales_order()
		self.create_job_card()
	def on_cancel(self):
		self.update_qty_in_sales_order(is_cancel=True)
		self.cancel_job_card()

	def cancel_job_card(self):
		sql="""select name from `tabJob Card for process` where reference="{}" """.format(self.name)
		data=frappe.db.sql(sql,as_dict=True)
		if data:
			for d in data:
				doc=frappe.get_doc("Job Card for process",d.name)
				if doc.docstatus==1:
					doc.cancel()
				doc.delete()
	


	def create_job_card(self):
		for d in self.items:
			c_p=self.get_customer_process(d.part_no)
			cp=frappe.get_doc("Customer Process",c_p)
			doc=frappe.new_doc("Job Card for process")
			doc.customer_dc=self.name
			doc.generated_on=self.tran_date
			doc.item_code=d.item_code
			doc.item_name=d.item_name
			doc.part_no=d.part_no
			doc.process_type=cp.process_type
			doc.process_name=cp.process_name
			doc.material=cp.material
			doc.customer_process_ref_no=d.customer_process_ref_no
			doc.customer_dc_no=d.customer_dc_no
			doc.customer_dc_date=d.customer_dc_date
			doc.commitment_date=d.commitment_date
			doc.card_colour=frappe.get_value("Process Type",doc.process_type,"job_card_color")
			doc.image=frappe.get_value("Part no",d.part_no,"image")
			doc.customer_code=self.customer
			doc.customer_name=self.customer_name
			doc.qty_in_kgs=d.qty_kgs
			doc.qty_in_nos=d.qty_nos




			cr_list = []


			for c in  cp.customer_requirements:
				row_c=doc.append("customer_requirements", {})
				row_c.process_parameter=c.process_parameter
				row_c.maximum_value=c.maximum_value
				row_c.minimum_value=c.minimum_value
				row_c.scale=c.scale
				row_c.microstructure_cutoff=c.microstructure_cutoff
				row_c.cr="{0},{1}-{2},{3}".format(c.process_parameter,c.minimum_value,c.maximum_value,c.scale)
				formatted = "{0},{1}-{2},{3}".format(
				c.process_parameter, c.minimum_value, c.maximum_value, c.scale
			)
				cr_list.append(formatted)
			merged_cr = ", ".join(cr_list)

			doc.customer_req = merged_cr


			for s in cp.sequence_lot_wise_internal_process:
				row_s=doc.append("sequence_lot_wise_internal_process", {})
				row_s.furnace_process=s.furnace_process
				row_s.internal_process=s.internal_process
				row_s.lot_no=s.lot_no
				row_s.media=s.media
			for p in cp.parameters_with_acceptance_criteria:
				row_p=doc.append("parameters_with_acceptance_criteria", {})
				row_p.lot_no=p.lot_no
				row_p.internal_process=p.internal_process
				row_p.control_parameter=p.control_parameter
				row_p.minimum_value=p.minimum_value
				row_p.maximum_value=p.maximum_value
				row_p.scale=p.scale
				row_p.microstructure_cutoff=p.microstructure_cutoff
				row_p.information=p.information
			doc.reference=self.name
			doc.save()
			doc.submit()

	def get_customer_process(self,part_no):
		sql="""select p.name from `tabCustomer Process` p inner join `tabPart No  Process Rate` c on p.name=c.parent where p.customer="{}" and c.part_no="{}" """.format(self.customer,part_no)
		data=frappe.db.sql(sql,as_dict=True)
		if data:
			return data[0].name
		else:
			frappe.throw("Customer Process not found for part no {}".format(part_no))


	def update_qty_in_sales_order(self, is_cancel=False):
		so = frappe.get_doc("Sales Order", self.sales_order_no)

		for item in self.items:
			if not item.sales_order_item:
				frappe.throw("Sales Order Item ref not found in row {}".format(item.idx))

			for so_item in so.items:
				if so_item.name == item.sales_order_item:
					sign = -1 if is_cancel else 1

					new_bal_nos = so_item.custom_bal_qty_in_nos + sign * item.qty_nos
					new_bal_kgs = so_item.custom_bal_qty_in_kgs + sign * item.qty_kgs

					if new_bal_nos < 0 or new_bal_kgs < 0:
						pass
						# frappe.throw(
						# 	f"Cannot update Sales Order Item {so_item.name} — resulting balance qty would be negative."
						# )

					so_item.db_set("custom_bal_qty_in_nos", new_bal_nos)
					so_item.db_set("custom_bal_qty_in_kgs", new_bal_kgs)
					break


	@frappe.whitelist()
	def set_part_no_details(self,row):
		if row.get("part_no"):
			sql="""select * from `tabSales Order Item` where parent="{}" and custom_part_no ="{}" """.format(self.sales_order_no,row.get("part_no"))
			data=frappe.db.sql(sql,as_dict=True)
			if data:
				for d in self.items:
					if str(d.idx)==str(row.get("idx")):
						d.qty_nos = data[0].custom_bal_qty_in_nos
						d.qty_kgs = data[0].custom_bal_qty_in_kgs
						
					
						d.balance_qty_nos=data[0].custom_bal_qty_in_nos
						d.balance_qty_kgs=data[0].custom_bal_qty_in_kgs
						if d.qty_kgs:
							d.qty = d.qty_kgs
						if d.qty_nos:
							d.qty = d.qty_nos

						d.rate= data[0].rate

						d.item_code = data[0].item_code
						d.item_name = data[0].item_name
						d.rate_uom = data[0].custom_rate_uom
						d.customer_process_ref_no = data[0].custom_customer_process_ref_no
						d.process_type=data[0].custom_process_type
						d.process_name=data[0].custom_process_name
						d.commitment_date=data[0].delivery_date
						d.sales_order_item=data[0].name
						d.material=data[0].custom_material

						break
		return True
	

@frappe.whitelist()
def map_sales_order_to_customer_dc(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.sales_order_no = source.name
		# copy more fields if needed

	def update_item(source, target, source_parent):
		target.sales_order_item = source.name
		target.qty_nos = source.custom_bal_qty_in_nos
		target.qty_kgs = source.custom_bal_qty_in_kgs
		if target.qty_kgs:
			target.qty = target.qty_kgs
		if target.qty_nos:
			target.qty = target.qty_nos


	return get_mapped_doc(
		"Sales Order",
		source_name,
		{
			"Sales Order": {
				"doctype": "Customer DC",
				"field_map": {
					"name": "sales_order_no",
					"customer": "customer",
				},
				"validation": {
					"docstatus": ["=", 1]
				}
			},
			"Sales Order Item": {
				"doctype": "Customer DC child",
				"field_map": {
					"item_code": "item_code",
					"item_name": "item_name",
					"uom": "uom",
					"rate": "rate",
					"custom_qty_in_nos":"qty_nos",
					"custom_qty_in_kgs":"custom_qty_in_kgs",

					"custom_part_no":"part_no",
					"custom_rate_uom":"rate_uom",
					"custom_customer_process_ref_no":"customer_process_ref_no",
					"custom_process_type":"process_type",
					"custom_process_name":"process_name",
					"delivery_date":"commitment_date",
					"name": "sales_order_item_id"  
				},
				"condition": lambda doc: (
					(doc.custom_bal_qty_in_nos or 0) > 0
					or (doc.custom_bal_qty_in_kgs or 0) > 0
				),
				"postprocess": update_item
			}
		},
		target_doc,
		set_missing_values  
	)



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_part_no(doctype, txt, searchfield, start, page_len, filters):
    so = filters.get('sales_order') if filters else None
    if not so:
        return []

    args = {
        'start': start,
        'so': so,
        'page_len': page_len,
        'txt': '%%%s%%' % txt
    }

    part = frappe.db.sql("""
        SELECT custom_part_no,item_code,item_name,custom_process_name,custom_customer_process_ref_no
        FROM `tabSales Order Item` 
        WHERE parent = %(so)s 
            AND custom_part_no LIKE %(txt)s
                  AND (
            custom_bal_qty_in_kgs > 0 
            OR custom_bal_qty_in_nos > 0 
            OR (custom_qty_in_kgs = 0 AND custom_qty_in_nos = 0)
        )

        ORDER BY custom_part_no ASC
        LIMIT %(start)s, %(page_len)s
    """, args)

    return part