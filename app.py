import meraki
import sys
import os
from collections import defaultdict
from output import export_public_ips_to_csv
from meraki.exceptions import APIError
from getpass import getpass

def get_app_root_dir():
    """Returns the directory the script or .exe is running from."""
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller executable
        return os.path.dirname(sys.executable)
    else:
        # Running from source
        return os.path.dirname(os.path.abspath(__file__))

def get_valid_dashboard_api():
    """Prompt user for API key if not found or invalid, and return a valid DashboardAPI instance."""
    while True:
        api_key = os.getenv('MERAKI_DASHBOARD_API_KEY')
        if not api_key:
            print("🔐 Meraki API key not found in environment.")
            api_key = getpass("Please enter your Meraki Dashboard API key (input is hidden): ").strip()

        try:
            dashboard = meraki.DashboardAPI(api_key=api_key, suppress_logging=True)
            # Test the key with a simple call
            dashboard.organizations.getOrganizations()
            return dashboard  # If successful, return the instance
        except APIError as e:
            if e.status == 401:
                print("❌ Invalid API key. Please try again.")
                os.environ.pop('MERAKI_DASHBOARD_API_KEY', None)  # Clear env to retry
            else:
                print(f"❌ API error: {e}")
                exit(1)

def select_organization(dashboard):
    orgs = dashboard.organizations.getOrganizations()

    if not orgs:
        print("❌ No organizations found.")
        exit(1)
    elif len(orgs) == 1:
        org = orgs[0]
        print(f"✅ One organization found: {org['name']} ({org['id']})")
        return org['id']
    else:
        print("📋 Select an organization:")
        for idx, org in enumerate(orgs, start=1):
            print(f"{idx}. {org['name']} ({org['id']})")
        
        while True:
            try:
                choice = int(input("\nEnter the number of the organization to use: "))
                if 1 <= choice <= len(orgs):
                    selected_org = orgs[choice - 1]
                    print(f"✅ Selected: {selected_org['name']} ({selected_org['id']})")
                    return selected_org['id']
                else:
                    print("⚠️ Invalid selection. Try again.")
            except ValueError:
                print("⚠️ Please enter a valid number.")

def main():
    # Make folder if doesnt exist
    app_root = get_app_root_dir()
    reports_dir = os.path.join(app_root, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    csv_path = os.path.join(reports_dir, 'public_ips_report.csv')

    dashboard = get_valid_dashboard_api()

    org_id = select_organization(dashboard)

    # Get all networks in the organization
    networks = dashboard.organizations.getOrganizationNetworks(org_id)

    # Build a map of network_id -> metadata
    network_meta = {
        net['id']: {
            'name': net.get('name', ''),
            'tags': net.get('tags', []),
            'url': net.get('url', ''),
        }
        for net in networks
    }

    # Get all uplink statuses
    data = dashboard.organizations.getOrganizationUplinksStatuses(org_id)

    # Group devices by networkId
    network_devices = defaultdict(list)
    for device in data:
        network_id = device['networkId']
        network_devices[network_id].append(device)

    export_public_ips_to_csv(csv_path, network_devices, network_meta, dashboard)

if __name__ == '__main__':
    main()
