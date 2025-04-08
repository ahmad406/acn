
import frappe

def validate(self,method=None):
	for d in self.get("items"):
		if d.part_no and d.customer:
			process_details = get_process_rate(d.part_no, d.customer)
			d.custom_process_type = process_details.process_type
			d.custom_process_name = process_details.process_name
			d.material = process_details.material
			d.custom_rate_uom = process_details.rate_uom
			d.rate = process_details.process_rate
			if process_details.rate_uom=="Minimum":
				d.qty=1
			elif process_details.rate_uom=="Nos":
				d.qty=d.custom_qty_in_nos
			elif process_details.rate_uom=="Kgs":
				d.qty=d.custom_qty_in_kgs
			else:
				frappe.throw("Invalid Rate UOM: {0}".format(process_details.rate_uom))


@frappe.whitelist()
def get_process_rate(part_no, customer):
	result = frappe.db.sql("""
		SELECT c.process_rate, c.rate_uom,p.process_type,p.process_name,p.material
		FROM `tabCustomer Process` p
		INNER JOIN `tabPart No  Process Rate` c ON p.name = c.parent
		WHERE c.part_no = %s AND p.customer = %s
		LIMIT 1
	""", (part_no, customer), as_dict=True)
	if result:
		return result
	else:
		frappe.throw("Customer Process not found for <b>Part:no {0}  and Customer: {1} </b>".format(part_no, customer))

