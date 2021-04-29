Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.network "forwarded_port", guest: 5432, host: 5431
  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.provision "ansible" do |ansible|
      ansible.verbose = "v"
      ansible.playbook = "ansible-nginx-uwsgi/nginx-uwsgi.yml"
  end
  config.vm.provision "ansible" do |ansible|
      ansible.verbose = "v"
      ansible.playbook = "postgres.yml"
  end
end
