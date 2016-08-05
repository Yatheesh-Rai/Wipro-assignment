#
# Cookbook Name:: empsys-common
# Recipe:: property_overwrite
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

property_dir   = "#{node['empsys-common']["app_dir"]}/prop"
deployable_dir = "#{node['empsys-common']["app_dir"]}/#{node['empsys-common']['jenkins']['artifact_name']}"
env            = "#{node['empsys-common']['property']['env']}"
property_name  = "#{node['empsys-common']['property']['property_name']}"
artifact_name  = "#{node['empsys-common']['jenkins']['artifact_name']}"



git "pull_property" do
  repository "#{node['empsys-common']['property']['git_url']}"
  revision "#{node['empsys-common']['property']['git_branch']}"
  destination "#{property_dir}"
  action :sync

  notifies :run, "bash[property_overwrite]", :immediately
end


bash 'property_overwrite' do
  user "#{node['empsys-common']["app_user"]}"
  cwd  "#{property_dir}/#{env}"
  action :nothing

  code <<-EOH
if [ -d #{artifact_name} ]; then
	cd #{artifact_name}
	tar cvf - . | (cd "#{deployable_dir}"; tar xvf -)
	cd .. 
else
	echo "no property directory in git, skip"
fi
  EOH
end
