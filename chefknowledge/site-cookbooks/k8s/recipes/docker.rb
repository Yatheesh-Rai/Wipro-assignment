#
# Cookbook Name:: k8s
# Recipe:: default
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

template 'docker.service' do
  mode "0644"
  owner "root"
  source "docker.service.erb"
  path "/usr/lib/systemd/system/docker.service"
end


service 'docker' do
  action [:enable, :start]
end
