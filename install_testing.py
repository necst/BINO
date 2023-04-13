#!/usr/bin/python3

import argparse
from os.path import isfile, exists, isdir, join, dirname, abspath
from os import remove, listdir, mkdir
from shutil import rmtree, copyfile

VOLUME_SERV_TEMPLATE = """volumes:
      - $CLASS_NAME$_volume:/home/inlinerecognizer"""

SERVICE_TEMPLATE = """  $CLASS_NAME$:
    restart: always  
    build:
      context: . 
      dockerfile: docker/images/$CLASS_NAME$/Dockerfile
    $OPT_VOLUME$

"""

VOLUME_TEMPLATE = """
  $CLASS_NAME$_volume:     
    driver: local
    driver_opts:
      type: 'none'
      o: 'bind'
      device: '$VOLUME_PATH$'
"""



def clear_directory(path):
    for file in listdir(path):
        if isfile(join(path,file)):
            remove(join(path,file))
        else:
            rmtree(join(path,file))

if __name__ == '__main__':
    """
    Installer for the testing environment
    """

    # Projecj path
    prj_path = dirname(abspath(__file__))
    # Argument parsing
    parser = argparse.ArgumentParser(description="Installer for the testing environment.")
    parser.add_argument("-cs",
                        "--classes", 
                        dest="classes_names",
                        nargs="+", 
                        help="List of classes to test. If not specified all classes inside the path are considered.")
    parser.add_argument("-d",
                        "--distro",
                        dest="distro",
                        help="Ubuntu distro")
    parser.add_argument("-vp",
                        "--volumes-path",
                        dest="vols_path",
                        help="Path for volumes")    
    args = parser.parse_args()
    # Parsing arguments
    distro = args.distro
    vols_path = args.vols_path
    classes = args.classes_names
    # Paths
    images_path = join(prj_path, "docker", "images")
    templates_path = join(prj_path, "docker", "templates")
    scripts_path = join(prj_path, "docker", "scripts")
    # Creating images directory if doesn't exists
    if not exists(images_path) or not isdir(images_path):
        mkdir(images_path)
    # Clearing images
    clear_directory(images_path)
    # Checking if distro is supported
    if distro is None:
        distro = "Ubuntu:18.04"
    dockerfile_template_name = "Dockerfile-" + distro + "_template"
    dockerfile_path = join(templates_path, dockerfile_template_name)
    if not exists(dockerfile_path) or not isfile(dockerfile_path):
        raise Exception("Unsupported distro!")
    # Creating Docker images directory
    if not classes:
        raise Exception("No classes specified!")
    # Creating services and volumes
    services_str = ""
    if vols_path:
        if vols_path[0] != "/":
            vols_path = join(prj_path, vols_path)
        volumes_str = "volumes:\n"
    else:
        volumes_str = ""       
    for class_name in classes:
        # Preparing run.sh
        f = open(join(templates_path, "run.sh_template"))
        content_simple = f.read()
        f.close()
        content_simple = content_simple.replace("$CLASS_NAME$", class_name)
        # Preparing no_hup_run.sh
        f = open(join(templates_path, "no_hup_run.sh_template"))
        content_nohup = f.read()
        f.close()
        content_nohup = content_nohup.replace("$CLASS_NAME$", class_name)  
        # Creating directory for image      
        class_name = class_name.replace("::", "_").lower()
        image_path = join(images_path, class_name)
        mkdir(image_path)
        # Creating dockerfile
        f = open(dockerfile_path)
        dockerfile = f.read()
        f.close()
        dockerfile = dockerfile.replace("$CLASS_NAME$", class_name)      
        f = open(join(image_path, "Dockerfile"), "w")
        f.write(dockerfile)
        f.close()
        # Creating service string
        current_service = SERVICE_TEMPLATE.replace("$CLASS_NAME$", class_name) + "\n\n"
        if vols_path:
            current_vol_path = join(vols_path, class_name)
            if exists(current_vol_path) and isdir(current_vol_path):
                raise Exception("Directory for volume " + current_vol_path + " already exists!")
            mkdir(current_vol_path)
            current_vol_serv = VOLUME_SERV_TEMPLATE.replace("$CLASS_NAME$", class_name)
            current_vol = VOLUME_TEMPLATE.replace("$CLASS_NAME$", class_name)
            current_vol = current_vol.replace("$VOLUME_PATH$", current_vol_path)
            current_service = current_service.replace("$OPT_VOLUME$", current_vol_serv)
            volumes_str += current_vol
        else:
            current_service = current_service.replace("$OPT_VOLUME$", "")
        services_str += current_service
        # Copying run.sh
        f = open(join(image_path, "run.sh"), "w")
        f.write(content_simple)
        f.close()
        # Copying no_hup_run.sh
        f = open(join(image_path, "no_hup_run.sh"), "w")
        f.write(content_nohup)
        f.close()
    # Creating docker-compose.yml
    f = open(join(templates_path, "docker-compose.yml_template"))
    compose_template = f.read()
    f.close()
    compose = compose_template.replace("$SERVICES$", services_str)
    compose = compose.replace("$VOLUMES$", volumes_str)
    f = open(join(prj_path, "docker-compose.yml"), "w+")
    f.write(compose)
    f.close()