##########################################

docker:

Don't forget to add .env to bot folder after instalation!

Also change RM_HOST, RM_PORT, RM_USER, RM_PASSWORD to your vm_to_monitor values

ansible:

In order to clone desired branch:

git clone -b docker --single-branch https://github.com/PDALlama/PDADevops.git

git clone -b tg_bot --single-branch https://github.com/PDALlama/PDADevops.git

git clone -b ansible --single-branch https://github.com/PDALlama/PDADevops.git

Also don't forget to change other inventory values to yours! 

.env file would be automatically compiled from inventory values

However, you should remember that project is targeted for 3 VMs, so RM and DB values are refering to same VM.

##########################################
