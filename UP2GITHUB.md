## Basic Git Command
* sudo apt install git
* cd ~/.ssh
* ls | grep pub

* ssh-keygen -t rsa -C "1909992592@qq.com"
* cat *.pub

* git clone https://github.com/zyl-mwy/NIR_system_formal.git
* git init
* git pull

* git add .

* git config --global user.email "1909992592@qq.com"
* git config --global user.name "zyl-mwy"
* git commit -m "xxx"

* git remote add origin git@github.com:zyl-mwy/NIR_system_formal.git
* git remote set-url origin git@github.com:zyl-mwy/NIR_system_formal.git
* git remote set-url origin https://github.com/zyl-mwy/NIR_system_formal.git

* git push -u origin main
* git push
### solve big file
* git rev-list --objects --all | grep "host_computer/build/log/result.csv"
  
* sudo apt install git-filter-repo
* git filter-repo --force --path host_computer/build/log/result.csv --invert-paths

* echo "host_computer/build/" >> .gitignore
* git add .gitignore
* git commit -m "chore: ignore build artifacts"

* git push origin main --force
### git push fail
* git remote -v

* git remote add origin git@github.com:zyl-mwy/NIR_system_formal.git
* git remote -v
* git push -u origin main --force
