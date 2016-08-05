#
# Cookbook Name:: empsys-common
# Recipe:: run-chef-client
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

APP_USER           = "#{node['empsys-common']['app_user']}"
CHEF_CLIENT_OPTION = "#{node['empsys-common']['chef-client']['options']['root']}"


bash 'run-chef-client' do
#  user "#{APP_USER}"
  user "root"

  code <<-EOH
  chef-client "#{CHEF_CLIENT_OPTION}"
  EOH

  only_if 'ps ax | grep -v grep | grep chef-client'
end

