#
# Cookbook Name:: empsys-common
# Recipe:: default
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#


package "git" do
  action :install
end

directory "/ngs/app/#{node['empsys-common']['app_user']}/softwares" do
  owner "#{node['empsys-common']['app_user']}"
  group "#{node['empsys-common']['app_user']}"
  mode '0750'
  action :create
  recursive true

  notifies :create, "directory[/ngs/app/#{node['empsys-common']['app_user']}/softwares/es_apps]", :immediately
end

directory "/ngs/app/#{node['empsys-common']['app_user']}/softwares/es_apps" do
  owner "#{node['empsys-common']['app_user']}"
  group "#{node['empsys-common']['app_user']}"
  mode '0750'
  action :create

  notifies :create, "directory[/ngs/app/#{node['empsys-common']['app_user']}/softwares/es_apps/applications]", :immediately
end

directory "/ngs/app/#{node['empsys-common']['app_user']}/softwares/es_apps/applications" do
  owner "#{node['empsys-common']['app_user']}"
  group "#{node['empsys-common']['app_user']}"
  mode '0750'
  action :create
end

