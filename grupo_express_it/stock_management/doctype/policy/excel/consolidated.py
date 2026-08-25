from io import BytesIO

from openpyxl.workbook import Workbook

import frappe
from frappe.desk.utils import provide_binary_file
from grupo_express_it.stock_management.doctype.policy.excel.unique import _write_policy, \
	_register_styles, _table_pre_header
from grupo_express_it.stock_management.doctype.policy.policy import Policy


@frappe.whitelist(allow_guest=False)
def download(policies: str) -> None:

	wb = Workbook()
	ws = wb.active          # Get Current Sheet

	_register_styles(wb)

	current_row = 1
	for policy in policies.split(','):
		doc = Policy('Policy', policy)

		current_row = _write_policy(ws, doc, current_row) + 4
		current_row = _table_pre_header(ws, row=current_row, col=2, value='', col_range=('A', 'N'))

	xlsx_file = BytesIO()
	wb.save(xlsx_file)
	provide_binary_file('Consolidado', 'xlsx', xlsx_file.getvalue())  # Build xlsx Response File -> See xlsxutils.py
