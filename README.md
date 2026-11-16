# Cuentas por pagar · Venejugos y NMS

Tablero de cuentas por pagar: deuda con proveedores, antigüedad, calendario de pagos y cuotas de préstamos, con la deuda en dólares convertida a bolívares a la tasa del BCV o a una tasa manual.
Misma estructura del sitio Eventos NMS: una página, una hoja de estilos, los datos en JSON y los logos como archivos. Se publica con GitHub Pages.

## Archivos

| Archivo | Para qué |
|---|---|
| `index.html` | El tablero, el registro de facturas y el panel administrativo |
| `styles.css` | Identidad visual (azul marino y ámbar, Barlow) |
| `cxp.json` | Registro inicial. El registro vivo se guarda en la rama `datos` (ver más abajo) |
| `tasa.json` | Tasa BCV, tasa manual e historial. Lo actualizan la tarea automática y el panel |
| `logo-venejugos.png`, `logo-nms.png`, `logo-nms-blanco.png` | Logos de las empresas |
| `logos/<nombre>.png` | Logos de proveedores y bancos (opcional) |
| `.github/workflows/tasa-bcv.yml`, `scripts/tasa_bcv.py` | Tarea que lee la tasa en bcv.org.ve de lunes a viernes |

`vista-previa.html` no va al repositorio: es la misma página con todo incorporado, para abrirla con doble clic.

## Puesta en marcha

1. Crea el repositorio y sube todo el contenido de la carpeta **respetando las subcarpetas** (`.github/workflows/`, `scripts/`, `logos/`).
2. *Settings → Pages*: *Deploy from a branch*, rama `main`, carpeta `/ (root)`.
3. *Settings → Actions → General → Workflow permissions*: marca **Read and write permissions**.
4. *Actions → Tasa BCV → Run workflow* para la primera lectura de la tasa.
5. Crea un token *fine-grained* con permiso **Contents: Read and write** solo sobre este repositorio. Lo ideal es uno por persona (cada una con su cuenta de GitHub y acceso al repositorio); también funciona uno compartido.

## Uso diario

**Registrar una factura** (pestaña *Registrar*). El formulario tiene los mismos ítems de la hoja PROVEEDORES:

| Ítem | Cómo se llena |
|---|---|
| PROVEEDOR, DOCUMENTO, F.EMISION, BASE IMPONIBLE, EXENTO | Se escriben |
| IVA | 16 % de la base; se puede corregir a mano |
| RETENCION | 75 % del IVA; se puede corregir a mano |
| F.VCTO. | Emisión más los días de crédito habituales de ese proveedor; se puede cambiar |
| TASA BCV FACT | La tasa BCV de la fecha de emisión si está guardada; se puede escribir |
| TOTAL FACTURA, $, POR PAGAR MENOS RETENCION, DEUDA EN USD, Días de vencimiento, STATUS | Se calculan solos, igual que en el Excel |

Además se elige la EMPRESA (Venejugos o NMS). Una misma factura (empresa, proveedor y documento) no se puede registrar dos veces.

En la lista *Registro*, cada factura se puede **corregir**, marcar como **pagada** (sale de la deuda y queda en *Pagadas* con su fecha) o **anular**. Nada se borra: todo se puede devolver a *por pagar*.

**Conectar un equipo.** La primera vez, en la pestaña *Registrar*, cada persona escribe su nombre y pega el token. Sin token puede ver el tablero, pero lo que registre se queda solo en su equipo.

**Cargar el Excel** (panel administrativo, contraseña `NMS2026`). Sirve para la carga inicial o masiva: *Actualizar por documento y agregar las nuevas* no toca lo demás; *Reemplazar* además retira las facturas que ya no vienen en el Excel. Las facturas marcadas como pagadas o anuladas no se reactivan por venir en el Excel.

Para cambiar la contraseña del panel, calcula el SHA-256 de la nueva y reemplaza `PASSWORD_HASH` al inicio del script de `index.html`. La contraseña solo oculta el panel; lo que protege el repositorio es el token.

## Varios equipos a la vez (15 usuarios)

- **Registro compartido.** Las facturas se guardan en `cxp.json` de la rama `datos`, que el sitio crea solo la primera vez que alguien guarda. Así registrar facturas no republica el sitio (GitHub Pages limita las publicaciones por hora).
- **Sin pisarse.** Cada guardado lee el registro, le suma los cambios de ese equipo y lo sube indicando la versión que leyó. Si otro equipo subió en ese instante, GitHub lo rechaza y el sitio repite con la versión nueva. Dos personas pueden registrar a la vez sin que se pierda nada.
- **Al día.** Con token, cada equipo consulta el registro cada 30 segundos; si nadie cambió nada, la consulta no gasta cuota de GitHub. Sin token (solo lectura) se actualiza cada pocos minutos.
- **Sin conexión.** Lo registrado queda en el equipo, marcado como *sin subir*, y se sube solo cuando vuelve la conexión.
- **Indicador.** Junto a las pestañas: *Sincronizado*, *N cambios por subir* o *Solo lectura*. Al pulsarlo se sincroniza en el momento.

