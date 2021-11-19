#!/usr/bin/env python3
# version 0.4.0

from PyQt5.QtWidgets import qApp, QSizePolicy, QBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QFileDialog, QDialogButtonBox, QApplication, QWidget, QHeaderView, QTreeWidget, QTreeWidgetItem, QPushButton, QDialog, QVBoxLayout, QGridLayout, QLabel
import sys
from PyQt5.QtGui import QIcon, QDrag, QPixmap
from PyQt5.QtCore import QObject, QEvent, Qt, QUrl, QMimeData, QSize, QMimeDatabase, QByteArray, QDataStream, QIODevice
import subprocess
import os, shutil
from xdg.BaseDirectory import *
from xdg.DesktopEntry import *

# usually 7z - 7za or compatible
EXTRACTOR="7z"

class firstMessage(QWidget):
    
    def __init__(self, *args):
        super().__init__()
        title = args[0]
        message = args[1]
        self.setWindowTitle(title)
        box = QBoxLayout(QBoxLayout.TopToBottom)
        box.setContentsMargins(5,5,5,5)
        self.setLayout(box)
        label = QLabel(message)
        box.addWidget(label)
        button = QPushButton("Close")
        box.addWidget(button)
        button.clicked.connect(self.close)
        self.show()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


WINW = 0
WINH = 0
WINM = ""
try:
    with open("winsize.cfg", "r") as ifile:
        fcontent = ifile.readline()
    aw, ah, am = fcontent.split(";")
    WINW = aw
    WINH = ah
    WINM = am.strip()
except:
    app = QApplication(sys.argv)
    fm = firstMessage("Error", "The file winsize.cfg cannot be read.")
    sys.exit(app.exec_())


class TreeWidget(QTreeWidget):
    
    def __init__(self, archive_path):
        QTreeWidget.__init__(self)
        self.archive_path = archive_path
        self.setSelectionMode(self.ExtendedSelection)
        self.customMimeType = "application/x-customqt5archiver"
        self.setDragEnabled(True)


    def startDrag(self, supportedActions):
        # EXTRACTION_TYPE: e is the mode for files - x for folders
        # archive name - extraction mode - item type - item name
        drag_data = "{}".format(self.archive_path)
        for iitem in self.selectedItems():
            item_path_temp = self.get_path(iitem)
            item_path = "/".join(item_path_temp)
            if iitem.data(3,0) == "file":
                EXTRACTION_TYPE = "e"
                item_type = "file"
                drag_data += "\n{}\n{}\n{}".format(EXTRACTION_TYPE, item_type, item_path)
            else:
                EXTRACTION_TYPE = "x"
                item_type = "folder"
                drag_data += "\n{}\n{}\n{}".format(EXTRACTION_TYPE, item_type, item_path)
        #
        drag = QDrag(self)
        #
        mimedata = QMimeData()
        # 
        data = QByteArray()
        data.append(bytes(drag_data, encoding="utf-8"))
        mimedata.setData(self.customMimeType, data)
        #
        drag.setMimeData(mimedata)
        pixmap = QPixmap("icons/extraction.png").scaled(48, 48, Qt.KeepAspectRatio)
        drag.setPixmap(pixmap)
        drag.exec_(supportedActions)
    
    
    # get the full path of the selected item
    def get_path(self, item):
        ipath = []
        if item:
            while item and item.data(0,0):
                ipath.insert(0, item.data(0,0))
                item = item.parent()
        #
        return ipath
    

