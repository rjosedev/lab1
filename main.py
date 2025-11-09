from class_device_config import ConfigDevices
from class_create_configs import CreateConfig
import json
import os
from datetime import datetime
from simple_term_menu import TerminalMenu

def main():
    print (f"-> Iniciando proceso de automatización de configuración de dispositivos de red...")
    net_conf = ConfigDevices()
    create_config = CreateConfig()

    # Leer archivo modelo de datos
    dic_modelo = create_config.read_yaml("modelo_datos.yaml")
    print (json.dumps(dic_modelo, indent=4))
    print(f"{'\n'}-> Archivo modelo de datos leído exitosamente.")
    print(f"-> Modelo de datos contiene {len(dic_modelo.get('modelo').get('infra_spec').get('devices'))} dispositivos: {[device.get('hostname') for device in dic_modelo.get('modelo').get('infra_spec').get('devices')]}")
    input("Presionar ENTER para continuar...")

    # Prompt con 2 opciones: aplicar configuraciones a todos los dispositivos o seleccionar dispositivos
    terminal_menu = TerminalMenu(
        menu_entries=["Aplicar configuraciones a todos los dispositivos del modelo",
                      "Seleccionar dispositivos específicos para aplicar configuraciones"],
        title="Selecciona el modo de aplicación de configuraciones",
        menu_cursor="> ",
        menu_cursor_style=("fg_green", "bold"),
        menu_highlight_style=("bg_green", "fg_black"),
        cycle_cursor=True,
        clear_screen=True,
    )
    menu_entry_index_mode = terminal_menu.show()
    print(menu_entry_index_mode)

    if menu_entry_index_mode == 0:
        # Seleccionar todos los dispositivos
        selected_devices = [device.get('hostname') for device in dic_modelo.get("modelo").get("infra_spec").get("devices")]
        print(f"-> Aplicar configuraciones a todos los dispositivos: {selected_devices}")
        input("Presionar ENTER para continuar...")
    else:
        # Menu de seleccion multiple de dispositivos en forma de lista, permitiendo seleccionar varios dispositivos
        terminal_menu = TerminalMenu(
            menu_entries=[device.get('hostname') for device in dic_modelo.get("modelo").get("infra_spec").get("devices")],
            title="-> Selecciona los dispositivos a configurar",
            menu_cursor="> ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black"),
            cycle_cursor=True,
            clear_screen=True,
            multi_select=True,
            show_multi_select_hint=True,
        )
        menu_entry_index_mode = terminal_menu.show()
        print(menu_entry_index_mode)
        print(terminal_menu.chosen_menu_entries)

    # Generar archivos de configuracion por dispositivo
    print (f"{'\n'}-> Generando archivos de configuración...")
    for device in dic_modelo.get("modelo").get("infra_spec").get("devices"):
        hostname = device.get('hostname')
        for config in device.get("config_spec"):
            config_template = config.get("template")
            data_path = config.get("data_path")
            config_file_name = f"{hostname}_{config.get('config_file')}"

            # Renderizar template
            print(f"Creando archivo de configuración '{config_file_name}' usando plantilla '{config_template}' para dispositivo '{hostname}'")
            template = create_config.render_template(template_name=config_template, data={data_path: device.get(data_path)})
            create_config.guardar_config_file(config_file_name, template)
            print(f"Archivos de configuración para {hostname} creados.")
    input("Presionar ENTER para continuar...")

    # Almacenar archivos de configuracion generados
    print(f"{'\n'}-> Archivos de configuración disponibles:")
    config_files = os.listdir("./configs")
    [print (f) for f in sorted(config_files) if f.endswith(".cfg")]
    input("Presionar ENTER para continuar...")

    # Mostrar contenido de archivos de configuracion generados (opcional)
    # print(f"{'\n'}-> Mostrar contenido de archivos de configuración disponibles:")
    # [os.system("cat ./configs/" + f) for f in sorted(config_files) if f.endswith(".cfg")]

    # Conectar y configurar cada dispositivo seleccionado
    if terminal_menu.chosen_menu_entries == None:
        print(f"{'\n'}-> Conectando a todos los dispositivos '{selected_devices}' y aplicando configuraciones...")
    else:
        print (f"{'\n'}-> Conectando a dispositivos seleccionados '{terminal_menu.chosen_menu_entries}' y aplicando configuraciones...")
    
    start_total_configuration_duration = datetime.now()
    start_time = datetime.now()
    for device in dic_modelo.get("modelo").get("infra_spec").get("devices"):
        if terminal_menu.chosen_menu_entries == None:
            pass
        elif device.get('hostname') not in terminal_menu.chosen_menu_entries:
            print(f"{'->'} Dispositivo '{device.get('hostname')}' no seleccionado. Saltando configuración.")
            continue
        ssh_connect_params = device.get("ssh_connect")
        host = ssh_connect_params.get("host")
        hostname = device.get("hostname")
        
        # Conectar al dispositivo
        connection = net_conf.connect_device(ssh_connect_params)
        print(f"{'\n'}Conectado al dispositivo '{hostname}' en IP '{host}'")
        
        # Leer archivos de configuracion y enviarlos a los dispositivos 
        print (f"{'\n'}-> Procesando archivos de configuración para dispositivo '{hostname}'...")
        
        # Almacenar solo los archivos de configuracion correspondientes al dispositivo
        conf_file_list = [conf_file for conf_file in config_files if conf_file.startswith(hostname)]

        # Inicializar menu de seleccion multiple de configuración en forma de lista, permitiendo seleccionar varias configuraciones
        print (f"-> Iniciando menu de selección de archivos de configuración a aplicar en dispositivos seleccionados...")
        terminal_menu_configs = TerminalMenu(
            menu_entries=conf_file_list,
            title=f"Selecciona los archivos de configuración a aplicar en el dispositivo '{hostname}'",
            menu_cursor="> ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black"),
            cycle_cursor=True,
            clear_screen=True,
            multi_select=True,
            show_multi_select_hint=True,
        )
        menu_entry_indices_configs = terminal_menu_configs.show()
        print(menu_entry_indices_configs)
        print(terminal_menu_configs.chosen_menu_entries)
        
        for config_file in conf_file_list:          
            if config_file not in terminal_menu_configs.chosen_menu_entries:
                print(f"{'->'} Config '{config_file}' no seleccionada. Saltando configuración.")
                continue
            print(f"Aplicando configuración seleccionada desde '{config_file}' para dispositivo '{hostname}'")
            output = net_conf.send_config_commands(connection=connection, config_file=config_file)
            
            # Verificar errores en la salida
            has_error = net_conf.check_output_error(output)
            if has_error:
                print(f"Errores encontrados en configuración para '{device.get('hostname')}'. Abortando configuraciones adicionales.")
                break
            else:
                print(f"Configuración desde '{config_file}' aplicada exitosamente al dispositivo '{hostname}'")

        # Guardar configuración
        if not has_error:
            net_conf.save_configuration(connection)
            print(f"{'->'} Configuración guardada exitosamente en dispositivo '{hostname}' en IP '{host}'")
        end_time = datetime.now()

        # Calcular e imprimir duración de configuración del dispositivo
        duration = end_time - start_time
        print(f"{'->'} Tiempo tomado para configurar dispositivo '{hostname}': {duration}")

        # Desconectar del dispositivo
        net_conf.disconnect_device(connection)
        print(f"{'->'} Desconectado del dispositivo '{hostname}' en IP '{host}'")
    
    # Imprimir duración total de configuración
    end_total_configuration_duration = datetime.now()
    total_configuration_duration = end_total_configuration_duration - start_total_configuration_duration
    print(f"{'\n'}-> Tiempo total tomado para configurar todos los dispositivos: {total_configuration_duration}")

if __name__ == "__main__":
    main()