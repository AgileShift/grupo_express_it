const companies = [
	"Grupo SyM, S.A.",
	"Grupo Express, S.A.",
	"Importadora Internacional, S.A.",
	"Grupo de Importaciones Express, S.A.",
];

const cost_types = [
	{label: __("Nationalization"), value: "Nationalization"},
	{label: __("Customs Taxes"), value: "Customs Taxes"},
];
const cost_type_values = cost_types.map((type) => type.value);

frappe.query_reports["Draft Policy Nationalization Costs"] = {
	onload(query_report) {
		const company_filter = query_report.get_filter("companies");
		const selected_companies = company_filter.get_value() || [];

		if (!selected_companies.length) {
			company_filter.set_value(companies);
		}

		const type_filter = query_report.get_filter("types");
		const selected_types = type_filter.get_value() || [];

		if (!selected_types.length) {
			type_filter.set_value(['Nationalization']);
		}
	},

	filters: [
		{
			fieldname: "companies",
			label: __("Empresas"),
			fieldtype: "MultiSelectList",
			options: companies,

			on_change(query_report) {
				const selected =
					query_report.get_filter_value("companies") || [];

				if (!selected.length) {
					query_report.set_filter_value("companies", companies);
					return;
				}

				query_report.refresh();
			},
		},
		{
			fieldname: "types",
			label: __("Type"),
			fieldtype: "MultiSelectList",
			options: cost_types,

			on_change(query_report) {
				const selected =
					query_report.get_filter_value("types") || [];

				if (!selected.length) {
					query_report.set_filter_value(
						"types",
						cost_type_values
					);
					return;
				}

				query_report.refresh();
			},
		},
	],
};
