#
# Cookbook Name:: empsys-common
# Recipe:: push-jobs-prepare
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

%w{artifactory-2.3.3.gem mixlib-versioning-1.1.0.gem mixlib-install-1.1.0.gem}.each do |pkg|
	remote_file pkg do
	  source "http://ci-server-1.rno.apple.com/#{pkg}"
	  owner 'root'
	  mode '0644'
	  action :create
	  path "/tmp/#{pkg}"
	end


	gem_package pkg do
	  action :install
	  source "/tmp/#{pkg}"
	  gem_binary '/opt/chef/embedded/bin/gem'
	end

end


%w{ runit-2.1.2-1.el6.x86_64.rpm }.each do |pkg|
	remote_file pkg do
	  source "http://ci-server-1.rno.apple.com/#{pkg}"
	  owner 'root'
	  mode '0644'
	  action :create
	  path "/tmp/#{pkg}"
	end


	package pkg do
	  source "/tmp/#{pkg}"
	  action :install
	end
end
