# CURRENTLY NOT INTENDED TO BE RUN DIRECTLY, BUT CUT AND PASTED INTO A TERMINAL

# Use a spot instance (cheaper but less certain)
# m1.large 64-bit:
ec2-request-spot-instances ami-7487651d --instance-type m1.large --availability-zone us-east-1a --key GZ --group db -p 0.20

sleep 30

# Use a normal instance
#ec2-run-instances ami-7487651d --instance-type m1.large --availability-zone us-east-1a --key GZ --group db

EC2STATUS=""
while [ "$EC2STATUS" != "running" ]
do
    sleep 10
    EC2STATUS=`ec2-describe-instances | grep INSTANCE | grep GZ | tail -1 | awk '{print $6}'`
done
EC2INSTANCE=`ec2-describe-instances | grep INSTANCE | grep GZ | tail -1 | awk '{print $2}'`
echo $EC2INSTANCE

# Create a volume from the GZ2 database snapshot
EC2VOLUME=`ec2-create-volume --snapshot snap-4b9b8922 --availability-zone us-east-1a | awk '{print $2}'`
# OR
# Create a volume saved from the previous GZ2 reduction
#EC2VOLUME=`ec2-create-volume --snapshot snap-31110958 --availability-zone us-east-1a | awk '{print $2}'`


EC2STATUS=""
while [ "$EC2STATUS" != 'available' ]
do
    sleep 10
    EC2STATUS=`ec2-describe-volumes $EC2VOLUME | grep VOLUME | awk '{print $6}'`
done
echo $EC2VOLUME

ec2-attach-volume $EC2VOLUME -i $EC2INSTANCE -d /dev/sdh

EC2STATUS=""
while [ "$EC2STATUS" != 'attached' ]
do
    sleep 5
    EC2STATUS=`ec2-describe-volumes $EC2VOLUME | grep ATTACHMENT | awk '{print $5}'`
done

ec2-reboot-instances $EC2INSTANCE

sleep 30

EC2URL=`ec2-describe-instances $EC2INSTANCE | grep INSTANCE | awk '{print $4}'`
echo $EC2URL

#ssh -i GZ.pem root@$EC2URL

# To access database remotely:
# mysql5 -A -u zoodb -p -h $EC2URL juggernaut_production
# OR to avoid a firewall:
# ssh -i GZ.pem root@$EC2URL
# mysql -A -u zoodb -p juggernaut_production
