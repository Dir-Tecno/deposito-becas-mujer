import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
import io

# Configuración de la página
st.set_page_config(
    page_title="Generador de Archivos .hab para Depósitos",
    page_icon="💰",
    layout="wide"
)

# Estilos personalizados
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .step-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar con instrucciones
st.sidebar.title("Instrucciones")
st.sidebar.markdown("""
### Generación de archivos .hab para depósitos

1. **Cargar archivo Excel** - Suba un archivo Excel que contenga las columnas requeridas.
2. **Seleccionar fecha** - Elija la fecha para el depósito.
3. **Descargar archivo** - Una vez procesado, descargue el archivo .hab generado.

### Columnas requeridas en el Excel
- SUCURSAL
- CUENTA
- IMPORTE
- SOLICITUD
- CBU
- CUOTA
- CUIL
- CUIL_APODERADO

### Reglas aplicadas
- Si CUIL_APODERADO es nulo, se añadirá '2' como primer carácter del CUIL.
- Si CUIL_APODERADO tiene valor, se añadirá '1' como primer carácter del CUIL.
- Se excluirán registros con CUOTA = '3'.
- Al IMPORTE se le añadirán dos ceros a la derecha.
""")

st.sidebar.info("Los archivos .hab se generan usando codificación latin-1 (ISO-8859-1/ANSI) para mantener la compatibilidad con el sistema que los procesa.")

# Título principal
st.title("Generador de Archivos .hab para Depósitos")

# Función para procesar los archivos
def procesar_archivo(lote_df, fecha_seleccionada):
    # Definir datos del formato cliente directamente en el código
    datos_formato_cliente = [
        {'Orden': 1, 'Campo': 'TIPO DE CONVENIO', 'Enteros': 3, 'Decimales': 0, 'Total': 3, 'Tipo': 'N', 'default': '013'},
        {'Orden': 2, 'Campo': 'SUCURSAL', 'Enteros': 5, 'Decimales': 0, 'Total': 5, 'Tipo': 'N', 'default': None},
        {'Orden': 3, 'Campo': 'MONEDA', 'Enteros': 2, 'Decimales': 0, 'Total': 2, 'Tipo': 'N', 'default': '01'},
        {'Orden': 4, 'Campo': 'SISTEMA', 'Enteros': 1, 'Decimales': 0, 'Total': 1, 'Tipo': 'N', 'default': '3'},
        {'Orden': 5, 'Campo': 'CUENTA', 'Enteros': 9, 'Decimales': 0, 'Total': 9, 'Tipo': 'N', 'default': None},
        {'Orden': 6, 'Campo': 'IMPORTE', 'Enteros': 18, 'Decimales': 2, 'Total': 18, 'Tipo': 'N', 'default': None},
        {'Orden': 7, 'Campo': 'FECHA', 'Enteros': 8, 'Decimales': 0, 'Total': 8, 'Tipo': 'N', 'default': fecha_seleccionada},
        {'Orden': 8, 'Campo': 'NRO CONVENIO CON LA EMPRESA', 'Enteros': 5, 'Decimales': 0, 'Total': 5, 'Tipo': 'N', 'default': '01465'},
        {'Orden': 9, 'Campo': 'SOLICITUD', 'Enteros': 6, 'Decimales': 0, 'Total': 6, 'Tipo': 'N', 'default': None},
        {'Orden': 10, 'Campo': 'CBU', 'Enteros': 22, 'Decimales': 0, 'Total': 22, 'Tipo': 'N', 'default': None},
        {'Orden': 11, 'Campo': 'CUOTA', 'Enteros': 2, 'Decimales': 0, 'Total': 2, 'Tipo': 'N', 'default': '00'},
        {'Orden': 12, 'Campo': 'CUIL', 'Enteros': 22, 'Decimales': 0, 'Total': 22, 'Tipo': 'A', 'default': None}
    ]
    
    # Crear DataFrame de formato_cliente
    formato_cliente = pd.DataFrame(datos_formato_cliente)
    
    # Obtener los campos necesarios del formato cliente
    campos = formato_cliente[formato_cliente['default'].isna()]['Campo'].tolist()
    
    # Filtrar registros con CUOTA != '3'
    lote = lote_df.copy()
    lote = lote[(lote['CUOTA'] != '3')]
    
    # Modificar la columna "Importe" para agregar dos ceros a la derecha
    if 'IMPORTE' in lote.columns:
        lote['IMPORTE'] = lote['IMPORTE'].astype(str) + '00'
    
    # Crear un DataFrame vacío para almacenar los resultados
    resultado = pd.DataFrame()
    
    for _, row in formato_cliente.iterrows():
        campo = row['Campo']
        default = row['default']
        enteros = row['Enteros']
        
        if pd.notna(default):  # Si hay un valor en 'default', usarlo
            resultado[campo] = [default.zfill(enteros)] * len(lote)
        else:  # Si no, leer el valor del archivo "lote"
            if campo in lote.columns:
                resultado[campo] = lote[campo].apply(lambda x: str(x).zfill(enteros))
    
    # Aplicar la regla: Si CUIL_APODERADO es null, a CUIL añadir un '2' antes del primer dígito, else '1'
    if 'CUIL' in resultado.columns:
        # Necesitamos usar los datos del DataFrame lote para esta lógica
        for idx, row in resultado.iterrows():
            # Buscar la fila correspondiente en el lote
            lote_row = lote.iloc[idx]
            cuil_apoderado = lote_row.get('CUIL_APODERADO', None)
            
            # Obtener el CUIL original antes del padding
            cuil_original = str(lote_row.get('CUIL', ''))
            
            # Determinar el prefijo según la regla
            prefijo = '2' if pd.isna(cuil_apoderado) or cuil_apoderado == '' or cuil_apoderado is None else '1'
            
            # Añadir el prefijo antes del primer dígito y luego aplicar el padding
            if cuil_original and cuil_original.strip():
                # Añadir el prefijo antes del primer dígito
                cuil_con_prefijo = prefijo + cuil_original
                # Aplicar padding hasta alcanzar la longitud requerida
                resultado.at[idx, 'CUIL'] = cuil_con_prefijo.zfill(22)
            else:
                # En caso de CUIL vacío o solo espacios, mantener vacío
                resultado.at[idx, 'CUIL'] = ''
    
    # Filtrar registros con SOLICITUD no nula
    resultado = resultado[(resultado['SOLICITUD'].notna())]
    
    # Generar el contenido del archivo .hab
    contenido_hab = []
    for _, row in resultado.iterrows():
        contenido_hab.append(''.join(row.astype(str).values))
    
    # Usar CRLF (\r\n) para saltos de línea y asegurar que haya un salto de línea al final
    contenido = '\r\n'.join(contenido_hab) + '\r\n'
    
    return resultado, contenido

