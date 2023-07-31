# checkRunningPrograms_Services.py
# 21.06.2023
import psutil
import json
from argparse import ArgumentParser

def programsRunning(program_D):
    """
    helper function to check for running programs
    
    inputs:
        program_D : dictionary of program info
     purpose:
    
    returns:
    
    None : no program in dictionary program_D is running
    True : all programs in dictionary program_D is running
    False: at least one program in dictionray program_D is not running
    """
    all_programs_running = None
    for name, info in program_D.items():
        all_programs_running = True
        # check if program exists
        if info is None:
            all_programs_running = False
            return all_programs_running
        
        # iterate over list of programs
        for p_info in info:
            if p_info['status'] != 'running':
                all_programs_running = False
                return all_programs_running
    return all_programs_running
          
def servicesRunning(service_D):
    """
    helper function to check for running services
    
    inputs:
        service_D : dictionary of service info
     purpose:
    
    returns:
    
    None : no service in dictionary service_D is running
    True : all services in dictionary service_D is running
    False: at least one service in dictionray service_D is not running
    """
    all_services_running = None
    for name, info in service_D.items():
        all_services_running = True
        # check if service exists
        if info is None:
            all_services_running = False
            return all_services_running
        
        # check status
        if info['status'] != 'running':
            all_services_running = False
            return all_services_running
        
    return all_services_running
    

if __name__ == "__main__":
    
    parser = ArgumentParser()
    parser.add_argument("configJS", help="configuration file (json)")
    parser.add_argument("resultJS", help="result file (json)")
    args = parser.parse_args()
    
    with open(args.configJS, 'r') as fid:
        config_D = json.load(fid)
        programs_L = config_D['programs']
        services_L = config_D['services']
    
    result_D = dict()
    
    # collecting status of programs
    result_D['programs'] = dict()
    for program_name in programs_L:
        try:
            info =  [process.info for process in psutil.process_iter(['pid', 'name', 'username', 'status']) if process.info['name'] == program_name]
            result_D['programs'][program_name] = info
        except:
            result_D['programs'][program_name] = None

    # collecting status of Windows services
    result_D['services'] = dict()        
    for service_name in services_L:
        try:
            result_D['services'][service_name] = psutil.win_service_get(service_name).as_dict()
        except:
            result_D['services'][service_name] = None

    # programs are running ?
    all_programs_running = programsRunning(result_D['programs'])
    print(f"all programs running            : {all_programs_running}")
    
    # all services are running ?
    all_services_running = servicesRunning(result_D['services'])
    print(f"all services running            : {all_services_running}")
    
    all_running = all_programs_running and all_services_running
    print(f"all programs & services running : {all_running}")
    
    # result file
    with open(args.resultJS, 'w') as fid:
        json.dump(result_D, fid, indent=2)