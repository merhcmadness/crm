import frappe
from frappe import _


@frappe.whitelist()
def get_linked_docs(deal):
	Get all ERPNext documents linked to a CRM Deal
	result = {
		'quotations': [],
		'sales_orders': [],
		'invoices': [],
		'projects': [],
	}

	if frappe.db.table_exists('Quotation'):
		result['quotations'] = frappe.get_all(
			'Quotation',
			filters={'crm_deal': deal},
			fields=['name', 'status', 'grand_total', 'currency', 'transaction_date'],
			order_by='transaction_date desc',
		)

	if frappe.db.table_exists('Sales Order'):
		result['sales_orders'] = frappe.get_all(
			'Sales Order',
			filters={'crm_deal': deal},
			fields=['name', 'status', 'grand_total', 'currency', 'transaction_date'],
			order_by='transaction_date desc',
		)

	if frappe.db.table_exists('Sales Invoice'):
		result['invoices'] = frappe.get_all(
			'Sales Invoice',
			filters={'crm_deal': deal},
			fields=['name', 'status', 'grand_total', 'currency', 'posting_date'],
			order_by='posting_date desc',
		)

	if frappe.db.table_exists('Project'):
		result['projects'] = frappe.get_all(
			'Project',
			filters={'crm_deal': deal},
			fields=['name', 'status', 'percent_complete'],
			order_by='creation desc',
		)

	return result


@frappe.whitelist()
def create_project_from_deal(deal):
	Create an ERPNext Project from a CRM Deal
	if not frappe.db.table_exists('Project'):
		frappe.throw(_('ERPNext is required to create projects'))

	deal_doc = frappe.get_doc('CRM Deal', deal)

	# Check if project already exists
	existing = frappe.get_all('Project', filters={'crm_deal': deal}, limit=1)
	if existing:
		return existing[0].name

	project = frappe.new_doc('Project')
	project.project_name = deal_doc.custom_deal_name or deal_doc.organization or deal
	project.crm_deal = deal
	project.expected_start_date = frappe.utils.nowdate()
	if deal_doc.expected_closure_date:
		project.expected_end_date = deal_doc.expected_closure_date
	if deal_doc.deal_owner:
		project.owner = deal_doc.deal_owner

	project.insert(ignore_permissions=True)
	frappe.db.commit()
	return project.name
