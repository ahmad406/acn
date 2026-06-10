# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate, nowdate


class SubcontractDeliveryNote(Document):

	def validate(self):
		self.validate_data()

	def validate_data(self):
		for d in self.items:
			if d.delivery_qty_nos is None or d.delivery_qty_nos <= 0:
				frappe.throw(
					_("Row {0}: Delivery Quantity (Nos) must be greater than zero.").format(d.idx)
				)

	def on_submit(self):
		make_stock_entry_on_submit(self)

	@frappe.whitelist()
	def get_item_details(self, row):
		item_details = frappe._dict()

		po = frappe.get_doc("Purchase Order", self.work_order_no)

		for d in po.items:
			if d.item_code == row.get("service_name"):
				item_details = {
					"description": d.description,
					"item_tax_template": d.item_tax_template,
					"expense_account": d.expense_account,
					"sub_account": d.sub_account,
					"cost_center": d.cost_center,
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
					"dc_qty_nos": d.qty_nos,
					"dc_qty_kgs": d.qty_kgs,
					"eway_bill_hsn": d.eway_bill_hsn,
					"rate": d.e_rate,
					"rate_uom": d.rate_uom
				}
				break

		return item_details


# ── Stock Entry on Submit ──────────────────────────────────────────────────────

def make_stock_entry_on_submit(sdn):
	se = frappe.new_doc("Stock Entry")

	se_type = frappe.db.get_value(
		"Stock Entry Type",
		{"purpose": "Material Issue"},
		"name"
	)
	if not se_type:
		frappe.throw(_("Stock Entry Type for 'Material Issue' not found."))

	se.stock_entry_type = se_type
	se.purpose = "Material Issue"
	se.company = sdn.company
	se.supplier = sdn.subcontractor

	company_address = frappe.db.get_value(
		"Address",
		{"is_your_company_address": 1},
		["name", "gstin", "gst_category"],
		as_dict=True
	)

	se.bill_from_address = company_address.name
	se.bill_from_gstin = company_address.gstin
	se.bill_from_gst_category = company_address.gst_category

	se.bill_to_address = frappe.db.get_value(
		"Supplier",
		{"name": se.supplier},
		"supplier_primary_address"
	)

	if se.bill_to_address:
		supplier_address = frappe.db.get_value(
			"Address",
			se.bill_to_address,
			["gstin", "gst_category"],
			as_dict=True
		)
		se.bill_to_gstin = supplier_address.gstin
		se.bill_to_gst_category = supplier_address.gst_category

	grand_total      = 0
	total_tax_amount = 0

	for row in sdn.items:
		stock_item_code, hsn, stock_item_name , stock_item_description = _get_or_create_stock_item(row)
		item_tax_template = get_valid_item_tax_template(hsn)

		basic_rate   = row.rate or 0
		if row.rate_uom == "Kgs":
			qty = row.delivery_qty_kgs or 0
		else:
			qty = row.delivery_qty_nos or 0
		basic_amount = basic_rate * qty

		# ── Fetch cumulative tax % from Item Tax Template ──────────────────────
		tax_rate    = _get_tax_rate_from_template(item_tax_template)
		tax_amount  = basic_amount * (tax_rate/2) / 100
		row_total   = basic_amount + tax_amount

		grand_total      += basic_amount
		total_tax_amount += tax_amount

		se.append("items", {
			"s_warehouse": "Stores - ACN",	
			"item_code": stock_item_code,
			"item_name":stock_item_name,
			"qty": qty,
			"uom": row.rate_uom,
			"conversion_factor": 1,
			"allow_zero_valuation_rate": 1,
			"description": stock_item_description,
			"item_tax_template": item_tax_template,
			"basic_rate": basic_rate,
			"basic_amount": basic_amount,
			"amount": basic_amount,
			"tax_amount": tax_amount,
			"tax_rate": tax_rate,
			"net_amount": row_total,
			"gst_hsn_code": hsn,
		})

	net_grand_total = grand_total + total_tax_amount

	se.base_grand_total  = net_grand_total
	se.total_taxes = total_tax_amount

	se.flags.ignore_validate  = True
	se.flags.ignore_permissions = True
	se.flags.ignore_mandatory = True
	se.flags.ignore_links     = True
	se.insert(ignore_permissions=True, ignore_mandatory=True)

	frappe.db.set_value("Stock Entry", se.name, "docstatus", 1)
	frappe.db.set_value("Subcontract Delivery Note", sdn.name, "stock_entry", se.name)

	frappe.msgprint(
		_("Stock Entry {0} created").format(
			frappe.utils.get_link_to_form("Stock Entry", se.name)
		),
		alert=True,
		indicator="green",
	)


def get_valid_item_tax_template(gst_hsn_code):
	"""
	Returns valid Item Tax Template from GST HSN Code
	based on validity dates.
	"""

	if not gst_hsn_code:
		return None

	hsn_doc = frappe.get_doc("GST HSN Code", gst_hsn_code)

	today = getdate(nowdate())

	valid_row = None

	for row in hsn_doc.taxes:

		valid_from = getdate(row.valid_from) if row.valid_from else None

		if valid_from and today < valid_from:
			continue

		valid_row = row
		break

	return valid_row.item_tax_template if valid_row else None


