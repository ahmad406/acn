app_name = "acn"
app_title = "ACN"
app_publisher = "Ahmad Sayyed"
app_description = "material process"
app_email = "ahmadsayyed@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "acn",
# 		"logo": "/assets/acn/logo.png",
# 		"title": "ACN",
# 		"route": "/acn",
# 		"has_permission": "acn.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/acn/css/acn.css"
# app_include_js = "/assets/acn/js/acn.js"

# include js, css files in header of web template
# web_include_css = "/assets/acn/css/acn.css"
# web_include_js = "/assets/acn/js/acn.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "acn/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {
     "Sales Order" : "custom_script/sales_order/sales_order.js",
     "Sales Invoice" : "custom_script/sales_invoice/sales_invoice.js",
     "Delivery Note" : "custom_script/delivery_note/delivery_note.js",
     "Journal Entry" : "custom_script/journal_entry/journal_entry.js",
     "Purchase Invoice" : "custom_script/purchase_invoice/purchase_invoice.js",
     "Purchase Order" : "custom_script/purchase_order/purchase_order.js",

    }
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "acn/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "acn.utils.jinja_methods",
# 	"filters": "acn.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "acn.install.before_install"
# after_install = "acn.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "acn.uninstall.before_uninstall"
# after_uninstall = "acn.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "acn.utils.before_app_install"
# after_app_install = "acn.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "acn.utils.before_app_uninstall"
# after_app_uninstall = "acn.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "acn.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
 "Sales Order": {
        "validate": "acn.custom_script.sales_order.sales_order.validate",
        
	},
    "Delivery Note": {
        "on_submit": "acn.custom_script.sales_order.sales_order.on_submit",
        "on_cancel": "acn.custom_script.sales_order.sales_order.on_cancel",
	},
    "Journal Entry": {
        "on_cancel": "acn.custom_script.journal_entry.journal_entry.on_cancel",
	},
 "Purchase Invoice": {
        "validate": "acn.custom_script.purchase_invoice.purchase_invoice.validate",
	 "on_submit": "acn.custom_script.purchase_invoice.purchase_invoice.on_submit",
	 "on_cancel": "acn.custom_script.purchase_invoice.purchase_invoice.on_cancel",
        },

         "Purchase Order": {
        "before_submit": "acn.custom_script.purchase_order.purchase_order.before_submit"
    }
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"acn.tasks.all"
# 	],
# 	"daily": [
# 		"acn.tasks.daily"
# 	],
# 	"hourly": [
# 		"acn.tasks.hourly"
# 	],
# 	"weekly": [
# 		"acn.tasks.weekly"
# 	],
# 	"monthly": [
# 		"acn.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "acn.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "acn.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "acn.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["acn.utils.before_request"]
# after_request = ["acn.utils.after_request"]

# Job Events
# ----------
# before_job = ["acn.utils.before_job"]
# after_job = ["acn.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"acn.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

