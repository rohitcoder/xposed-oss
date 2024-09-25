import subprocess
import logging
import json
import os
from rich import print
from rich.logging import RichHandler

# Configure rich for logging
print("[red]Note:[/red] This log will be less detailed. Check the log file for complete details.")
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler()]
)

def execute(config, output_path):
    users_and_permissions = []
    gcp_connections = config.get("connections", {}).get("gcp", {})

    for profile_name, profile_config in gcp_connections.items():
        logging.info(f"Processing GCP profile: {profile_name}")

        project_name = profile_config.get("project_name")
        service_account_key_path = profile_config.get("service_account_key_path")

        if not project_name or not service_account_key_path:
            raise ValueError("Project name and service account key path are required in the GCP configuration.")

        # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the service account key path
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_key_path

        # Run the gcloud command to get IAM policy in JSON format
        gcloud_command = f"gcloud projects get-iam-policy {project_name} --format=json"
        try:
            print("[bold cyan]Executing gcloud command...[/bold cyan]")
            iam_policy_json = subprocess.check_output(gcloud_command, shell=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running gcloud command: {e}")

        # Parse the IAM policy JSON
        iam_policy = json.loads(iam_policy_json)

        # Convert IAM policy into the required format
        formatted_data = convert_to_required_format(iam_policy, profile_name)
        # Save the output to a file in the data directory
        output_file = os.path.join(output_path, f"gcp_{profile_name}_data.json")
        save_output(formatted_data, output_file)

        # Append the formatted data to the list
        users_and_permissions.append(formatted_data)

    return users_and_permissions

def convert_to_required_format(iam_policy, profile_name):
    user_permissions_dict = {}

    bindings = iam_policy.get("bindings", [])
    for binding in bindings:
        role = binding.get("role").replace("roles/", "")
        members = binding.get("members", [])

        for member in members:
            user_type, email = extract_user_info(member)
            permission = f"{role}"

            user_data = {
                "user_type": user_type,
                "profile": profile_name,
                "metadata": {},  # You can add interesting metadata here
                "email": email,
                "permissions": [permission],
                "module": "gcp"
            }

            if email in user_permissions_dict:
                user_permissions_dict[email]["permissions"].append(permission)
            else:
                user_permissions_dict[email] = user_data

    return list(user_permissions_dict.values())

def extract_user_info(member):
    # Logic to extract user_type and email from the member string
    # Modify this based on the actual structure of the member string
    # For example, if the member is in the format "serviceAccount:email@example.com",
    # you can split it to get user_type and email.
    user_type, _, email = member.partition(":")
    # Truncate email to 10 characters
    truncated_email = email

    return user_type, truncated_email



def save_output(data, output_file):
    # Save the data to the specified output file
    with open(output_file, "w") as file:
        json.dump(data, file, indent=2)

    print(f"[bold green]Output saved to: {output_file}[/bold green]")
