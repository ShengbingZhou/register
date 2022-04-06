dpkg-deb --build --root-owner-group register_0.0.1_1_amd64

install:
sudo apt install ./register_0.0.1_1_amd64.deb

remove:
sudo apt remove register
