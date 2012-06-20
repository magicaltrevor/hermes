from engines.databases import *
from engines.jobs import *
from plugins import *

def job_to_class(job):
    klass = eval(job.plugin.capitalize())(login=job.login,password=job.password,to_address=job.to_address,from_address=job.from_address,message=job.message)
    return klass
    



