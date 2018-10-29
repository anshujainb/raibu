run:
	sudo docker run -d -p 5000:5000 --name provisioner raibu/provisioner
build:
	sudo docker build -t raibu/provisioner .
logs:
	sudo docker logs -f provisioner
clean:
	sudo docker stop provisioner
	sudo docker rm provisioner
