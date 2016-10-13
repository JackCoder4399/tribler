from time import localtime, strftime

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem

from TriblerGUI.utilities import get_ui_file_path, format_size
from TriblerGUI.tribler_request_manager import performed_requests as tribler_performed_requests, TriblerRequestManager


class DebugWindow(QMainWindow):

    def __init__(self):
        super(DebugWindow, self).__init__()

        uic.loadUi(get_ui_file_path('debugwindow.ui'), self)
        self.setWindowTitle("Tribler debug pane")

        self.window().debug_tab_widget.setCurrentIndex(0)
        self.window().dispersy_tab_widget.setCurrentIndex(0)
        self.window().debug_tab_widget.currentChanged.connect(self.tab_changed)
        self.window().dispersy_tab_widget.currentChanged.connect(self.dispersy_tab_changed)
        self.load_general_tab()

    def tab_changed(self, index):
        if index == 0:
            self.load_general_tab()
        elif index == 1:
            self.load_requests_tab()
        elif index == 2:
            self.load_multichain_tab()
        elif index == 3:
            self.dispersy_tab_changed(self.window().dispersy_tab_widget.currentIndex())

    def dispersy_tab_changed(self, index):
        if index == 0:
            self.load_dispersy_general_tab()
        elif index == 1:
            self.load_dispersy_communities_tab()

    def create_and_add_widget_item(self, key, value, widget):
        item = QTreeWidgetItem(widget)
        item.setText(0, key)
        item.setText(1, "%s" % value)
        widget.addTopLevelItem(item)

    def load_general_tab(self):
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("statistics/tribler", self.on_tribler_statistics)

    def on_tribler_statistics(self, data):
        data = data["tribler_statistics"]
        self.window().general_tree_widget.clear()
        self.create_and_add_widget_item("Number of channels", data["num_channels"], self.window().general_tree_widget)
        self.create_and_add_widget_item("Database size", format_size(data["database_size"]),
                                        self.window().general_tree_widget)
        self.create_and_add_widget_item("Number of collected torrents", data["torrents"]["num_collected"],
                                        self.window().general_tree_widget)
        self.create_and_add_widget_item("Number of torrent files", data["torrents"]["num_files"],
                                        self.window().general_tree_widget)
        self.create_and_add_widget_item("Total size of torrent files", format_size(data["torrents"]["total_size"]),
                                        self.window().general_tree_widget)

    def load_requests_tab(self):
        self.window().requests_tree_widget.clear()
        for endpoint, method, data, timestamp, status_code in sorted(tribler_performed_requests.values(), key=lambda x: x[3]):
            item = QTreeWidgetItem(self.window().requests_tree_widget)
            item.setText(0, "%s %s %s" % (method, endpoint, data))
            item.setText(1, "%d" % status_code)
            item.setText(2, "%s" % strftime("%H:%M:%S", localtime(timestamp)))
            self.window().requests_tree_widget.addTopLevelItem(item)

    def load_multichain_tab(self):
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("multichain/statistics", self.on_multichain_statistics)

    def on_multichain_statistics(self, data):
        self.window().multichain_tree_widget.clear()
        for key, value in data["statistics"].iteritems():
            self.create_and_add_widget_item(key, value, self.window().multichain_tree_widget)

    def load_dispersy_general_tab(self):
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("statistics/dispersy", self.on_dispersy_general_stats)

    def on_dispersy_general_stats(self, data):
        self.window().dispersy_general_tree_widget.clear()
        for key, value in data["dispersy_statistics"].iteritems():
            self.create_and_add_widget_item(key, value, self.window().dispersy_general_tree_widget)

    def load_dispersy_communities_tab(self):
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("statistics/communities", self.on_dispersy_community_stats)

    def on_dispersy_community_stats(self, data):
        self.window().communities_tree_widget.clear()
        for community in data["community_statistics"]:
            item = QTreeWidgetItem(self.window().communities_tree_widget)
            item.setText(0, community["classification"])
            item.setText(1, community["identifier"][:6])
            item.setText(2, community["member"][:6])
            item.setText(3, "%s" % community["candidates"])
            self.window().communities_tree_widget.addTopLevelItem(item)
