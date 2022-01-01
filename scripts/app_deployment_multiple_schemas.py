import re
import argparse
import psutil
import shutil
import random
from distutils.dir_util import copy_tree , remove_tree
import xml.etree.ElementTree as ET
import time
import traceback

from synonyms import get_synonyms
from multi_app_deployment_via_cmd import create_app, delete_all_apps
from app_dep_schema_variation import create_schema

"""
The experiment performed in via this script is to deploy applications with multiple schemas.
"""

app_location = "/home/ubuntu/application-pkgs/my-app"

def add_schema(counter, base_schema, base_schema_path):
    doc_name = base_schema_path.split("/")[-1].split(".")[0]
    new_doc_name = doc_name+str(counter)
    base_schema = base_schema.replace(doc_name, new_doc_name)
    new_schema = create_schema(base_schema)
    new_schema_file = doc_name+str(counter)+".sd"
    with open(app_location+"/schemas/" + new_schema_file, "w") as f:
        f.write(new_schema)
    tree = ET.parse(app_location+"/services.xml")
    tree.getroot()[1][1].append(ET.Element("document",attrib={"type": new_schema_file.split(".")[0], "mode":"index"}))
    tree.write(app_location+"/services.xml")
    services_string = ET.tostring(tree.getroot()).replace(b"\n", b" ")
    return services_string


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_log_file", help="The location csv file containing logs", type=str,
             default="/home/ubuntu/logs/logs_{tm}.csv".format(tm=time.time()))
    parser.add_argument("--base_schema", help="The base schema file to replicate", type=str,
                        default="news.sd")
    parser.add_argument("--delete_app", help="Delete app with container name", type=str, default="")

    args = parser.parse_args()
    csv_log_file = args.csv_log_file
    base_schema_file = args.base_schema
    delete_app = args.delete_app
    if delete_app:
        delete_all_apps(num_apps=1, container_name=delete_app)

    print("LOG FILE: {csv_log_file}\n".format(csv_log_file=csv_log_file))
    log_file_obj = open(csv_log_file, 'a')
    log_file_obj.write("container_name,app_port,vespa_port,cpu_percent,memory_percent,step,service\n")
    try:
        i=0
        tree = ET.parse(app_location+"/services.xml")
        services = ET.tostring(tree.getroot()).replace(b"\n", b" ")
        with open(app_location+"/schemas/" + base_schema_file, "r") as f:
            original_schema = f.read()
        mem = psutil.virtual_memory().percent
        while mem<90:
            print( "App Count : {i}".format(i=i+1))
            create_app(i, log_file_obj, app_location=app_location, app_info=services)
            mem = psutil.virtual_memory().percent
            services = add_schema(i+1, base_schema=original_schema, 
                            base_schema_path=app_location+"/schemas/" + base_schema_file)
            delete_all_apps(num_apps=1, container_name= 'vespa' + str(i))
            i+=1
    except Exception as e:
        print(e)
        print(traceback.print_exc())

    print("LOG FILE: {csv_log_file}\n".format(csv_log_file=csv_log_file))

    log_file_obj.close()





