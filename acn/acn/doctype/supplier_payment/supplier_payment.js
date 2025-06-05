// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Supplier Payment", {
 setup: function (frm) {
    frm.set_query('bank', function(doc) {
      return {
        filters: {
          company: doc.company,
          account_type: 'Bank',
          is_group: 0,
          disabled: 0
        }
      };
    });
    frm.fields_dict.supplier_details.grid.get_field('account').get_query = function(doc, cdt, cdn) {
      return {
        filters: {
          company: doc.company,
          account_type: 'Payable',
          is_group: 0,
          disabled: 0
        }
      };
    };


    frm.fields_dict.supplier_details.grid.get_field('name_ref').get_query = function (doc, cdt, cdn) {
      const row = locals[cdt][cdn];

      if (!row.type || !row.party_name) {
        frappe.msgprint(__('Please select Type and Party Name first.'));
        return;
      }

       return {
        query: "acn.acn.doctype.supplier_payment.supplier_payment.get_reference_docs",
        filters: {
          doctype: row.type,
          party_name: row.party_name,
          company: doc.company
        }
      };
    };
  }
});

frappe.ui.form.on('Supplier Payment Details', {
  name_ref: function(frm, cdt, cdn) {
    const row = locals[cdt][cdn];

    if (!row.type || !row.name_ref) {
      return;
    }
    if (row.type=="Purchase Invoice"){
        
        frappe.db.get_doc(row.type, row.name_ref).then(doc => {
            frappe.model.set_value(cdt, cdn, 'grand_total', doc.grand_total || doc.total || 0);
            frappe.model.set_value(cdt, cdn, 'outstanding', doc.outstanding_amount || 0);
            frappe.model.set_value(cdt, cdn, 'allocated_amount', doc.outstanding_amount || 0);
        }).catch(() => {
            frappe.msgprint(__('Unable to fetch document data for {0}', [row.name_ref]));
        });
    }
  }
});
