#
# Cookbook Name:: empsys-common
# Recipe:: download-artifact-prepare
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

deployable_dir = "#{node['empsys-common']["app_dir"]}/#{node['empsys-common']['jenkins']['artifact_name']}"


directory 'prepare_app_dir' do
  owner "#{node['empsys-common']["app_user"]}"
  group "#{node['empsys-common']["app_user"]}"
  mode '0750'
  action :create

  path "#{deployable_dir}"
end


file 'delete_target' do
  path "#{deployable_dir}/target.zip"

  action :delete
end


directory 'delete_target_dir' do
  path "#{deployable_dir}/target"
  recursive true

  action :delete
end
