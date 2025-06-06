
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt



def on_cancel(self, method=None):
    if self.supplier_payment:
        frappe.throw("Can't cancel this entry as it is system-generated from Supplier Payment")
