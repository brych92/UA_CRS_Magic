from qgis.core import QgsTask, QgsCoordinateTransform, \
    QgsCsException, QgsCoordinateReferenceSystem, \
    QgsGeometry, QgsDistanceArea, QgsCoordinateTransformContext, QgsUnitTypes, QgsPoint, QgsPointXY


class findCrs(QgsTask):
    def __init__(self, description, layers, click_point, canvas_crs, project):
        super().__init__(description, QgsTask.CanCancel)        
        self.status = None
        
        self.layers = layers #шари для яких буде підбиратися СК
        self.layers_qty=len(layers)
        
        self.canvas_crs = canvas_crs        
        self.project = project
        self.click_point = click_point
        #self.simple_search = simple_search Тут був прискорений пошук за центроїдом екстенту, але покишо відключу його
        
        self.failure_reason=None
        self.result=None
        
        self.message=''
        
        proj_list={'EPSG:3857' : '+proj=noop', #proj коди перетворень, без них на версії 3.22 не працювало
            'EPSG:4326' : '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5562' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=21 +k=1 +x_0=4500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.322 +y=-121.372 +z=-75.847 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5563' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=27 +k=1 +x_0=5500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5564' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=33 +k=1 +x_0=6500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5565' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=39 +k=1 +x_0=7500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5566' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=21 +k=1 +x_0=500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5567' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=27 +k=1 +x_0=500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5568' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=33 +k=1 +x_0=500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5569' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=39 +k=1 +x_0=500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5576' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=39 +k=1 +x_0=13500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5577' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=21 +k=1 +x_0=500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5578' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=24 +k=1 +x_0=500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5579' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=27 +k=1 +x_0=500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5580' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=30 +k=1 +x_0=500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5581' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=33 +k=1 +x_0=500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5582' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=36 +k=1 +x_0=500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5583' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=39 +k=1 +x_0=500000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:6381' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=21 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:6382' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=24 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:6383' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=27 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:6384' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=30 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:6385' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=33 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:6386' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=36 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:6387' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=39 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5558' : '+proj=pipeline +step +inv +proj=cart +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5560' : '+proj=pipeline +step +proj=unitconvert +xy_in=deg +z_in=m +xy_out=rad +z_out=m +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:5561' : '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9821' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=30.5 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9831' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=34.5 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9832' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=28.6666666666667 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9833' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=24.8333333333333 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9834' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=35 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9835' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=37.5 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9836' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=28.5 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9837' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=23.5 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9838' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=36 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9839' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=24.75 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9840' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=32 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9841' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=39 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9842' : '+proj=pipeline +step +inv +proj=lcc +lat_0=42 +lon_0=3 +lat_1=41.25 +lat_2=42.75 +x_0=1700000 +y_0=1200000 +ellps=GRS80 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9843' : '+proj=pipeline +step +inv +proj=lcc +lat_0=43 +lon_0=3 +lat_1=42.25 +lat_2=43.75 +x_0=1700000 +y_0=2200000 +ellps=GRS80 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9851' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=24 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9852' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=31.8333333333333 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9853' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=30 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9854' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=33.8333333333333 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9855' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=27 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9856' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=34.5 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9857' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=25.5 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9858' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=36.5 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9859' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=33.5 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9860' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=27 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9861' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=31.5 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9862' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=26 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9863' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=32 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9864' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=30.5 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:9865' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0 +lon_0=33 +k=1 +x_0=300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=24.353 +y=-121.36 +z=-75.968 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:4284' : '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=25 +y=-141 +z=-78.5 +rx=0 +ry=-0.35 +rz=-0.736 +s=0 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:4179' : '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=2.329 +y=-147.042 +z=-92.08 +rx=0.309 +ry=-0.325 +rz=-0.497 +s=5.69 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:4178' : '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=26 +y=-121 +z=-78 +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:7825' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0.0833333333333333 +lon_0=23.5 +k=1 +x_0=1300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=23.57 +y=-140.95 +z=-79.8 +rx=0 +ry=-0.35 +rz=-0.79 +s=-0.22 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:7826' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0.0833333333333333 +lon_0=26.5 +k=1 +x_0=2300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=23.57 +y=-140.95 +z=-79.8 +rx=0 +ry=-0.35 +rz=-0.79 +s=-0.22 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:7827' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0.0833333333333333 +lon_0=29.5 +k=1 +x_0=3300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=23.57 +y=-140.95 +z=-79.8 +rx=0 +ry=-0.35 +rz=-0.79 +s=-0.22 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:7828' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0.0833333333333333 +lon_0=32.5 +k=1 +x_0=4300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=23.57 +y=-140.95 +z=-79.8 +rx=0 +ry=-0.35 +rz=-0.79 +s=-0.22 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:7829' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0.0833333333333333 +lon_0=35.5 +k=1 +x_0=5300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=23.57 +y=-140.95 +z=-79.8 +rx=0 +ry=-0.35 +rz=-0.79 +s=-0.22 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:7830' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0.0833333333333333 +lon_0=38.5 +k=1 +x_0=6300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=23.57 +y=-140.95 +z=-79.8 +rx=0 +ry=-0.35 +rz=-0.79 +s=-0.22 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84',
            'EPSG:7831' : '+proj=pipeline +step +inv +proj=tmerc +lat_0=0.0833333333333333 +lon_0=41.5 +k=1 +x_0=7300000 +y_0=0 +ellps=krass +step +proj=push +v_3 +step +proj=cart +ellps=krass +step +proj=helmert +x=23.57 +y=-140.95 +z=-79.8 +rx=0 +ry=-0.35 +rz=-0.79 +s=-0.22 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84'
            }
        
        
        self.total_result={} #словник в форматі [назва шару : {чи шар перевірений, вірогідна ск, помилка, інші можливі СК з відстанями до них}
        main_crs=QgsCoordinateReferenceSystem('EPSG:3857')
        self.transformContext = QgsCoordinateTransformContext()#project.transformContext() мало брати з перетворень які заьиті як стандртні в проекті...але на 3.22 не працює
        
        for key, value in proj_list.items():
            crs=QgsCoordinateReferenceSystem(key)
            self.transformContext.addCoordinateOperation(crs,main_crs,value)
        #self.transformContext.readSettings()
        #self.message=''+str(self.transformContext.coordinateOperations())
    

    def getFailure(self):
        return self.failure_reason
    
    def run(self):
        self.setProgress(10)
        self.message=self.message+f'СК проекту: {self.canvas_crs.authid()}\r\n'
        self.message=self.message+f'Точка кліку: {self.click_point.toString(4)}\r\n'
        for layer in self.layers:            
            self.message=self.message+f'\r\nПеревіряємо шар: {layer.name()}\r\n*************************************************************\r'
            
            self.total_result[layer.name()]={}
            self.total_result[layer.name()]['Checked']=True #відмічаємо шо шар провірявся
            
            centroid=self.find_center(layer) #Визначаємо центроїд шару
            self.message=self.message+f'Центроїд шару: {centroid.toString(4)}\r\n===============================================================\r\n'
            if centroid:
                CRS_list=self.range_distances(centroid, self.click_point) #Отримуємо список з пар (СК, відстаь до точки кліку в цій СК)
            else:
                self.total_result[layer.name()]['Error']=self.failure_reason
            if CRS_list:
                found_crs=QgsCoordinateReferenceSystem(CRS_list[0][0])            
                layer.setCrs(found_crs)
                
                self.total_result[layer.name()]['PossibleCRS']=f"{CRS_list[0][0]} - {f'{CRS_list[0][1]:,.0f}'.replace(',', ' ')} метрів від точки кліку" #Головна СК
                if len(CRS_list)>1:
                    lowest_keys = [key for key, value in CRS_list[1:4]]
                    possible_crs = '\r\n'.join([f"{key} - {f'{value:,.0f}'.replace(',', ' ')} метрів від точки кліку" for key, value in CRS_list[1:4]])

                    self.total_result[layer.name()]['OtherPossibleCRS'] = f'\r\n\tІнші можливі СК:\r\n {possible_crs}' #Інші СК
                else:
                    self.total_result[layer.name()]['OtherPossibleCRS']=''
            else:
                self.total_result[layer.name()]['Error']=self.failure_reason
        if self.total_result:
            self.setProgress(100)
            return True
        else:            
            if not self.failure_reason:
                self.failure_reason='Помилка підбору СК для шарів'
            return False
    
    def range_distances(self, centroid, click_point):
        
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
        
        distance_results={}
        
        progress_step=30/len(crs_list)/self.layers_qty
        
        for crs_code in crs_list:                
            #Створюємо СК на основі коду з списку
            crs = QgsCoordinateReferenceSystem(crs_code)
            
            xform = QgsCoordinateTransform(crs, self.canvas_crs, self.transformContext)
            xform.invalidateCache()
            xform.setBallparkTransformsAreAppropriate(True)
            xform.setAllowFallbackTransforms(True)
            #Перетворюємо центроїд шару в СК карти приймаючи вихідну проекцію зі списку            
            if crs.isValid():
                self.message=self.message+f'{crs_code}: '
            else:
                self.message=self.message+f'{crs_code}(невалідна): '
            try:
                
                transformed_centroid = xform.transform(centroid)
                self.message=self.message+f'\t\t {transformed_centroid.toString(4)}\t\t '
                #Вираховуємо відстань від перетвореного центроїду до референсної точки
                distance = click_point.distance(transformed_centroid)                
                
                #Записуємо результат
                if distance<500000:
                    distance_results[crs_code]=int(distance)
                self.message=self.message+f'{int(distance):,} метрів від точки кліку\r\n'.replace(',',' ').rjust(36)
            except Exception as e:
                self.message=self.message+f'Помилка трансформації: {str(e)}\r\n'
                continue
            
            self.setProgress(self.progress()+progress_step)
            
        if distance_results:
            result=sorted(distance_results.items(), key=lambda x: x[1])
            return  result #повертаємо відсортовані результати як ліст лістів
        else:
            self.failure_reason="Не вдалося підібрати СК, можливо об'єкти у відносній СК, або мають неправильну геометрію"
            return None 
        
    def find_center(self,layer):
        # if self.simple_search:
            # self.setProgress(self.progress()+50/self.layers_qty)
            # extent = layer.extent()
            # geometry = QgsGeometry.fromRect(extent)
            # result = geometry.centroid().asPoint()
            # return result
        
        geometries = []
        featureQTY=layer.featureCount()
        
        progress_step=50/featureQTY/self.layers_qty #50 - Кількість вісотків виконання на функцію
        
        for feature in layer.getFeatures():
            if feature.hasGeometry():
                centroid=feature.geometry().makeValid().centroid()
                if not centroid.asWkt()=="Point (0 0)":                    
                    geometries.append(feature.geometry().makeValid().centroid())
            self.setProgress(self.progress()+progress_step)
        
        multipart_geometry = QgsGeometry.collectGeometry(geometries)
        if multipart_geometry.isEmpty():
            self.failure_reason="Центроїд не визначено, можливо геометрія об'єктів відсутня"
            return None
        else:
            result = multipart_geometry.centroid().asPoint()
            #self.message=self.message+result+'\r\n'
            return result
            