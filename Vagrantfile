Vagrant.configure("2") do |config|

  # Ubuntu VM
  config.vm.define "ubuntu" do |ubuntu|
    ubuntu.vm.box = "bento/ubuntu-22.04"
    ubuntu.vm.hostname = "ig-ubuntu"
    ubuntu.vm.network "private_network", ip: "192.168.56.11"

    ubuntu.vm.provider "virtualbox" do |vb|
      vb.name = "InfraGuardian-Ubuntu"
      vb.memory = 2048
      vb.cpus = 2
    end
  end

  # Rocky Linux VM
  config.vm.define "rocky" do |rocky|
    rocky.vm.box = "bento/rockylinux-9"
    rocky.vm.hostname = "ig-rocky"
    rocky.vm.network "private_network", ip: "192.168.56.12"

    rocky.vm.provider "virtualbox" do |vb|
      vb.name = "InfraGuardian-Rocky"
      vb.memory = 2048
      vb.cpus = 2
    end
  end

  # AlmaLinux VM
  config.vm.define "alma" do |alma|
    alma.vm.box = "bento/almalinux-9"
    alma.vm.hostname = "ig-alma"
    alma.vm.network "private_network", ip: "192.168.56.13"

    alma.vm.provider "virtualbox" do |vb|
      vb.name = "InfraGuardian-Alma"
      vb.memory = 2048
      vb.cpus = 2
    end
  end

end