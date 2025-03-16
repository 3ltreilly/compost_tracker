python manage.py loaddata up_load/data_to_django.json

handy website for django
https://ccbv.co.uk


# Docker Terminology

# In the last section, we used a lot of Docker-specific jargon which might be confusing to some. So before we go further, let me clarify some terminology that is used frequently in the Docker ecosystem.

# Images - The blueprints of our application which form the basis of containers. 
#     In the demo above, we used the docker pull command to download the busybox image.
# Containers - Created from Docker images and run the actual application. 
#     We create a container using docker run which we did using the busybox image that we downloaded. 
#     A list of running containers can be seen using the docker ps command.
# Docker Daemon - The background service running on the host that manages building, running and distributing Docker containers. 
#     The daemon is the process that runs in the operating system which clients talk to.
# Docker Client - The command line tool that allows the user to interact with the daemon. 
#     More generally, there can be other forms of clients too - such as Kitematic which provide a GUI to the users.
# Docker Hub - A registry of Docker images. You can think of the registry as a directory of all available Docker images. 
#     If required, one can host their own Docker registries and can use them for pulling images.

# list running containers
docker ps
# list previously run containers
docker ps -a
# delete all exited containers
docker rm $(docker ps -a -q -f status=exited)
# In later versions of Docker, the docker container prune command can be used to achieve the same effect.
docker container prune

# build for diskstation
docker build --no-cache --platform linux/amd64 -t 3ltreilly/compost_tracker .

# push
docker push 3ltreilly/compost_tracker

# ssh into milhouse
ssh 3ltreilly@milhouse.local
# docker commands on milhouse
# to update to latest image on docker hub
docker pull 3ltreilly/compost_tracker
docker stop compost_tracker
docker rm compost_tracker
docker run --network host \
-v /volume1/docker/compost_tracker/db:/app/db \
--name compost_tracker 3ltreilly/compost_tracker
