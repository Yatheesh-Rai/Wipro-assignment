#
# Cookbook Name:: empsys-common
# Recipe:: patch
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
SNAP = "#{node['empsys-common']['patch']['snap']}"

bash 'update_me' do
  user 'root'
  cwd '/tmp'
  code <<-EOH
  CURRENT_SNAP=`rpm -q oel-config-yumrepo | cut -d '-' -f 5` 
  if [ "#{SNAP}.noarch" = "${CURRENT_SNAP}" ]; then
    touch /tmp/chef_update_me_skip
  else
    rm -f /tmp/chef_update_me_skip
    /ngs/global/bin/update_me -d #{SNAP} --batch --skip-reboot -w 1 --override-monsoon
  fi
  EOH
end
