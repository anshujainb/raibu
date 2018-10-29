import boto3
import json
import pymongo
class EC2Instance:


    def __init__(self,clientName=None,Image_Id=None,Instance_type=None,MinCount=None,MaxCount=None,AccessKey=None,KeyName=None,SecretKey=None,Region=None,Security_group=None):
        self.my_session = boto3.Session(aws_access_key_id=AccessKey,aws_secret_access_key=SecretKey,region_name=Region)
        self.ec2 = self.my_session.resource('ec2')
        self.Image_Id=Image_Id
        self.Instance_type=Instance_type
        self.MinCount=MinCount
        self.MaxCount=MaxCount
        self.Security_group=Security_group
        self.AccessKey=AccessKey
        self.SecretKey=SecretKey
        self.KeyName=KeyName
        self.clientName=clientName
        self.Region=Region
    
    def createMongoDoc(self,cName,listOfVm):
        id='rb-'+cName
        jsonData={'clientName':cName,
        'clientId':id,
        'VmList':listOfVm
        }
        return jsonData
    
    def SaveToDb(self,mongoData):
        connection = pymongo.MongoClient("mongodb://localhost", 27017)
        db = connection.raibu
        raibuClients=db.raibuClients
        if(raibuClients.find_one({'clientId':mongoData['clientId']})is not None):
            for i in mongoData['VmList']:
                raibuClients.update({ 'clientId':mongoData['clientId']},{"$push": {'VmList': i}})
        else:
            raibuClients.update(mongoData,mongoData,upsert=True)
        return "data saved successfully........"

    def createNew(self,clientName,Image_Id,Instance_type,Min_Count,Max_Count,Security_group,keyname):
        key_name=self.getKeypair(keyname)
        new_Instance=self.ec2.create_instances(ImageId=Image_Id,InstanceType=Instance_type,KeyName=key_name,MinCount=Min_Count,MaxCount=Max_Count, NetworkInterfaces=[{}])
        count=0
        instance_Details=[]
        for inst in new_Instance:
            count+=1
            print("waiting for instance No. "+str(count)+" to run....")
            inst.wait_until_running()
            inst.load()
            print("instance no. "+str(count)+" is ready")
            Inst_Id=inst.id
            instance_Details.append(self.getInstanceDetail(Inst_Id))
        mongoData=self.createMongoDoc(clientName,instance_Details) 
        self.SaveToDb(mongoData)
        res=json.dumps(instance_Details, sort_keys=True,indent=4,separators=(',',':'))
        return res


    def getKeypair(self,keyname):
        ec2c=self.my_session.client('ec2')
        try:
         resp=ec2c.describe_key_pairs(KeyNames=[keyname])
         keyname=resp["KeyPairs"][0]["KeyName"]

        except:
            print("key pair not available will create keypair")
            newkey=ec2c.create_key_pair(KeyName=keyname)
            print(newkey)
        return keyname

        

    def getSecurityGroup(self,secgrpname,Reg):
        ec2c=self.my_session.client('ec2')
        resp=ec2c.describe_vpcs()
        vpcidtouse=resp['Vpcs'][0]['VpcId']	
        try: 		
            secgrpfilter = [
                {
                    'Name':'group-name','Values':[secgrpname]
                }
                    ]
            secgroups = ec2c.describe_security_groups(GroupNames=[secgrpname])
                       
            print(json.dumps(secgroups,indent=2,separators=(',',':')))
            secgrpid = secgroups["SecurityGroups"][0]['GroupId']
          	

        except:

            print('no security group, will create security group'+secgrpname)
            secgrptouse	= ec2c.create_security_group(	
                    GroupName=secgrpname,	
                    Description='aws class open ssh,http,https',	
                    VpcId=vpcidtouse)
            secgrpid = secgrptouse['GroupId']
            print("created security group:"+secgrpid)


    
    def stop(self,id):
        ids=[id]
        self.ec2.instances.filter(InstanceIds=ids).stop()
        print('stopped')

    def terminate(self,id):
        ids=[id]
        self.ec2.instances.filter(InstanceIds=ids).terminate()
        print('terminated')
    
   
    def getInstances(self,filters):
        instances = self.ec2.instances.filter(Filters=filters)
        RunningInstances = []
        for instance in instances:
            print(instance.id)
            RunningInstances.append(instance)
        return RunningInstances

    def startInstances(self,id):
        ids=[id]
        self.ec2.instances.filter(InstanceIds=ids).start()

    def getAllRunningInstancesID(self):
        filters = [
            {
                'Name': 'instance-state-name', 
                'Values': ['running']
            }
        ]
        runningInstances = self.getInstances(filters)
        return runningInstances

    def getAllInstances(self):
        filters = [
            {
                'Name': 'instance-state-name', 
                'Values': ['running','stopped','pending','terminated']
            }
        ]
        runningInstances = self.getInstances(filters)
        return runningInstances
        
    def getAllStoppedInstances(self):
        filters = [
            {
                'Name': 'instance-state-name', 
                'Values': ['stopped']
            }
        ]
        runningInstances = self.getInstances(filters)
        return runningInstances

    def jsonToInstance(self,obj):
        data=obj
        self.AccessKey=data['Access_Key']
        self.clientName=data['clientName']
        self.SecretKey=data['Secret_Key']
        self.Region=data['Region']
        self.Image_Id=data['Image_Id']
        self.KeyName=data['KeyName']
        self.Security_group=data['Security_group']
        self.Instance_type=data['Instance_type']
        self.MinCount=data['MinCount']
        self.MaxCount=data['MaxCount']
        return self


    def getIP(self,instId):
        ec2c=boto3.client('ec2',region_name="us-west-2")
        bGotIp = False 
        instid= instId
        while bGotIp== False: 
            outp= ec2c.describe_instances(InstanceIds=[instid])
            inst=outp["Reservations"][0]["Instances"][0]
            instid=inst["InstanceId"]
            publicip=inst.get('PublicIpAddress')
            if not publicip: 
                print('do not have ip address yet')
                continue 
            else: 
                bGotIp = True 
                print 'ip=' + publicip



    def getIp(self):
        instances=self.getAllRunningInstancesID()
        for instance in instances:
            print(instance.public_ip_address)
            print(instance.state['Name'])

    def getInstanceDetail(self,instId):

        bGotIp = False
        ins=self.ec2.Instance(instId)
        publicIp=ins.public_ip_address
        privateIp=ins.private_ip_address

        return self.returninstanceToJson(ins)

    def returninstanceToJson(self,obj):
        instance_details = {}
        instance_details["name"] = obj.public_dns_name
        instance_details["publicIp"] = obj.public_ip_address
        instance_details["privateIp"] =obj.private_ip_address
        return instance_details


    







