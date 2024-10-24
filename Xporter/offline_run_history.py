import requests
import re

# List of fhicl files and parameters to look for in the configuration
# provide also translation for corresponding metadata fields
parameter_spec = { 
    "metadata.fcl": 
    {
        'components':'components',
        'configuration':'config_name',
        'projectversion':'sbndaq_commit_or_version',
        #'start_time':'daqinterface_start_time',
        #'stop_time':'daqinterface_stop_time'
    }
}

# default uri for the run history (pending run records) database
# key is the run number
ucondb_uri = 'https://dbdata0vm.fnal.gov:9443/icarus_on_ucon_prod/app/data/run_records_pending/configuration/key=%d'

class RunHistoryiReader:
    def __init__(self,
                 parameter_spec=parameter_spec,
                 ucondb_uri=ucondb_uri):
        self.parameter_spec=parameter_spec
        self.ucondb_uri=ucondb_uri

    def unpack_clob(self,clob):
        pattern = re.compile (r'#{5}[^#{5}](.*\.fcl):\s#{5}\s([\s\S]*?)(?=(#{5}|End of Record))')
        for match in re.finditer(pattern, clob):
           yield (match.group(1),match.group(2))

    def fetch_clob(self,run_number):
        try:
            #in case of issues with RunHistory DB, a hotfix to disable SSL certificate checking
            #is to add verify=False option to the get command below
            response = requests.get(self.ucondb_uri%(run_number))
            response.raise_for_status()
            return (0, response.text)
        except requests.exceptions.HTTPError as ex:
            return (-1, "HTTP Error: %s"%(ex))
        except requests.exceptions.ConnectionError as ex:
            return (-2 , "Error Connecting: %s"% (ex))
        except requests.exceptions.Timeout as ex:
            return (-3, "Timeout Error: %s"%(ex))
        except requests.exceptions.RequestException as ex:
            return (-4,  "Error: %s"%(ex))

    def parse_fhicl(self,fhicl_file):
        #Rewrite to use the fhiclpy libary
        results = {}
        error_count=0
        for file_name, export_params in self.parameter_spec.items():
            for name, key in export_params.items():
                pattern=r'%s:\s+(.*)'%key
                matches=re.findall(pattern,fhicl_file[1])
                if matches is None or not matches:
                    results[name]='Error: no matches for the regex /%s/ in %s.'%(pattern,file_name)
                    error_count+=1
                    continue
                if len(matches) > 1 :
                    results[name]='Error: too many matches for the regex /%s/ in %s.'%(pattern,file_name)
                    error_count+=1
                    continue
                results[name]=matches[0].replace('"', '').strip()
        return (error_count,results)


    def read(self,run_number):
        err, clob = self.fetch_clob(run_number)
        if err != 0:
            return(err,{'error':clob})
        results = {}
        error_count=0
        for fhicl_file in self.unpack_clob(clob):
            if fhicl_file[0] not in self.parameter_spec:
                continue
            tmp=self.parse_fhicl(fhicl_file)
            error_count+=tmp[0]
            results = {**results, **tmp[1]}
        return (error_count, results)


if __name__ == '__main__':

    # for testing purposes only
    run_number = 12665
    my_existing_data = {'run_number':run_number }
    result = RunHistoryiReader().read(run_number)
   
    if(result[0]!=0):
        print("ErrorCode=%d."%result[0])
	
    print(my_existing_data)
    print(result)

