Vagrant.configure(2) do |config|
    config.vm.box = "bento/centos-7.3"
    config.ssh.insert_key = false
    config.vm.provider "virtualbox" do |vb|
        vb.memory = "2048"
        vb.cpus = 2
    end
    config.vm.define "dev_logs_kafka_01" do |dev_logs_kafka_01|
       dev_logs_kafka_01.vm.network "private_network", ip: "192.168.37.10"
       dev_logs_kafka_01.vm.provision "ansible" do |ansible|
           ansible.playbook = "db_kafka.yml"
           ansible.inventory_path= "develop"
           ansible.limit = 'all'
       end
    end
end
