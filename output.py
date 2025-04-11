import csv
import meraki

def export_public_ips_to_csv(file_path, network_devices, network_meta, dashboard):
    rows = []
    total_networks = len(network_devices)

    for idx, (network_id, devices) in enumerate(network_devices.items(), start=1):
        meta = network_meta.get(network_id, {})
        net_name = meta.get('name', 'Unknown Network')
        net_tags = ", ".join(meta.get('tags', [])) or "No Tags"
        net_url = meta.get('url', '')

        print(f"🔄 Processing network {idx} of {total_networks}: {net_name}")

        for device in devices:
            serial = device['serial']
            model = device.get('model', '')

            # Add uplink info
            for uplink in device.get('uplinks', []):
                interface = uplink.get('interface')
                public_ip = uplink.get('publicIp', 'N/A')
                private_ip = uplink.get('ip', 'N/A')
                status = uplink.get('status', '')
                rows.append([
                    net_name, network_id, net_tags, net_url,
                    serial, model, interface, "uplink",
                    public_ip, private_ip, '', status
                ])

        # Add One-to-Many NAT rules
        try:
            nat_rules = dashboard.appliance.getNetworkApplianceFirewallOneToManyNatRules(network_id)
            for rule in nat_rules.get('rules', []):
                rows.append([
                    net_name, network_id, net_tags, net_url,
                    '', '', rule.get('uplink', ''), 'one-to-many NAT',
                    rule.get('publicIp', ''), rule.get('localIp', ''), 
                    rule.get('name', ''), ''
                ])
        except meraki.APIError:
            print(f"  ⚠️ Failed to retrieve One-to-Many NAT rules for {net_name}")

        # Add One-to-One NAT rules
        try:
            one_to_one_rules = dashboard.appliance.getNetworkApplianceFirewallOneToOneNatRules(network_id)
            for rule in one_to_one_rules.get('rules', []):
                rows.append([
                    net_name, network_id, net_tags, net_url,
                    '', '', rule.get('uplink', ''), 'one-to-one NAT',
                    rule.get('publicIp', ''), rule.get('privateIp', ''), 
                    rule.get('name', ''), ''
                ])
        except meraki.APIError:
            print(f"  ⚠️ Failed to retrieve One-to-One NAT rules for {net_name}")

    # Write to CSV
    with open(file_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Network Name', 'Network ID', 'Tags', 'Dashboard URL',
            'Serial', 'Model', 'Interface/Uplink', 'Type',
            'Public IP', 'Private IP', 'Rule Name', 'Status'
        ])
        writer.writerows(rows)

    print(f"\n✅ Done! CSV exported to: {file_path}")



