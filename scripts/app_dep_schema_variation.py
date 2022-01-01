import re
import argparse
import psutil
import shutil
import random
from distutils.dir_util import copy_tree , remove_tree
import time
import traceback

from synonyms import get_synonyms
from multi_app_deployment_via_cmd import create_app, delete_all_apps

"""
Building on multi_app_deployment_via_cmd.py, this script creates multiple apps but with different schemas.
The new schemas are created using the existing schema but the field names are changed using a variable
`fract_field_change` that decides how many fields to change. For every field to change `spacy` library is 
used to create synonym names for the fields.
"""




app_location = "/home/ubuntu/application-pkgs/my-app"
orignal_schema_file = "news.sd"


def create_schema(original_schema, fract_field_change=0.75):
    pat = r"field\s\w+\stype\s\w+\s"
    match = re.findall(pat, original_schema)
    n_fields = len(match)
    new_schema = original_schema
    for _ in range(int(n_fields*fract_field_change)):
        matched_string = match[random.randrange(n_fields)]
        field_name = matched_string.split("field ")[1].split(" type")[0]
        new_field_name = random.choice(get_synonyms(field_name)).replace("-", "_")
        new_schema = new_schema.replace(field_name, new_field_name)
    
    return new_schema


def create_app_folder(original_app_location, count):
    new_app = original_app_location+str(count)
    copy_tree(original_app_location, new_app)
    print("App {} Created".format(count))
    return new_app


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_apps", help="The number of applications to be deployed", type=int, 
                default=1)
    parser.add_argument("--csv_log_file", help="The location csv file containing logs", type=str,
             default="/home/ubuntu/logs/logs_{tm}.csv".format(tm=time.time()))
    parser.add_argument("--delete_all", help="Delete all the existing applications", type=bool, default=False)

    args = parser.parse_args()
    num_apps = int(args.num_apps)
    csv_log_file = args.csv_log_file

    delete_all = args.delete_all
    if delete_all:
        delete_all_apps(num_apps)
        exit()

    print("LOG FILE: {csv_log_file}\n".format(csv_log_file=csv_log_file))
    log_file_obj = open(csv_log_file, 'a')
    log_file_obj.write("container_name,app_port,vespa_port,cpu_percent,memory_percent,step,schema\n")


    try:
        app_folders = []
        new_app_loc = app_location
        with open(app_location+"/schemas/" + orignal_schema_file, "r") as f:
            original_schema = f.read()
        new_schema = original_schema
        for i in range(num_apps):
            print( "App Count : {i}".format(i=i+1))
            if i>0:
                new_schema = create_schema(original_schema)
                new_app_loc = create_app_folder(app_location, i)
                with open(new_app_loc+"/schemas/" + orignal_schema_file, "w") as f:
                    f.write(new_schema)
                app_folders.append(new_app_loc)
            else:
                app_folders.append(app_location)
            new_schema = new_schema.replace("\n", " ").replace("\r"," ")
            create_app(i, log_file_obj, app_location=new_app_loc, app_info=new_schema)
            if psutil.virtual_memory().percent>90:
                print("Memory is full. Deleting all apps")
                delete_all_apps(num_apps)
                [remove_tree(app_loc) for app_loc in app_folders[1:]]
                break
            print("\n")
    except Exception as e:
        print(e)
        print(traceback.print_exc())
    
    print("LOG FILE: {csv_log_file}\n".format(csv_log_file=csv_log_file))
    log_file_obj.close()


    
    
    



