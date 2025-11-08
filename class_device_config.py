from netmiko import ConnectHandler
import yaml
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException

class ConfigDevices():
    # Leer archivo de configuracion
    def read_config_file(self, file_name: str, file_dir: str = "./configs") -> str:
        try:
            with open(f"{file_dir}/{file_name}", 'r') as f:
                return f.read()
        except Exception as error:
            print(f"Error leyendo archivo {file_name}: {error}")
            exit(1)

    # Conectar al dispositivo
    def connect_device(self, device_params: dict) -> ConnectHandler:
        try:
            connection = ConnectHandler(**device_params)
            return connection
        except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
            print(f"Error de conexión: {error}")
            exit(1)

    # Enviar comandos de configuracion
    def send_config_commands(self, connection: ConnectHandler, commands: list = None, config_file: str = None, config_dir: str = "./configs") -> str:
        try:
            output = connection.send_config_from_file(f"{config_dir}/{config_file}") if config_file else connection.send_config_set(commands)
            return output
        except Exception as error:
            print(f"Error enviando comandos: {error}")
            exit(1)

    # Verificar errores en la salida
    def check_output_error(self, output: str) -> bool:
        error_indicators = ["% Invalid input", "% Incomplete command", "% Ambiguous command"]
        for line in output.splitlines():
            if any(error in line for error in error_indicators):
                print(f"Error detectado en salida: {line}")
                return True
        return False

    # Desconectar del dispositivo
    def disconnect_device(self, connection: ConnectHandler) -> None:
        try:
            connection.disconnect()
        except Exception as error:
            print(f"Error desconectando: {error}")
            exit(1)

    # Salvar configuracion
    def save_configuration(self, connection: ConnectHandler) -> str:
        try:
            connection.save_config()
        except Exception as error:
            print(f"Error guardando configuración: {error}")
            exit(1)