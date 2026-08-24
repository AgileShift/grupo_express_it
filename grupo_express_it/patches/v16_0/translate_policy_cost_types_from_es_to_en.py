import frappe


def execute():
	"""Translate stored Policy cost types from Spanish to English."""
	# noinspection SpellCheckingInspection
	type_translations = {
		"Policy CIF Cost": {
			"Flete": "Freight",
			"Seguro": "Insurance",
		},
		"Policy Nationalization Cost": {
			"Impuestos Aduaneros": "Customs Taxes",
			"Nacionalizacion": "Nationalization",
		},
	}

	for doctype, translations in type_translations.items():
		for source, target in translations.items():
			frappe.db.set_value(
				doctype,
				{"type": source},
				"type",
				target,
				update_modified=False,
			)
