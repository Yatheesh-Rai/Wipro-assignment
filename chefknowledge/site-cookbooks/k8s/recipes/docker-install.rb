#
# Cookbook Name:: k8s
# Recipe:: default
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

RPM_SERVER = node['k8s']['rpm_server']

%w{ docker-engine-selinux-1.9.1-1.el7.noarch.rpm docker-engine-1.9.1-1.el7.x86_64.rpm }.each do |pkg|
        remote_file pkg do
          source "#{RPM_SERVER}/#{pkg}"
          owner 'root'
          mode '0644'
          action :create
          path "/tmp/#{pkg}"

          not_if "which docker"
        end


        package pkg do
          source "/tmp/#{pkg}"
          action :install

          not_if "which docker"
        end
end


group "docker" do
  action :modify
  append true
  members ['empsysd', 'e0488309']
end
