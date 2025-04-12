import pandas as pd

def process_excel_file(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, header=9)
        
        df = df.iloc[:-3]
        
        df = df.dropna(subset=['CI'])
        
        nombres = df['Apellidos y Nombre'].str.strip().tolist()

        return reordenar_nombres(nombres)
    
    except Exception as e:
        print(f"Error procesando archivo Excel: {e}")
        return []
    

def reordenar_nombres(nombres):
    nombres_ordenados = []
    for nombre in nombres:
        partes = nombre.split()
        
        # Caso típico: 4 partes (2 apellidos + 2 nombres)
        if len(partes) == 4:
            nuevo_nombre = f"{partes[2]} {partes[3]} {partes[0]} {partes[1]}"
        
        # Caso con 3 partes (2 apellidos + 1 nombre)
        elif len(partes) == 3:
            nuevo_nombre = f"{partes[2]} {partes[0]} {partes[1]}"
        
        # Caso con 2 partes (1 apellido + 1 nombre)
        elif len(partes) == 2:
            nuevo_nombre = f"{partes[1]} {partes[0]}"
        
        # Conservar original si no coincide
        else:
            nuevo_nombre = nombre
            
        nombres_ordenados.append(nuevo_nombre)
    
    return nombres_ordenados