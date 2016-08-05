#
# Cookbook Name:: empsys-common
# Recipe:: download_artifact
#
# Copyright 2016, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

deployable_dir = "#{node['empsys-common']["app_dir"]}/#{node['empsys-common']['jenkins']['artifact_name']}"
jenkins_url    = "#{node['empsys-common']['jenkins']['job_url']}"
jenkins_build  = "#{node['empsys-common']['jenkins']['build']}"
artifact_name  = "#{node['empsys-common']['jenkins']['artifact_name']}"


remote_file "artifact_from_jenkins" do

  source "#{jenkins_url}/#{jenkins_build}/artifact/#{artifact_name}/target/\*zip\*/target.zip"
  path "#{deployable_dir}/target.zip"

  owner "#{node['empsys-common']["app_user"]}"
  group "#{node['empsys-common']["app_user"]}"
  mode '0644'

  backup 5
  use_conditional_get true

  action :create

  notifies :run, "bash[untar_artifact]", :immediately
end


bash 'untar_artifact' do
  user "#{node['empsys-common']["app_user"]}"
  cwd  "#{deployable_dir}"
  action :nothing

  code <<-EOH
  unzip target.zip
  tar zxvf target/#{artifact_name}-\*-devops-distrib.tar.gz
  tar zxvf target/#{artifact_name}-\*-devops-conf.tar.gz
  EOH

end

