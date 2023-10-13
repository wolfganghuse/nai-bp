sudo sed -i "/#\$nrconf{restart} = 'i';/s/.*/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf
sudo apt-get -q update
sudo apt -q install openjdk-17-jdk python3-pip -y
curl -fSsl -O https://us.download.nvidia.com/tesla/@@{NVIDIA_DRIVER_VERSION}@@/NVIDIA-Linux-x86_64-@@{NVIDIA_DRIVER_VERSION}@@.run
sudo sh NVIDIA-Linux-x86_64-@@{NVIDIA_DRIVER_VERSION}@@.run -s
sudo apt -q install openmpi-bin -y
sudo apt -q install nfs-common -y
sudo mkdir -p /mnt/llm
sudo echo "@@{NFS_PATH}@@ /mnt/llm nfs nconnect=3 0 1" | sudo tee -a /etc/fstab
sudo mount -av
sudo mount /mnt/llm