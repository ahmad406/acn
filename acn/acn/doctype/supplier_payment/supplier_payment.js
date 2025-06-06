// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Supplier Payment", {
  onload:function(frm){
frm.ignore_doctypes_on_cancel_all = ["Journal Entry"];
  },
  setup: function (frm) {
    frm.set_query('bank', function (doc) {
      return {
        filters: {
          company: doc.company,
          account_type: 'Bank',
          is_group: 0,
          disabled: 0
        }
      };
    });
    frm.fields_dict.supplier_details.grid.get_field('account').get_query = function (doc, cdt, cdn) {
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
  name_ref: function (frm, cdt, cdn) {
    const row = locals[cdt][cdn];

    if (!row.type || !row.name_ref) {
      return;
    }
    frappe.call({
      method: "get_ref_doc_details",
      doc: cur_frm.doc,
      args:{"row":row},
      callback: function (r) {
        if (r.message) {
          cur_frm.referesh()

        }
      }
    });
  }
});
