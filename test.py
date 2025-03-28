import yaml
import boto3
from datetime import datetime, timedelta
import csv
import argparse
def update_inventory(csv_file, inventory_file):
    """
    Reads the inventory and CSV file, patches high-severity instances immediately,
    and schedules low-severity instances for patching in 2 days.
    """
    # Initialize the SSM client
    ssm_client = boto3.client('ssm', region_name='us-east-1')  # Replace with your region

    

    # Prepare a list to store instances with low severity
    low_severity_instances = []

    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        with open(inventory_file, 'r') as inv_file:
            inventory = yaml.safe_load(inv_file)

        for row in csv_reader:
            hostname = row['hostname']
            instance_id = row['instance_id']  # Read instance ID directly from the CSV
            os_type = row['os_type'].lower()
            ip_address = row['ip_address']
            severity = row['severity'].lower()
            owner_email = row['owner_email']

            host_entry = {'ansible_host': ip_address, 'owner_email': owner_email, 'severity': severity}

            if os_type == 'linux':
                inventory['all']['children']['linux']['hosts'][hostname] = host_entry
            elif os_type == 'windows':
                inventory['all']['children']['windows']['hosts'][hostname] = host_entry

            # Handle Severity
            if severity == 'high':
                print(f"Patching immediately for {hostname}")
                send_ssm_command(
                    ssm_client,
                    instance_id=instance_id,
                    os_type=os_type,
                    document_name="AWS-RunPatchBaseline",
                    operation="Install",
                    patch_baseline_id=custom_patch_baseline_id
                )
            elif severity == 'low':
                print(f"Saving instance {hostname} for patching in 2 days.")
                # Add instance details to the low severity list
                low_severity_instances.append({
                    'hostname': hostname,
                    'instance_id': instance_id,
                    'os_type': os_type,
                    'ip_address': ip_address,
                    'severity': severity,
                    'owner_email': owner_email,
                    'scheduled_date': (datetime.now() + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
                })

    # Save low severity instances to a CSV file
    if low_severity_instances:
        save_low_severity_instances(low_severity_instances)

    with open(inventory_file, 'w') as inv_file:
        yaml.safe_dump(inventory, inv_file)
    print("Inventory updated successfully!")

def send_ssm_command(ssm_client, instance_id=None, os_type=None, document_name=None, operation=None, patch_baseline_id=None):
    """
    Sends an SSM command to the specified instance using a custom patch baseline or default parameters.
    """
    try:
        # Prepare parameters for the AWS-RunPatchBaseline document
        Parameters = {
            'Operation': ['Install'],
            'RebootOption': ['RebootIfNeeded'],
        }

        

        # Send the SSM command
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunPatchBaseline',
            Parameters=Parameters
        )
        print(f"SSM command sent successfully to {instance_id}: {response['Command']['CommandId']}")
    except Exception as e:
        print(f"Failed to send SSM command to {instance_id}: {e}")

def save_low_severity_instances(instances):
    """
    Saves low severity instances to a CSV file for scheduling later.
    """
    output_file = 'scheduled_instances.csv'  # Save in the current working directory
    fieldnames = ['hostname', 'instance_id', 'os_type', 'ip_address', 'severity', 'owner_email', 'scheduled_date']

    try:
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(instances)
        print(f"Low severity instances saved to {output_file}")
    except Exception as e:
        print(f"Failed to save low severity instances: {e}")

def trigger_scheduled_patching(csv_file):
    """
    Reads the scheduled_instances.csv file and triggers patching for instances whose scheduled_date has passed.
    """
    ssm_client = boto3.client('ssm', region_name='us-east-1')
    updated_instances = []

    # Check if the file exists
    if not os.path.exists(csv_file):
        print(f"Scheduled patching file not found: {csv_file}. Creating an empty file.")
        # Create an empty file if it does not exist
        with open(csv_file, 'w', newline='') as file:
            fieldnames = ['hostname', 'instance_id', 'os_type', 'ip_address', 'severity', 'owner_email', 'scheduled_date']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
        return  # Exit the function since there are no instances to process

    try:
        with open(csv_file, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                scheduled_date = datetime.strptime(row['scheduled_date'], '%Y-%m-%d %H:%M:%S')
                if datetime.now() >= scheduled_date:
                    print(f"Patching instance {row['hostname']} as per schedule.")
                    send_ssm_command(
                        ssm_client,
                        instance_id=row['instance_id'],
                        os_type=row['os_type'],
                        document_name="AWS-RunPatchBaseline",
                        operation="Install"
                    )
                else:
                    # Keep instances that are not yet due for patching
                    updated_instances.append(row)

        # Update the CSV file with remaining instances
        with open(csv_file, 'w', newline='') as file:
            fieldnames = ['hostname', 'instance_id', 'os_type', 'ip_address', 'severity', 'owner_email', 'scheduled_date']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_instances)

    except Exception as e:
        print(f"Error processing scheduled patching: {e}")
if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="SSM Patching Script")
    parser.add_argument("--csv", required=True, help="Path to the instances CSV file")
    parser.add_argument("--inventory", required=True, help="Path to the inventory YAML file")
    parser.add_argument("--scheduled_csv", required=True, help="Path to the scheduled instances CSV file")
    args = parser.parse_args()

    # Update inventory and handle immediate and low-severity patching
    update_inventory(args.csv, args.inventory)

    # Trigger scheduled patching for low-severity instances
    trigger_scheduled_patching(args.scheduled_csv)
