# 1. Describe the instance to get details including VPC and Subnet
aws ec2 describe-instances --instance-ids i-03b729b63c679cf2d --query "Reservations[*].Instances[*].{InstanceId:InstanceId, VpcId:VpcId, SubnetId:SubnetId, PublicIpAddress:PublicIpAddress, PublicDnsName:PublicDnsName, PrivateIpAddress:PrivateIpAddress, State:State.Name, SecurityGroups:SecurityGroups, NetworkInterfaces:NetworkInterfaces}" > instance_details.json

# Extract VPC ID and Subnet ID from the instance details
VPC_ID=$(jq -r '.[0][0].VpcId' instance_details.json)
SUBNET_ID=$(jq -r '.[0][0].SubnetId' instance_details.json)

# 2. Describe the VPC to get more details
aws ec2 describe-vpcs --vpc-ids $VPC_ID --query "Vpcs[*].{VpcId:VpcId, CidrBlock:CidrBlock, DhcpOptionsId:DhcpOptionsId, State:State}" > vpc_details.json

# 3. Describe the subnet to get more details
aws ec2 describe-subnets --subnet-ids $SUBNET_ID --query "Subnets[*].{SubnetId:SubnetId, VpcId:VpcId, CidrBlock:CidrBlock, MapPublicIpOnLaunch:MapPublicIpOnLaunch, AvailabilityZone:AvailabilityZone, State:State, RouteTableAssociationId:RouteTableAssociationId}" > subnet_details.json

# Extract Route Table Association ID from the subnet details
ROUTE_TABLE_ASSOC_ID=$(jq -r '.[0].RouteTableAssociationId' subnet_details.json)

# 4. Describe the route table associated with the subnet
aws ec2 describe-route-tables --filters "Name=association.route-table-association-id,Values=$ROUTE_TABLE_ASSOC_ID" --query "RouteTables[*].{RouteTableId:RouteTableId, VpcId:VpcId, Routes:Routes, Associations:Associations, Tags:Tags}" > route_table_details.json

# 5. Describe the Internet Gateway
aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$VPC_ID" --query "InternetGateways[*].{InternetGatewayId:InternetGatewayId, Attachments:Attachments, Tags:Tags}" > internet_gateway_details.json

# 6. Describe DHCP Options associated with the VPC
aws ec2 describe-dhcp-options --dhcp-options-ids $(jq -r '.[0].DhcpOptionsId' vpc_details.json) --query "DhcpOptions[*].{DhcpOptionsId:DhcpOptionsId, DhcpConfigurations:DhcpConfigurations}" > dhcp_options_details.json

# 7. List all security groups associated with the instance
SECURITY_GROUP_IDS=$(jq -r '.[0][0].SecurityGroups[].GroupId' instance_details.json)
aws ec2 describe-security-groups --group-ids $SECURITY_GROUP_IDS --query "SecurityGroups[*].{GroupId:GroupId, GroupName:GroupName, VpcId:VpcId, Description:Description, IpPermissions:IpPermissions, IpPermissionsEgress:IpPermissionsEgress}" > security_groups_details.json

# Bundle all JSON files into a single file for sharing etc.
tar -czvf aws_details.tar.gz instance_details.json vpc_details.json subnet_details.json route_table_details.json internet_gateway_details.json dhcp_options_details.json security_groups_details.json

# Clean up individual files (optional)
rm instance_details.json vpc_details.json subnet_details.json route_table_details.json internet_gateway_details.json dhcp_options_details.json security_groups_details.json
