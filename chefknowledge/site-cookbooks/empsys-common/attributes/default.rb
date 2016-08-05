#
# user and home directory settings
#
default['empsys-common']['app_user'] = "empsysd"
default['empsys-common']['app_home'] = "/ngs/app/#{node['empsys-common']['app_user']}"
default['empsys-common']['app_dir']  = "#{node['empsys-common']['app_home']}/softwares/es_apps/applications"


#
# Java Package settings
#
default['empsys-common']['java_version'] = "jdk64-1.8.0_91"
default['empsys-common']['java_package'] = "#{node['empsys-common']['java_version']}.x86_64"


#
# Jenkins and artifact settings
#
# [important]
# each Node must overwrite these variable in node file
#
default['empsys-common']['jenkins']['job_url']       = "http://rn2-empsysd-lapp145.rno.apple.com:8080/jenkins"
default['empsys-common']['jenkins']['build']         = "lastStableBuild"
default['empsys-common']['jenkins']['artifact_name'] = "update_me"


#
# Property file settings
#
default['empsys-common']['property']['git_url']    = "https://gitlab.corp.apple.com/cisuperuser_systemaccount/empsys-propertes.git"
default['empsys-common']['property']['git_branch'] = "master"
default['empsys-common']['property']['env']        = "dev-int"


#
# Patch setting
# 
# snap should be YYYY.MM.DD such as 2016.7.3 or "Current"
#
default['empsys-common']['patch']['snap']        = "2016.7.3"


#
# Chef client setting
#
default['empsys-common']['chef-client']['options']['root'] = "-d -i 300"
default['empsys-common']['chef-client']['options']['non_root'] = "-c .chef/client.rb -d -i 300"
