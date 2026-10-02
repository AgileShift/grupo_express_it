const companies = [
	"Grupo SyM, S.A.",
	"Grupo Express, S.A.",
	"Importadora Internacional, S.A.",
	"Grupo de Importaciones Express, S.A.",
];

frappe.query_reports["Draft Policy Nationalization Costs"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Empresas"),
			fieldtype: "MultiSelectList",
			options: companies,
			default: 'All',
			on_change(query_report) {
				const selected = query_report.get_filter_value("company");

				if (!selected.length) {
					query_report.set_filter_value("company", companies);
					return;
				}

				query_report.refresh();
			},
		},
	],
};
