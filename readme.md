# Validador masivo RUC SUNAT

Este proyecto permite verificar una lista de RUC's, ya sean RUC 10 o RUC 20, directamente con el patrón oficial de la SUNAT, devolviendo: **RUC, razón social, estado del contribuyente y estado domiciliario.**

Todo esto se obtiene del [Padrón reducido RUC](https://www.sunat.gob.pe/descargaPRR/mrc137_padron_reducido.html) que ofrece la propia SUNAT, el cual posteriormente se optimiza y convierte en una base de datos SQL para un acceso eficiente y consultas rápidas.

### IMPORTANTE

**Este no es un proyecto individual, es un proyecto conjunto con _'Sr.Gato'_, y es un proyecto destinado al portafolio de Long Fall Systems S.A.C., sociedad conjunta entre ambos desarrolladores**

## Funcionamiento

1. Al ejecutar el programa por primera vez, necesitará descargar el padrón de la SUNAT, este proceso es completamente gestionado por el programa. Una vez descargado, se reducirá a las celdas necesarias para el programa y se guardara como una base de datos SQL para un acceso optimo.
2. Se debe seleccionar el archivo Excel a procesar desde la interfaz, por ahora solo se procesa si la columna tiene de encabezado `documento`, pero se planea dar soporte a encabezados personalizados.
3. Se da click en `Procesar lista` y en cuestión de segundos tendrás tu Excel de salida

## Formato de salida

| Documento origen                  | RUC validado                                | Nombre o razón social                                                   | Estado de contribuyente | Condición de domicilio |
| --------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------- | ----------------------- | ---------------------- |
| texto exacto del Excel de entrada | RUC limpio o `None` en caso de ser inválido | Nombre o razón social, en caso de error en la consulta se mostrará aquí | Estado de contribuyente | Condición de domicilio |

## Errores de consulta RUC

En caso de un error con el RUC al momento de consultar, se mostrará en la columna `Nombre o razón social` con un color de fondo correspondiente al error

```python
RUC_QUERY_ERRORS = {
    "NOT_FOUND":
        {
            "text":"NO SE ENCONTRÓ",
            "color":"#FFC052".removeprefix("#")
        },
    "INVALID_FORMAT":
        {
            "text":"RUC INVÁLIDO",
            "color":"#FF5252".removeprefix("#")
        }
}
```
