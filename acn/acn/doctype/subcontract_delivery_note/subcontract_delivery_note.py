# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import _


class SubcontractDeliveryNote(Document):

	def validate(self):
		self.validate_data()
	def validate_data(self):
		for d in self.items:
			if d.delivery_qty_nos is None or d.delivery_qty_nos <= 0:
				frappe.throw(
					_("Row {0}: Delivery Quantity (Nos) must be greater than zero.").format(d.idx)
				)
			# if d.delivery_qty_kgs is None or d.delivery_qty_kgs <= 0:
			# 	frappe.throw(
			# 		_("Row {0}: Delivery Quantity (Kgs) must be greater than zero.").format(d.idx)
			# 	)

	@frappe.whitelist()
	def get_item_details(self, row):
		item_details = frappe._dict()  

		po = frappe.get_doc("Purchase Order", self.work_order_no)

		for d in po.items:
			if d.item_code == row.get("service_name"):
				item_details = {
					"rate_uom": d.uom,
					"rate": d.rate,
					"description":d.description,
					"item_tax_template":d.item_tax_template,
					"expense_account":d.expense_account,
					"sub_account":d.sub_account,
					"cost_center":d.cost_center
				}
				break

		return item_details
	@frappe.whitelist()
	def get_dc_details(self, row):
		item_details = frappe._dict()  

		dc = frappe.get_doc("Customer DC", row.get("customer_dc_id"))


		for d in dc.items:
			if d.part_no == row.get("part_no"):
				item_details = {
					"customer_name": dc.customer_name,
					"process_name": d.process_name,
					"dc_qty_nos":d.qty_nos,
					"dc_qty_kgs":d.qty_kgs
				}
				break

		return item_details

				
				

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_items(doctype, txt, searchfield, start, page_len, filters):
	args = {
		'start': start,
		'page_len': page_len,
		'work': filters.get('work'),
		'txt': f"%{txt}%"  
	}

	return frappe.db.sql("""
		SELECT item_code, item_name
		FROM `tabPurchase Order Item`
		WHERE parent = %(work)s
		  AND item_code LIKE %(txt)s
		LIMIT %(start)s, %(page_len)s
	""", args)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_part_no(doctype, txt, searchfield, start, page_len, filters):
    customer_dc = filters.get('customer_dc_id')

    if not customer_dc:
        return []

    args = {
        'start': start,
        'page_len': page_len,
        'customer_dc': customer_dc,
        'txt': f"%{txt}%"
    }

    return frappe.db.sql("""
        SELECT c.part_no
        FROM `tabCustomer DC` p
        INNER JOIN `tabCustomer DC child` c ON p.name = c.parent
        WHERE p.name = %(customer_dc)s AND c.part_no LIKE %(txt)s
        LIMIT %(start)s, %(page_len)s
    """, args)



import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_purchase_invoice_from_subcontract_dn(source_name, target_doc=None):
	def postprocess(source, target):
		target.supplier = source.subcontractor
		target.items = []

		for d in target.subitem:
			qty = d.received_qty_in_nos if d.rate_uom == "Nos" else d.received_qty_in_kgs

			rate = d.rate  # Default
			

			target.append("items", {
				"item_code": d.service_name,
				"description": d.description or d.service_name,
				"qty": qty,
				"rate": rate,
				"amount": rate * qty,
				"uom": d.rate_uom,
				"stock_uom": d.rate_uom,
				"item_tax_template":d.item_tax_template,
				"expense_account":d.expense_account,
				"sub_account":d.sub_account,
				"cost_center":d.cost_center,
				"conversion_factor": 1
			})

		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def item_condition(source):
		# Include only items with pending quantity
		pending_nos = (source.delivery_qty_nos or 0) - (source.received_qty_in_nos or 0)
		pending_kgs = (source.delivery_qty_kgs or 0) - (source.received_qty_in_kgs or 0)
		return pending_nos > 0 or pending_kgs > 0

	doc = get_mapped_doc("Subcontract Delivery Note", source_name, {
		"Subcontract Delivery Note": {
			"doctype": "Purchase Invoice",
			"field_map": {
				"subcontractor": "supplier",
				"company": "company"
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Subcontract Delivery Item": {
			"doctype": "Subcontract Receipt Item",
			"field_map": {
				"service_name": "service_name",
				"customer_dc_id": "customer_dc_id",
				"customer_name": "customer_name",
				"process_name": "process_name",
				"description":"description",
				"part_name": "part_name",
				"part_no": "part_no",
				"dc_qty_nos": "dc_qty_nos",
				"dc_qty_kgs": "dc_qty_kgs",
				"delivery_qty_nos": "received_qty_in_nos",
				"delivery_qty_kgs": "received_qty_in_kgs",
				"rate": "rate",
				"rate_uom": "rate_uom",
				"parent": "subcontract_delivery_note",
				"name": "dn_details",
				"cost_center":"cost_center",
				"sub_account":"sub_account",
				"expense_account":"expense_account",
				"item_tax_template":"item_tax_template"
			},
			"postprocess": update_item_values,
			"condition": item_condition
		}
	}, target_doc, postprocess)

	return doc


def update_item_values(source, target, source_parent):
	# Calculate amount based on current invoice qty
	qty = target.received_qty_in_nos or target.received_qty_in_kgs or 0
	target.amount = (target.rate or 0) * qty

	# Balance = delivery - received so far (do NOT subtract current invoice qty again)
	target.balance_qty_nos = (source.delivery_qty_nos or 0) - (source.received_qty_in_nos or 0)
	target.balance_qty_kgs = (source.delivery_qty_kgs or 0) - (source.received_qty_in_kgs or 0)