def _get_tax_rate_from_template(item_tax_template):
	"""
	Returns the cumulative tax rate (%) from an Item Tax Template.
	Sums all tax rates in the template's tax_rates child table.
	Returns 0 if template is not set or has no rates.
	"""
	if not item_tax_template:
		return 0

	rates = frappe.db.get_all(
		"Item Tax Template Detail",
		filters={"parent": item_tax_template},
		fields=["tax_rate"],
	)

	return sum(r.tax_rate or 0 for r in rates)


def _get_or_create_stock_item(row):
	result = frappe.db.get_value(
		"Customer DC child",
		{
			"parent": row.customer_dc_id,
			"part_no": row.part_no,
		},
		["item_code","eway_bill_hsn"],
		as_dict=True,
	)

	if not result or not result.item_code:
		frappe.throw(
			_("Row {0}: Could not find Part No <b>{1}</b> in Customer DC <b>{2}</b>").format(
				row.idx, row.part_no, row.customer_dc_id
			)
		)

	original_item_code = result.item_code
	stock_item_code = f"{original_item_code} - Subcontract Item"

	item_doc = frappe.get_doc("Item", original_item_code)

	if not frappe.db.exists("Item", stock_item_code):

		item = frappe.new_doc("Item")
		item.item_code = stock_item_code
		item.item_name = item_doc.item_name
		item.item_group = item_doc.item_group
		item.is_stock_item = 1
		item.stock_uom = item_doc.stock_uom
		item.gst_hsn_code = result.eway_bill_hsn
		item.description = item_doc.description

		# ── Fetch Taxes from GST HSN Code ─────────────────────
		if result.eway_bill_hsn:

			hsn_doc = frappe.get_doc("GST HSN Code", result.eway_bill_hsn)

			for tax in hsn_doc.taxes:

				item.append("taxes", {
					"item_tax_template": tax.item_tax_template,
					"tax_category": tax.tax_category,
				})

		item.insert(ignore_permissions=True)

	return (
		stock_item_code,
		result.eway_bill_hsn,
		item_doc.item_name,
		item_doc.description
	)		

# ── Search helpers ─────────────────────────────────────────────────────────────

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_items(doctype, txt, searchfield, start, page_len, filters):
	args = {
		"start": start,
		"page_len": page_len,
		"work": filters.get("work"),
		"txt": f"%{txt}%",
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
	customer_dc = filters.get("customer_dc_id")

	if not customer_dc:
		return []

	args = {
		"start": start,
		"page_len": page_len,
		"customer_dc": customer_dc,
		"txt": f"%{txt}%",
	}
	return frappe.db.sql("""
		SELECT c.part_no
		FROM `tabCustomer DC` p
		INNER JOIN `tabCustomer DC child` c ON p.name = c.parent
		WHERE p.name = %(customer_dc)s AND c.part_no LIKE %(txt)s
		LIMIT %(start)s, %(page_len)s
	""", args)


# ── Create Purchase Invoice ────────────────────────────────────────────────────

@frappe.whitelist()
def make_purchase_invoice_from_subcontract_dn(source_name, target_doc=None):
	def postprocess(source, target):
		target.supplier = source.subcontractor
		target.items = []

		for d in target.subitem:
			qty = d.received_qty_in_nos if d.rate_uom == "Nos" else d.received_qty_in_kgs
			rate = d.rate

			target.append("items", {
				"item_code": d.service_name,
				"description": d.description or d.service_name,
				"qty": qty,
				"rate": rate,
				"amount": rate * qty,
				"uom": d.rate_uom,
				"stock_uom": d.rate_uom,
				"item_tax_template": d.item_tax_template,
				"expense_account": d.expense_account,
				"sub_account": d.sub_account,
				"cost_center": d.cost_center,
				"conversion_factor": 1,
			})

		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def item_condition(source):
		pending_nos = (source.delivery_qty_nos or 0) - (source.received_qty_in_nos or 0)
		pending_kgs = (source.delivery_qty_kgs or 0) - (source.received_qty_in_kgs or 0)
		return pending_nos > 0 or pending_kgs > 0

	doc = get_mapped_doc("Subcontract Delivery Note", source_name, {
		"Subcontract Delivery Note": {
			"doctype": "Purchase Invoice",
			"field_map": {
				"subcontractor": "supplier",
				"company": "company",
			},
			"validation": {"docstatus": ["=", 1]},
		},
		"Subcontract Delivery Item": {
			"doctype": "Subcontract Receipt Item",
			"field_map": {
				"service_name": "service_name",
				"customer_dc_id": "customer_dc_id",
				"customer_name": "customer_name",
				"process_name": "process_name",
				"description": "description",
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
				"cost_center": "cost_center",
				"sub_account": "sub_account",
				"expense_account": "expense_account",
				"item_tax_template": "item_tax_template",
			},
			"postprocess": update_item_values,
			"condition": item_condition,
		},
	}, target_doc, postprocess)

	return doc


def update_item_values(source, target, source_parent):
	qty = target.received_qty_in_nos or target.received_qty_in_kgs or 0
	target.amount = (target.rate or 0) * qty
	target.balance_qty_nos = (source.delivery_qty_nos or 0) - (source.received_qty_in_nos or 0)
	target.balance_qty_kgs = (source.delivery_qty_kgs or 0) - (source.received_qty_in_kgs or 0)