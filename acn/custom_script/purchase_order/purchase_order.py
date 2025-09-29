import frappe
from frappe.model.document import Document



@frappe.whitelist()
def before_submit(self, method=None):
    if self.reopen:
        frappe.throw("This Purchase Order is reopened. You cannot submit it. Please click on Re-Close first.")
 

@frappe.whitelist()
def reopen_order(name,docstatus=0):
    """
    Reopen a submitted Purchase Order by setting flags
    """
    try:
        docstatus = int(docstatus)
        po = frappe.get_doc("Purchase Order", name)
        
      
        po.db_set("docstatus",docstatus)
        po.db_set("reopen", 0 if docstatus else 1)


        for d in  po.items:
            d.db_set("docstatus",docstatus)
        for d in  po.taxes:
            d.db_set("docstatus",docstatus)


        frappe.db.commit()

        return {"status": "success", "message": f"Purchase Order {name} reopened successfully."}
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Reopen Purchase Order Error")
        return {"status": "error", "message": str(e)}
