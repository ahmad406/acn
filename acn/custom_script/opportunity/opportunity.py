import frappe
from frappe.model.mapper import get_mapped_doc
from erpnext.crm.doctype.lead.lead import _set_missing_values
from erpnext.crm.doctype.opportunity.opportunity import (
	make_quotation as original_make_quotation
)


@frappe.whitelist()
def make_opportunity(source_name, target_doc=None):
	def set_missing_values(source, target):
		_set_missing_values(source, target)

	target_doc = get_mapped_doc(
		"Lead",
		source_name,
		{
			"Lead": {
				"doctype": "Opportunity",
				"field_map": {
					"campaign_name": "campaign",
					"doctype": "opportunity_from",
					"name": "party_name",
					"lead_name": "contact_display",
					"company_name": "customer_name",
					"email_id": "contact_email",
					"mobile_no": "contact_mobile",
					"lead_owner": "opportunity_owner",
					"notes": "notes",
					"company_name":"organization_name"
				},
			}
		},
		target_doc,
		set_missing_values,
	)

	return target_doc



def copy_opportunity_attachments(doc, method):

	if not doc.opportunity:
		return

	files = frappe.get_all(
		"File",
		filters={
			"attached_to_doctype": "Opportunity",
			"attached_to_name": doc.opportunity
		},
		fields=[
			"file_name",
			"file_url",
			"is_private"
		]
	)

	for file in files:

		exists = frappe.db.exists(
			"File",
			{
				"attached_to_doctype": "Quotation",
				"attached_to_name": doc.name,
				"file_url": file.file_url
			}
		)

		if exists:
			continue

		new_file = frappe.new_doc("File")

		new_file.update({
			"file_name": file.file_name,
			"file_url": file.file_url,
			"is_private": file.is_private,
			"attached_to_doctype": "Quotation",
			"attached_to_name": doc.name
		})

		new_file.insert(ignore_permissions=True)


def update_opportunity_valuation_type(doc, method=None):
	try:
		amount = doc.opportunity_amount or 0

		doc.opportunity_valuation_type = (
			"High Value"
			if amount >= 100000
			else "Low Value"
		)

	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			f"Opportunity Valuation Update Failed - {doc.name}"
		)