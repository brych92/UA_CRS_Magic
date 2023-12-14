import os
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QApplication
from qgis.core import Qgis, QgsApplication, QgsVectorLayer, QgsProject, QgsMapLayerType, QgsCoordinateTransform, QgsCsException, QgsCoordinateReferenceSystem,\
    QgsWkbTypes, QgsGeometry, QgsRectangle, QgsPointXY
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand
from .find_crs import findCrs
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics, QCursor, QPixmap


class CustomMessageBox(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)

        # Set the window icon
        self.plugin_dir = os.path.dirname(__file__)
        icon = QIcon(os.path.join(self.plugin_dir,"icon.png"))        
        self.setWindowIcon(icon)

        # Create a QLabel widget with HTML formatting
        text_edit = QTextEdit()
        
        html_text=message.replace("\n", "<br>")
        
        text_edit.setHtml(html_text)
        max_line_width = 0
        font_metrics=QFontMetrics(text_edit.font())
        for line in html_text.split('<br>'):
            line_width = font_metrics.width(line)
            max_line_width = max(max_line_width, line_width)
        self.setMinimumWidth(int(max_line_width) + 20)
        
        line_height = font_metrics.height()
        height=min(640,int(html_text.count('<br>')*line_height*1.5))
        self.setMinimumHeight(height)
        
        text_edit.setReadOnly(True)
        
        # Create a QPushButton to close the dialog
        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self.accept)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(ok_button)

        self.setLayout(layout)