class Window(QWidget):
    def __init__(self, path, hasPassWord):
        super(Window, self).__init__()
        self.setWindowIcon(QIcon("icons/qt5archiver.svg"))
        self.path = path
        # 2 yes - 1 no
        self.hasPassWord = hasPassWord
        self.passWord = ""
        self.setWindowTitle("qt5archiver - {}".format(os.path.basename(self.path)))
        self.resize(int(WINW), int(WINH))
        if WINM == "True":
            self.showMaximized()
        #
        # destination folder
        if os.path.dirname(self.path):
            self.pdest = os.path.dirname(self.path)
        else:
            self.pdest = os.getcwd()
        # main box
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.createHeader()
        self.createLayout()
        self.populateTree()
        self.show()
        #
        self.selected_item = None
    
    
    #
    def on_close(self):
        new_w = self.size().width()
        new_h = self.size().height()
        if new_w != int(WINW) or new_h != int(WINH):
            # WINW = width
            # WINH = height
            # WINM = maximized
            isMaximized = self.isMaximized()
            if isMaximized == True and WINM == "True":
                qApp.quit()
                return
            #
            try:
                ifile = open("winsize.cfg", "w")
                if isMaximized:
                    if WINM == "False":
                        ifile.write("{};{};{}".format(WINW, WINH, isMaximized))
                else:
                    ifile.write("{};{};False".format(new_w, new_h))
                ifile.close()
            except Exception as E:
                MyDialog("Error", str(E), self)
        qApp.quit()
    
    
    def createHeader(self):
        gboxLayout = QGridLayout()
        self.vbox.addLayout(gboxLayout)
        # extract the item
        extract_btn_f = QPushButton()
        extract_btn_f.setIcon(QIcon("icons/extract-item-full-path.svg"))
        extract_btn_f.setIconSize(QSize(48, 48))
        extract_btn_f.setToolTip("Extract the item.")
        extract_btn_f.clicked.connect(lambda:self.fextract_btn("x"))
        gboxLayout.addWidget(extract_btn_f,0,1,1,1)
        # extract the whole archive
        extract_archive = QPushButton()
        extract_archive.setIcon(QIcon("icons/full-archive.svg"))
        extract_archive.setIconSize(QSize(48, 48))
        extract_archive.setToolTip("Extract the whole archive.")
        extract_archive.clicked.connect(lambda:self.fextract_btn("a"))
        gboxLayout.addWidget(extract_archive,0,2,1,1)
        # extract in the folder
        folder_btn = QPushButton()
        folder_btn.setIcon(QIcon("icons/choose-folder.svg"))
        folder_btn.setIconSize(QSize(48, 48))
        folder_btn.setToolTip("Choose where to extract.")
        folder_btn.clicked.connect(self.folder_btnf)
        gboxLayout.addWidget(folder_btn,0,3,1,1)
        # exit button
        exit_btn = QPushButton()
        exit_btn.setIcon(QIcon.fromTheme("exit"))
        exit_btn.setIconSize(QSize(48, 48))
        exit_btn.setToolTip("Close")
        exit_btn.clicked.connect(lambda:self.on_close())
        gboxLayout.addWidget(exit_btn,0,4,1,1)
    
    
    def createLayout(self):
        self.treeWidget = TreeWidget(os.path.realpath(self.path))
        self.vbox.addWidget(self.treeWidget)
        self.treeWidget.setColumnCount(4)
        self.treeWidget.setColumnHidden(3, True)
        self.treeWidget.doubleClicked.connect(self.getRow2)
        self.treeWidget.clicked.connect(self.getRow)
        self.treeWidget.setHeaderLabels(["Name", "Size", "Modification", "Type"])
        self.treeWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.treeWidget.setIconSize(QSize(48, 48))
        self.folder_icon = QIcon.fromTheme("folder", QIcon("icons/folder.svg"))
        self.file_icon = QIcon.fromTheme("text-plain", QIcon("icons/file.svg"))
        # 
        self.bobox = QHBoxLayout()
        self.vbox.addLayout(self.bobox)
        self.bottom_label = QLabel("Extract to: {}".format(os.path.basename(self.pdest)))
        self.bottom_label.setToolTip(self.pdest)
        self.bobox.addWidget(self.bottom_label)
        #
        if self.hasPassWord == 2:
            self.pwd_label = QLabel("")
            self.pwd_label.setPixmap(QPixmap("icons/passworded.svg"))
            self.pwd_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
            self.bobox.addWidget(self.pwd_label)
    
    
    # remove duplicated paths
    def on_itemList(self, llist):
        # path - type - size - modified
        itemList = llist[:]
        for item in llist:
            ipath = item[0]
            ppath = os.path.dirname(ipath)
            # 
            while ppath:
                for iitem in itemList:
                    if iitem[0] == ppath:
                        try:
                            itemList.remove(iitem)
                        except:
                            pass
                ppath = os.path.dirname(ppath)
        #
        return itemList
    
    
    def getItems(self, lines):
        ffields = []
        # starting index
        temp_list = []
        fdate = 0
        ftyte = 0
        fsize = 0
        fcompressed = 0
        fname = 0
        #
        items = []
        istart = 0
        for line in lines:
            if istart:
                if line[0:10] == "----------":
                    return items
                #
                idate = line[0:temp_list[0]]
                itype = line[ftype:fsize]
                isize = line[fsize:fcompressed-1]
                iname = line[fname:]
                # 
                if itype[0] == "D":
                    items.append([iname, "+", isize.strip(" "), idate])
                else:
                    items.append([iname, "-", isize.strip(" "), idate])
                #
            else:
                if line[0:10] == "----------":
                    istart = 1
                    fields = line.split(" ")
                    for ff in fields:
                        temp_list.append(len(ff) or 1)
                    # 
                    fdate = 0
                    ftype = fdate + temp_list[0] + 1
                    fsize = ftype + temp_list[1] + 1
                    fcompressed = fsize + temp_list[2] + 1
                    fname = fcompressed + temp_list[3] + temp_list[4] + 1
    
    
    # fill the treewidget
    def populateTree(self):
        byte_output=subprocess.check_output('7z l {}'.format(self.path), shell=True)
        str_output = byte_output.decode('utf-8')
        llines = str_output.splitlines()
        files = self.getItems(llines)
        #
        itemList = self.on_itemList(files)
        root_index = self.treeWidget.rootIndex()
        ### ADD THE TOP LEVEL ITEMS
        top_level_items_data = []
        #
        for item in itemList:
            splitted_path = item[0].split(os.sep)
            # no toplevels at all
            if not top_level_items_data:
                iitem = splitted_path[0]
                # 
                if item[1] == "-": 
                    if iitem != splitted_path[-1]:
                        top1 = QTreeWidgetItem([iitem,None,None,"folder"])
                        top1.setIcon(0, self.folder_icon)
                        self.treeWidget.addTopLevelItem(top1)
                        top_level_items_data.append([iitem, top1])
                    else:
                        top1 = QTreeWidgetItem([iitem,item[2],item[3],"file"])
                        top1.setIcon(0, self.file_icon)
                        self.treeWidget.addTopLevelItem(top1)
                        top_level_items_data.append([iitem, top1])
                elif item[1] == "+":
                    top1 = QTreeWidgetItem([iitem,None,None,"folder"])
                    top1.setIcon(0, self.folder_icon)
                    self.treeWidget.addTopLevelItem(top1)
                    top_level_items_data.append([iitem, top1])
            else:
                iitem = splitted_path[0]
                trovato = 0
                # if not iitem in top_level_items_data:
                for el in top_level_items_data:
                    if iitem == el[0]:
                        trovato = 1
                if trovato == 0:
                    if iitem != splitted_path[-1]:
                        top1 = QTreeWidgetItem([iitem,None,None,"folder"])
                        top1.setIcon(0, self.folder_icon)
                        self.treeWidget.addTopLevelItem(top1)
                        top_level_items_data.append([iitem, top1])
                    else:
                        top1 = QTreeWidgetItem([iitem,item[2],item[3],"file"])
                        top1.setIcon(0, self.file_icon)
                        self.treeWidget.addTopLevelItem(top1)
                        top_level_items_data.append([iitem, top1])
            # children
            node = None
            # node_root = None
            iitem = splitted_path[0]
            for el in top_level_items_data:
                if iitem == el[0]:
                    node = el[1]
            #
            for eitem in splitted_path[1:]:
                is_found = 0
                # 
                if node:
                    for i in range(node.childCount()):
                        if node.child(i).text(0) == eitem:
                            node = node.child(i)
                            is_found = 1
                            break
                #
                if is_found:
                    continue
                #
                if item[1] == "-":
                    if not eitem == splitted_path[-1]:
                        child = QTreeWidgetItem([eitem,None,None,"folder"])
                        child.setIcon(0, self.folder_icon)
                        node.addChild(child)
                        node = child
                    else:
                        child = QTreeWidgetItem([eitem,item[2],item[3],"file"])
                        child.setIcon(0, self.file_icon)
                        node.addChild(child)
                        node = child
                elif item[1] == "+":
                    child = QTreeWidgetItem([eitem,None,None,"folder"])
                    child.setIcon(0, self.folder_icon)
                    node.addChild(child)
                    node = child
        #
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.sortByColumn(3, Qt.DescendingOrder)
    
    # select the destination folder
    def folder_btnf(self):
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folderpath:
            self.pdest = folderpath
            self.bottom_label.setText("Extract to: {}".format(os.path.basename(self.pdest)))
            self.bottom_label.setToolTip(self.pdest)
    
    
    # without folders (e) - with folders (x) - extract all (a)
    def fextract_btn(self, etype):
        ret = -5
        #
        if self.hasPassWord == 2:
            if not self.passWord:
                self.passWord = passWord(self.path).arpass
                if not self.passWord:
                    return
        #
        if etype in ["e", "x"]:
            if not self.selected_item:
                return
            ipathL = self.get_path(self.selected_item)
            ipath = "/".join(ipathL)
            if etype == "x":
                fpath = ipath
            elif etype == "e":
                fpath = self.selected_item.data(0)
            full_path = os.path.join(self.pdest, fpath)
            # 
            if os.path.exists(full_path):
                dlg = message("Overwrite?", "OC")
                retd = dlg.exec_()
                if retd:
                    ret = os.system("{0} {1} '-i!{2}' {3} -p{4} -y -o{5} 1>/dev/null".format(EXTRACTOR, etype, ipath, self.path, self.passWord, self.pdest))
            else:
                ret = os.system("{0} {1} '-i!{2}' {3} -p{4} -y -o{5} 1>/dev/null".format(EXTRACTOR, etype, ipath, self.path, self.passWord, self.pdest))
        elif etype == "a":
            # 0 with no errors but without verifying
            ret = os.system("{0} x {1} -y -o{2} 1>/dev/null".format(EXTRACTOR, self.path, self.pdest))
        ### exit codes
        # 0 No error
        # 1 Warning (Non fatal error(s)). For example, one or more files were locked by some other application, so they were not compressed.
        # 2 Fatal error
        # 7 Command line error
        # 8 Not enough memory for operation
        # 255 User stopped the process
        if ret == 0:
            # check it the base folder exists
            dlg = message("Extracted.", "O")
            retd = dlg.exec_()
        elif ret != -5:
            dlg = message("Error:\n{}".format(ret), "O")
            dlg.exec_()
        #
        self.selected_item = None
    
    
    # get the path of the selected item
    def get_path(self, item):
        ipath = []
        while item.data(0):
            ipath.insert(0, item.data(0))
            item = item.parent()
        #
        return ipath
    
    
    # single click
    def getRow(self, item):
        ipath = self.get_path(item)
        self.selected_item = item

    
    # double click
    def getRow2(self, item):
        idx = self.treeWidget.currentItem()
        item_size = idx.data(1, 0)
        # not folder or empty items
        if item_size:
            # extract into /tmp the item if file
            ipathL = self.get_path(self.selected_item)
            ipath = "/".join(ipathL)
            if self.hasPassWord == 2:
                if not self.passWord:
                    self.passWord = passWord(self.path).arpass
                    if not self.passWord:
                        return
            ret = os.system("{0} {1} '-i!{2}' {3} -p{4} -y -o{5}".format(EXTRACTOR, "e", ipath, self.path, self.passWord, "/tmp"))
            # get the default application and open it
            defApp = getDefaultApp(ipath).defaultApplication()
            file_name = self.selected_item.data(0)
            #
            if defApp != "None":
                try:
                    subprocess.Popen([defApp, os.path.join("/tmp", file_name)])
                except Exception as E:
                    dlg = message("Error\n{}".format(str(E)), "O")
                    dlg.exec_()
            elif defApp == "None":
                dlg = message("Info:\nno application found for\n{}".format(file_name), "O")
                dlg.exec_()



