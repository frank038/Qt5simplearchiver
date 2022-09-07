#!/usr/bin/env python3
# version 0.8

from PyQt5.QtWidgets import QDesktopWidget, qApp, QSizePolicy, QBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QFileDialog, QDialogButtonBox, QApplication, QWidget, QHeaderView, QTreeWidget, QTreeWidgetItem, QPushButton, QDialog, QVBoxLayout, QGridLayout, QLabel, QMessageBox
import sys
from PyQt5.QtGui import QIcon, QDrag, QPixmap
from PyQt5.QtCore import QFileSystemWatcher, QTimer, QObject, QEvent, Qt, QUrl, QMimeData, QSize, QMimeDatabase, QByteArray, QDataStream, QIODevice
import subprocess
import os, shutil
from xdg.BaseDirectory import *
from xdg.DesktopEntry import *

CURRENT_PROG_DIR = os.getcwd()

# use libarchive for reading: 0 use 7z - 1 use libarchive
USE_LIBARCHIVE = 0
if USE_LIBARCHIVE:
    import libarchive
    from datetime import datetime

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
    with open(os.path.join(CURRENT_PROG_DIR, "winsize.cfg"), "r") as ifile:
        fcontent = ifile.readline()
    aw, ah, am = fcontent.split(";")
    WINW = aw
    WINH = ah
    WINM = am.strip()
except:
    app = QApplication(sys.argv)
    fm = firstMessage("Error", "The file winsize.cfg cannot be read.")
    sys.exit(app.exec_())

def create_where_to_extract():
    try:
        ifile = open(os.path.join(CURRENT_PROG_DIR, "where_to_extract"), "w")
        ifile.close()
    except:
        app = QApplication(sys.argv)
        fm = firstMessage("Error", "The file where_to_extract cannot be written.")
        sys.exit(app.exec_())
create_where_to_extract()

# 
DRAG_SUCCESS = 0
class TreeWidget(QTreeWidget):
    
    def __init__(self, archive_path, parent):
        QTreeWidget.__init__(self)
        self.parent = parent
        self.archive_path = archive_path
        self.setSelectionMode(self.ExtendedSelection)
        self.customMimeType = "application/x-customqt5archiver"
        self.setDragEnabled(True)
    
    
    def startDrag(self, supportedActions):
        # reset
        self.parent.in_extraction = 0
        # send the working directory of this program - needed for where_to_extract
        drag_data = CURRENT_PROG_DIR
        drag = QDrag(self)
        mimedata = QMimeData()
        data = QByteArray()
        data.append(bytes(drag_data, encoding="utf-8"))
        mimedata.setData(self.customMimeType, data)
        drag.setMimeData(mimedata)
        pixmap = QPixmap("icons/extraction.png").scaled(48, 48, Qt.KeepAspectRatio)
        drag.setPixmap(pixmap)
        # drag.exec_(supportedActions)
        # 1 success - 0 failure
        ret = drag.exec_(Qt.CopyAction)
        # # if ret == 0:
            # # drag.deleteLater()
            # # mimedata.deleteLater()
        #
        if ret:
            global DRAG_SUCCESS
            DRAG_SUCCESS = ret
        #
        return
        
    
    # get the full archive path of the selected item
    def get_path(self, item):
        ipath = []
        if item:
            while item and item.data(0,0):
                ipath.insert(0, item.data(0,0))
                item = item.parent()
        #
        return ipath
    
# 
class arcExtract():
    def __init__(self, ePath, full_list, etype, edest, epassword):
        # the path of the archive
        self.ePath = ePath
        # list of the items in the archive to extract - full path
        self.elist = full_list
        # type of extraction: x and e single item - a full archive
        self.etype = etype
        # destination - full path
        self.edest = edest
        # the password
        self.password = epassword
        #
        self.fextract()
        
    def fextract(self):
        ret = -5
        #
        if self.etype in ["e", "x"]:
            retd = 1
            for iitem in self.elist:
                # if os.path.isdir(os.path.join(self.edest, iitem)):
                    # continue
                if os.path.exists(os.path.join(self.edest, iitem)):
                    dlg = message("Some items already exist.\nOverwrite?", "OC")
                    retd = dlg.exec_()
                    break
            if retd:
                for iitem in self.elist:
                    ret = os.system("{0} {1} '-i!{2}' '{3}' -p'{4}' -y -o'{5}' 1>/dev/null".format(EXTRACTOR, self.etype, iitem, self.ePath, self.password, self.edest))
        elif self.etype == "a":
            # 0 with no errors but without verifying
            ret = os.system("{0} x '{1}' -p'{2}' -y -o'{3}' 1>/dev/null".format(EXTRACTOR, self.ePath, self.password, self.edest))
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
   

