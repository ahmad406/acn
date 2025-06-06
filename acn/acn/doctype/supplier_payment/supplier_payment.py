# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt



import frappe
from frappe.model.document import Document
from frappe import _

class SupplierPayment(Document):
	def validate(self):
		self.validate_required_fields()
		self.validate_allocated_amount()
		self.validate_total_vs_cheque()

	@frappe.whitelist()
	def get_ref_doc_details(self, row):
		for d in self.supplier_details:
			if str(d.idx) == str(row.get("idx")):
				if d.type == "Purchase Invoice":
					out, grand = frappe.get_value("Purchase Invoice", d.name_ref, ["outstanding_amount", "grand_total"])
					d.grand_total = grand
					d.outstanding = out
					d.allocated_amount = out
					return

				if d.type == "Journal Entry":
					sql = """
						SELECT
							SUM(amount) AS outstanding,
							SUM(CASE WHEN against_voucher_no = voucher_no THEN amount ELSE 0 END) AS grand_total
						FROM `tabPayment Ledger Entry`
						WHERE against_voucher_type = 'Journal Entry'
						AND against_voucher_no = %s
						AND DeLinked = 0
					"""
					data = frappe.db.sql(sql, (d.name_ref,), as_dict=True)
					if data and data[0]:
						d.grand_total = data[0].grand_total or 0
						d.outstanding = data[0].outstanding or 0
						d.allocated_amount = d.outstanding
					return



	def validate_required_fields(self):
		if not self.date_of_cheque:
			frappe.throw(_("Date of cheque is required."))

		if not self.company:
			frappe.throw(_("Company is required."))

		if not self.bank:
			frappe.throw(_("Bank is required."))

		if not self.cheque_no:
			frappe.throw(_("Cheque No is required."))

		if not self.cheque_amount or self.cheque_amount <= 0:
			frappe.throw(_("Cheque Amount must be greater than zero."))

		if not self.supplier_details:
			frappe.throw(_("Please add at least one row in Supplier Details."))

		default_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		if not default_account:
			frappe.throw(_("Default Payable Account is not set for company {0}").format(self.company))

		for i, row in enumerate(self.supplier_details, start=1):
			if not row.party_name:
				frappe.throw(_("Row {0}: Party Name is required.").format(i))
			if not row.type:
				frappe.throw(_("Row {0}: Type is required.").format(i))
			if not row.name_ref:
				frappe.throw(_("Row {0}: Reference Name is required.").format(i))
			if not row.account:
				row.account = default_account 
			if not row.allocated_amount or row.allocated_amount <= 0:
				frappe.throw(_("Row {0}: Allocated Amount must be greater than zero.").format(i))


	def validate_allocated_amount(self):
		for row in self.supplier_details:
				if row.allocated_amount > row.outstanding:
					frappe.throw(_("Row {0}: Allocated Amount cannot exceed Outstanding Amount.").format(row.idx))

	def validate_total_vs_cheque(self):
		total_allocated = sum(row.allocated_amount for row in self.supplier_details)
		if round(total_allocated, 2) != round(self.cheque_amount, 2):
			frappe.throw(_("Total Allocated Amount ({0}) must equal Cheque Amount ({1}).").format(
				frappe.format_value(total_allocated, dict(fieldtype="Currency")),
				frappe.format_value(self.cheque_amount, dict(fieldtype="Currency"))
			))




	def on_submit(self):
		self.create_journal_entry()
	def on_cancel(self):
		sql="""select * from `tabJournal Entry` where supplier_payment="{}" """.format(self.name)
		data=frappe.db.sql(sql,as_dict=1)
		for d in data:
			je = frappe.get_doc("Journal Entry",d.name)
			je.db_set("supplier_payment",None)
			if je.docstatus==1:
				je.cancel()
			je.delete()


	def create_journal_entry(self):
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.date_of_cheque
		je.company = self.company
		je.reference_number = self.cheque_no
		je.reference_date = self.date_of_cheque
		je.user_remark = f"Auto created from Supplier Payment with {self.name}"


		je.append("accounts", {
			"account": self.bank,
			"credit_in_account_currency": self.cheque_amount
		})

		for row in self.supplier_details:
			je.append("accounts", {
				"account": row.account,
				"party_type": "Supplier",
				"party": row.party_name,
				"debit_in_account_currency": row.allocated_amount,
				"reference_type": row.type,
				"reference_name": row.name_ref
			})
		je.supplier_payment=self.name
		je.save()
		je.submit()


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_reference_docs(doctype, txt, searchfield, start, page_len, filters=None):
    filters = filters or {}

    doctype_filter = filters.get('doctype')
    party_name = filters.get('party_name')
    company = filters.get('company')

    if not doctype_filter or not party_name:
        return []

    txt = txt or ""

    if doctype_filter == "Purchase Invoice":
        conditions = [
            "docstatus = 1",
            "outstanding_amount > 0",
            "supplier = %(party_name)s"
        ]
        params = {
            "party_name": party_name
        }

        if company:
            conditions.append("company = %(company)s")
            params["company"] = company

        if txt:
            conditions.append(f"{searchfield} LIKE %(txt)s")
            params["txt"] = f"%{txt}%"

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT name
            FROM `tabPurchase Invoice`
            WHERE {where_clause}
            ORDER BY posting_date DESC
            LIMIT %(start)s, %(page_len)s
        """

        params.update({
            "start": start,
            "page_len": page_len
        })

        return frappe.db.sql(query, params)

    elif doctype_filter == "Journal Entry":
        conditions = [
            "against_voucher_type = 'Journal Entry'",
            "DeLinked = 0",
            "party = %(party_name)s"
        ]
        params = {
            "party_name": party_name,
            "start": start,
            "page_len": page_len
        }

        if company:
            conditions.append("company = %(company)s")
            params["company"] = company

        where_clause = " AND " + " AND ".join(conditions)

        query = f"""
            SELECT against_voucher_no, SUM(amount)
            FROM `tabPayment Ledger Entry`
            WHERE 1=1 {where_clause}
            GROUP BY against_voucher_no
            HAVING SUM(amount) > 0
            ORDER BY against_voucher_no DESC
            LIMIT %(start)s, %(page_len)s
        """

        # Use as_dict=False to avoid KeyError
        raw_results = frappe.db.sql(query, params, as_dict=False)

        # Filter by txt manually if needed
        if txt:
            raw_results = [r for r in raw_results if txt.lower() in r[0].lower()]

        # Return only voucher numbers for autocomplete
        return [[r[0]] for r in raw_results]

    else:
        return []
