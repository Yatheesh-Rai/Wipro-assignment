#
# Cookbook Name:: empsys-common
# Recipe:: property_overwrite
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
  deployment_dir = "#{app_dir}/#{directory_name}"

  property_name  = deployable_data['deployment']['property_name']
  property_dir   = "#{deployment_dir}/prop"


  log 'deployment_dir' do
    level :warn
    message "deployment_dir = #{deployment_dir}"
  end

  log 'data_bag_item_name' do
    level :warn
    message "data_bag_item_name = #{data_bag_item_name}"
  end

  directory "property_dir_cleanup_#{data_bag_item_name}" do
    action :delete
    recursive true
    path   "#{property_dir}"
  end

end
