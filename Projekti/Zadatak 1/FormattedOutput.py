from datetime import datetime

formatOut = lambda value : print(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}, Content = {value}") 