import getopt
import sys
import subprocess
import argparse
import os
import re
import time
import requests

# Función para obtener los datos de fabricación de una tarjeta de red por IP
def obtener_datos_por_ip(ip):
    try:
        uri = f"https://api.maclookup.app/v2/macs/d4:9d:c0"

        start_time = time.time()  # Inicia el temporizador
        response = requests.get(uri)
        end_time = time.time()  # Detiene el temporizador
        elapsed_time = end_time - start_time  # Calcula el tiempo transcurrido

        resultado_decodificado = response.text
        fabricante = obtener_fabricante_desde_arp(resultado_decodificado)

        if fabricante:
            print(f"IP address: {ip} Fabricante: {fabricante} Tiempo de respuesta: {round(elapsed_time*1000)}ms")
           
        else:
            print(f"IP address: {ip} No se encontró información del fabricante. Tiempo de respuesta: {round(elapsed_time*1000)}ms")
    except Exception as e:
        print(f"Error: {e}")

# Función para obtener los datos de fabricación de una tarjeta de red por MAC

def obtener_datos_por_mac(mac):
    # Define la URI para la API REST
    uri = f"https://api.maclookup.app/v2/macs/{mac}"

    # Registra el tiempo de inicio de la solicitud
    start_time = time.time()

    # Realiza la solicitud a la API REST
    response = requests.get(uri)

    # Registra el tiempo de finalización de la solicitud
    end_time = time.time()

    # Calcula el tiempo transcurrido (latencia)
    elapsed_time = round((end_time - start_time) * 1000) 
    

    # Extrae el fabricante de la respuesta de la API
    fabricante = response.json().get('company', '')

    return fabricante, elapsed_time
# Función para obtener los datos de fabricación de una tarjeta de red por MAC usando la API


# Función para procesar la tabla ARP
def obtener_fabricante_desde_arp(arp_output):
    lines = arp_output.split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            ip = parts[0]
            mac = parts[1]
            if ip.startswith("192.168.1.") and len(mac) == 17:
                return mac

# Parsear los argumentos de línea de comandos
parser = argparse.ArgumentParser(description="Herramienta para consultar el fabricante de una tarjeta de red dada su dirección MAC o su IP.")
parser.add_argument("--ip", help="IP del host a consultar.")
parser.add_argument("--mac", help="MAC a consultar. P.e. aa:bb:cc:00:00:00.")
parser.add_argument("--arp", help="Muestra los fabricantes de los host disponibles en la tabla arp.", action="store_true")
parser.add_argument("--api", help="MAC a consultar usando la API. P.e. aa:bb:cc:00:00:00.")
args = parser.parse_args()

if args.mac:
    mac_address = args.mac
    vendor = obtener_datos_por_mac(mac_address)
    if vendor:
        print(f"IP address: {mac_address} Fabricante: {vendor}ms")
    else:
        print(f"No se encontró información del fabricante para la dirección MAC {mac_address}.")
elif args.ip:
    ip_address = args.ip
    obtener_datos_por_ip(ip_address)
elif args.arp:
    response = os.popen("arp -a").read()
    arp_table = re.findall(r"((\d{1,3}\.){3}\d{1,3})\s+([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\s+(\w+)", response)
    print("IP/MAC/Vendor:")
    for arp_entry in arp_table:
        ip_address, _, mac_address, _, _ = arp_entry
        vendor = obtener_datos_por_mac(mac_address)
        if vendor:
            print(ip_address + " / " + mac_address + " / " + vendor)
        else:
            print(ip_address + " / " + mac_address + " / No se encontró información del fabricante.")
else:
    parser.print_help()