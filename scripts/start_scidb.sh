# CURRENTLY NOT INTENDED TO BE RUN DIRECTLY, BUT CUT AND PASTED INTO A TERMINAL

# Use a spot instance (cheaper but less certain)
# m1.large 64-bit:
#ec2-request-spot-instances ami-7487651d --instance-type m1.large --availability-zone us-east-1a --key GZ --group db -p 0.20
# m2.xlarge 64-bit (extra memory helps for initial reduction):
#ec2-request-spot-instances ami-7487651d --instance-type m2.xlarge --availability-zone us-east-1a --key GZ --group db -p 0.25

sleep 30

# Use a normal instance
ec2-run-instances ami-7487651d --instance-type m1.large --availability-zone us-east-1a --key GZ --group db
#ec2-run-instances ami-7487651d --instance-type m2.xlarge --availability-zone us-east-1a --key GZ --group db

# Create a volume from the GZ2 database snapshot
#EC2VOLUME=`ec2-create-volume --size 50 --snapshot snap-6ec77206 --availability-zone us-east-1a | awk '{print $2}'`
# OR
# Use volume saved from the previous GZ2 reduction
EC2VOLUME="vol-8b59e7e2"

EC2STATUS=""
while [ "$EC2STATUS" != "running" ]
do
    sleep 60
    EC2STATUS=`ec2-describe-instances | grep INSTANCE | grep GZ | tail -1 | awk '{print $6}'`
done
EC2INSTANCE=`ec2-describe-instances | grep INSTANCE | grep GZ | tail -1 | awk '{print $2}'`
echo $EC2INSTANCE

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

EC2URL=`ec2-describe-instances $EC2INSTANCE | grep INSTANCE | awk '{print $4}'`
echo $EC2URL


# RESIZE PARTITION IF VOLUME CREATED FROM ORIGINAL SNAPSHOT
#ssh -i GZ.pem root@$EC2URL
#apt-get install xfsprogs
#mount /vol
#xfs_growfs /vol
# CHANGE RAM AND DISK SPACE USABLE BY MYSQL
# see ec2.cnf

ec2-reboot-instances $EC2INSTANCE

sleep 30

# To access database remotely:
# mysql5 -A -u zoodb -p -h $EC2URL juggernaut_production
# OR to avoid a firewall:
# ssh -i GZ.pem root@$EC2URL
# mysql -A -u zoodb -p juggernaut_production

# # Swap?
# EC2SWAP=`ec2-create-volume --size 20 --availability-zone us-east-1a | awk '{print $2}'`
# ec2-attach-volume $EC2SWAP -i $EC2INSTANCE -d /dev/sdd
# ssh -i GZ.pem root@$EC2URL
# # then on instance:
# mkswap /dev/sdd
# swapon /dev/sdd