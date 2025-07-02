frappe.ui.form.on('Journal Entry', {
    setup: function (frm) {
        cur_frm.cscript.onload = function () {
            frm.set_query("account", "accounts", function (doc, cdt, cdn) {
                const row = locals[cdt][cdn];
                const ns = doc.naming_series;
                const idx = row.idx;

                let filters = {
                    company: doc.company,
                    is_group: 0,
                };

                if (["BR-.FY.-", "BJ-.FY.-"].includes(ns) && idx === 1) {
                    filters.account_type = "Bank";
                } else if (ns === "BP-.FY.-" && idx === 2) {
                    filters.account_type = "Bank";
                } else if (ns === "CD-.FY.-") {
                    if (idx === 1) filters.account_type = "Bank";
                    if (idx === 2) filters.account_type = "Cash";
                } else if (ns === "CP-.FY.-" && idx === 2) {
                    console.log("yeso")
                    filters.account_type = "Cash";
                } else if (ns === "CR-.FY.-" && idx === 1) {
                    filters.account_type = "Cash";
                } else if (ns === "DC-.FY.-") {
                    if (idx === 1) filters.account_type = "Cash";
                    if (idx === 2) filters.account_type = "Bank";
                }

                return { filters };
            });
        }
    },
    naming_series:function(frm){
        cur_frm.refresh()
        cur_frm.refresh()
        cur_frm.refresh()

    },

    async onload(frm) {
        if (cur_frm.is_new()){

            cur_frm.set_value("accounts", [])
        }
        console.log("iop")
        if (frm.doc.company) {
            const company_doc = await frappe.db.get_doc("Company", frm.doc.company);
            frm.default_bank_account = company_doc.default_bank_account;
            frm.default_cash_account = company_doc.default_cash_account;
        }
    }
});


frappe.ui.form.on('Journal Entry Account', {
    accounts_add: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const ns = frm.doc.naming_series;
        const idx = row.idx;

        if (["BR-.FY.-", "BJ-.FY.-"].includes(ns) && idx === 1) {
            frappe.model.set_value(cdt, cdn, "account", frm.default_bank_account);
        }
        if (ns === "BP-.FY.-" && idx === 2) {
            frappe.model.set_value(cdt, cdn, "account", frm.default_bank_account);
        }
        if (ns === "CD-.FY.-") {
            if (idx === 1) frappe.model.set_value(cdt, cdn, "account", frm.default_bank_account);
            if (idx === 2) frappe.model.set_value(cdt, cdn, "account", frm.default_cash_account);
        }
        if (ns === "CP-.FY.-" && idx === 2) {
            frappe.model.set_value(cdt, cdn, "account", frm.default_cash_account);
        }
        if (ns === "CR-.FY.-" && idx === 1) {
            frappe.model.set_value(cdt, cdn, "account", frm.default_cash_account);
        }
        if (ns === "DC-.FY.-") {
            if (idx === 1) frappe.model.set_value(cdt, cdn, "account", frm.default_cash_account);
            if (idx === 2) frappe.model.set_value(cdt, cdn, "account", frm.default_bank_account);
        }
    }
});
