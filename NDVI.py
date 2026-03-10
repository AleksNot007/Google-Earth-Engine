import datetime as dt
import ee

def init_ee():
    ee.Authenticate(quiet=True)
    ee.Initialize(project='crucial-runner-444819-i7')

def load_fields(asset_id):
    return ee.FeatureCollection(asset_id)

def generate_intervals(start_date, end_date, step_days):
    intervals = []
    step = dt.timedelta(days=step_days)
    cur = start_date
    while cur < end_date:
        nxt = min(cur + step, end_date)
        intervals.append((cur, nxt))
        cur = nxt
    return intervals

def get_ndvi_and_cloud_for_region(start_str, end_str, region):
    l8_sr = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
             .filterDate(start_str, end_str).filterBounds(region)
             .sort('CLOUD_COVER').limit(15))
    l9_sr = (ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
             .filterDate(start_str, end_str).filterBounds(region)
             .sort('CLOUD_COVER').limit(15))
    col_sr = l8_sr.merge(l9_sr)

    def mask_sr(img):
        qa = img.select('QA_PIXEL')
        mask = (qa.bitwiseAnd(1 << 3).eq(0)
                  .And(qa.bitwiseAnd(1 << 4).eq(0)))
        return img.updateMask(mask)

    masked = col_sr.map(mask_sr)
    has_sr = masked.size().gt(0)
    ndvi = ee.Image(ee.Algorithms.If(
        has_sr,
        masked.median().normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI'),
        ee.Image.constant(-9999).rename('NDVI')
    ))

    l8_toa = (ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')
              .filterDate(start_str, end_str).filterBounds(region)
              .sort('CLOUD_COVER').limit(15))
    l9_toa = (ee.ImageCollection('LANDSAT/LC09/C02/T1_TOA')
              .filterDate(start_str, end_str).filterBounds(region)
              .sort('CLOUD_COVER').limit(15))
    col_toa = l8_toa.merge(l9_toa)

    def add_cloud_score(img):
        scored = ee.Algorithms.Landsat.simpleCloudScore(img)
        return scored.select('cloud').divide(100).rename('cloud_score')

    has_toa = col_toa.size().gt(0)
    cloud = ee.Image(ee.Algorithms.If(
        has_toa,
        col_toa.map(add_cloud_score).mean().rename('cloud_score'),
        ee.Image.constant(-9999).rename('cloud_score')
    ))

    return ndvi.addBands(cloud)

def process_interval(fields, start_date, end_date):
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    def process_field(field):
        region = field.geometry()
        image = get_ndvi_and_cloud_for_region(start_str, end_str, region).unmask(-9999)
        reduced = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=60,
            tileScale=8,
            bestEffort=True
        )
        stats = ee.Dictionary(reduced)
        return (field
                .set('NDVI', ee.Number(stats.get('NDVI')))
                .set('cloud_score', ee.Number(stats.get('cloud_score')))
                .set('start_date', start_str)
                .set('end_date', end_str))

    return fields.map(process_field)

def export_to_csv(result_fc, start_date, end_date):
    prefix = f"ndvi_{start_date}_{end_date}"
    desc = f"NDVI_{start_date}_{end_date}"
    task = ee.batch.Export.table.toDrive(
        collection=result_fc,
        description=desc[:100],
        folder='gee_ndvi',
        fileNamePrefix=prefix,
        fileFormat='CSV'
    )
    task.start()
    print(f'Export started: {task.id} ({prefix})')

def main():
    init_ee()

    fields_asset = 'projects/crucial-runner-444819-i7/assets/field'
    fields = load_fields(fields_asset)

    start_date = dt.date(2025, 1, 1)
    end_date   = dt.date(2026, 1, 1)
    intervals  = generate_intervals(start_date, end_date, step_days=14)

    for start, end in intervals:
        print(f'Processing {start} -> {end}...')
        interval_fc = process_interval(fields, start, end)
        export_to_csv(interval_fc, start, end)

if name == '__main__':
    main()
