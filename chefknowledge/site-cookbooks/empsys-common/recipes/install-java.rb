#
# Cookbook Name:: empsys-common
# Recipe:: install-java
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#



package "#{node['empsys-common']['java_package']}" do
  action :install
  notifies :create, 'template[dot_profile]', :immediately
end


template 'dot_profile' do
  action :create

  mode "0755"
  owner "#{node['empsys-common']['app_user']}"
  path  "#{node['empsys-common']['app_home']}/.profile"

  source "dot_profile.erb"
  variables :jdk_version => "#{node['empsys-common']['java_version']}"
end
