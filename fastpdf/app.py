from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex,QRegularExpression
from PySide6.QtGui import QPainter,QRegularExpressionValidator
from PySide6.QtWidgets import ( 
                               QMainWindow, 
                               QApplication,  
                               QVBoxLayout,
                               QHBoxLayout, 
                               QWidget, 
                               QPushButton,
                               QTreeView,
                               QSizePolicy,
                               QDialog,
                               QDialogButtonBox,
                               QLabel,
                               QLineEdit,
                               QGroupBox,
                               QComboBox,
                               )

import sys, os, csv
from File import File
import utility

__VERSION__ = 1.1

class TreeListView(QTreeView):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        
    def paintEvent(self, event):
        
        super().paintEvent(event)
        if self.model() is not None and self.model().rowCount() > 0:
            return
        painter = QPainter(self.viewport())
        painter.save()
        col = self.palette().placeholderText().color()
        painter.setPen(col)
        fm = self.fontMetrics()
        elided_text = fm.elidedText(
            "Przerzuć pliki tutaj", Qt.TextElideMode.ElideRight, self.viewport().width()
        )
        painter.drawText(self.viewport().rect(), Qt.AlignmentFlag.AlignCenter, elided_text)
        painter.restore()
        
class TreeListModel(QAbstractItemModel):
    
    def __init__(self, data=None):
        super().__init__()
        self.dataArr = data or []
        
    def rowCount(self,parent=QModelIndex()):
        
        if not parent.isValid():
            return len(self.dataArr)  
        return 0
    
    def columnCount(self,parent=QModelIndex()):
        return 3
        
    #no hierarchy?
    def parent(self, index): # type: ignore
        return QModelIndex()
    
    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row,column)
    
    def data(self, index, role=None):
        
        if not index.isValid():
            return None
            
        item = self.dataArr[index.row()]
            
        try:
                if role == Qt.ItemDataRole.DisplayRole:
                    if index.column() == 0:
                        return item.filename
                    elif index.column() == 1:
                        return item.size
                    elif index.column() == 2:
                        return item._state
                return None
        except IndexError:
                return ''
        
    
    def headerData(self,section,orientation,role=None):
        
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if section == 0:
                return "Nazwa"
            elif section == 1:
                return "Rozmiar"
            elif section == 2:
                return "Status"
        return None

class CustomComboBox(QComboBox):
    
    def __init__(self):
        super().__init__()
        self.path = path = f'{os.getcwd()}\\src\\suffix.csv'
    
    def setModel(self):
        
        with open(self.path, 'r', encoding="utf8") as fp:
    
            #delimiter na później
            rdr = csv.reader(fp, delimiter=",")\
        
            #iterator skip
            header = next(rdr, None)
    
            data_read = [row for row in rdr] 
            data_ready = utility.flattenArr(data_read)
                    
        return data_ready
       
