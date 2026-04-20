import re

import frappe
from frappe import _


def _ensure_raven_installed():
	if "raven" not in frappe.get_installed_apps():
		frappe.throw(_("Raven is not installed on this site."))


def _get_linked_channel(organization: str):
	channel_name = frappe.db.get_value(
		"Raven Channel",
		{"linked_doctype": "CRM Organization", "linked_document": organization},
		"name",
	)
	if channel_name:
		return frappe.get_doc("Raven Channel", channel_name)

	stored_channel = frappe.db.get_value("CRM Organization", organization, "raven_channel")
	if stored_channel and frappe.db.exists("Raven Channel", stored_channel):
		return frappe.get_doc("Raven Channel", stored_channel)

	return None


def _get_workspace():
	workspaces = frappe.get_all("Raven Workspace", pluck="name")
	if len(workspaces) == 1:
		return workspaces[0]
	if len(workspaces) > 1:
		frappe.throw(
			_(
				"Multiple Raven workspaces exist. Please set the workspace in the CRM Raven integration before creating organization channels."
			)
		)
	frappe.throw(_("No Raven workspace found."))


def _get_channel_name(organization: str) -> str:
	channel_name = re.sub(r"[^a-z0-9]+", "-", organization.strip().lower())
	channel_name = re.sub(r"-{2,}", "-", channel_name).strip("-")
	return channel_name or f"organization-{frappe.generate_hash(length=6).lower()}"


def _serialize_channel(channel):
	return {
		"name": channel.name,
		"channel_name": channel.channel_name,
		"type": channel.type,
		"workspace": channel.workspace,
		"route": f"/raven/channel/{channel.name}",
	}


@frappe.whitelist()
def get_linked_raven_channel(organization: str):
	frappe.has_permission("CRM Organization", doc=organization, throw=True)
	_ensure_raven_installed()

	channel = _get_linked_channel(organization)
	if not channel:
		return {"channel": None}

	if frappe.db.get_value("CRM Organization", organization, "raven_channel") != channel.name:
		frappe.db.set_value("CRM Organization", organization, "raven_channel", channel.name, update_modified=False)

	return {"channel": _serialize_channel(channel)}


@frappe.whitelist()
def create_public_raven_channel(organization: str):
	frappe.has_permission("CRM Organization", doc=organization, ptype="write", throw=True)
	_ensure_raven_installed()

	channel = _get_linked_channel(organization)
	created = False

	if not channel:
		channel = frappe.get_doc(
			{
				"doctype": "Raven Channel",
				"channel_name": _get_channel_name(organization),
				"type": "Public",
				"linked_doctype": "CRM Organization",
				"linked_document": organization,
				"workspace": _get_workspace(),
			}
		)
		channel.insert(ignore_permissions=True)
		created = True

	frappe.db.set_value("CRM Organization", organization, "raven_channel", channel.name, update_modified=False)

	return {
		"channel": _serialize_channel(channel),
		"created": created,
	}
