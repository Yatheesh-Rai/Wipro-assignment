#
# Cookbook Name:: k8s
# Recipe:: k8s-node
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

API_SERVER  = node['k8s']['api_server']
ETCD_SERVER = node['k8s']['etcd_server']


template 'k8s-node.service' do
  mode "0644"
  owner "root"
  source "k8s-node.service.erb"
  path "/usr/lib/systemd/system/k8s-node.service"

  variables ({
        :ETCD_SERVER => "#{ETCD_SERVER}",
        :API_SERVER  => "#{API_SERVER}"
  })
end


template 'k8s-proxy.service' do
  mode "0644"
  owner "root"
  source "k8s-proxy.service.erb"
  path "/usr/lib/systemd/system/k8s-proxy.service"

  variables ({
        :API_SERVER  => "#{API_SERVER}"
  })
end


service 'k8s-node' do
  action [:enable, :start]
end


service 'k8s-proxy' do
  action [:enable, :start]
end
