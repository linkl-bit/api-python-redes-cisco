# API del Network Controller con Python – TP N° 4 Integrador, Grupo 06

Redes de Computadoras (3643) – UNLaM – 2° cuatrimestre 2026

Scripts en Python que usan la API REST (Northbound API) del Network Controller de Cisco Packet Tracer. El repositorio parte de los scripts de la cátedra ([redes-computadoras/api-python-redes-cisco](https://github.com/redes-computadoras/api-python-redes-cisco)) y suma un script propio del grupo.

## Qué hace cada script

| Script | Endpoints | Qué hace |
|---|---|---|
| `src/01_get-ticket.py` | `POST /ticket` | Pide el ticket de autenticación al controlador y lo muestra. *(cátedra)* |
| `src/02_get-network-device.py` | `GET /network-device` | Lista los equipos de red con su plataforma e IP de gestión. Usa un ticket pegado a mano. *(cátedra)* |
| `src/03_get-host.py` | `GET /host` | Lista los hosts con su IP, MAC e interfaz a la que están conectados. Usa un ticket pegado a mano. *(cátedra)* |
| `src/04_tabulate.py` | `POST /ticket`, `GET /network-device`, `GET /host` | Pide el ticket solo y muestra equipos y hosts en tablas con `tabulate`. *(cátedra)* |
| `src/05_inventario_csv.py` | `POST /ticket`, `GET /network-device`, `GET /host`, `DELETE /ticket/{ticket}` | **Script propio.** Arma el inventario completo de la red, muestra un resumen por estado de gestión (Managed, Wrong credential…) y lo exporta a `inventario_dispositivos.csv` e `inventario_hosts.csv`. Pide el ticket solo y lo cierra al terminar. |

### Script propio: `05_inventario_csv.py`

Qué agrega respecto de los scripts de la cátedra:

- **No hay que pegar el ticket a mano:** lo pide con `POST /ticket` y, al terminar, cierra la sesión con `DELETE /ticket/{ticket}`.
- **No guarda la clave en el código:** toma el usuario y la clave del controlador de las variables de entorno `NC_USER` y `NC_PASS` o, si no están, los pide por teclado. Así el repositorio, que es público, no expone credenciales.
- **Muestra el estado de gestión de cada equipo:** se ve qué equipos administra el controlador (Managed) y cuáles no. En nuestra topología, el ISP aparece con *Wrong credential* porque está fuera del sistema autónomo.
- **Exporta a CSV:** genera dos archivos con separador `;`, que Excel en español abre directamente en columnas.

Ejecución (con el entorno virtual activado y Packet Tracer abierto, con el acceso externo del controlador habilitado):

```bash
python src/05_inventario_csv.py
```

Opcionalmente, para no tipear las credenciales cada vez:

```bash
# Linux / macOS
export NC_USER=admin
export NC_PASS=<clave>
# Windows (PowerShell)
$env:NC_USER="admin"; $env:NC_PASS="<clave>"
```

---

# Entorno de virtualización Python

# Pasos de instalación en Linux:

## 1. Clonación del proyecto

Desde la terminal ejecutar:

**git clone** <URL_del_repositorio> <nombre_de_la_carpeta_de_destino>

Luego ejecutar **cd** <nombre_de_la_carpeta_de_destino>. Esta carpeta será la raíz de nuestro proyecto en Python.

## 2. Creación del entorno virtual

Supongamos que el nombre que le damos al entorno virtual es **cisco**, entonces se creará una carpeta **cisco** con todas las librerías y dependencias necesarias paea nuestro proyecto. 

La manera de realizarlo es la siguiente:

# python3 -m venv <nombre_del_entorno>
Ejemplo: python3 -m venv cisco

Para activar el entorno escribimos **source cisco/bin/activate**, en la carpeta raíz del proyecto. El nombre del entorno virtual aparecerá entre paréntesis ().

## 3. Instalación de las dependencias, en este caso las librerías requests y tabulate

En la carpeta raíz de nuestro proyecto y dentro del entorno virtual escribimos: **pip install -r requirements.txt**

## 4. Selección del intérprete Python para nuestro entorno virtual

<img width="881" height="118" alt="image" src="https://github.com/user-attachments/assets/18c41d8e-d338-48b6-953c-b2499c57319f" />

<img width="736" height="412" alt="image" src="https://github.com/user-attachments/assets/2a795fcd-2cf8-47ef-a5a6-d21e09ce967f" />

Tal como se ve en la figura seleccionamos Python 3.10.12 (cisco) que se mostrará como entorno recomendado.

## 5. Desactivación del entorno virtual

Simplemente escribimos en la línea de comandos: **deactivate**



## Antes de ejecutar los scripts

- **Credenciales del controlador:** los scripts usan el usuario `cisco` y la clave `cisco123!`. Si en tu Network Controller creaste otro usuario, cambialos en `01_get-ticket.py` y en `04_tabulate.py`.
- **Ticket (X-Auth-Token):** `02_get-network-device.py` y `03_get-host.py` traen escrito un ticket de ejemplo que **no va a funcionar** en tu Packet Tracer, porque el controlador genera uno nuevo en cada sesión y vence. Ejecutá primero `01_get-ticket.py`, copiá el ticket que muestra y reemplazalo en el header `X-Auth-Token` de esos dos scripts. `04_tabulate.py` no necesita este paso: pide el ticket solo.
