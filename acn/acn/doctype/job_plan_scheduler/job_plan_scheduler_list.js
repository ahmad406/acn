
frappe.views.calendar["Job Plan Scheduler"] = {
    field_map: {
        start: "job_loading_plan_date",
        end: "job_loading_plan_date",
        id: "name",
        title: "name",
        allDay: "all_day"
    },
    gantt: true
};
