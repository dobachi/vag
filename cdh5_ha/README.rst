README
==========

This is a Vagrant configuration of Hadoop cluster.
We use CentOS7 as a base box.

Unfortunately, Vagrant cannot configure CentOS7's private network IP addresses.
That is why, we use config.vm.guest option to use Fedora's module.
But this causes a failure about hostname configuration.
