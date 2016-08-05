#
# Cookbook Name:: empsys-common
# Recipe:: download_artifact
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

  jenkins_url     = deployable_data['jenkins']['job_url']
  jenkins_build   = deployable_data['jenkins']['build']
  artifact_name   = deployable_data['jenkins']['artifact_name']

  deployment_dir = "#{app_dir}/" + deployable_data['deployment']['directory_name']


  log 'deployment_dir' do
    level :warn
    message "deployment_dir = #{app_dir}/" + deployable_data['deployment']['directory_name']
  end

  log 'data_bag_item_name' do
    level :warn
    message "data_bag_item_name = #{data_bag_item_name}"
  end


  remote_file "artifact_from_jenkins_#{data_bag_item_name}" do

    source "#{jenkins_url}/#{jenkins_build}/artifact/#{artifact_name}/target/\*zip\*/target.zip"
    path   "#{app_dir}/" + deployable_data['deployment']['directory_name'] + '/target.zip'

    owner #{app_user_name}
    group #{app_user_name}
    mode '0644'

    backup 5
    use_conditional_get true

    action :create

    notifies :run, "bash[untar_artifact_#{data_bag_item_name}]", :immediately
  end


  bash "untar_artifact_#{data_bag_item_name}" do

    user "#{app_user_name}"
    cwd  "#{app_dir}/" + deployable_data['deployment']['directory_name']
    action :nothing

    code <<-EOH
    unzip target.zip
    tar zxvf target/#{artifact_name}-\*-devops-distrib.tar.gz
    tar zxvf target/#{artifact_name}-\*-devops-conf.tar.gz
    EOH

  end
end

