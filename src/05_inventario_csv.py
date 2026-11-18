"""
05_inventario_csv.py - Inventario de la red exportado a CSV
TP N° 4 Integrador - Redes de Computadoras (3643) - Grupo 06

Qué hace:
  1. Pide el ticket al Network Controller (POST /ticket).
  2. Lee los equipos de red (GET /network-device) y los hosts (GET /host).
  3. Muestra en pantalla un resumen y dos tablas.
  4. Exporta todo a dos archivos CSV que se abren con Excel:
       inventario_dispositivos.csv y inventario_hosts.csv
  5. Cierra la sesión borrando el ticket (DELETE /ticket/{ticket}).

Valor agregado respecto de los scripts suministrados:
  - Pide el ticket solo y lo cierra al terminar (no hay que pegarlo a mano).
  - No guarda la clave en el código: la toma de variables de entorno
    (NC_USER y NC_PASS) o la pide por teclado.
  - Muestra el estado de gestión de cada equipo (Managed, Wrong credential...),
    así se ve qué equipos administra el controlador y cuáles no.
  - Deja el inventario en archivos CSV, listos para documentar o comparar.
"""

import csv
import getpass
import os
import sys
from collections import Counter

import requests
from tabulate import tabulate

BASE_URL = os.environ.get("NC_URL", "http://localhost:58000/api/v1")
HEADERS_JSON = {"Content-Type": "application/json"}


def pedir_ticket(usuario, clave):
    """POST /ticket: devuelve el serviceTicket para usar en X-Auth-Token."""
    resp = requests.post(f"{BASE_URL}/ticket",
                         json={"username": usuario, "password": clave},
                         headers=HEADERS_JSON, timeout=10)
    print("POST /ticket ->", resp.status_code)
    if resp.status_code not in (200, 201):
        print("No se pudo obtener el ticket. Revisá usuario y clave del controlador.")
        print(resp.text)
        sys.exit(1)
    return resp.json()["response"]["serviceTicket"]


def leer(recurso, ticket):
    """GET de un recurso de la API; devuelve la lista 'response'."""
    resp = requests.get(f"{BASE_URL}/{recurso}",
                        headers={"X-Auth-Token": ticket}, timeout=10)
    print(f"GET /{recurso} ->", resp.status_code)
    resp.raise_for_status()
    return resp.json().get("response", [])


def cerrar_sesion(ticket):
    """DELETE /ticket/{ticket}: invalida el ticket al terminar.
    La API de Packet Tracer exige Content-Type aunque no haya cuerpo."""
    try:
        resp = requests.delete(f"{BASE_URL}/ticket/{ticket}",
                               headers={**HEADERS_JSON, "X-Auth-Token": ticket},
                               timeout=10)
        print("DELETE /ticket ->", resp.status_code)
    except requests.RequestException as error:
        print("No se pudo cerrar la sesión:", error)


def exportar_csv(nombre, columnas, filas):
    """Escribe un CSV con separador ';' para que Excel en español lo abra
    directamente en columnas."""
    with open(nombre, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        escritor.writerow(columnas)
        escritor.writerows(filas)
    print(f"Archivo generado: {os.path.abspath(nombre)} ({len(filas)} filas)")


def main():
    usuario = os.environ.get("NC_USER") or input("Usuario del controlador: ")
    clave = os.environ.get("NC_PASS") or getpass.getpass("Clave del controlador: ")

    ticket = pedir_ticket(usuario, clave)
    try:
        equipos = leer("network-device", ticket)
        hosts = leer("host", ticket)
    finally:
        cerrar_sesion(ticket)

    # ---- Equipos de red ----
    col_eq = ["Hostname", "IP de gestión", "Plataforma", "Versión de software",
              "Número de serie", "Alcanzable", "Estado de gestión"]
    filas_eq = sorted(
        [[e.get("hostname") or "(sin nombre)",
          e.get("managementIpAddress", ""),
          e.get("platformId", ""),
          e.get("softwareVersion", ""),
          e.get("serialNumber", ""),
          e.get("reachabilityStatus", ""),
          e.get("collectionStatus", "")] for e in equipos],
        key=lambda fila: fila[0])

    # ---- Hosts ----
    col_ho = ["Hostname", "IP", "MAC", "Tipo",
              "Conectado a (IP del equipo)", "Interfaz"]
    filas_ho = sorted(
        [[h.get("hostName", ""),
          h.get("hostIp", ""),
          h.get("hostMac", ""),
          h.get("hostType", ""),
          h.get("connectedNetworkDeviceIpAddress", ""),
          h.get("connectedInterfaceName", "")] for h in hosts],
        key=lambda fila: fila[1])

    # ---- Resumen ----
    estados = Counter(fila[6] or "(sin estado)" for fila in filas_eq)
    print("\n=== Resumen ===")
    print(f"Equipos de red: {len(filas_eq)}")
    for estado, cantidad in estados.most_common():
        print(f"   {estado}: {cantidad}")
    print(f"Hosts: {len(filas_ho)}")

    print("\n=== Equipos de red ===")
    print(tabulate(filas_eq, headers=col_eq, tablefmt="rst"))
    print("\n=== Hosts ===")
    print(tabulate(filas_ho, headers=col_ho, tablefmt="rst"))
    print()

    exportar_csv("inventario_dispositivos.csv", col_eq, filas_eq)
    exportar_csv("inventario_hosts.csv", col_ho, filas_ho)


if __name__ == "__main__":
    main()
