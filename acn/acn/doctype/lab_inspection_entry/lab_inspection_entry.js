// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lab Inspection Entry", {
    refresh(frm) {
        if (cur_frm.doc.inspect_info && cur_frm.doc.inspect_info.length > 0) {
            frm.add_custom_button("View checklist", () => {
                open_checklist_dialog(frm);
            });
        }
        cur_frm.get_field("test_results").grid.cannot_add_rows = true
        // cur_frm.fields_dict['test_results'].grid.wrapper.find('.grid-remove-all-rows').hide();
        // cur_frm.fields_dict['test_results'].grid.wrapper.find('.grid-remove-rows').hide();
        // frm.fields_dict['test_results'].grid.wrapper.find('.grid-delete-row').hide();
        // frm.fields_dict['test_results'].grid.wrapper.find('.edit-grid-row').hide();

    },
    setup(frm) {
        cur_frm.set_query("job_plan_id", function (frm) {
            return {
                query: 'acn.acn.doctype.job_execution_logsheet.job_execution_logsheet.job_plan',
                filters: { "internal_process_for": "Lab Inspection" }

            }
        });
    },
    job_plan_id(frm) {
        if (cur_frm.doc.job_plan_id) {

            frappe.call({
                method: "set_job_plan_details",
                doc: cur_frm.doc,
                callback: function (r) {
                    if (r.message) {
                        cur_frm.refresh()
                        open_checklist_dialog(frm);
                    }
                }
            });
        }
    },
    set_parameters: function (frm) {
        frappe.call({
            method: "set_plan",
            doc: cur_frm.doc,
            callback: function (r) {
                if (r.message) {
                    cur_frm.dirty()
                    cur_frm.refresh()
                }
            }
        });
    },
});



frappe.ui.form.on("Lab inspection", {
    other_details: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        showOtherDetailsDialog(frm, row);
    },
    traverse_readings: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        showCaseDepthDialog(frm, row);
    }
});

function showOtherDetailsDialog(frm, row) {
    let dialog = new frappe.ui.Dialog({
        title: __('Other Details'),
        fields: [
            { label: __('Other Detail'), fieldname: 'other_detail_1', fieldtype: 'Data' },
            { fieldname: 'other_detail_2', fieldtype: 'Data' },
            { fieldname: 'other_detail_3', fieldtype: 'Data' },
            { fieldname: 'other_detail_4', fieldtype: 'Data' },
            { fieldname: 'other_detail_5', fieldtype: 'Data' },
            { label: __('Micro Structure'), fieldname: 'micro', fieldtype: 'Check', reqd: 1 },
            { label: __('Reference Standard'), fieldname: 'ref_standard', fieldtype: 'Data' },
            { label: __('Core'), fieldname: 'core', fieldtype: 'Data' },
            { label: __('Case'), fieldname: 'case', fieldtype: 'Data' },
            { fieldname: 'col_break', fieldtype: 'Column Break' },
            { fieldname: 'other_detail_6', fieldtype: 'Data' },
            { fieldname: 'other_detail_7', fieldtype: 'Data' },
            { fieldname: 'other_detail_8', fieldtype: 'Data' },
            { fieldname: 'other_detail_9', fieldtype: 'Data' }
        ],
        size: 'large',
        primary_action: function () {
            let values = dialog.get_values();

            Object.assign(row, values);

            frm.refresh();

            frappe.show_alert(__('Row updated successfully'));
            dialog.hide();
        },
        primary_action_label: __('Save')
    });

    let fieldnames = [
        'other_detail_1', 'other_detail_2', 'other_detail_3', 'other_detail_4', 'other_detail_5',
        'micro', 'ref_standard', 'core', 'case',
        'other_detail_6', 'other_detail_7', 'other_detail_8', 'other_detail_9'
    ];

    let prefilled_values = {};
    fieldnames.forEach(field => {
        if (row[field] !== undefined) {
            prefilled_values[field] = row[field];
        }
    });

    dialog.set_values(prefilled_values);
    dialog.show();
}






