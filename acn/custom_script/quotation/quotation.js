frappe.ui.form.on("Quotation Item", {
    uom_rate: function (frm, cdt, cdn) {
        calculate_opportunity_value(frm, cdt, cdn);
    },

    qty_in_nos: function (frm, cdt, cdn) {
        calculate_opportunity_value(frm, cdt, cdn);
    },

    qty_in_kgs: function (frm, cdt, cdn) {
        calculate_opportunity_value(frm, cdt, cdn);
    },

    rate: function (frm, cdt, cdn) {
        calculate_opportunity_value(frm, cdt, cdn);
    }
});

function calculate_opportunity_value(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    let rate = flt(row.rate);
    let value = 0;

    if (row.uom_rate == "Nos") {
        value = flt(row.qty_in_nos) * rate;

    } else if (row.uom_rate == "Kgs") {
        value = flt(row.qty_in_kgs) * rate;

    } else if (row.uom_rate == "Minimum") {
        value = 1 * rate;
    }

    frappe.model.set_value(
        cdt,
        cdn,
        "opportunity_value",
        value
    );
}