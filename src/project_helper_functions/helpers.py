import yaml
from pathlib import Path
import pytz
from datetime import datetime

def load_config():
    for file in Path(__file__).parent.parent.parent.glob('*'):
        if str(file).endswith('yaml'):
            with open(str(file), "r") as stream:
                return yaml.safe_load(stream)

def convert_to_utc(datetime_str):
    timezone = pytz.timezone("Etc/UTC")
    try:
        return timezone.localize(datetime.strptime(datetime_str, '%d-%m-%Y %H:%M:%S'))
    except ValueError:
        print("Invalid datetime format. Please provide datetime in 'dd-mm-yyyy HH:MM:SS' format.")
        return None
