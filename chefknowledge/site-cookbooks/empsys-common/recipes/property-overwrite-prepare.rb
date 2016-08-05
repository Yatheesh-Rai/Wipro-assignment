#
# Cookbook Name:: empsys-common
# Recipe:: property_overwrite
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

property_dir   = "#{node['empsys-common']["app_dir"]}/prop"



directory 'property_dir_cleanup' do
  action :delete
  recursive true
  path   "#{property_dir}"
end
