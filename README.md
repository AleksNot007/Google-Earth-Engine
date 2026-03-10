# Google Earth Engine NDVI Analysis

Автоматизированная система для расчета и экспорта индекса NDVI (Normalized Difference Vegetation Index) с использованием данных спутников Landsat 8/9 через Google Earth Engine API.

---

## 📋 Описание проекта

Проект предназначен для мониторинга состояния растительности сельскохозяйственных полей с использованием спутниковых данных Landsat. Система автоматически:
- Извлекает снимки Landsat за заданные временные интервалы
- Вычисляет индекс NDVI для каждого поля
- Оценивает облачность снимков
- Экспортирует результаты в CSV файлы на Google Drive

### Основные возможности

✅ **Автоматическая обработка множества полей** — пакетная обработка всех полей из FeatureCollection  
✅ **Временные интервалы** — разбиение периода анализа на 14-дневные окна  
✅ **Фильтрация облачности** — маскирование облаков и теней с использованием QA_PIXEL  
✅ **Комбинирование данных** — использование Landsat 8 и Landsat 9 для увеличения покрытия  
✅ **Обработка пропусков данных** — специальное значение -9999 при отсутствии снимков  
✅ **Экспорт в CSV** — автоматическое сохранение результатов на Google Drive

---

## 🛰️ О спутниковых данных Landsat

### Landsat 8 и Landsat 9

Проект использует данные **Landsat Collection 2, Tier 1, Level 2** (Surface Reflectance):
- **LANDSAT/LC08/C02/T1_L2** — Landsat 8 OLI/TIRS (запущен в 2013)
- **LANDSAT/LC09/C02/T1_L2** — Landsat 9 OLI-2/TIRS-2 (запущен в 2021)

### Спектральные каналы для NDVI

| Канал | Название | Длина волны | Разрешение | Применение |
|-------|----------|-------------|------------|------------|
| **SR_B4** | Red (красный) | 0.636-0.673 μm | 30m | Хлорофилл, биомасса |
| **SR_B5** | NIR (ближний ИК) | 0.851-0.879 μm | 30m | Структура растений |

**Источник:** [Google Earth Engine Landsat 8 Dataset](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2)

### Формула NDVI

```
NDVI = (NIR - Red) / (NIR + Red)
NDVI = (SR_B5 - SR_B4) / (SR_B5 + SR_B4)
```

### Интерпретация значений NDVI

#### Валидные значения (диапазон -1.0 до 1.0)

| Диапазон | Интерпретация | Применение |
|----------|---------------|------------|
| **0.8 - 1.0** | Густая растительность | Тропические леса, орошаемые культуры |
| **0.5 - 0.8** | Здоровая растительность | Активная вегетация, пик роста |
| **0.2 - 0.5** | Редкая растительность | Кустарники, сухостой, начало вегетации |
| **0.0 - 0.2** | Голая почва | Песок, открытая почва, пастбища |
| **-0.1 - 0.0** | Вода, снег | Водные объекты, снежный покров |

#### Специальные и аномальные значения

| Значение | Причина | Описание | Действие |
|----------|---------|----------|----------|
| **-9999** | Отсутствие данных | Нет снимков за период (облачность 100%, техническая недоступность) | Исключить из анализа |
| **< -1000** | Технические ошибки | Ошибки обработки, артефакты маскирования, недостаточно валидных пикселей | Исключить из анализа |
| **-1000 до -100** | Сильная облачность | Остаточные тени, края облаков, артефакты атмосферной коррекции | Исключить из анализа |
| **-100 до -1** | Аномальные отражения | Смешанные пиксели (вода+почва), лед, искусственные покрытия | Проверить вручную |

**Примеры реальных аномальных значений из данных:**
- `-9246.629` — технический артефакт маскирования облаков
- `-9182.568` — ошибка обработки Surface Reflectance
- `-3387.339` — недостаточно валидных пикселей после фильтрации
- `-590.297` — остаточная облачность, края теней
- `-84.851` — смешанные пиксели, водные объекты

#### ⚠️ Порог аномалии для фильтрации

**Рекомендуемый порог:** `NDVI < -100`

Все значения ниже -100 следует **исключать из анализа**, так как они указывают на:
- Недостаточное количество чистых пикселей после маскирования облаков
- Технические ошибки обработки данных
- Артефакты атмосферной коррекции
- Остаточные облака и тени

