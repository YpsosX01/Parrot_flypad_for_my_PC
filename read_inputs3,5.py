import asyncio
import logging
import vgamepad as vg  # pip install vgamepad
from bleak import BleakClient

# ID de la caractéristique Bluetooth (remplace par le bon ID si nécessaire)
INPUT_ID = "9e35fa01-4344-44d4-a2e2-0c7f6046878b"

# Paramètres de base du Flypad
address = "C7:41:41:B2:60:29"  # Remplace par l'adresse MAC correcte de ton Flypad
gamepad = vg.VX360Gamepad()  # Initialisation du gamepad
current_state = {"a": False, "b": False, "1": False, "2": False, "l3": False, "r3": False, "l2": False, "r2": False, "l1": False, "r1": False, "takeoff": False}
sensitivity_factorR = 1
sensitivity_factorL = 0.25

# Configurer les logs
logging.basicConfig(level=logging.DEBUG)

# Fonction pour gérer les données reçues du Flypad
def print_data(handle, data):
    global current_state
    converted = bytes(data)
    button = ord(bytes(data[1:2]))
    extrabutton = ord(bytes(data[2:3]))

    # Gestion des boutons
    if button & 0x02:
        current_state["1"] = True
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
    else:
        current_state["1"] = False
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)

    if button & 0x04:
        current_state["2"] = True
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
    else:
        current_state["2"] = False
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)

    if button & 0x08:
        current_state["b"] = True
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
    else:
        current_state["b"] = False
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)

    if button & 0x10:
        current_state["a"] = True
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    else:
        current_state["a"] = False
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

    # Gestion des gâchettes et sticks
    if button & 0x40:
        current_state["r2"] = True
        gamepad.right_trigger(value=255)
    else:
        current_state["r2"] = False
        gamepad.right_trigger(value=0)

    if button & 0x20:
        current_state["r1"] = True
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    else:
        current_state["r1"] = False
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)

    if extrabutton & 0x02:
        current_state["l3"] = True
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
    else:
        current_state["l3"] = False
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)

    if extrabutton & 0x01:
        current_state["l2"] = True
        gamepad.left_trigger(value=255)
    else:
        current_state["l2"] = False
        gamepad.left_trigger(value=0)

    # Joysticks
    right_x = bytes(data[3:4])
    right_y = bytes(data[4:5])
    left_x = bytes(data[5:6])
    left_y = bytes(data[6:7])

    f_rx = ((float(ord(right_x)) - 128) / 128) * sensitivity_factorR
    f_ry = -((float(ord(right_y)) - 128) / 128) * sensitivity_factorR
    f_lx = ((float(ord(left_x)) - 128) / 128) * sensitivity_factorR
    f_ly = -((float(ord(left_y)) - 128) / 128) * sensitivity_factorR

    gamepad.left_joystick_float(x_value_float=f_lx, y_value_float=f_ly)
    gamepad.right_joystick_float(x_value_float=f_rx, y_value_float=f_ry)
    gamepad.update()

# Fonction principale pour la connexion Bleak
async def connect_to_flypad(address):
    logging.info(f"Connexion au Flypad à l'adresse {address}...")

    try:
        async with BleakClient(address) as client:
            if not client.is_connected:
                logging.error("Erreur de connexion : impossible de se connecter au Flypad.")
                raise RuntimeError("Le client n'est pas connecté.")

            logging.info("Connexion réussie avec le Flypad.")
            
            # Démarrer les notifications pour la caractéristique des entrées
            await client.start_notify(INPUT_ID, print_data)
            logging.info("Notifications activées. Attente des données...")

            await asyncio.sleep(1000000000000)  # Garder la connexion active pendant un très long moment
            await client.stop_notify(INPUT_ID)

    except Exception as e:
        logging.error(f"Erreur de connexion Bluetooth : {str(e)}")
        raise RuntimeError("Échec de la connexion Bluetooth.")

if __name__ == "__main__":
    logging.info("Démarrage du programme Flypad avec Bleak...")
    asyncio.run(connect_to_flypad(address))
