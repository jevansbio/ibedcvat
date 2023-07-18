### 18-07-2023
- Features implemented
    - Modified compose settings to run containers on podman
    - modified cvat_server
        - Modified authentication - requires email confirmation and then manual activation by admins.
            - Included migration to automatically set site name/domain
        - Implemented per-organisation data limits.
            - Modified organization model to include GB_limit
            - Added model methods to  organization, task, project to calculate the filesize of the data models attached.
            - Modified task data POST to prevent users creating tasks/projects in their personal workspace.
            - Modified task data POST to check if the uploaded files would push the organization over their GB_limit

### Requirements (summarised from Berend's old readme included below). 
- Download latest podman-compose (Develop) Stable = 1.0.3 and develop is 1.0.4
- Set podman storage
    - mkdir ~/.config/containers
    - create ~/.config/containers/storage.conf
    - edit default config file and set storage location
      ```
         runroot = "/data/podman_storage/runroot"
         graphroot = "/data/podman_storage/graphroot"
      ```
- export environmental variables for CVAT_HOST, CVAT_EMAIL and CVAT_EMAIL_PASSWORD
- Create podman socket (location currently hard coded in our compose file)
- Start podman socket - set to run indefinitey and not block
  
  ```podman system service --time=0 unix:///data/podman.sock &```
- Build latest version of cvat_server container.
- Service should now be able to run.      
  

## Old readme
- Full working on Ubuntu 22.04 with Podman written on 17-03-2023
  - download CVAT
  - download latest podman-compose (Develop) Stable = 1.0.3 and develop is 1.0.4
    - Problem description
      - https://github.com/containers/podman-compose/issues/88
    - Solution
      - pip3 install --user https://github.com/containers/podman-compose/archive/devel.tar.gz
  - edit docker-compose.yml
    - edit dockerhub searches. unqualified search registries. Resolve by appending 'docker.io/' before the actual image name
      - i.e.
        - alpine:14 -> docker.io/alpine:14
    - edit docker socket for podman socket and disable security on traefik
      - security_opt:
        - 'label=disable'
      - volumes:
        - $XDG_RUNTIME_DIR/podman/podman.sock:/var/run/docker.sock:ro
  - set a hostname for remote access (default is localhost only)
    - export CVAT_HOST=your-ip-adress
  - NOTE: If you run on a small machine and have mounted storage, make a podman storage config file
    - information
      - https://docs.oracle.com/en/operating-systems/oracle-linux/podman/podman-ConfiguringStorageforPodman.html#:~:text=By%20default%2C%20images%20are%20stored,Container%20Initiative%20(OCI)%20specifications.
    - note on how I did it for ibed-cvat.science.uva.nl
      - edit default config file and set
        - runroot = "/data/podman_storage/runroot"
        - graphroot = "/data/podman_storage/graphroot"
    - place config file
      - ~/.config/containers/storage.conf
      - if the directory does not exist yet (did not for me) create it
        - mkdir ~/.config/containers
    - make directories on data storage mount
      - mkdir /data/podman_storage/graphroot
      - mkdir /data/podman_storage/runroot
    -
  - Start the podman socket
    - podman system service -t 0
    - this would run the podman socket indefinetly. Send dont block process '&'
      - podman system service -t 0 &
  - Start CVAT
    - podman-compose up -d
  - Create a super user
    - docker exec -it cvat_server bash -ic 'python3 ~/manage.py createsuperuser'
  - Go to the adress specified in CVAT_HOST with default ports
    - e.g. CVAT_HOST=ibed-cvat.science.uva.nl
      - chrome
        - ibed-cvat.science.uva.nl:8080
    - if you want to test if it runs fine on localhost and dont have access to browser
      - export CVAT_HOST=
      - podman system service -t 0 &
      - podman-compose up -d
      - curl localhost:8080
        - If you get a response regarding annotation tool, CVAT is running