class CustomDialog(QDialog):
    
    def __init__(self,text,title=None):
        super().__init__()
        self.setWindowTitle(title or "Błąd")
        self.text = text

        QBtn = QDialogButtonBox.StandardButton.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        

        layout = QVBoxLayout()
        message = QLabel(text)
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
            
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.bindHandlers()
        
    def initUI(self):
        self.setWindowTitle(f'FastPDF {str(__VERSION__)}')
        self.resize(500,500)
        
        layout_main = QVBoxLayout()
        
        layout_main_rasterize = QVBoxLayout()
        layout_main_rasterize_btns = QHBoxLayout()
        
        layout_main_flat = QVBoxLayout()
        layout_main_flat_btns = QHBoxLayout()
        
        layout_main_organize = QVBoxLayout()
        layout_main_organize_btns = QHBoxLayout()
        
        layout_main_shx = QVBoxLayout()
        layout_main_shx_btns = QHBoxLayout()
        
        group_prepare = QGroupBox("Przygotowanie")
        group_shx = QGroupBox("Doczyść SHX")
        group_rasterize = QGroupBox("Konwertowanie")
        group_final = QGroupBox("Wyjściowe")
        
        self.tree_view = TreeListView()
        self.model = TreeListModel()
        
        self.view_suffix = CustomComboBox()
        self.view_suffix.addItems(self.view_suffix.setModel())
        
        self.view_suffix_wniosek = CustomComboBox()
        self.view_suffix_wniosek.addItems(self.view_suffix.setModel())
        
        self.tree_view.setModel(self.model)
        
        #resize header after model created
        self.tree_view.header().resizeSection(0,250)
        self.tree_view.header().resizeSection(1,75)
        self.tree_view.setSelectionMode(self.tree_view.selectionMode().ExtendedSelection)
        
        layout_main.addWidget(self.tree_view)
        
        self.btn_resetAll = QPushButton('Wyczyść wszystko', self)
        self.btn_resetAll.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum )
        self.btn_wniosek = QPushButton('Wyodrębnij', self)
        self.btn_wniosek.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Minimum )
        self.input_wniosek = QLineEdit(self)
        self.input_wniosek.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred )
        self.input_wniosek.setMinimumWidth(60)
        self.btn_delete = QPushButton('Usuń', self)
        self.btn_delete.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum )
        

        group_prepare.setLayout(layout_main_organize_btns)
        layout_main_organize_btns.addWidget(self.btn_wniosek)
        layout_main_organize_btns.addWidget(self.input_wniosek)
        layout_main_organize_btns.addWidget(self.view_suffix_wniosek)
        layout_main_organize_btns.addSpacing(10)
        layout_main_organize_btns.addWidget(self.btn_delete)
        layout_main_organize_btns.addWidget(self.btn_resetAll)  
        layout_main_organize.addWidget(group_prepare)
        
        group_shx.setLayout(layout_main_shx_btns)
        self.btn_deleteSHX =  QPushButton('Wyczyść SHX', self)
        self.btn_deleteSHX.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum )
        layout_main_shx_btns.addWidget(self.btn_deleteSHX, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_main_shx_btns.addSpacing(10)
        layout_main_shx.addWidget(group_shx)
        
        group_rasterize.setLayout(layout_main_rasterize_btns)
        self.btn_rasterizePDF =  QPushButton('Konwertuj', self)
        self.label_dpi_edit = QLabel("DPI")
        #Maximum wypełni do labela
        self.btn_rasterizePDF.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        self.label_dpi_edit.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        self.dpi_edit = QLineEdit(self)
        self.dpi_edit.setValidator(QRegularExpressionValidator(QRegularExpression('^[0-9]*$')))
        self.dpi_edit.setMaxLength(3)
        self.dpi_edit.setFixedWidth(10 * self.dpi_edit.maxLength())
        self.dpi_edit.setText("72")
        self.btn_info_page = QPushButton('Info (1 strona)',self)
        layout_main_rasterize_btns.addWidget(self.btn_rasterizePDF)
        layout_main_rasterize_btns.addWidget(self.label_dpi_edit)
        layout_main_rasterize_btns.addWidget(self.dpi_edit)
        layout_main_rasterize_btns.addWidget(self.btn_info_page, alignment=Qt.AlignmentFlag.AlignRight)
        layout_main_rasterize_btns.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_main_rasterize.addWidget(group_rasterize)
        
        group_final.setLayout(layout_main_flat_btns)
        self.btn_flat = QPushButton('Flat', self)
        self.btn_flat.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum )
        layout_main_flat_btns.addWidget(self.btn_flat)
        layout_main_flat_btns.addWidget(self.view_suffix)
        layout_main_flat_btns.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_main_flat.addWidget(group_final)
        
        
        layout_main.addLayout(layout_main_organize)
        layout_main.addLayout(layout_main_shx)
        layout_main.addLayout(layout_main_rasterize)
        layout_main.addLayout(layout_main_flat)
        
        #cntr
        cntr_widget = QWidget()
        cntr_widget.setLayout(layout_main)
        self.setCentralWidget(cntr_widget)

    
    def populateArrayModel(self,obj):
        
        tmp_filepath = str(obj.toLocalFile())
        tmp_size = os.path.getsize(tmp_filepath)
        
        self.model.dataArr.append(File(obj.fileName(),tmp_filepath,utility.convertBytes(tmp_size)))
        self.model.layoutChanged.emit()
        
        file_example = self.model.dataArr[0].__dict__
        
        for key in file_example:
          print(key + ' => ' + file_example[key])
      
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:

            event.accept()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.DropAction.CopyAction)
        else:
            event.ignore()
            
    def dropEvent(self,event):
        if event.mimeData().hasUrls:
            
            event.setDropAction(Qt.DropAction.CopyAction)
            
            for url in event.mimeData().urls():
                if url.isLocalFile() and utility.extChecker(str(url.fileName())):
                    self.populateArrayModel(url)
                else:
                    event.ignore()
    
    # ---- HANDLERS ----
    def bindHandlers(self):
        
        self.btn_deleteSHX.clicked.connect(self.deleteSHXItems)
        self.btn_flat.clicked.connect(self.flatSelectedItem)
        self.btn_resetAll.clicked.connect(self.resetModelView)
        self.btn_delete.clicked.connect(self.deleteItem)
        self.btn_wniosek.clicked.connect(self.processWniosek)
        self.btn_rasterizePDF.clicked.connect(self.rasterizePDF)
        self.btn_info_page.clicked.connect(self.getInfoPage)
        
    def flatSelectedItem(self):
           
        indexes = self.tree_view.selectedIndexes()
        cmbbox_index = self.view_suffix.currentText()

        config = dict(combo_val=cmbbox_index)
        

        if len(indexes) == 0:
            error_dialog = CustomDialog("Brak zaznaczonych map")
            error_dialog.exec() 
            return False        
            
        for index in indexes:
        
            row = index.row()
            
            if(index.column() == 0):
                
                self.model.layoutChanged.emit()
                self.model.dataArr[row]._state = 'Przetwarzam mape...'
                self.model.dataChanged.emit(index,index)
                
            
                #process event queue before running external code
                app.processEvents()
            
                utility.flattenPDFs(self.model.dataArr[row]._filepath,config)

                self.model.dataArr[row]._state = 'Przetworzony'
                self.model.dataChanged.emit(index,index)
                self.model.layoutChanged.emit()
            
            
        return True
        
    def resetModelView(self):
        
        self.model.dataArr = []
        self.model.layoutChanged.emit()    
    
    def deleteItem(self):
        
        indexes = self.tree_view.selectedIndexes()
        
        if indexes:
            
            index = indexes[0]
            del self.model.dataArr[index.row()]
            self.model.layoutChanged.emit()
            self.tree_view.clearSelection
            
    def processWniosek(self):
        
        indexes = self.tree_view.selectedIndexes()

        if len(indexes) == 0:
            error_dialog = CustomDialog("Brak zaznaczonego pdf do wyodrębnienia")
            error_dialog.exec() 
            return False  
        
        #TODO do poprawy 
        if len(indexes) > 3:
            error_dialog = CustomDialog("Zaznacz tylko jeden pdf")
            error_dialog.exec() 
            return False  
        
        if indexes:
            
            index = indexes[0]
            astr = self.input_wniosek.text()
      
            
            if(astr == ""):
                
                error_dialog = CustomDialog("Wybierz jakie strony do wyodrębnienia w polu obok np '1-4' '1,3,5'")
                error_dialog.exec() 
                return False 
            
            elif(utility.has_numbers(astr)):
                
                resultArr = utility.parse_range(astr)
            
            else:
                 
                error_dialog = CustomDialog("Wprowadź liczby")
                error_dialog.exec() 
                return False  
            
            self.model.layoutChanged.emit()
            self.model.dataArr[index.row()]._state = 'Przetwarzam pdf...'
            self.model.dataChanged.emit(index,index)
            
            #process event queue before running external code
            app.processEvents()
            
            utility.TrimPDF(self.model.dataArr[index.row()]._filepath,resultArr)

            self.model.dataArr[index.row()]._state = 'Przetworzony'
            
            #reset
            resultArr = None
            
            self.model.dataChanged.emit(index,index)
            self.model.layoutChanged.emit()
            
        return True    
    
    def deleteSHXItems(self):
        
        indexes = self.tree_view.selectedIndexes()

        if len(indexes) == 0:
            error_dialog = CustomDialog("Brak zaznaczonego pdf do wyczyszczenia SHX")
            error_dialog.exec() 
            return False  
        
        #TODO do poprawy 
        if len(indexes) > 3:
            error_dialog = CustomDialog("Zaznacz tylko jeden pdf")
            error_dialog.exec() 
            return False  
        
        if indexes:
            
            index = indexes[0]
            
            self.model.layoutChanged.emit()
            self.model.dataArr[index.row()]._state = 'Przetwarzam pdf...'
            self.model.dataChanged.emit(index,index)
            
            #process event queue before running external code
            app.processEvents()
            
            utility.deleteSHX(self.model.dataArr[index.row()]._filepath)

            self.model.dataArr[index.row()]._state = 'Przetworzony'
            
            #reset
            resultArr = None
            
            self.model.dataChanged.emit(index,index)
            self.model.layoutChanged.emit()
        
        return True
    
    def rasterizePDF(self):
        
        indexes = self.tree_view.selectedIndexes()
        dpi_value = int(self.dpi_edit.text())
        suffix_name = "--RASTER-OUT.pdf"

        config = dict(combo_val=suffix_name,dpi_value=dpi_value)
        

        if len(indexes) == 0:
            error_dialog = CustomDialog("Brak zaznaczonych plików to konwersji")
            error_dialog.exec() 
            return False        
            
        for index in indexes:
        
            row = index.row()
            dpi_val = self.dpi_edit.text()
            
            if(index.column() == 0):
            
                self.model.dataArr[row]._state = 'Konwertuje...'
                self.model.dataChanged.emit(index,index)

                #process event queue before running external code
                app.processEvents()
            
                utility.simplifyRasterize(self.model.dataArr[row]._filepath,config)

                self.model.dataArr[row]._state = 'Przetworzony'
                self.model.dataChanged.emit(index,index)
                self.model.layoutChanged.emit()
            
            
        return True
    
    def getInfoPage(self):
        
        indexes = self.tree_view.selectedIndexes()

        if len(indexes) == 0:
            error_dialog = CustomDialog("Brak zaznaczonego pdf'a")
            error_dialog.exec() 
            return False  
        
        #TODO do poprawy 
        if len(indexes) > 3:
            error_dialog = CustomDialog("Zaznacz tylko jeden pdf")
            error_dialog.exec() 
            return False  
        
        if indexes:
            
            index = indexes[0]
            callback = utility.isVectorOrScan(self.model.dataArr[index.row()]._filepath)
            info_dialog = CustomDialog(callback, "Info")
            info_dialog.exec()
            
        return True
    
app = QApplication(sys.argv)
app.setStyle("Fusion")
app.setStyleSheet('QPushButton { font-size: 10px } QGroupBox { font-size: 10px; margin: 8px }')

w = MainWindow()
w.show()

#event loop
sys.exit(app.exec())