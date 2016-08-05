#
# Cookbook Name:: nagios
# Recipe:: generate_config
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

NAGIOS_CFG_DIR = "/ngs/app/k8s-store"


%w{devops dev dev-int lt it}.each do |p|
    SERVERS = search("node", "chef_environment:#{p}")

    template "server-cfg-#{p}" do
      source "servers.cfg.erb"
      path   "#{NAGIOS_CFG_DIR}/nagios-#{p}/etc/servers/servers.cfg"
      variables ({
	:servers => SERVERS.uniq.sort,
	:host_group => "#{p}",
	:service_group => "all"
      })
    end

    template "commands-cfg-#{p}" do
      source "commands.cfg.erb"
      path   "#{NAGIOS_CFG_DIR}/nagios-#{p}/etc/objects/commands.cfg"
    end

    template "template-cfg-#{p}" do
      source "templates.cfg.erb"
      path   "#{NAGIOS_CFG_DIR}/nagios-#{p}/etc/objects/templates.cfg"
    end

    template "contacts-cfg-#{p}" do
      source "contacts.cfg.erb"
      path   "#{NAGIOS_CFG_DIR}/nagios-#{p}/etc/objects/contacts.cfg"
    end



    template "server-cfg-#{p}-influxdb" do
      source "servers.cfg.erb"
      path   "#{NAGIOS_CFG_DIR}/nagios-#{p}-influxdb/etc/servers/servers.cfg"
      variables ({
	:servers => SERVERS.uniq.sort,
	:host_group => "influxdb",
	:service_group => "all"
      })
    end

    template "commands-cfg-#{p}-influxdb" do
      source "commands.cfg.erb"
      path   "#{NAGIOS_CFG_DIR}/nagios-#{p}-influxdb/etc/objects/commands.cfg"
    end

    template "template-cfg-#{p}-influxdb" do
      source "templates.cfg.erb"
      path   "#{NAGIOS_CFG_DIR}/nagios-#{p}-influxdb/etc/objects/templates.cfg"
    end

end
