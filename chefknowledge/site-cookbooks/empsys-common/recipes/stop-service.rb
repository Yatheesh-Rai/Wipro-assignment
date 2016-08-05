#
# Cookbook Name:: empsys-common
# Recipe:: stop-service
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#


data_bag_name       = node['empsys-common']['data_bags']['bag_name']
data_bag_item_names = node['empsys-common']['data_bags']['items']
app_user_name       = node['empsys-common']['app_user']
app_dir             = node['empsys-common']['app_dir']



data_bag_item_names.each do |data_bag_item_name|
  deployable_data = data_bag_item("#{data_bag_name}", "#{data_bag_item_name}")
  deployment_dir  = "#{app_dir}/" + deployable_data['deployment']['directory_name']


  bash 'stop_service' do
    user "#{app_user_name}"
    cwd  "#{deployment_dir}"
    action :run

    code <<-EOH
if [ -f #{deployment_dir}/bin/shutdown.sh ]; then
	#{deployment_dir}/bin/shutdown.sh || echo "fail to shutdown"
else
	echo "no shutdown script, skip"
fi
    EOH
  end

end
