import frappe


def validate(self,method=None):
    set_delivery_note_header(self)
    set_po_details_from_customer_dc(self)




def set_delivery_note_header(self, method=None):
    # If no items, skip
    if not self.items:
        return

    # Fetch delivery note from first row
    dn = self.items[0].delivery_note

    # If there is a delivery note, store in header field `dl`
    if dn:
        self.dl = dn


def set_po_details_from_customer_dc(self, method=None):

    if not self.items:
        return

    first_row = self.items[0]

    if not first_row.customer_dc_id:
        return

    dc = frappe.db.get_value(
        "Customer DC",
        first_row.customer_dc_id,
        ["customer_order_no", "customer_order_date"],
        as_dict=True
    )

    if not dc:
        return

    self.po_no = dc.customer_order_no
    self.po_date = dc.customer_order_date