// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lab Inspection Entry", {
	refresh(frm) {
      

	},
    setup(frm) {
        console.log("lep")
        cur_frm.set_query("job_plan_id", function (frm) {
			return {
				 query: 'acn.acn.doctype.job_execution_logsheet.job_execution_logsheet.job_plan',
				 filters: {"internal_process_for":"Lab Inspection"}

			}	
		});
    },
    job_plan_id(frm) {
		frappe.call({
            method: "set_job_plan_details",
			doc: cur_frm.doc,
            callback: function(r) {
                if (r.message) {
                   cur_frm.refresh()
                }
            }
        });
	},
    set_parameters:function(frm) {
		frappe.call({
            method: "set_plan",
			doc: cur_frm.doc,
            callback: function(r) {
                if (r.message) {
                    cur_frm.dirty()
                   cur_frm.refresh()
                }
            }
        });
	},
});



frappe.ui.form.on("Lab inspection", {
    other_details: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        showOtherDetailsDialog(frm, row);
    },
    traverse_readings: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        showCaseDepthDialog(frm, row);
    }
}); 

function showOtherDetailsDialog(frm, row) {
    let dialog = new frappe.ui.Dialog({
        title: __('Other Details'),
        fields: [
            {label: __('Other Detail'), fieldname: 'other_detail_1', fieldtype: 'Data'},
            {fieldname: 'other_detail_2', fieldtype: 'Data'},
            {fieldname: 'other_detail_3', fieldtype: 'Data'},
            {fieldname: 'other_detail_4', fieldtype: 'Data'},
            {fieldname: 'other_detail_5', fieldtype: 'Data'},
            {label: __('Micro Structure'), fieldname: 'micro', fieldtype: 'Check', reqd: 1},
            {label: __('Reference Standard'), fieldname: 'ref_standard', fieldtype: 'Data'},
            {label: __('Core'), fieldname: 'core', fieldtype: 'Data'},
            {label: __('case'), fieldname: 'case', fieldtype: 'Data'},
            {fieldname: 'col_break', fieldtype: 'Column Break'},
            {fieldname: 'other_detail_6', fieldtype: 'Data'},
            {fieldname: 'other_detail_7', fieldtype: 'Data'},
            {fieldname: 'other_detail_8', fieldtype: 'Data'},
            {fieldname: 'other_detail_9', fieldtype: 'Data'}
        ],
        size: 'large',
        primary_action: function() {
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
            // First Case Depth Row (10 fields)
            {label: __('Case Depth'), fieldname: 'case_depth_1_1', fieldtype: 'Data'},
            {fieldname: 'case_depth_1_2', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_1_3', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_1_4', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_1_5', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_1_6', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_1_7', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_1_8', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_1_9', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_1_10', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            
            // First Hardness Row (10 fields)
            {fieldtype: 'Section Break'},
            {label: __('Hardness'), fieldname: 'hardness_1_1', fieldtype: 'Data'},
            {fieldname: 'hardness_1_2', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},

            {fieldname: 'hardness_1_3', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},

            {fieldname: 'hardness_1_4', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_1_5', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_1_6', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_1_7', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_1_8', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_1_9', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_1_10', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            
            // Second Case Depth Row (10 fields)
            {fieldtype: 'Section Break'},
            {label: __('Case Depth'), fieldname: 'case_depth_2_1', fieldtype: 'Data'},
            {fieldname: 'case_depth_2_2', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_2_3', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_2_4', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_2_5', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_2_6', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_2_7', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_2_8', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_2_9', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'case_depth_2_10', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            
            // Second Hardness Row (10 fields)
            {fieldtype: 'Section Break'},
            {label: __('Hardness'), fieldname: 'hardness_2_1', fieldtype: 'Data'},
            {fieldname: 'hardness_2_2', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_2_3', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_2_4', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_2_5', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_2_6', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_2_7', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_2_8', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_2_9', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldname: 'hardness_2_10', fieldtype: 'Data'},
            {fieldtype: 'Column Break'},
            {fieldtype: 'Section Break'},
            
          
        ],
        size: 'extra-large',
        primary_action: function() {
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