# dialog for asking the archive password
class passWord(QDialog):
    def __init__(self, path, parent=None):
        super(passWord, self).__init__(parent)
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("7z extractor")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(600,100)
        #
        self.path = path
        # main box
        mbox = QBoxLayout(QBoxLayout.TopToBottom)
        mbox.setContentsMargins(5,5,5,5)
        # label
        self.label = QLabel("Enter The Password:")
        mbox.addWidget(self.label)
        # checkbox
        self.ckb = QCheckBox("Hide/Show the password")
        self.ckb.setChecked(True)
        self.ckb.toggled.connect(self.on_checked)
        mbox.addWidget(self.ckb)
        # lineedit
        self.le1 = QLineEdit()
        self.le1.setEchoMode(QLineEdit.Password)
        mbox.addWidget(self.le1)
        ##
        button_box = QBoxLayout(QBoxLayout.LeftToRight)
        button_box.setContentsMargins(0,0,0,0)
        mbox.addLayout(button_box)
        #
        button_ok = QPushButton("     Accept     ")
        button_box.addWidget(button_ok)
        #
        button_close = QPushButton("     Close     ")
        button_box.addWidget(button_close)
        #
        self.setLayout(mbox)
        button_ok.clicked.connect(self.getpswd)
        button_close.clicked.connect(self.close)
        #
        self.arpass = ""
        #
        self.exec_()
    
    def on_checked(self):
        if self.ckb.isChecked():
            self.le1.setEchoMode(QLineEdit.Password)
        else:
            self.le1.setEchoMode(QLineEdit.Normal)
    
    def getpswd(self):
        passwd = self.le1.text()
        try:
            ptest = subprocess.check_output('{} t -p{} -bso0 -- "{}"'.format(EXTRACTOR, passwd, self.path), shell=True)
            if ptest.decode() == "":
                self.arpass = passwd
                self.close()
        except:
            self.label.setText("Wrong Password:")
            self.le1.setText("")


