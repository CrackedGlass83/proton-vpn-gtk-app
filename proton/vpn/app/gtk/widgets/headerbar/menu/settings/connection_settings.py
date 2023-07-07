"""
Connection settings module.


Copyright (c) 2023 Proton AG

This file is part of Proton VPN.

Proton VPN is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Proton VPN is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ProtonVPN.  If not, see <https://www.gnu.org/licenses/>.
"""

from gi.repository import Gtk
from proton.vpn.app.gtk.controller import Controller
from proton.vpn.app.gtk.widgets.main.notification_bar import NotificationBar
from proton.vpn.app.gtk.widgets.headerbar.menu.settings.common import (
    RECONNECT_MESSAGE, CategoryHeader, SettingRow, SettingName, SettingDescription
)


class ConnectionSettings(Gtk.Box):
    """Settings related to connection are all grouped under this class."""
    CATEGORY_NAME = "Connection"
    PROTOCOL_LABEL = "Protocol"
    VPN_ACCELERATOR_LABEL = "VPN Accelerator"
    VPN_ACCELERATOR_DESCRIPTION = "Increase your connection speed by up to 400% "\
        "with performance enhancing technologies."

    def __init__(self, controller: Controller, notification_bar: NotificationBar):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._controller = controller
        self._notification_bar = notification_bar

        self.set_halign(Gtk.Align.FILL)
        self.set_spacing(15)

        self.vpn_accelerator_row = None
        self.protocol_row = None

        self.get_style_context().add_class("setting-category")

    def build_ui(self):
        """Builds the UI, invoking all necessary methods that are
        under this category."""
        self.pack_start(CategoryHeader(self.CATEGORY_NAME), False, False, 0)
        self.build_protocol()
        self.build_vpn_accelerator()

    @property
    def protocol(self) -> str:
        """Shortcut property that returns the current `protocol` setting"""
        return self._controller.get_settings().protocol

    @protocol.setter
    def protocol(self, newvalue: str):
        """Shortcut property that sets the new `protocol` setting and
        stores to disk."""
        self._controller.get_settings().protocol = newvalue
        self._controller.save_settings()

    @property
    def vpn_accelerator(self) -> bool:
        """Shortcut property that returns the current `vpn_accelerator` setting"""
        return self._controller.get_settings().features.vpn_accelerator

    @vpn_accelerator.setter
    def vpn_accelerator(self, newvalue: bool):
        """Shortcut property that sets the new `vpn_accelerator` setting and
        stores to disk."""
        self._controller.get_settings().features.vpn_accelerator = newvalue
        self._controller.save_settings()

    def build_protocol(self):
        """Builds and adds the `protocol` setting to the widget."""
        def on_combobox_changed(combobox):
            model = combobox.get_model()
            treeiter = combobox.get_active_iter()
            protocol = model[treeiter][1]
            self.protocol = protocol
            if self._controller.is_connection_active:
                self._notification_bar.show_info_message(
                    f"{RECONNECT_MESSAGE}"
                )

        available_protocols = self._controller.get_available_protocols()
        protocol_combobox = Gtk.ComboBoxText()
        protocol_combobox.set_hexpand(True)
        protocol_combobox.set_halign(Gtk.Align.END)

        human_readeable_protocol = {
            "openvpn-tcp": "OpenVPN (TCP)",
            "openvpn-udp": "OpenVPN (UDP)",
        }

        for protocol in available_protocols:
            protocol_combobox.append(protocol, human_readeable_protocol.get(protocol, protocol))

        protocol_combobox.set_entry_text_column(1)
        protocol_combobox.set_active_id(self.protocol)
        protocol_combobox.connect("changed", on_combobox_changed)

        self.protocol_row = SettingRow(
            SettingName(self.PROTOCOL_LABEL),
            protocol_combobox
        )
        self.pack_start(self.protocol_row, False, False, 0)

    def build_vpn_accelerator(self):
        """Builds and adds the `vpn_accelerator` setting to the widget."""
        def on_switch_state(_, new_value: bool):
            self.vpn_accelerator = new_value
            if self._controller.is_connection_active:
                self._notification_bar.show_info_message(
                    f"{RECONNECT_MESSAGE}"
                )

        if not self._controller.vpn_data_refresher.client_config.feature_flags.vpn_accelerator:
            if self.vpn_accelerator:
                self.vpn_accelerator = False
            return

        vpn_accelerator_switch = Gtk.Switch()
        vpn_accelerator_switch.set_halign(Gtk.Align.END)
        vpn_accelerator_switch.set_hexpand(True)

        self.vpn_accelerator_row = SettingRow(
            SettingName(self.VPN_ACCELERATOR_LABEL),
            vpn_accelerator_switch,
            SettingDescription(self.VPN_ACCELERATOR_DESCRIPTION)
        )

        vpn_accelerator_switch.set_state(self.vpn_accelerator)
        vpn_accelerator_switch.connect("state-set", on_switch_state)
        self.pack_start(self.vpn_accelerator_row, False, False, 0)