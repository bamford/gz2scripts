# CURRENTLY NOT INTENDED TO BE RUN DIRECTLY, BUT CUT AND PASTED INTO A TERMINAL

# Use a spot instance (cheaper but less certain)
# m1.large 64-bit:
#ec2-request-spot-instances ami-7487651d --instance-type m1.large --availability-zone us-east-1a --key GZ --group db -p 0.20
# m2.xlarge 64-bit (extra memory helps for initial reduction):
#ec2-request-spot-instances ami-7487651d --instance-type m2.xlarge --availability-zone us-east-1a --key GZ --group db -p 0.25

sleep 30

# Use a normal instance
# Used to use ami-7487651d, which is now depreciated
# Try latest official ubuntu image: ami-08f40561
# And again: ami-0d273b64

ec2-run-instances ami-0d273b64 --instance-type m1.large --availability-zone us-east-1a --key GZ --group db
#ec2-run-instances ami-7487651d --instance-type m2.xlarge --availability-zone us-east-1a --key GZ --group db

# Create a volume from the GZ2 database snapshot
#EC2VOLUME=`ec2-create-volume --size 50 --snapshot snap-6ec77206 --availability-zone us-east-1a | awk '{print $2}'`
# OR
# Use the saved reduction snapshot
#EC2VOLUME=`ec2-create-volume --snapshot snap-24c7c24f --availability-zone us-east-1a | awk '{print $2}'`
# OR
# Use volume saved from the previous GZ2 reduction
#EC2VOLUME="vol-44207b2d"

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

# apt-get update
# apt-get upgrade
# apt-get install mysql-server emacs23-nox

# RESIZE PARTITION IF VOLUME CREATED FROM ORIGINAL SNAPSHOT
#ssh -i GZ.pem root@$EC2URL
#apt-get install xfsprogs
#mount /vol
#xfs_growfs /vol

# prevent apparmour from preventing mysql starting
# apt-get install apparmor-utils
# aa-complain /usr/sbin/mysqld


# CHANGE RAM AND DISK SPACE USABLE BY MYSQL
# see ec2.cnf
# scp -i GZ.pem scripts/ec2.cnf ubuntu@$EC2URL:/etc/mysql/conf.d/

#ec2-reboot-instances $EC2INSTANCE
#sleep 30

#ssh -i GZ.pem root@$EC2URL
#/etc/init.d/mysql start

# UPLOAD/UPDATE SCRIPTS
rsync -a -e'ssh -i GZ.pem' scripts/*.sql root@$EC2URL:/vol/scripts/

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
