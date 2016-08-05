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


template "nrpe-cfg" do
  source "nrpe.cfg.erb"
  path   "#{NAGIOS_DIR}/etc/nrpe.cfg"
  variables ({
	:nagios_dir    => "#{NAGIOS_DIR}",
	:app_user_name => "#{APP_USER_NAME}"
  })
end


template 'init-script' do
  mode   "0755"
  owner  #{APP_USER_NAME}
  source 'init-script.erb'
  path   "#{NAGIOS_DIR}/init-script"
  variables :nagios_dir => "#{NAGIOS_DIR}"
end


bash 'start-nrpe' do
  user #{APP_USER}
  cwd  #{NAGIOS_DIR}

  code <<-EOH
	cd "#{NAGIOS_DIR}"
	./init-script restart
  EOH
end
