# Generador de Archivos .hab para Depósitos

## Descripción

Aplicación web desarrollada con Streamlit para generar archivos .hab utilizados en el sistema de depósitos a cuentas bancarias. Esta aplicación permite cargar un archivo Excel con datos de depósitos, validar su contenido, aplicar reglas específicas de formato y generar un archivo .hab compatible con el sistema de procesamiento bancario.

## Características principales

- **Interfaz intuitiva**: Aplicación web con una interfaz simple y fácil de usar.
- **Validación de datos**: Verifica que el archivo Excel contenga todas las columnas necesarias.
- **Procesamiento de reglas de negocio**: 
  - Modifica el campo CUIL según el valor de CUIL_APODERADO (añade '1' o '2' como primer carácter).
  - Agrega dos ceros a la derecha del importe.
  - Filtra registros con CUOTA = '3'.
- **Formato específico**: Genera un archivo .hab con codificación ANSI (latin-1) y saltos de línea CRLF para mantener la compatibilidad con el sistema de procesamiento.
- **Previsualización**: Muestra una vista previa de los datos cargados y procesados.
- **Resumen estadístico**: Provee un resumen de los datos procesados.

## Requisitos del sistema

- Python 3.7 o superior
- Streamlit
- Pandas
- Base64 (incluido en Python estándar)
- Datetime (incluido en Python estándar)

## Instalación

1. Asegúrate de tener Python instalado en tu sistema.
2. Instala las dependencias necesarias:

```bash
pip install streamlit pandas
```

3. Descarga todos los archivos del repositorio.

## Uso

1. Ejecuta la aplicación con el siguiente comando:

```bash
streamlit run app.py
```

2. Sigue estos pasos en la interfaz web:
   - Carga un archivo Excel con los datos requeridos.
   - Selecciona la fecha para el depósito.
   - Haz clic en "Procesar datos".
   - Una vez procesado, descarga el archivo .hab generado.

## Estructura del archivo Excel de entrada

El archivo Excel debe contener las siguientes columnas:

- **SUCURSAL_1**: Código de la sucursal.
- **CUENTA**: Número de cuenta.
- **IMPORTE**: Monto a depositar (sin decimales, se añadirán automáticamente).
- **SOLICITUD**: Número de solicitud.
- **CBU**: Clave Bancaria Uniforme.
- **CUOTA**: Número de cuota (los registros con CUOTA = '3' serán excluidos).
- **CUIL**: CUIL/CUIT del titular.
- **CUIL_APODERADO**: CUIL/CUIT del apoderado (puede estar vacío).

## Formato del archivo .hab generado

El archivo .hab generado tiene las siguientes características:

- **Codificación**: ANSI (latin-1)
- **Saltos de línea**: CRLF (Windows)
- **Estructura**: Cada línea representa un registro con campos concatenados sin separadores.
- **Orden de campos**:
  1. TIPO DE CONVENIO (3 caracteres, default: '013')
  2. SUCURSAL (5 caracteres)
  3. MONEDA (2 caracteres, default: '01')
  4. SISTEMA (1 caracter, default: '3')
  5. NRO CTA (9 caracteres)
  6. IMPORTE (18 caracteres)
  7. FECHA (8 caracteres en formato AAAAMMDD)
  8. NRO CONVENIO CON LA EMPRESA (5 caracteres, default: '01465')
  9. SOLICITUD (6 caracteres)
  10. CBU (22 caracteres)
  11. CUOTA (2 caracteres, default: '00')
  12. CUIL (22 caracteres, con prefijo '1' o '2')

## Reglas de negocio aplicadas

1. **Modificación del campo CUIL**:
   - Si CUIL_APODERADO está vacío: Se añade '2' al inicio del CUIL.
   - Si CUIL_APODERADO contiene datos: Se añade '1' al inicio del CUIL.

2. **Modificación del IMPORTE**:
   - Se añaden dos ceros al final (para representar centavos).

3. **Filtrado de registros**:
   - Los registros con CUOTA = '3' son excluidos del procesamiento.

## Notas importantes

- La aplicación utiliza el estado de sesión de Streamlit para mantener los datos entre interacciones.
- El archivo .hab incluye un salto de línea al final para cumplir con el formato requerido por el sistema de procesamiento.
- Todos los campos numéricos se rellenan con ceros a la izquierda hasta alcanzar la longitud requerida.

## Contacto y soporte

Para consultas o reportes de problemas, por favor contacte al departamento de Administración.

---

© 2025 - Aplicación desarrollada para el Departamento de Administración
