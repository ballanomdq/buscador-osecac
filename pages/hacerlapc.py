import pyautogui
import time
import os

# --- CONFIGURACIÓN DE SEGURIDAD ---
pyautogui.FAILSAFE = True  # Si movés el mouse a una esquina de la pantalla, el robot se apaga (por si se vuelve loco)

class RobotOsecac:
    def __init__(self):
        self.tandas_exitosas = 0
        self.errores = []

    def informe(self, mensaje):
        print(f"[{time.strftime('%H:%M:%S')}] 🤖 {mensaje}")

    def esperar_y_cerrar_cartel(self):
        self.informe("Buscando el cartel de seguridad amarillo...")
        # Intentamos cerrar con teclado primero (es más rápido)
        time.sleep(2)
        pyautogui.press('esc')
        time.sleep(1)
        pyautogui.press('enter')
        self.informe("Comando de cierre enviado. Verificando...")

    def procesar_impresion(self):
        self.informe("Localizando botones de la ventana modal...")
        # Navegación ciega pero efectiva por TAB (ya que el modal tiene el foco)
        # TAB 1: Cantidad de copias
        # TAB 2: Checkbox S/Ciudad
        # TAB 3: Link Imprimir
        try:
            time.sleep(2)
            for _ in range(3):
                pyautogui.press('tab')
                time.sleep(0.3)
            
            pyautogui.press('space') # Tilda 'S/Ciudad'
            self.informe("✓ Checkbox S/Ciudad tildado")
            
            time.sleep(0.5)
            pyautogui.press('enter') # Ejecuta Imprimir
            self.informe("✓ Botón Imprimir presionado")
            return True
        except Exception as e:
            self.errores.append(f"Falla en controles: {str(e)}")
            return False

    def ejecutar(self, cantidad_tandas=5):
        self.informe("¡INICIANDO OPERACIÓN RESCATE!")
        self.informe("Tenés 5 segundos para poner Edge al frente...")
        time.sleep(5)

        for i in range(cantidad_tandas):
            self.informe(f"--- INICIANDO TANDA {i+1} ---")
            
            # Paso 1: Ejecutar tu Favorito (Botón Mágico)
            # Asumimos que el mouse está sobre el botón o lo apretás vos la primera vez
            # Si querés que el robot haga clic en el favorito, pasame la coordenada
            
            # Paso 2: El bloqueo de seguridad
            self.esperar_y_cerrar_cartel()

            # Paso 3: Operar la ventana
            if self.procesar_impresion():
                self.tandas_exitosas += 1
                self.informe(f"Tanda {i+1} completada. Esperando descarga...")
            else:
                self.informe(f"Hubo un problema en la tanda {i+1}")
            
            time.sleep(10) # Tiempo para que el servidor de OSECAC respire

        self.mostrar_resumen()

    def mostrar_resumen(self):
        print("\n" + "="*30)
        print("      RESUMEN DEL ROBOT")
        print("="*30)
        print(f"Actas procesadas (aprox): {self.tandas_exitosas * 2}")
        print(f"Errores encontrados: {len(self.errores)}")
        for err in self.errores:
            print(f"- {err}")
        print("="*30)

if __name__ == "__main__":
    bot = RobotOsecac()
    bot.ejecutar(cantidad_tandas=10) # Cambiá este número según cuántas actas tengas
