import os

def remove_csv_extension(filename):
    # Împarte numele fișierului în rădăcină și extensie
    root, ext = os.path.splitext(filename)
    
    # Verifică dacă extensia este .csv și returnează doar rădăcina
    if ext.lower() == '.csv':
        return root
    else:
        return filename  