function showCaseDepthDialog(frm, row) {
    let dialog = new frappe.ui.Dialog({
        title: __('Case Depth Measurements'),
        fields: [
            { label: __('Case Depth'), fieldname: 'case_depth_1_1', fieldtype: 'Data' },
            { fieldname: 'case_depth_1_2', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_1_3', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_1_4', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_1_5', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_1_6', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_1_7', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_1_8', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_1_9', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_1_10', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },

            { fieldtype: 'Section Break' },
            { label: __('Hardness'), fieldname: 'hardness_1_1', fieldtype: 'Data' },
            { fieldname: 'hardness_1_2', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },

            { fieldname: 'hardness_1_3', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },

            { fieldname: 'hardness_1_4', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_1_5', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_1_6', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_1_7', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_1_8', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_1_9', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_1_10', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },

            { fieldtype: 'Section Break' },
            { label: __('Case Depth'), fieldname: 'case_depth_2_1', fieldtype: 'Data' },
            { fieldname: 'case_depth_2_2', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_2_3', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_2_4', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_2_5', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_2_6', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_2_7', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_2_8', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_2_9', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'case_depth_2_10', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },

            // Second Hardness Row (10 fields)
            { fieldtype: 'Section Break' },
            { label: __('Hardness'), fieldname: 'hardness_2_1', fieldtype: 'Data' },
            { fieldname: 'hardness_2_2', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_2_3', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_2_4', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_2_5', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_2_6', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_2_7', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_2_8', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_2_9', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldname: 'hardness_2_10', fieldtype: 'Data' },
            { fieldtype: 'Column Break' },
            { fieldtype: 'Section Break' },


        ],
        size: 'extra-large',
        primary_action: function () {
            let values = dialog.get_values();
            Object.assign(row, values);
            frm.refresh_field('items');
            frappe.show_alert(__('All measurements saved'));
            dialog.hide();
        },
        primary_action_label: __('Save')
    });

    let prefilled = {};

    // Case Depth 1
    for (let col = 1; col <= 10; col++) {
        if (row['case_depth_1_' + col] !== undefined) {
            prefilled['case_depth_1_' + col] = row['case_depth_1_' + col];
        }
    }

    // Hardness 1
    for (let col = 1; col <= 10; col++) {
        if (row['hardness_1_' + col] !== undefined) {
            prefilled['hardness_1_' + col] = row['hardness_1_' + col];
        }
    }

    // Case Depth 2
    for (let col = 1; col <= 10; col++) {
        if (row['case_depth_2_' + col] !== undefined) {
            prefilled['case_depth_2_' + col] = row['case_depth_2_' + col];
        }
    }

    // Hardness 2
    for (let col = 1; col <= 10; col++) {
        if (row['hardness_2_' + col] !== undefined) {
            prefilled['hardness_2_' + col] = row['hardness_2_' + col];
        }
    }



    dialog.set_values(prefilled);
    dialog.show();
}



function open_checklist_dialog(frm) {
    let existing_data = frm.doc.inspect_info || [];

    if (existing_data.length > 0) {
        let grouped = group_by_header(existing_data);
        render_checklist_dialog(frm, grouped);
    } else {
        frappe.call({
            method: "acn.acn.doctype.lab_inspection_entry.lab_inspection_entry.get_checklist",
            args: { "internal_process": cur_frm.doc.internal_process },
            callback: function (r) {
                if (r.message) {
                    let grouped = group_by_header(r.message);
                    render_checklist_dialog(frm, grouped);
                }
            }
        });
    }
}

function group_by_header(data) {
    const grouped = {};
    for (const row of data) {
        if (!grouped[row.header]) grouped[row.header] = [];
        grouped[row.header].push(row);
    }
    return grouped;
}

function render_checklist_dialog(frm, grouped_data) {
    let d = new frappe.ui.Dialog({
        title: 'Inspection Checklist',
        fields: [
            { fieldtype: 'HTML', fieldname: 'checklist_html' }
        ],
        size: 'extra-large',
        primary_action_label: 'Save',
        primary_action: async function () {
            frappe.dom.freeze("Saving, please wait...");

            const rows = $(d.wrapper).find('.checklist-row');
            let has_error = false;
            let data = [];

            rows.each(function () {
                const $row = $(this);
                const header = $row.data('header');
                const to_check = $row.data('check');
                const result = $row.find('select.result-select').val();
                const remarks = $row.find('textarea').val();
                const file_input = $row.find('input.image-upload')[0];
                const preview_img = $row.find('.preview-wrapper img');
                const existing_image_url = preview_img.length ? preview_img.attr('src') : null;
                 const options = $row.data('options'); 
                if (!result) {
                    has_error = true;
                    return false;
                }

               data.push({ 
                header, 
                to_check, 
                result, 
                remarks, 
                file_input, 
                existing_image_url,
                options: $row.data('options') 
                });
            });

            if (has_error) {
                frappe.dom.unfreeze();
                return frappe.msgprint("Please select an option for all rows.");
            }

            if (!frm.doc.name) {
                await frm.save();
            }

            frm.clear_table('inspect_info');

            for (const row of data) {
                let image_url = null;

                if (row.file_input?.files?.length) {
                    const file = row.file_input.files[0];
                    const form_data = new FormData();
                    form_data.append("file", file);
                    form_data.append("is_private", "0");
                    form_data.append("folder", "Home/Attachments");
                    form_data.append("doctype", frm.doctype);
                    form_data.append("docname", frm.doc.name);

                    const response = await fetch("/api/method/upload_file", {
                        method: "POST",
                        body: form_data,
                        headers: {
                            "X-Frappe-CSRF-Token": frappe.csrf_token,
                        },
                        credentials: 'same-origin'
                    });

                    const json = await response.json();
                    if (json.message?.file_url) {
                        image_url = json.message.file_url;
                    }
                } else if (row.existing_image_url) {
                    image_url = row.existing_image_url;
                }

                frm.add_child("inspect_info", {
                    header: row.header,
                    to_check: row.to_check,
                    result: row.result,
                    remarks: row.remarks,
                    image: image_url,
                     options: row.options
                });
            }

            await frm.save();
            frappe.dom.unfreeze();
            frappe.msgprint("Checklist saved successfully.");
            d.hide();
        }
    });

    // Disable save if doc is submitted
    setTimeout(() => {
        if (frm.doc.docstatus !== 0) {
            const $btn = d.get_primary_btn();
            if ($btn) $btn.prop("disabled", true);
        }
    }, 100);

    // Generate HTML dynamically
    let html = '';
    for (let header in grouped_data) {
        html += `<h4 style="margin-top: 20px;">${header}</h4>`;
        html += `<table class="table table-bordered" style="width:100%;"><thead>
            <tr>
                <th style="width: 30%">To Be Checked</th>
                <th style="width: 10%">Result</th>
                <th style="width: 30%">Remarks</th>
                <th style="width: 30%">Image</th>
            </tr></thead><tbody>`;

        grouped_data[header].forEach(row => {
            const saved_image_url = row.image || row.default_image || "";
            const options_list = (row.options || "").split(',').map(o => o.trim());

            html += `
                            <tr class="checklist-row" 
    data-header="${header}" 
    data-check="${row.to_check}" 
    data-options="${options_list.join(',')}">
                    <td>${row.to_check}</td>
                    <td>
                        <select class="form-control result-select">
                            <option value="">Select</option>
                            ${options_list.map(opt => `
                                <option value="${opt}" ${row.result === opt ? "selected" : ""}>${opt}</option>
                            `).join('')}
                        </select>
                    </td>
                    <td><textarea class="form-control" rows="2">${row.remarks || ""}</textarea></td>
                    <td style="text-align: center;">
                        <div class="preview-wrapper">
                            ${saved_image_url ? `<div style="margin-bottom:5px;">
                                <a href="${saved_image_url}" target="_blank" title="Click to view full image">
                                    <img src="${saved_image_url}" alt="Checklist Image"
                                        style="height:60px;border-radius:6px;box-shadow:0 0 5px rgba(0,0,0,0.15);transition:transform 0.2s;"
                                        onmouseover="this.style.transform='scale(1.1)'"
                                        onmouseout="this.style.transform='scale(1)'"
                                    />
                                </a>
                            </div>` : ''}
                        </div>
                       <label class="btn btn-sm btn-primary" style="margin-top: 2px;">
        Capture
        <input type="file" class="image-upload" accept="image/*" capture="environment" hidden />
    </label>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
    }

    d.fields_dict.checklist_html.$wrapper.html(html);
    d.show();

    // Image preview functionality
    $(d.wrapper).find('.image-upload').on('change', function () {
        const file = this.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            const $previewWrapper = $(this).closest('td').find('.preview-wrapper');
            reader.onload = function (e) {
                $previewWrapper.html(`
                    <div style="margin-bottom: 5px;">
                        <img src="${e.target.result}" alt="Preview"
                            style="height: 60px; border-radius: 6px; box-shadow: 0 0 5px rgba(0,0,0,0.15); transition: transform 0.2s;"
                            onmouseover="this.style.transform='scale(1.1)'"
                            onmouseout="this.style.transform='scale(1)'"
                        />
                    </div>
                `);
            };
            reader.readAsDataURL(file);
        }
    });
}