# find the default application for a given mimetype if any
# using xdg-mime
class getDefaultApp():
    
    def __init__(self, path):
        self.path = path
        
    def defaultApplication(self):
        # where to look for desktop files or default locations
        if xdg_data_dirs:
            xdgDataDirs = list(set(xdg_data_dirs))
        else:
            xdgDataDirs = ['/usr/local/share', '/usr/share', os.path.expanduser('~')+"/.local/share"]
        # consistency
        if "/usr/share" not in xdgDataDirs:
            xdgDataDirs.append("/usr/share")
        if os.path.expanduser('~')+"/.local/share" not in xdgDataDirs:
            xdgDataDirs.append(os.path.expanduser('~')+"/.local/share")
        #
        ret = shutil.which("xdg-mime")
        if ret:
            imime = QMimeDatabase().mimeTypeForFile(self.path, QMimeDatabase.MatchDefault).name()
            #
            if imime in ["application/x-zerosize", "application/x-trash"]:
                mimetype = "text/plain"
            else:
                mimetype = imime
            #
            try:
                associatedDesktopProgram = subprocess.check_output([ret, "query", "default", mimetype], universal_newlines=False).decode()
            except Exception as E:
                return "None"
            #
            if associatedDesktopProgram:
                for ddir in xdgDataDirs:
                    if ddir[-1] == "/":
                        ddir = ddir[:-1]
                    desktopPath = os.path.join(ddir+"/applications", associatedDesktopProgram.strip())
                    #
                    if os.path.exists(desktopPath):
                        applicationName2 = DesktopEntry(desktopPath).getExec()
                        if applicationName2:
                            applicationName = applicationName2.split()[0]
                        else:
                            return "None"
                        applicationPath = shutil.which(applicationName)
                        if applicationPath:
                            if os.path.exists(applicationPath):
                                return applicationPath
                            else:
                                dlg = message("Error:\n{} cannot be found".format(applicationPath), self.window)
                                dlg.exec_()
                        else:
                            return "None"
                #
                # no apps found
                return "None"
            else:
                return "None"
        else:
            dlg = message("Error:\nxdg-mime cannot be found", "O")
            dlg.exec_()


