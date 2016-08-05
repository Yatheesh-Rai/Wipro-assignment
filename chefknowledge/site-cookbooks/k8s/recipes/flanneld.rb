#
# Cookbook Name:: k8s
# Recipe:: flanneld
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#


ETCD_SERVER = node['k8s']['etcd_server']


template 'flanneld.service' do
  mode "0644"
  owner "root"
  source "flanneld.service.erb"
  path "/usr/lib/systemd/system/flanneld.service"
  action :create

  variables ({
	:ETCD_SERVER => "#{ETCD_SERVER}"
  })

end


service 'flanneld' do
   action [:enable, :start]
end
