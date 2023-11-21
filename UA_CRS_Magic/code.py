import os
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QApplication
from qgis.core import Qgis, QgsVectorLayer, QgsProject, QgsMapLayerType, QgsCoordinateTransform, QgsCsException, QgsCoordinateReferenceSystem
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsMapToolEmitPoint

class CRS_Magic:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.folder_path=os.path.expanduser('~')
        self.activated=False
        self.message_item=None
        self.action_reference=None
        self.pointTool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.give_center=False
        self.centroid=None
        
    def initGui(self):
        icon = QIcon(os.path.join(self.plugin_dir,"Icon.png"))
        action = QAction(icon, "Підібрати систему кординат для вибраного шару",self.iface.mainWindow())
        action.triggered.connect(self.Find_CRS)
        action.setEnabled(True)
        action.setCheckable(True)
        self.iface.addToolBarIcon(action)
        self.actions.append(action)
        self.action_reference=action
        
    def unload(self):
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
    
    def isControlOrShift(self):
        ctrl_pressed = Qt.ControlModifier & QApplication.keyboardModifiers()
        shift_pressed = Qt.ShiftModifier & QApplication.keyboardModifiers()
            
        if ctrl_pressed or shift_pressed:
            return True
        else:
            return False
    
    def Find_CRS(self):
        message_bar = self.iface.messageBar()
        #Якщо інструмент увімкнено - вимикаємо
        if self.activated:
            self.activated=False
            self.action_reference.setChecked(False)
            self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())
            
            try:
                self.message_item.dismiss()
            except RuntimeError as e:
                pass
            return
        layer = self.iface.activeLayer()
        
        #перевірка на те що шар векторний
        if layer is None or layer.type() != QgsMapLayerType.VectorLayer:
            self.message_item = message_bar.pushMessage("Спочатку виберіть векторний шар", Qgis.MessageLevel.Warning, 5)
            self.action_reference.setChecked(False)
            return
        
        #перевірка на наявність об'єктів в шарі
        if layer.featureCount() == 0:
            message_item = message_bar.pushMessage("Неможливо підібрати СК. Вибраний шар не містить об'єктів.", Qgis.MessageLevel.Warning, 5)
            self.action_reference.setChecked(False)
            return
        
        #позначаємо як увімкнений
        self.activated=True
        self.action_reference.setChecked(True)
        
        project = QgsProject.instance()
        canvas = self.iface.mapCanvas()
        map_crs = canvas.mapSettings().destinationCrs()
        
        #Список СК для перебору
        crs_list = [
            # WGS 84
            'EPSG:3857', 'EPSG:4326',
            # UCS2000 Gauss-Kruger zones
            'EPSG:5562', 'EPSG:5563', 'EPSG:5564', 'EPSG:5565', 'EPSG:5566', 'EPSG:5567', 'EPSG:5568', 'EPSG:5569',
            # Застарілі
            # 'EPSG:5570', 'EPSG:5571', 'EPSG:5572', 'EPSG:5573', 'EPSG:5574', 'EPSG:5575',
            'EPSG:5576', 'EPSG:5577', 'EPSG:5578', 'EPSG:5579', 'EPSG:5580', 'EPSG:5581', 'EPSG:5582', 'EPSG:5583',
            # Додала Юлія
            'EPSG:6381', 'EPSG:6382', 'EPSG:6383', 'EPSG:6384', 'EPSG:6385', 'EPSG:6386', 'EPSG:6387',
            # UCS Geocentric Meters
            'EPSG:5558',
            # UCS2000 Geographic
            'EPSG:5560', 'EPSG:5561',
            # UCS2000 Locals
            'EPSG:9821', 'EPSG:9831', 'EPSG:9832', 'EPSG:9833', 'EPSG:9834',
            'EPSG:9835', 'EPSG:9836', 'EPSG:9837', 'EPSG:9838', 'EPSG:9839',
            'EPSG:9840', 'EPSG:9841', 'EPSG:9842', 'EPSG:9843', 'EPSG:9851',
            'EPSG:9852', 'EPSG:9853', 'EPSG:9854', 'EPSG:9855', 'EPSG:9856',
            'EPSG:9857', 'EPSG:9858', 'EPSG:9859', 'EPSG:9860', 'EPSG:9861',
            'EPSG:9862', 'EPSG:9863', 'EPSG:9864', 'EPSG:9865',
            # Pulkovo Geographic
            'EPSG:4284', 'EPSG:4179', 'EPSG:4178',
            # CS63 XZones
            'EPSG:7825', 'EPSG:7826', 'EPSG:7827', 'EPSG:7828', 'EPSG:7829', 'EPSG:7830', 'EPSG:7831'
        ]        
        self.give_center=False
        if self.isControlOrShift():
            self.give_center=True
            message_bar.pushMessage(f"Клацніть на карті на об'єктах шару '{layer.name()}', що являються правильною геометрією", Qgis.MessageLevel.Info, 10)
            self.message_item=message_bar.currentItem()
        else:
            message_bar.pushMessage(f"Клацніть на карті приблизне можливе місцезнаходження об'єктів шару '{layer.name()}'", Qgis.MessageLevel.Info, 10)
            self.message_item=message_bar.currentItem()
        
        self.centroid=None
        def find_crs(click_point):
            if self.give_center:
                print('with shift activated')
                canvas_crs = canvas.mapSettings().destinationCrs()
                layer_crs = layer.crs()
                transform = QgsCoordinateTransform(canvas_crs, layer_crs, QgsProject.instance())

                # Transform the canvas point to layer coordinates
                self.centroid = transform.transform(click_point)
                try:
                    self.message_item.dismiss()
                except RuntimeError as e:
                    pass
                message_bar.pushMessage(f"Клацніть на карті приблизне можливе місцезнаходження об'єктів шару '{layer.name()}'", Qgis.MessageLevel.Info, 10)
                self.message_item=message_bar.currentItem()
                self.give_center=False
                return
            elif not self.centroid:
                print('not centroid')
                self.centroid = layer.extent().center()
            centroid=self.centroid
            print(self.centroid)
            distance_results={}
            def zoomToLayerExtent(layer, canvas):                  
                layer_extent = layer.extent()
                layer_crs = layer.crs()
                canvas_crs = canvas.mapSettings().destinationCrs()
                if layer.crs()!=canvas.mapSettings().destinationCrs(): 
                    transform = QgsCoordinateTransform(layer_crs, canvas_crs, QgsProject.instance())
                    canvas_extent = transform.transformBoundingBox(layer_extent)
                else:
                    canvas_extent = layer_extent
                canvas.setExtent(canvas_extent)
                self.iface.mapCanvas().zoomScale(self.iface.mapCanvas().scale()*3)
                canvas.refresh()
            
            # Беремо центроїд шару
            centroid = layer.extent().center()
            # Приймаємо за базову точку точку кліку
            reference_point=click_point
            # створюємо пусті змінні в які буе записуватися СК з найменшою відстанню від точки кліку
            closest_crs = None
            min_distance = float("inf")
            
            for crs_code in crs_list:                
                #Створюємо СК на основі коду з списку
                crs = QgsCoordinateReferenceSystem(crs_code)
                
                xform = QgsCoordinateTransform(crs, map_crs, project)
                #Перетворюємо центроїд шару в СК карти приймаючи вихідну проекцію зі списку
                try:
                    transformed_centroid = xform.transform(centroid)
                    #Вираховуємо відстань від перетвореного центроїду до референсної точки                
                    distance = reference_point.distance(transformed_centroid)
                    #print(f'Відстань: {distance} {crs_code}({crs})')
                    #Якщо Відстань менша за попередньозбережену записуємо СК як найвірогіднішу на даній ітерації циклу
                    distance_results[crs_code]=distance
                    if distance < min_distance:                        
                        min_distance = distance
                        closest_crs = crs
                except QgsCsException as e:                    
                    #print(f"Не вдалося застосувати трансформацію {crs_code}: {e}")
                    continue
            
            # Застосовуємо підібрану СК до шару
            if closest_crs:
                layer.setCrs(closest_crs)
                zoomToLayerExtent(layer, canvas)
                
                #відображення інших можливих перетворень
                sorted_crs = sorted(distance_results.items(), key=lambda x: x[1])
                lowest_keys = [key for key, value in sorted_crs[1:4]]
                result_string = f'Інші можливі СК: {", ".join(lowest_keys)}'
                
                message_item = message_bar.pushMessage(f"СК змінено на {closest_crs.authid()}. Перевірте коректність підбору СК по фотоплану. {result_string}.", Qgis.MessageLevel.Info, 10)
                
                self.activated=False
                self.action_reference.setChecked(False)
                self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())                
                try:
                    self.message_item.dismiss()
                except RuntimeError as e:
                    pass
                #print(f"CRS changed to {closest_crs.authid()}")
            else:
                message_item = message_bar.pushMessage("Не вдалося знайти СК для даного шару", Qgis.MessageLevel.Warning, 5)
                self.activated=False
                self.action_reference.setChecked(False)
                self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())
                
                try:
                    self.message_item.dismiss()
                except RuntimeError as e:
                    pass
                
                #self.action_reference.setChecked(False)
                #print("No CRS found from the list.")
                
        
        self.pointTool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.pointTool.canvasClicked.connect(find_crs)
        canvas.setMapTool(self.pointTool)

    
   