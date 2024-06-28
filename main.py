# Updated main.py

import argparse
import json
from rich import print
from rich.logging import RichHandler
import logging
import importlib
import os
from utils import graph_builder, data_loader

def parse_args():
    parser = argparse.ArgumentParser(description="Xposed Cybersecurity Tool to Build Relationship Graph")
    parser.add_argument("--config", help="Path to the configuration file (config.yaml)", required=True)
    parser.add_argument("-m", "--modules", nargs="+", help="Specify the modules/tools to analyze")
    parser.add_argument("-o", "--output", help="Path to the output data directory", required=False, default="output")
    parser.add_argument("--log", help="Path to the log file", default="Xposed_tool.log")
    parser.add_argument("-v", "--verbose", help="Enable verbose mode", action="store_true", default=False)
    parser.add_argument("-d", "--debug", help="Enable debug mode", action="store_true", default=False)
    return parser.parse_args()

def setup_logging(log_file, verbose, debug):
    level = logging.WARNING
    if verbose:
        level = logging.INFO
    if debug:
        level = logging.DEBUG

    # Remove the 'filename' argument from basicConfig
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    # Add RichHandler to the root logger
    handler = RichHandler()
    logging.root.addHandler(handler)

    # Log to a file if log_file is provided
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logging.root.addHandler(file_handler)

def load_modules(module_names):
    modules = []
    for module_name in module_names:
        try:
            module = importlib.import_module(f"modules.{module_name}")
            modules.append(module)
        except ImportError:
            logging.warning(f"Module '{module_name}' not found. Skipping.")

    return modules


def main():
    args = parse_args()
    setup_logging(args.log, args.verbose, args.debug)

    # Load configuration
    config = data_loader.load_config(args.config)

    # Load Xposed modules
    modules_to_run = load_modules(args.modules) if args.modules else []

    if not modules_to_run:
        logging.warning("No modules specified. Running all available modules.")

        # Run all modules
        module_names = [name.replace(".py", "") for name in os.listdir("modules") if name.endswith("_module.py")]
        modules_to_run = load_modules(module_names)
    
    # Only run modules specified in the config for this connection
    for module_name, module_config in config.get("connections", {}).items():
        print(f"[bold cyan]Running module: {module_name}[/bold cyan]")
        logging.info(f"Running module: {module_name}")
        for profile_name, profile_config in module_config.items():
            logging.info(f"Running module: {module_name} for profile: {profile_name}")
            print(f"[bold cyan]Running module: {module_name} for profile: {profile_name}[/bold cyan]")
            try:
                module = importlib.import_module(f"modules.{module_name}_module")
                module.execute(config, args.output)
            except ImportError:
                logging.warning(f"Module '{module_name}' not found. Skipping.")
                continue

    output_file = data_loader.build_result()
    # Assuming your JSON data is in a file named 'output_data.json'
    with open('output_data.json', 'r') as json_file:
        data = json.load(json_file)

    # Generate and save the vis network HTML
    vis_network_code = graph_builder.generate_vis_network(data)
    with open(f'graphviz.html', 'w') as html_file:
        html_file.write(vis_network_code)
    print(f"[bold green]Xposed tool execution completed for all specified connections.[/bold green]")

if __name__ == "__main__":
    main()
