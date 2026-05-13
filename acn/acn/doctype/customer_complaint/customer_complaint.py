# Copyright (c) 2026, Ahmad Sayyed and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CustomerComplaint(Document):
	pass



import frappe
from frappe import _


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_part_no(doctype, txt, searchfield, start, page_len, filters):

	customer_dc = filters.get("customer_dc")

	if not customer_dc:
		return []

	return frappe.db.sql("""
		SELECT
			part_no
		FROM `tabCustomer DC child`
		WHERE parent = %(customer_dc)s
			AND part_no LIKE %(txt)s
		GROUP BY part_no
		LIMIT %(start)s, %(page_len)s
	""", {
		"customer_dc": customer_dc,
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len,
	})


@frappe.whitelist()
def get_part_details(customer_dc, part_no):

	customer_dc_doc = frappe.get_doc("Customer DC", customer_dc)

	row = frappe.db.get_value(
		"Customer DC child",
		{
			"parent": customer_dc,
			"part_no": part_no
		},
		[
			"item_code",
			"part_no",
			"material",
			"process_name",
			"qty_nos",
			"qty_kgs",
			"customer_dc_no"
		],
		as_dict=True
	)

	if not row:
		return {}


	sales_invoice = frappe.db.sql("""
		SELECT DISTINCT
			si.name
		FROM `tabSales Invoice` si
		INNER JOIN `tabSales Invoice Item` sii
			ON sii.parent = si.name
		WHERE si.docstatus = 1
			AND sii.customer_dc_id = %(customer_dc)s
			AND sii.part_no = %(part_no)s
		ORDER BY si.posting_date DESC, si.creation DESC
		LIMIT 1
	""", {
		"customer_dc": customer_dc,
		"part_no":row.part_no
	}, as_dict=True)

	invoice_no = sales_invoice[0].name if sales_invoice else None

	return {
		"item_code": row.item_code,
		"item_name": row.part_no,
		"customer": customer_dc_doc.customer_name,
		"customer_dc_no": row.customer_dc_no,
		"invoice_no": invoice_no,
		"material": row.material,
		"process_type": row.process_name,
		"total_qty_nos": row.qty_nos,
		"total_qty_kgs": row.qty_kgs
	}