**Справочная документация:**
- [Landsat Algorithms](https://developers.google.com/earth-engine/guides/landsat)
- [Landsat 8 Bands Description](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2#bands)

---

## 📂 Структура проекта

```
Google-Earth-Engine/
├── README.md                      # Документация проекта
├── NDVI.py               # Основной Python скрипт
├── javascript_prototype.js        # Прототип для Code Editor
└── data/
    ├── Контуры полей.shp                  # Shapefiles с геометрией полей
    ├── Контуры полей.shx                  # (требуются .cpg, .shp, .dbf, .sbx)
    └── ...
```

---

## 🚀 Быстрый старт

### 1. Предварительные требования

- Python 3.7+
- Google Cloud Project с активированным Earth Engine API
- Учетная запись Google Earth Engine
- Данные о полях (shapefiles) загружены как Earth Engine Asset

### 2. Установка зависимостей

```bash
pip install earthengine-api pandas numpy matplotlib
```

### 3. Аутентификация Earth Engine

**Первый запуск (однократно):**

```bash
earthengine authenticate
```

Откроется браузер для авторизации. После успешной авторизации токен будет сохранен локально.

**Официальная документация:** [Earth Engine Authentication Guide](https://developers.google.com/earth-engine/guides/auth)

### 4. Подготовка данных

#### Загрузка shapefiles в Earth Engine

1. Откройте [Earth Engine Code Editor](https://code.earthengine.google.com/)
2. Перейдите на вкладку **Assets** → **New** → **Shape files**
3. Загрузите файлы: `.cpg`, `.shp`, `.dbf`, `.sbx`
4. Укажите Asset ID (например: `projects/crucial-runner-444819-i7/assets/field`)

**Примечание:** Earth Engine не поддерживает `.kml`/`.kmz` напрямую — используйте shapefiles.

### 5. Настройка скрипта

Откройте `ndvi_analysis.py` и измените параметры:

```python
# Ваш Google Cloud Project ID
ee.Initialize(project='your-project-id')

# Путь к вашему Asset
fields_asset = 'projects/your-project-id/assets/field'

# Период анализа
start_date = dt.date(2025, 1, 1)
end_date   = dt.date(2026, 1, 1)

# Интервал (дни)
step_days = 14
```

### 6. Запуск

```bash
python ndvi_analysis.py
```

Скрипт создаст задачи экспорта на Google Drive в папке `gee_ndvi/`.

### 7. Мониторинг задач

Проверить статус экспорта:
- [Earth Engine Tasks](https://code.earthengine.google.com/tasks)
- Или в коде:

```python
import ee
ee.Initialize(project='your-project-id')
tasks = ee.batch.Task.list()
for task in tasks[:5]:
    print(f"{task.status()['state']}: {task.status()['description']}")
```

---

## 🧪 Прототип JavaScript (Code Editor)

Перед запуском Python скрипта рекомендуется проверить данные в интерактивном Code Editor:

```javascript
// 0. Указать system:index нужного поля
var FIELD_INDEX = '00000000000000000023';

// 1. Загрузить все поля
var fields = ee.FeatureCollection('projects/crucial-runner-444819-i7/assets/field');

// Выбрать одно поле
var field = ee.Feature(
  fields.filter(ee.Filter.eq('system:index', FIELD_INDEX)).first()
);
print('Выбранное поле', field);

var region = field.geometry();

// 2. Задать временной интервал
var start = ee.Date('2025-06-01');
var end   = ee.Date('2025-06-15');

// 3. Загрузить Landsat Surface Reflectance
var colSr = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterDate(start, end)
    .filterBounds(region);

// 4. Вычислить NDVI по медианной мозаике
var medianSr = colSr.median();

var ndvi = medianSr.expression(
  '(nir - red) / (nir + red)',
  {
    nir: medianSr.select('SR_B5'),
    red: medianSr.select('SR_B4')
  }
).rename('NDVI');

// 5. Диагностика
print('Количество сцен:', colSr.size());
print('Bands NDVI:', ndvi.bandNames());

// 6. Визуализация
Map.addLayer(region, {color: 'red'}, 'field');
Map.addLayer(
  ndvi.clip(region),
  {min: 0, max: 0.8, palette: ['white', 'yellow', 'green']},
  'NDVI'
);
Map.centerObject(region, 13);

// 7. Выборка точек внутри поля
var ndviSamples = ndvi.sample({
  region: region,
  numPixels: 500,
  scale: 30,
  geometries: true
});

print('Выборка NDVI по точкам', ndviSamples);

// 8. Экспорт в CSV
Export.table.toDrive({
  collection: ndviSamples,
  description: 'NDVI_samples_field_23',
  fileFormat: 'CSV'
});
```

**Откройте скрипт:** [Earth Engine Code Editor](https://code.earthengine.google.com/)

---

## 📊 Описание Python скрипта

### Основные функции

#### `init_ee()`
Инициализация Earth Engine с аутентификацией и указанием проекта.

```python
def init_ee():
    ee.Authenticate(quiet=True)
    ee.Initialize(project='crucial-runner-444819-i7')
```

#### `load_fields(asset_id)`
Загрузка FeatureCollection с геометрией полей.

```python
fields = load_fields('projects/project-id/assets/field')
```

#### `generate_intervals(start_date, end_date, step_days)`
Генерация временных интервалов (например, 14-дневные окна).

```python
intervals = generate_intervals(
    dt.date(2025, 1, 1),
    dt.date(2026, 1, 1),
    step_days=14
)
# [(2025-01-01, 2025-01-15), (2025-01-15, 2025-01-29), ...]
```

#### `get_ndvi_and_cloud_for_region(start_str, end_str, region)`
Ключевая функция обработки:

1. **Загрузка данных** — Landsat 8 и 9 Surface Reflectance
2. **Маскирование облаков** — использование `QA_PIXEL` битовых масок
3. **Вычисление NDVI** — через `normalizedDifference(['SR_B5', 'SR_B4'])`
4. **Оценка облачности** — через `simpleCloudScore` для TOA данных
5. **Обработка отсутствующих данных** — возврат `-9999` при недостатке снимков

**QA_PIXEL биты для маскирования:**
- **Bit 3** — Cloud
- **Bit 4** — Cloud Shadow

```python
def mask_sr(img):
    qa = img.select('QA_PIXEL')
    mask = (qa.bitwiseAnd(1 << 3).eq(0)
              .And(qa.bitwiseAnd(1 << 4).eq(0)))
    return img.updateMask(mask)
```

**Источник:** [QA_PIXEL Bitmask Documentation](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2#bands)

#### `process_interval(fields, start_date, end_date)`
Обработка всех полей за один временной интервал:
- Вычисление средних значений NDVI и облачности для каждого поля
- Использование `reduceRegion` с параметрами:
  - `reducer=ee.Reducer.mean()` — среднее значение
  - `scale=60` — агрегация до 60м для ускорения
  - `tileScale=8` — оптимизация для больших полей

#### `export_to_csv(result_fc, start_date, end_date)`
Экспорт результатов на Google Drive в формате CSV.

```python
task = ee.batch.Export.table.toDrive(
    collection=result_fc,
    description=f"NDVI_{start_date}_{end_date}",
    folder='gee_ndvi',
    fileNamePrefix=f"ndvi_{start_date}_{end_date}",
    fileFormat='CSV'
)
task.start()
```

---

## 📈 Формат выходных данных

### Структура CSV файла

Каждый файл `ndvi_YYYY-MM-DD_YYYY-MM-DD.csv` содержит следующие колонки:

| Колонка | Тип | Описание | Пример значения |
|---------|-----|----------|-----------------|
| `system:index` | String | Уникальный ID поля в Earth Engine | `00000000000000000023` |
| `GDB_ARCHIV` | Integer | Архивный идентификатор из исходной БД | `1042131` |
| `NDVI` | Float | Среднее значение NDVI по полю | `0.6234` или `-9999` |
| `Shape_STAr` | Float | Площадь поля (кв. метры) | `145680.5` |
| `Shape_STLe` | Float | Периметр поля (метры) | `1856.3` |
| `cloud_score` | Float | Средний процент облачности (0-1) | `0.12` или `-9999` |
| `start_date` | String | Начало интервала | `2025-06-01` |
| `end_date` | String | Конец интервала | `2025-06-15` |
| `farm` | String | Название хозяйства | `"Агрофирма Север"` |
| `name` | String | Название поля | `"Поле #23"` |
| `season` | Integer | Сезон/год посева | `2025` |
| `.geo` | JSON | Геометрия поля (GeoJSON Polygon) | `{"type":"Polygon",...}` |

### Пример записи

```csv
system:index,GDB_ARCHIV,NDVI,Shape_STAr,Shape_STLe,cloud_score,start_date,end_date,farm,name,season,.geo
00000000000000000023,1042131,0.6234,145680.5,1856.3,0.12,2025-06-01,2025-06-15,Агрофирма Север,Поле #23,2025,"{""type"":""Polygon"",""coordinates"":[[[37.5,55.7],...]]}"
00000000000000000024,1042132,-9999.0,89456.2,1234.5,0.64,2025-06-01,2025-06-15,Агрофирма Север,Поле #24,2025,"{""type"":""Polygon"",""coordinates"":[[[37.6,55.8],...]]}"
```

### Интерпретация данных

#### Валидные значения

```python
import pandas as pd

df = pd.read_csv('ndvi_2025-06-01_2025-06-15.csv')

# Фильтр валидных данных (исключить аномалии)
df_valid = df[df['NDVI'] > -100]

# Только поля с растительностью
df_vegetation = df[(df['NDVI'] >= 0.2) & (df['NDVI'] <= 1.0)]

print(f"Полей с валидными данными: {len(df_valid)}")
print(f"Полей с растительностью: {len(df_vegetation)}")
print(f"Средний NDVI: {df_vegetation['NDVI'].mean():.4f}")
```

#### Обработка специальных значений

```python
# Подсчет записей по категориям
missing_data = len(df[df['NDVI'] == -9999])           # Нет снимков
technical_errors = len(df[df['NDVI'] < -1000])        # Технические ошибки
cloud_artifacts = len(df[(df['NDVI'] >= -1000) & (df['NDVI'] < -100)])  # Облачность
water_snow = len(df[(df['NDVI'] >= -100) & (df['NDVI'] < 0)])  # Вода/снег
bare_soil = len(df[(df['NDVI'] >= 0) & (df['NDVI'] < 0.2)])    # Голая почва
vegetation = len(df[df['NDVI'] >= 0.2])                # Растительность

print(f"Отсутствие данных (-9999): {missing_data}")
print(f"Технические ошибки (< -1000): {technical_errors}")
print(f"Артефакты облачности (-1000..-100): {cloud_artifacts}")
print(f"Вода/снег (-100..0): {water_snow}")
print(f"Голая почва (0..0.2): {bare_soil}")
print(f"Растительность (>= 0.2): {vegetation}")
```

---

## ⚠️ Обработка особых случаев

### Сильная облачность

**Проблема:** При высокой облачности каналы SR_B4/SR_B5 могут отсутствовать после маскирования.

**Решение:** Скрипт возвращает `NDVI = -9999` при отсутствии валидных снимков.

```python
has_sr = masked.size().gt(0)
ndvi = ee.Image(ee.Algorithms.If(
    has_sr,
    masked.median().normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI'),
    ee.Image.constant(-9999).rename('NDVI')
))
```

### Фильтрация в постобработке

```python
import pandas as pd

df = pd.read_csv('ndvi_2025-01-01_2025-01-15.csv')

# ШАБЛОН ФИЛЬТРАЦИИ ДЛЯ АНАЛИЗА

# Шаг 1: Удалить записи с отсутствующими данными
df_step1 = df[df['NDVI'] != -9999]
print(f"После удаления -9999: {len(df_step1)} записей")

# Шаг 2: Удалить аномальные значения (порог -100)
df_step2 = df_step1[df_step1['NDVI'] > -100]
print(f"После удаления аномалий (< -100): {len(df_step2)} записей")

# Шаг 3: Фильтр по облачности (< 30%)
df_step3 = df_step2[df_step2['cloud_score'] < 0.3]
print(f"После фильтра облачности (< 30%): {len(df_step3)} записей")

# Шаг 4: Только поля с растительностью (NDVI > 0.2)
df_final = df_step3[df_step3['NDVI'] > 0.2]
print(f"Финальная выборка (NDVI > 0.2): {len(df_final)} записей")

# Статистика по финальной выборке
print(f"\nСтатистика NDVI:")
print(f"  Среднее: {df_final['NDVI'].mean():.4f}")
print(f"  Медиана: {df_final['NDVI'].median():.4f}")
print(f"  Min: {df_final['NDVI'].min():.4f}")
print(f"  Max: {df_final['NDVI'].max():.4f}")
```

### Обработка временных рядов с пропусками

```python
import pandas as pd
import numpy as np
import glob

# Загрузить все CSV файлы за год
files = sorted(glob.glob('ndvi_*.csv'))
field_id = '00000000000000000023'

data = []
for file in files:
    df = pd.read_csv(file)
    field_data = df[df['system:index'] == field_id]
    if not field_data.empty:
        data.append({
            'date': field_data['start_date'].values[0],
            'ndvi': field_data['NDVI'].values[0],
            'cloud': field_data['cloud_score'].values[0]
        })

ts = pd.DataFrame(data)

# Заменить аномалии на NaN для интерполяции
ts.loc[ts['ndvi'] < -100, 'ndvi'] = np.nan

# Интерполяция пропущенных значений
ts['ndvi_interpolated'] = ts['ndvi'].interpolate(method='linear')

print(ts)
```

---

## 🔧 Параметры конфигурации

### Временные параметры

```python
start_date = dt.date(2025, 1, 1)  # Начало периода
end_date   = dt.date(2026, 1, 1)  # Конец периода
step_days  = 14                    # Размер интервала (дни)
```

**Рекомендации:**
- **14 дней** — оптимально для мониторинга вегетации
- **30 дней** — для долгосрочного анализа
- **7 дней** — для интенсивного мониторинга (больше пропусков из-за облаков)

### Параметры обработки

```python
# В функции get_ndvi_and_cloud_for_region()
.sort('CLOUD_COVER').limit(15)  # Ограничение количества снимков

# В функции process_interval()
scale=60,        # Разрешение агрегации (метры)
tileScale=8,     # Параллелизация для больших полей
bestEffort=True  # Использовать грубое разрешение если не хватает памяти
```

**Оптимизация:**
- `scale=30` — максимальная точность (медленно)
- `scale=60` — баланс скорость/качество (рекомендуется)
- `scale=100` — быстрая обработка больших территорий

---

## 📚 Дополнительные ресурсы

### Официальная документация

- [Google Earth Engine Homepage](https://earthengine.google.com/)
- [Earth Engine Python API Guide](https://developers.google.com/earth-engine/guides/python_install)
- [Landsat Collection 2 Overview](https://www.usgs.gov/landsat-missions/landsat-collection-2)
- [NDVI Theory and Applications](https://www.usgs.gov/special-topics/remote-sensing-phenology/science/ndvi-foundation-remote-sensing-phenology)

### Tutorials

- [Earth Engine Guides](https://developers.google.com/earth-engine/guides)
- [Landsat Time Series Analysis](https://developers.google.com/earth-engine/tutorials/tutorial_api_06)
- [Cloud Masking Best Practices](https://developers.google.com/earth-engine/tutorials/community/landsat-etm-to-oli-harmonization)

### Community

- [GIS StackExchange - Earth Engine](https://gis.stackexchange.com/questions/tagged/google-earth-engine)
- [Earth Engine Developers Group](https://groups.google.com/g/google-earth-engine-developers)

---

## 🐛 Устранение неполадок

### Ошибка аутентификации

```
EEException: Please authorize access to Earth Engine
```

**Решение:**
```bash
earthengine authenticate --auth_mode=localhost
```

### Ошибка проекта

```
EEException: Please specify a project ID
```

**Решение:**
```python
ee.Initialize(project='your-project-id')
```

Проверить проект: [Earth Engine Code Editor](https://code.earthengine.google.com/) → Settings → Cloud Project

### Превышение квоты

```
EEException: User memory limit exceeded
```

**Решение:**
- Увеличить `scale` (например, до 100)
- Уменьшить количество снимков: `.limit(10)`
- Использовать `tileScale=16`

### Много аномальных значений NDVI

**Проблема:** Большой процент записей с NDVI < -100

**Причины:**
1. Зимний период — снежный покров, отсутствие вегетации
2. Период сильных дождей — постоянная облачность
3. Неправильная геометрия полей — пересечение с водоемами

**Решение:**
```python
# Проверить распределение по месяцам
df['month'] = pd.to_datetime(df['start_date']).dt.month
anomaly_by_month = df[df['NDVI'] < -100].groupby('month').size()
print("Аномалии по месяцам:")
print(anomaly_by_month)

# Анализ облачности
df_anomaly = df[df['NDVI'] < -100]
print(f"Средняя облачность для аномальных значений: {df_anomaly['cloud_score'].mean():.2%}")
```

### Пустые результаты (NDVI = -9999)

**Причины:**
1. Высокая облачность в указанный период (100%)
2. Нет снимков Landsat над регионом
3. Неправильная геометрия поля

**Проверка:**
```javascript
// В Code Editor проверить наличие снимков
var col = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterDate('2025-06-01', '2025-06-15')
  .filterBounds(region);
  
print('Количество снимков:', col.size());
print('Облачность снимков:', col.aggregate_array('CLOUD_COVER'));

// Проверка после маскирования
var masked = col.map(function(img) {
  var qa = img.select('QA_PIXEL');
  var mask = qa.bitwiseAnd(1 << 3).eq(0).and(qa.bitwiseAnd(1 << 4).eq(0));
  return img.updateMask(mask);
});

print('Снимков после маскирования:', masked.size());
```

---

## 📝 Примеры использования

### Анализ одного поля за сезон

```python
import ee
import datetime as dt

ee.Initialize(project='your-project-id')

fields = ee.FeatureCollection('projects/your-project-id/assets/field')
field = fields.filter(ee.Filter.eq('system:index', '00000000000000000023')).first()
region = field.geometry()

# Вегетационный сезон 2025
intervals = [
    (dt.date(2025, 4, 1), dt.date(2025, 4, 15)),   # Ранняя весна
    (dt.date(2025, 6, 1), dt.date(2025, 6, 15)),   # Активная вегетация
    (dt.date(2025, 8, 1), dt.date(2025, 8, 15)),   # Созревание
    (dt.date(2025, 10, 1), dt.date(2025, 10, 15)), # Уборка
]

for start, end in intervals:
    result = process_interval(fields.filter(ee.Filter.eq('system:index', '00000000000000000023')), start, end)
    export_to_csv(result, start, end)
```

### Сравнение полей

```python
import pandas as pd
import matplotlib.pyplot as plt

# Загрузить данные за июнь
df = pd.read_csv('ndvi_2025-06-01_2025-06-15.csv')

# Фильтрация валидных данных
df_valid = df[df['NDVI'] > 0.2]

# Топ-10 полей по NDVI
top_fields = df_valid.nlargest(10, 'NDVI')

plt.figure(figsize=(12, 6))
plt.barh(top_fields['name'], top_fields['NDVI'], color='green')
plt.xlabel('NDVI')
plt.ylabel('Название поля')
plt.title('Топ-10 полей по NDVI (июнь 2025)')
plt.tight_layout()
plt.savefig('top_fields_ndvi.png', dpi=300)
```

## 📌 Краткая справка

### Быстрые команды

```bash
# Установка
pip install earthengine-api pandas numpy matplotlib

# Аутентификация
earthengine authenticate

# Запуск
python ndvi_analysis.py

# Проверка задач
earthengine task list
```

### Основные параметры

| Параметр | Значение | Описание |
|----------|----------|----------|
| `scale` | 60 | Разрешение обработки (метры) |
| `step_days` | 14 | Интервал анализа (дни) |
| `limit` | 15 | Макс. снимков на интервал |
| `NDVI_missing` | -9999 | Значение при отсутствии данных |
| `NDVI_anomaly_threshold` | -100 | Порог для исключения аномалий |
| `vegetation_threshold` | 0.2 | Минимальный NDVI для растительности |

### Интерпретация NDVI (краткая)

| Диапазон | Значение |
|----------|----------|
| **-9999** | ⛔ Нет данных (исключить) |
| **< -100** | ⛔ Аномалия (исключить) |
| **-100..0** | 💧 Вода, снег |
| **0..0.2** | 🟤 Голая почва |
| **0.2..0.5** | 🟡 Редкая растительность |
| **0.5..0.8** | 🟢 Здоровая растительность |
| **> 0.8** | 🌳 Густая растительность |

### Полезные ссылки

| Ресурс | URL |
|--------|-----|
| Code Editor | https://code.earthengine.google.com/ |
| Dataset Catalog | https://developers.google.com/earth-engine/datasets |
| Tasks Monitor | https://code.earthengine.google.com/tasks |
| Community Forum | https://groups.google.com/g/google-earth-engine-developers |
| Landsat 8 Docs | https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2 |

## ✅ РЕЗУЛЬТАТ
**Google-drive:** [GEE_NDVI](https://drive.google.com/drive/folders/1tlXrjxn9wEkKdc-A6BPYx0S-uQAIZQ5i)
