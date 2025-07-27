
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
    validate_Subcontract_item(self)
    
            # d.purchase_order=None
def validate_Subcontract_item(self):
    for d in self.get("subitem", []):  
        if flt(d.received_qty_in_nos) > flt(d.balance_qty_nos):
            frappe.throw(
                _("Row {0}: Received Quantity in Nos ({1}) cannot be greater than Balance Quantity ({2})").format(
                    d.idx,
                    flt(d.received_qty_in_nos),
                    flt(d.balance_qty_nos)
                ),
                title=_("Quantity Validation Error")
            )
        
        if flt(d.received_qty_in_kgs) > flt(d.balance_qty_kgs):
            frappe.throw(
                _("Row {0}: Received Quantity in Kgs ({1}) cannot be greater than Balance Quantity ({2})").format(
                    d.idx,
                    flt(d.received_qty_in_kgs),
                    flt(d.balance_qty_kgs)
                ),
                title=_("Quantity Validation Error")
            )


def on_submit(self, method=None):
    update_subcontract_qty(self,is_cancel=False)

def on_cancel(self, method=None):
    update_subcontract_qty(self,is_cancel=True)

def update_subcontract_qty(self, is_cancel=True):
    for d in self.subitem:
        if d.subcontract_delivery_note:
            dn = frappe.get_doc("Subcontract Delivery Note", d.subcontract_delivery_note)
            for n in dn.items:
                if d.dn_details == n.name:
                    if is_cancel:
                        new_nos = (n.received_qty_in_nos or 0) - (d.received_qty_in_nos or 0)
                        new_kgs = (n.received_qty_in_kgs or 0) - (d.received_qty_in_kgs or 0)
                    else:
                        new_nos = (n.received_qty_in_nos or 0) + (d.received_qty_in_nos or 0)
                        new_kgs = (n.received_qty_in_kgs or 0) + (d.received_qty_in_kgs or 0)

                    n.db_set("received_qty_in_nos", new_nos)
                    n.db_set("received_qty_in_kgs", new_kgs)
