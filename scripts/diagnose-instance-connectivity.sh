#!/bin/bash

mkdir instance-report
# Check IP Configuration
echo "### IP Configuration ###"
ip addr show > instance-report/ip-configuration.txt

# Check Default Gateway
echo "### Default Gateway ###"
ip route show > instance-report/default-gateway.txt

# Check DNS Configuration
echo "### DNS Configuration ###"
cat /etc/resolv.conf > instance-report/dns-configuration.txt

# Check Current Firewall Rules
echo "### Firewall Rules ###"
sudo iptables -L -v -n > instance-report/firewall-rules.txt

# Check Network Interface Statistics
echo "### Network Interface Statistics ###"
netstat -i > instance-report/network-interface-statistics.txt

# Check Active Network Connections
echo "### Active Network Connections ###"
netstat -tuln > instance-report/active-network-connections.txt

# Check Network Manager Status
echo "### Network Manager Status ###"
systemctl status systemd-networkd > instance-report/network-manager-status.txt

# Check Cloud-Init Status
echo "### Cloud-Init Status ###"
systemctl status cloud-init > instance-report/cloud-init-status.txt

# Check System Logs for Network-Related Issues
echo "### System Logs for Network-Related Issues (systemd-networkd) ###"
sudo journalctl -u systemd-networkd > instance-report/systemd-networkd-logs.txt

echo "### System Logs for Network-Related Issues (cloud-init) ###"
sudo journalctl -u cloud-init > instance-report/cloud-init-logs.txt

# Check if IPv6 is Disabled
echo "### IPv6 Disabled Status ###"
cat /etc/sysctl.conf | grep net.ipv6.conf.all.disable_ipv6 > instance-report/ipv6-disabled-status.txt
cat /etc/sysctl.conf | grep net.ipv6.conf.default.disable_ipv6 > instance-report/ipv6-default-disabled-status.txt

# Check HTTP Connectivity Directly
echo "### HTTP Connectivity Check ###"
curl -v http://us-east-1.ec2.archive.ubuntu.com/ubuntu/dists/focal-backports/InRelease > instance-report/apt-repository-curl.txt

# Check DNS Resolution for the Repository
echo "### DNS Resolution for the Repository ###"
host us-east-1.ec2.archive.ubuntu.com > instance-report/apt-repository-dns.txt
dig us-east-1.ec2.archive.ubuntu.com > instance-report/apt-repository-dig.txt