# dialog
class message(QDialog):
    def __init__(self, msg, mtype):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.title = "Info"
        # self.resize(800,400)
        # main box
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        #
        self.label = QLabel(msg)
        self.vbox.addWidget(self.label)
        #
        if mtype == "OC":
            btns = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        elif mtype == "O":
            btns = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(btns)
        self.buttonBox.accepted.connect(self.accept)
        if mtype == "OC":
            self.buttonBox.rejected.connect(self.reject)
        self.vbox.addWidget(self.buttonBox)
        #

    def close(self):
        self.close()

#######################
if __name__ == '__main__':
    
    # check it the archive is password protected
    def test_archive(path):
        szdata = None
        try:
            szdata = subprocess.check_output('{} l -slt -bso0 -- "{}"'.format(EXTRACTOR, path), shell=True)
        except:
            return 0
        #
        if szdata != None:
            szdata_decoded = szdata.decode()
            ddata = szdata_decoded.splitlines()
            if "Encrypted = +" in ddata:
                return 2
            else:
                return 1
    
    app = QApplication(sys.argv)
    # 
    if len(sys.argv) == 1:
        dlg = message("No archive to open.", "O")
        dlg.exec_()
        sys.exit()
    path = sys.argv[1]
    if not os.path.exists(path):
        dlg = message("The archive {} doesn't exist.".format(os.path.basename(path)), "O")
        dlg.exec_()
        sys.exit()
    window = Window(path, test_archive(path))
    sys.exit(app.exec_())