class CRS_Magic:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.folder_path=os.path.expanduser('~')
        self.activated=False
        
        self.pointTool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        cursor_pixmap=QPixmap(os.path.join(self.plugin_dir,"cursor.png")).scaledToHeight(32,Qt.SmoothTransformation)
        cursor=QCursor(cursor_pixmap)
        self.pointTool.setCursor(cursor)
        self.pointTool.canvasClicked.connect(self.get_CRS_dict)
        self.pointTool.deactivated.connect(self.tool_chaged)
        
        self.layers=[]
        self.selected_layers=[]
        
    def initGui(self):
        icon = QIcon(os.path.join(self.plugin_dir,"icon.png"))
        tooltip=f"・*.ﾟ☆ <b>UA CRS Magic</b> ☆ﾟ.*・\nПідібрати СК для вибраних шарів"
        
        action = QAction(icon, tooltip, self.iface.mainWindow())
        action.triggered.connect(self.Run)
        action.setEnabled(True)
        action.setCheckable(True)
        self.iface.addToolBarIcon(action)
        self.actions.append(action)
        self.action_reference=action
        
    def unload(self):
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
    
    def clearMBar(self):        
        mbar=self.iface.messageBar()
        for message in mbar.items():
            if message.text().startswith("[CRS Magic]"):
                message.dismiss()
    
    
    def get_CRS_dict(self,click_point):
        def status_changed(status):
            if status==3:
                fk_b_s=r'<span style="color:black">'
                fk_r_s='<span style="color:red">'
                fk_e=r'</span>'
                self.clearMBar()
                #print("Завершено!")
                #print('Звіт:')
                #print(task.message)
                result_message=f'[CRS Magic] Перевірте коректність підбору СК по фотоплану.\r\n\r\n'
                number=1
                
                for layer in self.selected_layers:
                    result_message=result_message+f'\r\n{number}. '
                    number=number+1
                    if layer.name() in task.total_result and task.total_result[layer.name()]['Checked']:
                        if 'PossibleCRS' in task.total_result[layer.name()]:
                            crs=task.total_result[layer.name()]['PossibleCRS']
                            other_crs=task.total_result[layer.name()]['OtherPossibleCRS']
                            result_message=result_message+f"{fk_b_s}Шар '{layer.name()}':\r\n СК змінено на {crs}.  {other_crs}{fk_e}\r\n"                                
                        else:
                            result_message=result_message+f"{fk_r_s}Шар '{layer.name()}': помилка підбору СК - {task.total_result[layer.name()]['Error']}{fk_e}\r\n"
                            
                    elif layer.type() != QgsMapLayerType.VectorLayer:
                        result_message=result_message+f"{fk_r_s}Шар '{layer.name()}': не було перевірено, так як він не векторний{fk_e}\r\n"
                        
                    elif layer.featureCount() == 0:
                        result_message=result_message+f"{fk_r_s}Шар '{layer.name()}': не було перевірено, так як в ньому відсутні об'єкти{fk_e}\r\n"
                                
                
                canvas.refreshAllLayers()
                self.clearMBar()
                custom_message_box = CustomMessageBox('Готово!', result_message)
                custom_message_box.exec_()
                # if len(self.selected_layers)>0:
                    # custom_message_box = CustomMessageBox('Готово!', result_message)
                    # custom_message_box.exec_()
                # else:
                    # message_bar.pushMessage(result_message, Qgis.MessageLevel.Success,0)
                    # print(result_message)
                self.activated=False
                self.action_reference.setChecked(False)
                self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())
                # print(task.message)
                return
            if status==4:
                self.clearMBar()
                # print(task.message)
                # print(task.last_action)
                if task.isCanceled():
                    print("Відмінено користувачем!")
                else:
                    if task.getFailure():                            
                        failure=task.getFailure()
                    else:
                        failure="Помилка, спробуйте ще раз!"
                    message_bar.pushMessage(f"[CRS Magic] {failure}", Qgis.MessageLevel.Warning, 5)                        
                
        self.clearMBar()
        message_bar = self.iface.messageBar()
        #print(f'Точка кліку до входження в задачу: {click_point.toString(4)}')
        project = QgsProject.instance()
        canvas = self.iface.mapCanvas()
        canvas_crs = canvas.mapSettings().destinationCrs()        
        work_crs = QgsCoordinateReferenceSystem('EPSG:3857')
        
        transformation = QgsCoordinateTransform(canvas_crs, work_crs, project)
        transformation.disableFallbackOperationHandler(True)
        tr_click_point=transformation.transform(click_point)
        
        message_bar.pushMessage('[CRS Magic] Зачекайте будь ласка, йде підбір СК...', Qgis.MessageLevel.Success,0)
        
        task = findCrs("Пошук можливих систем координат", self.layers, tr_click_point, work_crs, project)        
        
        task.statusChanged.connect(status_changed)
        task.setDependentLayers(self.layers)
        QgsApplication.taskManager().addTask(task)
        
        print('Запускаю процес підбору...')
    
    
    def Run(self):
        # simple_search=False
        
        # if self.isControlOrShift()=='shift':#якщо зажато шифт - виконуємо підбір по центру екстенту
            # simple_search=True            
        
        message_bar = self.iface.messageBar()
        self.clearMBar()
        
        if self.activated:#Якщо увімкнено то вимикаємо і відключаємо інструмент
            self.activated=False
            self.action_reference.setChecked(False)
            self.iface.mapCanvas().unsetMapTool(self.pointTool)            
            return
        
        layers=[]
        
        selected_layers = self.iface.layerTreeView().selectedLayersRecursive()
        
        if len(selected_layers)<1:
            message_bar.pushMessage("[CRS Magic] Спочатку виділіть векторні шари в панелі шарів!", Qgis.MessageLevel.Warning, 5)
            self.action_reference.setChecked(False)
            return
        
        for layer in selected_layers:
            if layer.type() == QgsMapLayerType.VectorLayer and layer.featureCount() != 0:
                layers.append(layer)
        
        if len(layers)<1:
            message_bar.pushMessage("[CRS Magic] Жоден з вибраних шарів не векторний або в не містить об'єктів для аналізу. Будь ласка спочатку виберіть векторні шари", Qgis.MessageLevel.Warning, 5)
            self.action_reference.setChecked(False)
            return
        
        # if self.isControlOrShift()=='ctrl':
            # self.visualizeExtent(layers)
            # self.action_reference.setChecked(False)
            # return
        
        layers_warning=''
        if not all(element in layers for element in selected_layers):
            layers_warning=".Зверніть увагу: деякі з вибраних шарів не векторні або в них відсутні об'єкти!" 
        
        self.activated=True
        self.action_reference.setChecked(True)
        
        if len(layers)==1:
            message_bar.pushMessage(f"[CRS Magic] Клікніть на карті приблизне можливе місцезнаходження об'єктів шару '{layers[0].name()}'{layers_warning}", Qgis.MessageLevel.Info, 0)
        else:
            message_bar.pushMessage(f"[CRS Magic] Клікніть на карті приблизне можливе місцезнаходження об'єктів вибраних шарів({len(selected_layers)}шт.) {layers_warning}", Qgis.MessageLevel.Info, 0)
        
        self.layers=layers
        self.selected_layers=selected_layers
        
        self.iface.mapCanvas().setMapTool(self.pointTool)
        

    def tool_chaged(self):
        self.activated=False
        self.action_reference.setChecked(False)
        self.clearMBar()
    
    def isControlOrShift(self):
        ctrl_pressed = Qt.ControlModifier & QApplication.keyboardModifiers()
        shift_pressed = Qt.ShiftModifier & QApplication.keyboardModifiers()
            
        if ctrl_pressed and shift_pressed:
            print('ctrl+shift')
            return 'ctrl+shift'
        elif ctrl_pressed:
            print('ctrl')
            return 'ctrl'
        elif shift_pressed:
            print('shift')
            return 'shift'
        else:
            return False
    
    def visualizeExtent(self, layers):
        canvas = self.iface.mapCanvas()
        canvas_crs = canvas.mapSettings().destinationCrs()

        # Create a rubber band for the total extent
        total_rubber_band = QgsRubberBand(canvas, QgsWkbTypes.LineGeometry)
        total_extent = QgsRectangle()

        for current_layer in layers:
            layer_extent = current_layer.extent()

            # Transform layer extent to canvas CRS
            transform = QgsCoordinateTransform(current_layer.crs(), canvas_crs, QgsProject.instance())
            layer_extent = transform.transformBoundingBox(layer_extent)
            # Combine the layer geometry with the total extent
            total_extent.combineExtentWith(layer_extent)

        # Set the geometry of the total rubber band
        total_rubber_band.setToGeometry(QgsGeometry.fromRect(total_extent).convertToType(QgsWkbTypes.LineGeometry), None)

        # Set the color and width of the total rubber band
        total_rubber_band.setColor(Qt.red)
        total_rubber_band.setWidth(1)        
        # Reset the total rubber band after a timeout
        def aaa():
            canvas = self.iface.mapCanvas()

            # Get all rubber bands on the canvas
            rubber_bands = [item for item in canvas.scene().items() if isinstance(item, QgsRubberBand)]

            # Remove each rubber band
            for band in rubber_bands:
                band.reset()

            # Refresh the canvas
            canvas.refresh()
        timer = QTimer()
        timer.timeout.connect(aaa)
        timer.start(10)  # Adjust the timeout as needed

        # Set the extent and zoom the canvas
        canvas.setExtent(total_extent)
        canvas.zoomScale(canvas.scale() * 1.5)
        canvas.refresh()
    
   