class Window(QWidget):
    def __init__(self, path, hasPassWord):
        super(Window, self).__init__()
        self.setWindowIcon(QIcon("icons/qt5archiver.svg"))
        self.path = path
        self.is_opened = 0
        # 2 yes - 1 no
        self.hasPassWord = hasPassWord
        self.password = ""
        self.setWindowTitle("qt5archiver - {}".format(os.path.basename(self.path)))
        self.resize(int(WINW), int(WINH))
        if WINM == "True":
            self.showMaximized()
        # an error occour while reading the archive
        self.open_with_error = 0
        # destination folder
        if os.path.dirname(self.path):
            self.pdest = os.path.dirname(self.path)
        else:
            self.pdest = os.getcwd()
        # main box
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        #
        self.createHeader()
        self.createLayout()
        # self.populateTree()
        #
        self.installEventFilter(self)
        #
        # self.show()
        # extration type: x with folders - e without folders
        self. etype = "e"
        #
        self.selected_item = None
        #
        self.extraction_dest = None
        self.in_extraction = 0
        # check for changes in the directory
        fPath = [os.path.join(CURRENT_PROG_DIR,"where_to_extract")]
        self.fileSystemWatcher = QFileSystemWatcher(fPath)
        self.fileSystemWatcher.fileChanged.connect(self.checkDest)
    
    
    def checkDest(self, nfile):
        if self.in_extraction:
            return
        #
        if os.path.exists(nfile):
            self.in_extraction = 1
            with open(os.path.join(CURRENT_PROG_DIR, "where_to_extract"), "r") as efile:
                self.extraction_dest = efile.readline().strip()
            if not self.extraction_dest:
                MyDialog("Error", "Destination missed.", self)
                return
            #
            self.fextract_btn()
        
    #
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Show:
            if not self.is_opened:
                self.is_opened = 1
                QTimer.singleShot(1000, self.populateTree)
                return True
        return super(Window, self).eventFilter(obj, event)
    
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
        # with subfolders or not
        self.sub_btn_f = QPushButton()
        self.sub_btn_f.setCheckable(True)
        self.sub_btn_f.setIcon(QIcon("icons/alternate.svg"))
        self.sub_btn_f.setIconSize(QSize(48, 48))
        self.sub_btn_f.setToolTip("Extraction without folder(s).")
        self.sub_btn_f.clicked.connect(self.fsub_btn)
        gboxLayout.addWidget(self.sub_btn_f,0,1,1,1)
        # extract the item
        extract_btn_f = QPushButton()
        extract_btn_f.setIcon(QIcon("icons/extract-item-full-path.svg"))
        extract_btn_f.setIconSize(QSize(48, 48))
        extract_btn_f.setToolTip("Extract the item.")
        extract_btn_f.clicked.connect(self.fextract_btn)
        gboxLayout.addWidget(extract_btn_f,0,2,1,1)
        # extract the whole archive
        extract_archive = QPushButton()
        extract_archive.setIcon(QIcon("icons/full-archive.svg"))
        extract_archive.setIconSize(QSize(48, 48))
        extract_archive.setToolTip("Extract the whole archive.")
        extract_archive.clicked.connect(lambda:self.fextract_btn("a"))
        gboxLayout.addWidget(extract_archive,0,3,1,1)
        # extract in the folder
        folder_btn = QPushButton()
        folder_btn.setIcon(QIcon("icons/choose-folder.svg"))
        folder_btn.setIconSize(QSize(48, 48))
        folder_btn.setToolTip("Choose where to extract.")
        folder_btn.clicked.connect(self.folder_btnf)
        gboxLayout.addWidget(folder_btn,0,4,1,1)
        # exit button
        exit_btn = QPushButton()
        exit_btn.setIcon(QIcon.fromTheme("exit"))
        exit_btn.setIconSize(QSize(48, 48))
        exit_btn.setToolTip("Close")
        exit_btn.clicked.connect(lambda:self.on_close())
        gboxLayout.addWidget(exit_btn,0,5,1,1)
    
    
    def createLayout(self):
        self.treeWidget = TreeWidget(os.path.realpath(self.path), self)
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
        self.bottom_label = QLabel()
        self.bobox.addWidget(self.bottom_label)
        self.bottom_label.setText("Opening: {}".format(os.path.basename(self.path)))
        #
        self.pwd_label = QLabel("")
        self.pwd_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.bobox.addWidget(self.pwd_label)
    
    
    def fsub_btn(self):
        if self.sender().isChecked():
            # set etype x
            self.etype = "x"
            self.sender().setToolTip("Extraction with folder(s).")
        else:
            # set etype e
            self.etype = "e"
            self.sender().setToolTip("Extraction without folder(s).")
    
    # # remove duplicated paths - rar issue?
    # def on_itemList(self, llist):
        # # path - type - size - modified
        # itemList = llist[:]
        # for item in llist:
            # if item[1] == '+':
                # ipath = item[0]
                # ppath = os.path.dirname(ipath)
                # # 
                # while ppath:
                    # for iitem in itemList:
                        # if iitem[0] == ppath:
                            # try:
                                # itemList.remove(iitem)
                            # except:
                                # pass
                    # ppath = os.path.dirname(ppath)
        # #
        # return itemList
    
    
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
                    # 
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
        itemList = []
        if USE_LIBARCHIVE == 1:
            # ['name', '+' or '-', 'size', 'date']
            try:
                with libarchive.file_reader(self.path) as file_archive:
                    for item_entry in file_archive:
                        if item_entry.isdir:
                            item_type = "+"
                        else:
                            item_type = "-"
                        item_mtime_temp = item_entry.mtime
                        item_mtime = datetime.fromtimestamp(item_mtime_temp).strftime('%Y-%m-%d %H:%M:%S')
                        item_name = item_entry.name
                        if item_type == "+" and item_name[-1] == "/":
                            item_name = item_name[:-1]
                        itemList.append([item_name, item_type, str(item_entry.size), item_mtime])
            except Exception as E:
                MyDialog("Error", str(E), self)
                # set the label
                self.bottom_label.setText("Error: {}".format(os.path.basename(self.path)))
                self.bottom_label.setToolTip(self.pdest)
                return
        else:
            try:
                byte_output=subprocess.check_output('7z l "{}"'.format(self.path), shell=True)
            except:
                self.bottom_label.setText("Error.")
                return
            #
            str_output = byte_output.decode('utf-8')
            llines = str_output.splitlines()
            try:
                itemList = self.getItems(llines)
            except Exception as E:
                MyDialog("Error", str(E)+"\nor unsupported archive.", self)
                self.open_with_error = 1
                return
        #
        ##############################
        tw = self.treeWidget
        for iitem in itemList:
            # node to fill
            cchh = None
            el_iitem = iitem[0].split("/")
            len_iitem = len(el_iitem)
            for ii,el in enumerate(el_iitem):
                # 0 is top level
                if ii == 0:
                    is_found = 0
                    top_num = self.treeWidget.topLevelItemCount()
                    if top_num:
                        for jj in range(top_num):
                            if el == self.treeWidget.topLevelItem(jj).text(0):
                                cchh = self.treeWidget.topLevelItem(jj)
                                is_found = 1
                                break
                    if is_found:
                        continue
                    # add a toplevel
                    child = QTreeWidgetItem([el, iitem[2], iitem[3]])
                    if iitem[1] == "-":
                        child.setIcon(0, self.file_icon)
                    else:
                        child.setIcon(0, self.folder_icon)
                    self.treeWidget.addTopLevelItem(child)
                    cchh = child
                    continue
                    continue
                # child if ii > 0
                else:
                    is_found = 0
                    ch_count = cchh.childCount()
                    #
                    if ch_count:
                        for jj in range(ch_count):
                            if cchh.child(jj).text(0) == el:
                                cchh = cchh.child(jj)
                                is_found = 1
                                break
                    #
                    if is_found:
                        continue
                    #
                    # add a child
                    child = QTreeWidgetItem([el, iitem[2], iitem[3]])
                    if iitem[1] == "-":
                        child.setIcon(0, self.file_icon)
                    else:
                        child.setIcon(0, self.folder_icon)
                    cchh.addChild(child)
                    cchh = child
                    continue
        ############################## OLD
        # itemList2 = self.on_itemList(itemList)
        # # 
        # ####
        # root_index = self.treeWidget.rootIndex()
        # ### ADD THE ITEMS
        # for item in itemList2:
            # splitted_path = item[0].split(os.sep)
            # ###################
            # tnode = None
            # for i in range(len(splitted_path)-1):
                # iitem = splitted_path[i]
                # if i == 0:
                    # # find an existent top level
                    # top_num = self.treeWidget.topLevelItemCount()
                    # if top_num:
                        # for tl in range(top_num):
                            # node = self.treeWidget.topLevelItem(tl)
                            # if node.text(0) == iitem:
                                # tnode = node
                                # break
                    # #
                    # if not tnode:
                        # top1 = QTreeWidgetItem([iitem,None,None,"folder"])
                        # top1.setIcon(0, self.folder_icon)
                        # self.treeWidget.addTopLevelItem(top1)
                        # tnode = top1
                # else:
                    # child_node = None
                    # for j in range(tnode.childCount()):
                        # if tnode.child(j).text(0) == iitem:
                            # child_node = tnode.child(j)
                            # break
                    # # 
                    # if not child_node:
                        # child = QTreeWidgetItem([iitem,None,None,"folder"])
                        # child.setIcon(0, self.folder_icon)
                        # tnode.addChild(child)
                        # tnode = child
                    # else:
                        # tnode = child_node
            # 
            # #
            # # the last index
            # litem = splitted_path[-1]
            # if item[1] == "+":
                # child = QTreeWidgetItem([litem,None,None,"folder"])
                # child.setIcon(0, self.folder_icon)
            # else:
                # child = QTreeWidgetItem([litem,item[2],item[3],"file"])
                # child.setIcon(0, self.file_icon)
            # if tnode:
                # tnode.addChild(child)
            # else:
                # self.treeWidget.addTopLevelItem(child)
            # 
        ############
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.sortByColumn(0, Qt.AscendingOrder)
        # set the label
        self.bottom_label.setText("Extract to: {}".format(os.path.basename(self.pdest)))
        self.bottom_label.setToolTip(self.pdest)
        #
        if self.hasPassWord == 2:
            self.pwd_label.setPixmap(QPixmap("icons/passworded.svg"))
            self.pwd_label.setToolTip("Password protected.")
    
    
    # select the destination folder
    def folder_btnf(self):
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folderpath:
            self.pdest = folderpath
            self.bottom_label.setText("Extract to: {}".format(os.path.basename(self.pdest)))
            self.bottom_label.setToolTip(self.pdest)
    
    
    # with folders (x) - without folders (e) - extract all (a)
    def fextract_btn(self, eftype=None):
        if self.open_with_error == 1:
            dlg = message("Error on opening.", "O")
            dlg.exec_()
            return
        #
        if self.treeWidget.selectedIndexes() == []:
            dlg = message("Nothing selected.", "O")
            dlg.exec_()
            return
        #
        if eftype:
            self.etype = eftype
            self.sub_btn_f.setChecked(False)
        #
        full_list = []
        for i in range(0, len(self.treeWidget.selectedIndexes()), 3):
            iit = self.treeWidget.selectedIndexes()[i]
            full_list.append("/".join(self.get_path(iit)))
        #
        if self.hasPassWord == 2:
            if not self.password:
                self.password = passWord(self.path).arpass
                if not self.password:
                    return
                else:
                    if self.password and self.hasPassWord == 2:
                        self.pwd_label.setPixmap(QPixmap("icons/passwordedn.svg"))
                        self.pwd_label.setToolTip("Password protected. Decrypted.")
        # archive path - items to extract - type of extraction - where to extract - password
        if self.extraction_dest:
            arcExtract(self.path, full_list, self.etype, self.extraction_dest, self.password)
        else:
            arcExtract(self.path, full_list, self.etype, self.pdest, self.password)
        #
        self.extraction_dest = None
        # reset
        try:
            ifile = open(os.path.join(CURRENT_PROG_DIR, "where_to_extract"), "w")
            ifile.close()
        except Exception as E:
            dlg = message("Error:\n{}".format(str(E)), "O")
            dlg.exec_()
            return
        
    
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
                if not self.password:
                    self.passord = passWord(self.path).arpass
                    if not self.password:
                        return
            ret = os.system("{0} {1} '-i!{2}' '{3}' -p'{4}' -y -o'{5}'".format(EXTRACTOR, "e", ipath, self.path, self.password, "/tmp"))
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
            #
            if self.password and self.hasPassWord == 2:
                self.pwd_label.setPixmap(QPixmap("icons/passwordedn.svg"))
                self.pwd_label.setToolTip("Password protected. Decrypted.")
                

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
            ptest = subprocess.check_output('{} t -p"{}" -bso0 -- "{}"'.format(EXTRACTOR, passwd, self.path), shell=True)
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
                                dlg = message("Error:\n{} cannot be found".format(applicationPath), "O")
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


# simple dialog message
# type - message - parent
class MyDialog(QMessageBox):
    def __init__(self, *args):
        super(MyDialog, self).__init__(args[-1])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Information)
            self.setStandardButtons(QMessageBox.Ok)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Critical)
            self.setStandardButtons(QMessageBox.Ok)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Question)
            self.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle(args[0])
        DIALOGWIDTH = 600
        self.resize(DIALOGWIDTH,300)
        self.setText(args[1])
        retval = self.exec_()
    
    def event(self, e):
        result = QMessageBox.event(self, e)
        #
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 
        return result

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
    #
    app = QApplication(sys.argv)
    # 
    if len(sys.argv) == 1:
        dlg = message("No archive to open.", "O")
        dlg.exec_()
        sys.exit()
    path = os.path.abspath(sys.argv[1])
    if not os.path.exists(path):
        dlg = message("The archive\n {} \ndoesn't exist.".format(os.path.basename(path)), "O")
        dlg.exec_()
        sys.exit()
    #
    ret = test_archive(path)
    if ret == 0:
        dlg = message("Cannot open the archive: {}.".format(os.path.basename(path)), "O")
        dlg.exec_()
        sys.exit()
    #
    window = Window(path, ret)
    window.show()
    sys.exit(app.exec_())
