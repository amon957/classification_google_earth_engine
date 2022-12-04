import ee
import geemap

ee.Authenticate()
ee.Initialize()

study_area=ee.Collection.loadTable("projects/ee-amon-melly/assets/kapchorwa")

study_area_geometry=study_area.geometry()

x,y = study_area_geometry.centroid().coordinates().getInfo()[0],aoi.centroid().coordinates().getInfo()[1]
aoi=ee.Geometry.Point(x,y)

image = (ee.ImageCollection("COPERNICUS/S2")
                       .filterBounds(aoi)
                       .filterDate('2021-03-01','2021-03-30')
                       .sort('CLOUDY_PIXEL_PERCENTAGE')
                       .first()
                       .select('B[1-8]')
                       .clip(study_area_geometry)
                      )

#1-Cultivated Land #FA8072
#2-Dense Forest #00CC66
#3-Tea Plantation #00FF00
#4-Grassland  #48D1CC
#5-Shrubs  #FFFF00
#6-Bareland #F5DEB3

features=[]
for f in m.draw_features:
    features.append(f.set('class',1))

training_areas=ee.FeatureCollection(features)
training_pixes=image.sampleRegions(collection=training_areas,properties=['class'])
classifier=ee.Classifier.smileRandomForest(100).train(features=training_pixes,
                                                     classProperty='class'
                                                     )
new_classified_image=image.classify(classifier)

#Results Visualization

legend_dict={'Cultivated Land':'FA8072',
             'Dense Forest':'00CC66',
             'Tea Plantation':'00FF00',
             'Grassland':'48D1CC',
             'Shrubs':'FFFF00',
             'Bareland':'F5DEB3'}

c_parameters = {'min':1, 'max':6, 'palette': ['FA8072','00CC66','00FF00','48D1CC','FFFF00','F5DEB3']}

m = geemap.Map(location=[y,x], zoom_start=12)    
m.addLayer(classified_image,c_parameters,'Classified Image')
m.add_legend(title="Legend", legend_dict=legend_dict)
m.addLayerControl()
m

#Save to file
import os

out_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
out_file = os.path.join(out_dir, 'Classified_2021.tif')
geemap.ee_export_image(new_classified_image, filename=out_file, scale=10)