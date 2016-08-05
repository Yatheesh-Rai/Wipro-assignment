#
# Cookbook Name:: k8s
# Recipe:: k8s-install
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

RPM_SERVER  = node['k8s']['rpm_server']
KUBE_PKG    = 'kubernetes-server-linux-amd64.tar.gz'


remote_file "#{KUBE_PKG}" do
  source "#{RPM_SERVER}/#{KUBE_PKG}"
  owner 'root'
  mode '0644'
  action :create
  path "/ngs/app/#{KUBE_PKG}"

  not_if "which hyperkube"

  notifies :run, 'bash[untar]', :immediately
end


bash 'untar' do
  action :nothing

  user "root"
  cwd  "/ngs/app"
  action :nothing

  code <<-EOH
      tar zxvf #{KUBE_PKG}
      pushd .
      cd kubernetes
      cp server/bin/* /usr/local/bin
      cd addons
      docker load -i gcr.io~google_containers~pause\:2.0.tar 
      popd

      rm -rf kubernetes
      rm -f #{KUBE_PKG}
  EOH
end
