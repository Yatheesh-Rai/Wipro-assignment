#
# Cookbook Name:: k8s
# Recipe:: flanneld-install
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#


FLANNEL_VER = "flannel-0.5.5"
FLANNEL_PKG = "#{FLANNEL_VER}-linux-amd64.tar"
RPM_SERVER  = node['k8s']['rpm_server']


remote_file 'install' do
  source "#{RPM_SERVER}/#{FLANNEL_PKG}"
  owner 'root'
  mode '0644'
  action :create
  path "/tmp/#{FLANNEL_PKG}"

  not_if do ::File.exists?('/usr/local/bin/flanneld') end

  notifies :run, 'bash[untar]', :immediately
end


bash 'untar' do
  user "root"
  cwd  "/tmp"
  action :nothing

  code <<-EOH
      pushd .
      tar xvf #{FLANNEL_PKG}
      cd #{FLANNEL_VER}
      cp flanneld /usr/local/bin
      chmod 755 /usr/local/bin/flanneld
      popd

      rm -rf #{FLANNEL_VER}
      rm -f #{FLANNEL_PKG}
  EOH
end
