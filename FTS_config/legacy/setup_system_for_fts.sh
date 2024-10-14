#
# Things to do to setup for FTS
#
# Generally this follows from these webpages:
#  https://opensciencegrid.org/docs/common/yum/
#  https://opensciencegrid.org/docs/common/ca/
#
# Need OSG 3.4 installed: I think with care to make sure all the OSG packages are given preference vs EPEL/others.
#
#
# This will need to run as root.

yum install yum-plugin-priorities
yum install yum-conf-extras
#yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
#yum install epel-release-latest-7

#(make sure sl-extras and epel repos are enabled)
#yum install https://repo.opensciencegrid.org/osg/3.4/osg-3.4-el7-release-latest.rpm
#yum install osg-3.4-el7-release-latest

#Then we need CA certificates installed, which I think means following this:
yum install osg-ca-certs
yum install osg-wn-client
yum install fetch-crl

#Then, make sure fetch-crl-boot and fetch-crl-cron are enabled.
systemctl enable fetch-crl-boot.service
systemctl enable fetch-crl-cron.service

systemctl start fetch-crl-boot.service &
systemctl start fetch-crl-cron.service &