Límites que conviene conocer:

- No es en tiempo real: los demás ven un cambio en unos 30 segundos.
- Si muchos guardan en el mismo segundo, las subidas hacen fila; en la prueba con 15 equipos a la vez la última tardó unos 13 segundos.
- Si dos personas corrigen la misma factura a la vez, queda la última que guardó.
- Cada equipo que registra necesita un token con permiso de escritura sobre el repositorio. Quien lo tiene puede cambiar cualquier factura; el nombre de cada persona es el que ella escribe. No hay permisos por usuario.
- Si el equipo crece mucho más o hace falta control de permisos y auditoría, conviene pasar el registro a una base de datos.

## Empresas y logos dinámicos

- El selector **Empresa** aparece cuando el Excel trae más de una. El logo del encabezado cambia con la empresa elegida; con *Todas* se muestran todos.
- Las cuotas de préstamos traen su empresa desde el Excel (el bloque `RESUMEN CXP FINANCIERO DISTRIBUIDORA NMS 2023, C.A`).
- Al registrar una factura se elige la empresa. La hoja PROVEEDORES del Excel no la indica, así que lo que se cargue desde ahí se asigna a Venejugos, salvo que le agregues una columna **EMPRESA**.
- Una empresa nueva usa `logos/<nombre>.png`; para darle logo propio en el encabezado, agrégala a la lista `MARCAS` del script.
- Proveedores y bancos: el tablero busca `logos/<nombre>.png` (minúsculas, sin acentos, con guiones: `ALIMENTOS POLAR` → `logos/alimentos-polar.png`). Si no existe muestra las iniciales. El panel lista cada nombre y publica la imagen que subas.

## Columnas de proveedores

`PROVEEDOR · DOCUMENTO · F.EMISION · BASE IMPONIBLE · EXENTO · IVA · TOTAL FACTURA · $ · RETENCION · F.VCTO. · POR PAGAR MENOS RETENCION · TASA BCV FACT · DEUDA EN USD · Días de vencimiento · STATUS`

- Los montos se toman del Excel. Una celda vacía se calcula como en la hoja: IVA = base × 16 %; total = base + exento + IVA; retención = IVA × 75 %; por pagar = total − retención; $ = total ÷ tasa de la factura; deuda en USD = por pagar ÷ tasa de la factura.
- **Días de vencimiento** = fecha de cálculo − F.VCTO. (positivo: atraso). **STATUS**: `VENCIDO` si la fecha de cálculo es posterior a F.VCTO.; si no, `POR VENCER`.
- Columna adicional: **Bs. a la tasa en uso** = deuda en USD × tasa en uso.
- Antigüedad: vencido 1–7, 8–30, 31–60 y más de 60 días; por vencer hoy–7, 8–15 y más de 15.

## Tasa de cambio

Prioridad de la tasa en uso:

1. Tasa manual escrita en la barra (solo en ese equipo).
2. Tasa manual publicada desde el panel (para todos, hasta que se quite).
3. Tasa BCV más reciente con fecha de hoy o anterior: la de `tasa.json` o la que consulte el navegador. El BCV publica por la tarde la tasa del siguiente día hábil; se muestra como próxima y aplica cuando llega su fecha.
4. Si aún no hay ninguna, la última tasa de las facturas, y la barra lo avisa en ámbar.

- **Tarea automática:** lee el dólar en `https://www.bcv.org.ve` y actualiza `tasa.json`. No toca la tasa manual.
- **Actualizar desde el BCV:** el navegador no puede leer bcv.org.ve directamente, así que consulta servicios públicos que replican la tasa oficial (DolarApi, PyDolarVE, bcv-api). Queda en ese equipo; **Publicar la tasa en uso** la deja para todos.
- `tasa.json` usa el mismo formato de Eventos NMS (`valor`, `fecha`, `actualizada`, `fuente`) más `manual` e `historial`.

## Financiero

Se lee cada hoja con nombre de mes: columnas `CUOTA · FECHA · CUOTA $ · CAPITAL · INTERESES · BANCO` hasta la fila TOTAL.

- El total del mes suma todas las filas. En el Excel la fila TOTAL usa `SUBTOTAL` y omite las filas ocultas, por eso puede diferir.
- El Excel marca las cuotas pagadas con colores, que no se pueden leer de forma confiable. El estado sale de la fecha. Con una columna `ESTATUS` que diga `PAGADA`, el tablero la muestra como pagada.

## Notas

- El lector de Excel (SheetJS) y las tipografías se cargan de internet, igual que en Eventos NMS.
- El repositorio es público: quien tenga el enlace puede ver el registro. La casilla del panel permite dejar fuera las cuotas de préstamos.
- La rama `datos` no se edita a mano. Para respaldar, usa *Descargar cxp.json* en el panel.
