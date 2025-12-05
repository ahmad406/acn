import frappe


def validate(self,method=None):
    set_delivery_note_header(self)




def set_delivery_note_header(self, method=None):
    # If no items, skip
    if not self.items:
        return

    # Fetch delivery note from first row
    dn = self.items[0].delivery_note

    # If there is a delivery note, store in header field `dl`
    if dn:
        self.dl = dn
