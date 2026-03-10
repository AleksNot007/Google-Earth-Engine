
// 0. НУЖНЫЙ system:index
var FIELD_INDEX = '00000000000000000023';

// 1. Все поля
var fields = ee.FeatureCollection('projects/crucial-runner-444819-i7/assets/field');

// одно поле как Feature
var field = ee.Feature(
  fields.filter(ee.Filter.eq('system:index', FIELD_INDEX)).first()
);
print('Выбранное поле', field);

// Геометрия этого поля
var region = field.geometry();

// 2. Даты
var start = ee.Date('2025-06-01');
var end   = ee.Date('2025-06-15');

// 3. Landsat SR
var colSr = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterDate(start, end)
    .filterBounds(region);

// 4. NDVI по мозаике (через expression)
var medianSr = colSr.median();

// Посмотреть имена бэндов, что реально есть:
print('Бэнды medianSr', medianSr.bandNames());

// NDVI = (NIR - RED) / (NIR + RED)
// для Landsat 8/9 SR: NIR = SR_B5, RED = SR_B4
var ndvi = medianSr.expression(
  '(nir - red) / (nir + red)',
  {
    nir: medianSr.select('SR_B5'),
    red: medianSr.select('SR_B4')
  }
).rename('NDVI');

// 5. Диагностика
print('Кол-во сцен', colSr.size());
print('Бэнды ndvi', ndvi.bandNames());

// 6. Слои на карту
Map.addLayer(region, {color: 'red'}, 'field');
Map.addLayer(
  ndvi.clip(region),
  {min: 0, max: 0.8, palette: ['white', 'yellow', 'green']},
  'NDVI'
);

// Сетка точек внутри поля + значения NDVI в этих точках
var ndviSamples = ndvi.sample({
  region: region,
  numPixels: 500,    // сколько точек взять
  scale: 30,
  geometries: true   // чтобы были координаты
});

print('Выборка NDVI по точкам', ndviSamples);

Export.table.toDrive({
  collection: ndviSamples,
  description: 'NDVI_samples_field_23',
  fileFormat: 'CSV'
});
