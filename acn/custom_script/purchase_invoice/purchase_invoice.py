
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt



def validate(self, method=None):
    for d in self.items:
        if d.purchase_order:
            is_open_order = frappe.get_value("Purchase Order", d.purchase_order, "open_order")
            if is_open_order:
                d.po_detail=None
		d.apply_tds=1
                # d.purchase_order=None
