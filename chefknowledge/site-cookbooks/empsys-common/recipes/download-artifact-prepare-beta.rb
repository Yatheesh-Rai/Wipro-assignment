#
# Cookbook Name:: empsys-common
# Recipe:: download-artifact-prepare
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#


data_bag_name       = node['empsys-common']['data_bags']['bag_name']
data_bag_item_names = node['empsys-common']['data_bags']['items']
app_user_name       = node['empsys-common']['app_user']
app_dir             = node['empsys-common']['app_dir']



data_bag_item_names.each do |data_bag_item_name|
  deployable_data = data_bag_item("#{data_bag_name}", "#{data_bag_item_name}")
  directory_name  = deployable_data['deployment']['directory_name']
  deployment_dir = "#{app_dir}/" + deployable_data['deployment']['directory_name']

  log 'deployment_dir' do
    level :warn
    message "deployment_dir = #{deployment_dir}"
  end

  log 'data_bag_item_name' do
    level :warn
    message "data_bag_item_name = #{data_bag_item_name}"
  end

  directory 'delete_app_dir' do
    path "#{deployment_dir}/application"
    recursive true

    action :delete
    only_if "ls #{deployment_dir}/application"
  end

  directory 'prepare_app_dir' do
    owner "#{app_user_name}"
    group "#{app_user_name}"
    mode '0750'
    action :create

    path "#{deployment_dir}"
  end


  file 'delete_target' do
    path "#{deployment_dir}/target.zip"

    action :delete
  end


  directory 'delete_target_dir' do
    path "#{deployment_dir}/target"
    recursive true

    action :delete
  end
end
