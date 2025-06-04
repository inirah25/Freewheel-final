import pandas as pd
import os
from django.conf import settings
 
def read_admin_excel():
    excel_path = os.path.join(settings.MEDIA_ROOT, 'admin_data.xlsx')  # or your Excel filename
    try:
        df = pd.read_excel(excel_path)
        return df.to_dict(orient='records')  # or whatever format you need
    except FileNotFoundError:
        return []  # or empty if no file found