import requests
import urllib.parse

route_url = "https://graphhopper.com/api/1/route?"
key = "33ba2915-0f73-4662-85b7-d638ea9a91d1"


def geocoding(location, key):
    while not location.strip():
        location = input("Ingrese la ubicación nuevamente (s/salir para salir): ").strip()
    if location.lower() in ("s", "salir"):
        return None, None, None, location

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({
        "q": location, "limit": 1, "key": key
    })
    try:
        replydata = requests.get(url, timeout=30)
    except requests.exceptions.RequestException:
        print("Error de conexión. Revise el internet e intente nuevamente.")
        return None, None, None, location
    json_status = replydata.status_code
    try:
        json_data = replydata.json()
    except ValueError:
        print("Estado de la API de GEOCODE:", json_status, "La respuesta no es JSON.")
        return json_status, None, None, location

    if json_status == 200 and json_data.get("hits"):
        hit = json_data["hits"][0]
        lat = hit["point"]["lat"]
        lng = hit["point"]["lng"]
        name = hit.get("name", location)
        state = hit.get("state", "")
        country = hit.get("country", "")
        value = hit.get("osm_value", "unknown")
        new_loc = ", ".join(part for part in (name, state, country) if part)
        print("URL para la API de GEOCODE " + new_loc +
              " (Location Type: " + value + "):\n" + url)
        return json_status, lat, lng, new_loc
    if json_status == 200:
        print("No se encontraron resultados. Ingrese una ubicación más especifica.")
    else:
        print("Estado de la API de GEOCODE:", json_status)
        print("Mensaje de error:", json_data.get("message", "Unknown API error"))
    return json_status, None, None, location


while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Perfil de vehiculos: auto, bicicleta, pie")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    profiles = ["auto", "bicicleta", "pie"]
    VehiculoEscogido = input("Ingrese un vehiculo (s/salir para salir): ").strip().lower()
    if VehiculoEscogido in ("s", "salir"):
        print("Saliendo del programa")
        break
    if VehiculoEscogido not in profiles:
        vehicle = "car"
        print("No se ingreso un vehiculo valido. Utilizando auto.")
    
    if VehiculoEscogido == "auto":
        vehicle = "car"
    elif VehiculoEscogido == "bicicleta":
        vehicle = "bike"
    elif VehiculoEscogido == "pie":
        vehicle = "foot"

    loc1 = input("Punto de partida: ").strip()
    if loc1.lower() in ("s", "salir"):
        print("Saliendo del programa")
        break
    orig = geocoding(loc1, key)
    if orig[3].lower() in ("s", "salir"):
        print("Saliendo del programa")
        break
    if orig[0] != 200 or orig[1] is None or orig[2] is None:
        continue

    loc2 = input("Destino: ").strip()
    if loc2.lower() in ("s", "salir"):
        print("Saliendo del programa")
        break
    dest = geocoding(loc2, key)
    if dest[3].lower() in ("s", "salir"):
        print("Saliendo del programa")
        break
    if dest[0] != 200 or dest[1] is None or dest[2] is None:
        continue

    params = [
        ("key", key),
        ("profile", vehicle),
        ("point", str(orig[1]) + "," + str(orig[2])),
        ("point", str(dest[1]) + "," + str(dest[2])),
        ("instructions", "true"),
        ("locale", "es_MX")
    ]
    paths_url = route_url + urllib.parse.urlencode(params)
    try:
        paths_reply = requests.get(paths_url, timeout=30)
    except requests.exceptions.RequestException:
        print("Error de conexión. Revisar internet e intentar nuevamente.")
        continue
    paths_status = paths_reply.status_code
    print("=================================================")
    print("Estado de la API de rutas:", paths_status)
    print("URL de la API de rutas:\n" + paths_url)
    try:
        paths_data = paths_reply.json()
    except ValueError:
        print("La respuesta no es JSON.")
        continue
    if paths_status != 200:
        print("Mensaje de error:", paths_data.get("message", "Unknown API error"))
        print("*************************************************")
        continue
    if not paths_data.get("paths"):
        print("No se obtuvo una ruta.")
        continue

    path = paths_data["paths"][0]
    km = path["distance"] / 1000
    miles = km / 1.61
    total_seconds = int(path["time"] / 1000)
    hr = total_seconds // 3600
    minute = (total_seconds // 60) % 60
    sec = total_seconds % 60
    print("Direcciones desde " + orig[3] + " hacia " + dest[3] + " en " + VehiculoEscogido)
    print("Distancia recorrida: {0:.2f} millas / {1:.2f} km".format(miles, km))
    print("Duración del viaje: {0:.2f}:{1:.2f}:{2:.2f}".format(hr, minute, sec))
    print("=================================================")
    for instruction in path.get("instructions", []):
        text = instruction["text"]
        distance = instruction["distance"]
        print("{0} ( {1:.2f} km / {2:.2f} millas )".format(
            text, distance / 1000, distance / 1000 / 1.61
        ))
    print("=================================================")