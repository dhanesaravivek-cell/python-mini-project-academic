"""Creates demo data in data/rainfall.csv  (python make_sample_data.py)"""
import numpy as np
import pandas as pd
import storage

random = np.random.default_rng(42)
average_rain = {1: 1, 2: 1, 3: 2, 4: 3, 5: 6, 6: 60, 7: 150, 8: 120,
                9: 70, 10: 15, 11: 4, 12: 1}          
df = storage.empty_table()
for location, factor in (("Ahmedabad", 1.0), ("Surat", 1.6), ("Rajkot", 0.8)):
    for day in pd.date_range("2025-10-05", "2026-09-27", freq="7D"):
        rain = min(random.exponential(average_rain[day.month]) * factor, 250)
        if random.random() > 0.7:
            rain = 0                                 
        df = storage.add_record(df, day, location, round(float(rain), 1))
storage.save_records(df)
print(len(df), "records saved")
