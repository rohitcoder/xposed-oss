import yaml, os, json
from rich import print

def load_config(config_path):
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        print("[bold green]Configuration loaded successfully.[/bold green]")
        return config
    except Exception as e:
        print(f"[bold red]Error loading configuration: {e}[/bold red]")
        raise

def build_result():
    final_result = []

    # Iterate through all .json files in the output directory
    output_path = os.path.join(os.getcwd(), "output")
    ## create output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for filename in os.listdir(output_path):
        if filename.endswith(".json"):
            file_path = os.path.join(output_path, filename)

            with open(file_path, "r") as json_file:
                module_data = json.load(json_file)
                for entry in module_data:
                    email = entry.get("email")
                    profile = entry.get("profile")
                    module_name = entry.get("module")
                    permissions = entry.get("permissions")

                    # Check if the entry already exists in the final result
                    existing_entry = next((user_entry for user_entry in final_result if user_entry["email"] == email), None)

                    if existing_entry:
                        # Entry exists, update permissions and module_name, we can get new profile also so create a new profile entry
                        if profile not in existing_entry["assets"][module_name]:
                            existing_entry["assets"][module_name][profile] = permissions
                        else:
                            existing_entry["assets"][module_name][profile].extend(permissions)
                    else:
                        # Entry doesn't exist, create a new entry
                        user_entry = {
                            "user_type": entry.get("user_type"),
                            "metadata": entry.get("metadata", {}),
                            "email": email,
                            "assets": {
                                module_name: {
                                    profile: permissions
                                }
                            }
                        }
                        final_result.append(user_entry)

    # Save the final result to the output_data.json file
    output_path = os.path.join(os.getcwd())
    output_file = os.path.join(output_path, "output_data.json")
    with open(output_file, "w") as file:
        json.dump(final_result, file, indent=2)

    return output_file