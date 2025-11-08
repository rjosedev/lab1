from jinja2 import Environment, FileSystemLoader
import yaml
import json

class CreateConfig():
    # Renderizar plantilla Jinja2 para crear archivos de configuracion
    def render_template(self, template_name: str, data: any, template_dir: str = "./templates") -> str:
        loader = FileSystemLoader(template_dir)
        env = Environment(loader=loader)
        template = env.get_template(template_name)
        return template.render(data)

    # Guardar archivo de configuracion
    def guardar_config_file(self, filename: str, configuration: str, file_dir: str = "./configs") -> None:
        try:
            with open(f"{file_dir}/{filename}", 'w') as f:
                f.write(configuration)
        except Exception as error:
            print(f"Error creando archivo {filename}: {error}")
            exit(1)

    # Leer archivo Modelo de Datos
    def read_yaml(self, file_path: str) -> dict:
        try:
            with open(file_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as error:
            print(f"Error leyendo archivo {file_path}: {error}")
            exit(1)

    # Escribir archivo JSON
    def write_json(self, data: dict, file_path: str):
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as error:
            print(f"Error creando archivo {file_path}: {error}")
            exit(1)