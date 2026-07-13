app_name = "grupo_express_it"
app_title = "Grupo Express Invoice Tool"
app_publisher = "Agile Shift"
app_description = "Invoice Tool"
app_email = "contacto@gruporeal.org"
app_license = "MIT"

# Apps
# ------------------

required_apps = [
	'shridarpatil/frappe_whatsapp'
]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "grupo_express",
# 		"logo": "/assets/grupo_express/logo.png",
# 		"title": "Grupo Express IT",
# 		"route": "/grupo_express",
# 		"has_permission": "grupo_express.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, CSS files in header of desk.html
app_include_css = "grupo_express.bundle.css"
app_include_js = "grupo_express.bundle.js"

# include js, CSS files in header of web template
# web_include_css = "/assets/grupo_express_it/css/grupo_express_it.css"
# web_include_js = "/assets/grupo_express_it/js/grupo_express_it.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "grupo_express_it/public/scss/website"

# include js, CSS files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#    "Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "grupo_express_it.install.before_install"
# after_install = "grupo_express_it.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "grupo_express_it.notifications.get_notification_config"

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

override_doctype_class = {
	"WhatsApp Message": "grupo_express_it.config.overrides.CustomWhatsAppMessage"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#   }
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"grupo_express_it.tasks.all"
# 	],
# 	"daily": [
# 		"grupo_express_it.tasks.daily"
# 	],
# 	"hourly": [
# 		"grupo_express_it.tasks.hourly"
# 	],
# 	"weekly": [
# 		"grupo_express_it.tasks.weekly"
# 	]
# 	"monthly": [
# 		"grupo_express_it.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "grupo_express_it.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "grupo_express_it.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "grupo_express_it.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# Require all whitelisted methods to have type annotations
require_type_annotated_api_methods = True

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
ignore_translatable_strings_from = ["frappe"]
