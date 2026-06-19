import frappe
from frappe.contacts.doctype.address.address import get_address_display


@frappe.whitelist()
def update_bill_from_info(stock_entry, bill_from_address):
    addr = frappe.db.get_value(
        "Address",
        bill_from_address,
        ["gstin", "gst_category"],
        as_dict=True,
    )
    if not addr:
        frappe.throw("Address not found.")

    display = get_address_display(frappe.get_doc("Address", bill_from_address).as_dict())

    frappe.db.set_value("Stock Entry", stock_entry, {
        "bill_from_address": bill_from_address,
        "bill_from_gstin": addr.gstin,
        "bill_from_gst_category": addr.gst_category,
    }, update_modified=False)

    frappe.db.commit()
    return True