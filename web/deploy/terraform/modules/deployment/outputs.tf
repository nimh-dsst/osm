output "vpc_id" {
  value = module.shared_resources.vpc_id
}

output "internet_gateway_id" {
  value = module.shared_resources.internet_gateway_id
}

output "route_table_id" {
  value = module.shared_resources.route_table_id
}

output "network_acl_id" {
  value = module.shared_resources.aws_network_acl_id
}

output "security_group_id" {
  value = module.shared_resources.security_group_id
}

output "subnet_id" {
  value = module.shared_resources.subnet_id
}

output "instance_id" {
  value = aws_instance.staging.id
}

output "public_dns" {
  value = aws_eip.staging.public_dns
}

output "public_ip" {
  value = aws_eip.staging.public_ip
}
