from .scrapping_criptos import *
from .models import *
from datetime import datetime

def generate():
    today = datetime.today().strftime('%Y-%m-%d')
    data = get_fear_and_greed_index()
    fear_greed = FearGreed.objects.create(name=data[0], index=data[1])
    fear_greed.save()
