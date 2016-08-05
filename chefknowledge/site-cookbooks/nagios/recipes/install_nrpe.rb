#
# Cookbook Name:: nagios
# Recipe:: configure_nrpe
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

APP_USER_NAME  = node['nagios']['app_user_name']
APP_USER_DIR   = "/ngs/app/#{APP_USER_NAME}"
NAGIOS_DIR     = "#{APP_USER_DIR}/nagios"


NRPE_PKG    = "nrpe-empsysd.tar"
RPM_SERVER  = node['nagios']['nrpe_pkg_server']


remote_file 'download' do
  source "#{RPM_SERVER}/#{NRPE_PKG}"
  owner  "#{APP_USER_NAME}"
  mode '0644'
  action :create
  path "#{APP_USER_DIR}/#{NRPE_PKG}"

  not_if do ::Dir.exist? "#{NAGIOS_DIR}" end

  notifies :run, 'bash[untar]', :immediately
end


bash 'untar' do
  user   #{APP_USER_NAME}
  cwd    #{APP_USER_DIR}
  action :nothing

  code <<-EOH
      cd "#{APP_USER_DIR}"
      tar xvf "#{NRPE_PKG}"
      rm -f "#{NRPE_PKG}"
  EOH
end
