import os
import psutil
import time
import argparse

from spacy import info


app_location = "/home/ubuntu/sample-apps/news/my-app"

def create_app(container_idx, log_file_obj, app_location=app_location, app_info=""):
    container_name = 'vespa' + str(container_idx)
    app_port = 8080 + container_idx
    vespa_port = 19071 + container_idx

    steps = ["vesp_docker", "docker_curl", "curl_vespa", "app_created"]
    app_run_cmd = [0]*5
    sleep_time = [10, 3, 0, 0,0]

    app_run_cmd[0] = """sudo docker run --detach --name {container_name} --hostname vespa-container --privileged \
            --publish {app_port}:8080 --publish {vespa_port}:19071 -v {app_location}:/app vespaengine/vespa
                """.format(app_location=app_location, container_name=container_name, app_port=app_port,
                           vespa_port=vespa_port)


    app_run_cmd[1] = """sudo docker exec -it {container_name} bash -c \
                'curl -s --head http://localhost:19071/ApplicationStatus'
              """.format(container_name=container_name, vespa_port=vespa_port)

    app_run_cmd[2] = """ curl -s --head http://localhost:{vespa_port}/ApplicationStatus """.format(vespa_port=vespa_port)


    app_run_cmd[3] = """ sudo docker exec -it {container_name} bash -c 'cd /app && zip -r - . | \
                    curl --header Content-Type:application/zip --data-binary @- \
                    localhost:19071/application/v2/tenant/default/prepareandactivate'
                     """.format(container_name=container_name, vespa_port=vespa_port)

    #app_run_cmd[4] = """ curl  --head http://localhost:{app_port}/ApplicationStatus """.format(app_port=app_port)



    for i in range(len(app_run_cmd)):
        if not app_run_cmd[i]:
            break
        print(app_run_cmd[i])
        t0 = time.time()
        out = os.system(app_run_cmd[i])
        t1 = time.time()
        tm = t1-t0 if out==0 else -1
        print("CPU : {cpu}  Mem: {mem}".format(cpu=psutil.cpu_percent(), mem=psutil.virtual_memory().percent))
    
        log_file_obj.write("{container_name},{app_port},{vespa_port},{cpu},{mem},{step},{tm},{info}\n".
        format(container_name=container_name, app_port=app_port, vespa_port=vespa_port,
               cpu=psutil.cpu_percent(), mem=psutil.virtual_memory().percent, step=steps[i],tm=tm, info=app_info))
        time.sleep(sleep_time[i])
        print("\n")
    
def delete_all_apps(num_apps, container_name=""):
    if container_name:
        app_run_cmd = """ sudo docker rm -f {container_name} """.format(container_name=container_name)
        os.system(app_run_cmd)
        print("App {} Deleted".format(container_name))
        return
    for i in range(num_apps):
        container_name = 'vespa' + str(i)
        app_run_cmd = """ sudo docker rm -f {container_name} """.format(container_name=container_name)
        os.system(app_run_cmd)
    print("All apps deleted")


if __name__ == "__main__":
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
    log_file_obj.write("container_name,app_port,vespa_port,cpu_percent,memory_percent,step,info\n")

    try:
        for i in range(num_apps):
            print( "App Count : {i}".format(i=i+1))
            create_app(i, log_file_obj)
            if psutil.virtual_memory().percent>90:
                print("Memory is full. Deleting all apps")
                delete_all_apps(num_apps)
                break
            print("\n")
    except Exception as e:
        print(e)
    
    print("LOG FILE: {csv_log_file}\n".format(csv_log_file=csv_log_file))

    log_file_obj.close()

    
