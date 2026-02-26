frappe.query_reports["Material Stock Statement"] = {

    filters: [
        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer",
            reqd: 1
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1
        }
    ],
onload: function(report) {

    report.page.add_inner_button("Export With Summary", function () {

        const filters = report.get_values();

        const query = new URLSearchParams({
            cmd: "acn.acn.report.material_stock_statement.material_stock_statement.export_with_summary",
            filters: JSON.stringify(filters)
        });

        // DIRECT DOWNLOAD
        window.location.href = "/api/method?" + query.toString();

    });

},

    after_datatable_render: function (report) {
        console.log("hi");


        // remove old block
        document.getElementById("stock-footer-container")?.remove();

        const wrapper = document.querySelector(".report-wrapper");
        const rows = report.datamanager?.data || [];
        const from_date = frappe.datetime.str_to_user(
            frappe.query_report.get_filter_value("from_date")
        );

        const to_date = frappe.datetime.str_to_user(
            frappe.query_report.get_filter_value("to_date")
        );


        if (!wrapper || !rows.length) return;


        /* CALCULATE TOTALS */

        let opening = 0,
            received = 0,
            dispatched = 0,
            closing = 0;

        rows.forEach(row => {

            if (row.particulars === "OPENING STOCK") {
                opening += flt(row.opening_qty_nos);
            }
            if (row.particulars === "MATERIAL RECEIVED") {
                received += flt(row.opening_qty_nos);
                
            }
            dispatched += flt(row.dispatch_qty_nos);
            closing += flt(row.pending_qty_nos);

        });

        /* MAIN FLEX CONTAINER */
        const container = document.createElement("div");
        container.id = "stock-footer-container";

        container.style.display = "flex";
        container.style.justifyContent = "space-between";
        container.style.alignItems = "flex-start";
        container.style.marginTop = "30px";
        container.style.gap = "30px";

        /* LEFT SIDE (TERMS) */
        const left = document.createElement("div");
        left.style.flex = "1";

        left.innerHTML = `
        <p>If this statement is related to your material laying with us, please note the following:</p>
        <ol>
            <li>Review the details for accuracy and ensure they align with your stock book/ledger.</li>
            <li>If any discrepancy in stock quantity or missing items, please revert within one week.</li>
        </ol>
        <b>
            Kindly sign and return the statement within one week. 
            If no reply is received, we will assume the stock is correct and undisputed.
        </b>
    `;

        /* RIGHT SIDE (SUMMARY TABLE) */
        const right = document.createElement("div");
        right.style.minWidth = "420px";

        right.innerHTML = `
    <table style="border-collapse:collapse;width:100%;font-weight:600;">
        <tr>
            <td style="border:1px solid #ccc;padding:6px;">
                OPENING STOCK AS ON ${from_date}
            </td>
            <td style="border:1px solid #ccc;padding:6px;text-align:right;">
                ${opening}
            </td>
        </tr>

        <tr>
            <td style="border:1px solid #ccc;padding:6px;">
                MATERIAL RECEIPT FROM ${from_date} TO ${to_date}
            </td>
            <td style="border:1px solid #ccc;padding:6px;text-align:right;">
                ${received}
            </td>
        </tr>

        <tr>
            <td style="border:1px solid #ccc;padding:6px;">
                MATERIAL DESPATCHED FROM ${from_date} TO ${to_date}
            </td>
            <td style="border:1px solid #ccc;padding:6px;text-align:right;">
                ${dispatched}
            </td>
        </tr>

        <tr>
            <td style="border:1px solid #ccc;padding:6px;">
                CLOSING STOCK AS ON ${to_date}
            </td>
            <td style="border:1px solid #ccc;padding:6px;text-align:right;">
                ${closing}
            </td>
        </tr>
    </table>
`;

        container.appendChild(left);
        container.appendChild(right);

        wrapper.appendChild(container);
    }
};