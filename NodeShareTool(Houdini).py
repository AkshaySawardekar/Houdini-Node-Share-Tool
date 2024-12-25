import os
import hou
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
 
dirPath = "/usr/people/akshay-sa/Desktop/Mill/Houdini_python/test"
 
class NodeSharingTool(QtWidgets.QWidget):
    def __init__(self):
        super(NodeSharingTool, self).__init__()
        self.setWindowTitle("Node Sharing Tool")
        self.setMinimumSize(300, 200)
        self.setWindowFlags(Qt.Window | Qt.Tool)
 
        layout = QtWidgets.QVBoxLayout(self)
        self.export_button = QtWidgets.QPushButton("Export Selected Nodes")
        self.import_button = QtWidgets.QPushButton("Import Nodes")
        self.file_list = QtWidgets.QListWidget()
 
        layout.addWidget(QtWidgets.QLabel("Available Shared Nodes:"))
        layout.addWidget(self.file_list)
        layout.addWidget(self.export_button)
        layout.addWidget(self.import_button)
 
        self.refresh_node_list()
 
        self.export_button.clicked.connect(self.take_userInput_to_saveNodeName)
        self.import_button.clicked.connect(self.import_nodes)
 
    def take_userInput_to_saveNodeName(self):
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Save Node")
        userInput_layout = QtWidgets.QVBoxLayout(dialog)
 
        name_input = QtWidgets.QLineEdit()
        userInput_layout.addWidget(name_input)
 
        save_button = QtWidgets.QPushButton("--Save--")
        cancel_button = QtWidgets.QPushButton("--Cancel")
        userInput_layout.addWidget(save_button)
        userInput_layout.addWidget(cancel_button)
 
        cancel_button.clicked.connect(dialog.reject)
 
        def save_and_close():
            filename = name_input.text().strip()
            if filename:
                filename += ".cpio"
                dialog.accept()
                self.export_nodes(filename)
            else:
                hou.ui.displayMessage("Filename cannot be empty")
        
        save_button.clicked.connect(save_and_close)
 
        dialog.exec_()
 
    def refresh_node_list(self):
        self.file_list.clear()
        if os.path.exists(dirPath):
            files = [f for f in os.listdir(dirPath) if f.endswith((".hip", ".hda", ".cpio"))]
            for f in files:
                displayName = f[:-5]
                self.file_list.addItems(files)
 
    def export_nodes(self, filename):
        sel = hou.selectedNodes()
        if not sel:
            hou.ui.displayMessage("No nodes selected to Export")
            return
        if not filename:
            hou.ui.displayMessage("Invalid Filename")
            return
 
        file_path = os.path.join(dirPath, filename)
        try:
            sel[0].parent().saveChildrenToFile(sel, [], file_path)
            self.refresh_node_list()
            hou.ui.displayMessage("Nodes succesfully Exported")
            self.close()
        except Exception as e:
            hou.ui.displayMessage("Failed to export nodes " + str(e))
 
 
    def import_nodes(self):
        selected_file = self.file_list.selectedItems()
        if not selected_file:
            hou.ui.displayMessage("No file selected")
            return
 
        network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
 
        if network_editor:
            parent_node = network_editor.pwd()
 
            selected_nodes = parent_node.selectedChildren()
            if selected_nodes:
                parent_node = selected_nodes[0]
        else:
            parent_node = hou.node('/obj').createNode("geo", "importedGeo")
 
        for file in selected_file:
            file_path = os.path.join(dirPath, file.text())
            try:
                parent_node.loadChildrenFromFile(file_path)
                #print('\n'*5 + "node created")
            except hou.OperationFailed:
                print("Failed to load " + file.text() + " into" + parent_node.path() + "trying a new geo")
                try :
                    temp_geo_node = parent_node.createNode("geo", "importGeo")
                    temp_geo_node.loadChildrenFromFile(file_path)
                except hou.OperationFailed as e:
                    print(str(e))
 
tool = NodeSharingTool()
tool.show()