# Función para descargar el archivo
def get_download_link(content, filename):
    # Aseguramos que se use la codificación latin-1 (ANSI) para compatibilidad
    b64 = base64.b64encode(content.encode('latin-1')).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="download-link">Descargar archivo {filename}</a>'
    return href

# Inicializar el estado de la sesión
if 'lote_df' not in st.session_state:
    st.session_state.lote_df = None
if 'fecha' not in st.session_state:
    st.session_state.fecha = datetime.now()
if 'resultado_df' not in st.session_state:
    st.session_state.resultado_df = None
if 'contenido_hab' not in st.session_state:
    st.session_state.contenido_hab = None
if 'nombre_archivo' not in st.session_state:
    st.session_state.nombre_archivo = "deposito.hab"
if 'procesado' not in st.session_state:
    st.session_state.procesado = False
if 'error' not in st.session_state:
    st.session_state.error = None

# Función para reiniciar el procesamiento
def reiniciar_procesamiento():
    st.session_state.procesado = False
    st.session_state.resultado_df = None
    st.session_state.contenido_hab = None

# Contenedor principal
with st.container():
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.subheader("Cargar archivo Excel")
    
    # Sección para subir el archivo Excel
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader("Seleccione el archivo Excel", type=['xlsx', 'xls'], 
                                         on_change=reiniciar_procesamiento)
    
    # Sección para seleccionar la fecha
    with col2:
        fecha = st.date_input("Fecha para el depósito", st.session_state.fecha, on_change=reiniciar_procesamiento)
        st.session_state.fecha = fecha
        fecha_formateada = fecha.strftime('%Y%m%d')
    
    # Mostrar información de la fecha seleccionada
    st.info(f"La fecha seleccionada en formato AAAAMMDD es: {fecha_formateada}")
    
    # Si hay un archivo cargado
    if uploaded_file is not None:
        try:
            # Intentar leer el archivo
            df = pd.read_excel(uploaded_file, converters={
                'SUCURSAL': str, 'CUENTA': str, 'IMPORTE': str, 
                'SOLICITUD': str, 'CBU': str, 'CUOTA': str,
                'CUIL': str, 'CUIL_APODERADO': str
            })
            
            # Verificar columnas requeridas
            columnas_requeridas = ['SUCURSAL', 'CUENTA', 'IMPORTE', 'SOLICITUD', 'CBU', 'CUOTA', 'CUIL', 'CUIL_APODERADO']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                st.error(f"El archivo no contiene las siguientes columnas requeridas: {', '.join(columnas_faltantes)}")
            else:
                st.session_state.lote_df = df
                st.success(f"Archivo cargado exitosamente. Se encontraron {len(df)} registros.")
                
                # Vista previa de los datos cargados
                st.markdown("### Vista previa del archivo")
                st.dataframe(df.head(10))
                
                # Botón para procesar datos
                if st.button("Procesar datos"):
                    try:
                        resultado_df, contenido_hab = procesar_archivo(
                            st.session_state.lote_df,
                            fecha_formateada
                        )
                        st.session_state.resultado_df = resultado_df
                        st.session_state.contenido_hab = contenido_hab
                        # Generar nombre de archivo con fecha actual
                        nombre_archivo = f"deposito_{fecha.strftime('%Y%m%d')}.hab"
                        st.session_state.nombre_archivo = nombre_archivo
                        st.session_state.procesado = True
                        st.session_state.error = None
                    except Exception as e:
                        st.session_state.error = str(e)
                        st.error(f"Error al procesar los datos: {str(e)}")
                
                # Si los datos han sido procesados, mostrar resultados y opción de descarga
                if st.session_state.procesado and st.session_state.error is None:
                    st.markdown("---")
                    st.success(f"¡Procesamiento exitoso! Se generaron {len(st.session_state.resultado_df)} registros.")
                    
                    # Mostrar resumen de datos
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Resumen de datos")
                        st.write(f"Registros totales: {len(st.session_state.lote_df)}")
                        st.write(f"Registros con CUOTA = '3' (excluidos): {len(st.session_state.lote_df[st.session_state.lote_df['CUOTA'] == '3'])}")
                        st.write(f"Registros procesados: {len(st.session_state.resultado_df)}")
                        st.write(f"Registros con CUIL_APODERADO nulo: {st.session_state.lote_df['CUIL_APODERADO'].isna().sum()}")
                        st.write(f"Registros con CUIL_APODERADO no nulo: {len(st.session_state.lote_df) - st.session_state.lote_df['CUIL_APODERADO'].isna().sum()}")
                    
                    with col2:
                        # Permitir al usuario cambiar el nombre del archivo
                        nuevo_nombre = st.text_input("Nombre del archivo a generar", st.session_state.nombre_archivo)
                        if nuevo_nombre != st.session_state.nombre_archivo:
                            if not nuevo_nombre.endswith('.hab'):
                                nuevo_nombre += '.hab'
                            st.session_state.nombre_archivo = nuevo_nombre
                        
                        # Botón para descargar el archivo
                        st.markdown("### Descargar archivo")
                        st.markdown(get_download_link(st.session_state.contenido_hab, st.session_state.nombre_archivo), unsafe_allow_html=True)
                    
                    # Mostrar vista previa de los datos procesados
                    st.markdown("### Vista previa de los datos procesados")
                    st.dataframe(st.session_state.resultado_df.head(10))
                    
                    # Mostrar contenido del archivo
                    with st.expander("Ver contenido del archivo .hab"):
                        st.text(st.session_state.contenido_hab)
        except Exception as e:
            st.error(f"Error al leer el archivo Excel: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# Pie de página
st.markdown("---")
st.markdown("Desarrollado para gestión de depósitos en cuentas bancarias.")
