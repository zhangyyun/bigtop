# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Hadoop RPM spec file
#

# FIXME: we need to disable a more strict checks on native files for now,
# since Hadoop build system makes it difficult to pass the kind of flags
# that would make newer RPM debuginfo generation scripts happy.
%undefine _missing_build_ids_terminate_build

%define hadoop_sname hadoop
%define hadoop_home %{hadoop_base}/%{hadoop_sname}
%define etc_hadoop %{hadoop_base}/etc/%{hadoop_sname}
%define etc_yarn %{etc_hadoop}
%define etc_httpfs %{hadoop_base}/etc/%{hadoop_sname}-httpfs
%define tomcat_deployment_httpfs /etc/hadoop-httpfs/tomcat-conf
%define lib_hadoop_dirname %{hadoop_base}
%define lib_hadoop %{lib_hadoop_dirname}/%{hadoop_sname}
%define lib_httpfs %{lib_hadoop_dirname}/%{hadoop_sname}-httpfs
%define lib_hdfs %{lib_hadoop_dirname}/%{hadoop_sname}-hdfs
%define lib_yarn %{lib_hadoop_dirname}/%{hadoop_sname}-yarn
%define lib_mapreduce %{lib_hadoop_dirname}/%{hadoop_sname}-mapreduce
%define log_hadoop_dirname /var/log
%define log_hadoop %{log_hadoop_dirname}/%{hadoop_sname}
%define log_yarn %{log_hadoop_dirname}/%{hadoop_sname}-yarn
# weired
%define log_hdfs %{log_hadoop_dirname}/%{hadoop_sname}/hdfs
%define log_httpfs %{log_hadoop_dirname}/%{hadoop_sname}-httpfs
%define log_mapreduce %{log_hadoop_dirname}/%{hadoop_sname}-mapreduce
%define run_hadoop_dirname /var/run
%define run_hadoop %{run_hadoop_dirname}/%{hadoop_sname}
%define run_yarn %{run_hadoop_dirname}/%{hadoop_sname}-yarn
%define run_hdfs %{run_hadoop_dirname}/%{hadoop_sname}/hdfs
%define run_httpfs %{run_hadoop_dirname}/%{hadoop_sname}-httpfs
%define run_mapreduce %{run_hadoop_dirname}/%{hadoop_sname}-mapreduce
%define state_hadoop_dirname /var/lib
%define state_hadoop %{state_hadoop_dirname}/%{hadoop_sname}
%define state_yarn %{state_hadoop_dirname}/%{hadoop_sname}-yarn
%define state_hdfs %{state_hadoop_dirname}/%{hadoop_sname}-hdfs
%define state_mapreduce %{state_hadoop_dirname}/%{hadoop_sname}-mapreduce
%define state_httpfs %{state_hadoop_dirname}/%{hadoop_sname}-httpfs
%define bin_hadoop %{hadoop_home}/bin
%define man_hadoop %{hadoop_home}/man
%define doc_hadoop %{hadoop_home}/doc
%define httpfs_services httpfs
%define mapreduce_services mapreduce-historyserver
%define hdfs_services hdfs-namenode hdfs-secondarynamenode hdfs-datanode hdfs-zkfc hdfs-journalnode
%define yarn_services yarn-resourcemanager yarn-nodemanager yarn-proxyserver yarn-timelineserver
%define hadoop_services %{hdfs_services} %{mapreduce_services} %{yarn_services} %{httpfs_services}
# Hadoop outputs built binaries into %{hadoop_build}
%define hadoop_build_path build
%define static_images_dir src/webapps/static/images
%define libexecdir /usr/lib

%ifarch i386
%global hadoop_arch Linux-i386-32
%endif
%ifarch amd64 x86_64
%global hadoop_arch Linux-amd64-64
%endif
%ifarch arm64 aarch64
%global hadoop_arch Linux-arm64-64
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0

# FIXME: brp-repack-jars uses unzip to expand jar files
# Unfortunately aspectjtools-1.6.5.jar pulled by ivy contains some files and directories without any read permission
# and make whole process to fail.
# So for now brp-repack-jars is being deactivated until this is fixed.
# See BIGTOP-294
%define __os_install_post \
    %{_rpmconfigdir}/brp-compress ; \
    %{_rpmconfigdir}/brp-strip-static-archive %{__strip} ; \
    %{_rpmconfigdir}/brp-strip-comment-note %{__strip} %{__objdump} ; \
    /usr/lib/rpm/brp-python-bytecompile ; \
    %{nil}

%define netcat_package nc
%global initd_dir %{_sysconfdir}/rc.d/init.d
%endif


%if  %{?suse_version:1}0

# Only tested on openSUSE 11.4. le'ts update it for previous release when confirmed
%if 0%{suse_version} > 1130
%define suse_check \# Define an empty suse_check for compatibility with older sles
%endif

# Deactivating symlinks checks
%define __os_install_post \
    %{suse_check} ; \
    /usr/lib/rpm/brp-compress ; \
    %{nil}

%define netcat_package netcat-openbsd
%define doc_hadoop %{_docdir}/%{name}
%global initd_dir %{_sysconfdir}/rc.d
%endif

%if  0%{?mgaversion}
%define netcat_package netcat-openbsd
%define doc_hadoop %{_docdir}/%{name}-%{hadoop_version}
%global initd_dir %{_sysconfdir}/rc.d/init.d
%endif


# Even though we split the RPM into arch and noarch, it still will build and install
# the entirety of hadoop. Defining this tells RPM not to fail the build
# when it notices that we didn't package most of the installed files.
%define _unpackaged_files_terminate_build 0

# RPM searches perl files for dependancies and this breaks for non packaged perl lib
# like thrift so disable this
%define _use_internal_dependency_generator 0

Name: %{hadoop_name}
Version: %{hadoop_version}
Release: %{hadoop_release}
Summary: Hadoop is a software platform for processing vast amounts of data
License: ASL 2.0
URL: http://hadoop.apache.org/core/
Group: Development/Libraries
Source0: %{hadoop_sname}-%{hadoop_base_version}.tar.gz
Source1: do-component-build
Source2: install_%{hadoop_sname}.sh
Source3: hadoop.default
Source4: hadoop-fuse.default
Source5: httpfs.default
Source6: hadoop.1
Source7: hadoop-fuse-dfs.1
Source8: hdfs.conf
Source9: yarn.conf
Source10: mapreduce.conf
Source11: init.d.tmpl
Source12: hadoop-hdfs-namenode.svc
Source13: hadoop-hdfs-datanode.svc
Source14: hadoop-hdfs-secondarynamenode.svc
Source15: hadoop-mapreduce-historyserver.svc
Source16: hadoop-yarn-resourcemanager.svc
Source17: hadoop-yarn-nodemanager.svc
Source18: hadoop-httpfs.svc
Source19: mapreduce.default
Source20: hdfs.default
Source21: yarn.default
Source22: hadoop-layout.sh
Source23: hadoop-hdfs-zkfc.svc
Source24: hadoop-hdfs-journalnode.svc
Source25: httpfs-tomcat-deployment.sh
Source26: yarn.1
Source27: hdfs.1
Source28: mapred.1
Source29: hadoop-yarn-timelineserver.svc
Source30: kill-name-node.sh
Source31: kill-secondary-name-node.sh
#BIGTOP_PATCH_FILES
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id} -u -n)
BuildRequires: fuse-devel, fuse, cmake
Requires: coreutils, /usr/sbin/useradd, /usr/sbin/usermod, bigtop-utils >= 0.7, zookeeper%{hdp_suffix} >= 3.4.0
Requires: psmisc, %{netcat_package}
# Sadly, Sun/Oracle JDK in RPM form doesn't provide libjvm.so, which means we have
# to set AutoReq to no in order to minimize confusion. Not ideal, but seems to work.
# I wish there was a way to disable just one auto dependency (libjvm.so)
AutoReq: no

%if  %{?suse_version:1}0
BuildRequires: pkg-config, libfuse2, libopenssl-devel, gcc-c++
# Required for init scripts
Requires: sh-utils, insserv
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0
BuildRequires: pkgconfig, fuse-libs, redhat-rpm-config, lzo-devel, openssl-devel
# Required for init scripts
Requires: sh-utils, /lib/lsb/init-functions
%endif

%if  0%{?mgaversion}
BuildRequires: pkgconfig, libfuse-devel, libfuse2 , libopenssl-devel, gcc-c++, liblzo-devel, zlib-devel
Requires: chkconfig, xinetd-simple-services, zlib, initscripts
%endif


%description
Hadoop is a software platform that lets one easily write and
run applications that process vast amounts of data.

Here's what makes Hadoop especially useful:
* Scalable: Hadoop can reliably store and process petabytes.
* Economical: It distributes the data and processing across clusters
              of commonly available computers. These clusters can number
              into the thousands of nodes.
* Efficient: By distributing the data, Hadoop can process it in parallel
             on the nodes where the data is located. This makes it
             extremely rapid.
* Reliable: Hadoop automatically maintains multiple copies of data and
            automatically redeploys computing tasks based on failures.

Hadoop implements MapReduce, using the Hadoop Distributed File System (HDFS).
MapReduce divides applications into many small blocks of work. HDFS creates
multiple replicas of data blocks for reliability, placing them on compute
nodes around the cluster. MapReduce can then process the data where it is
located.

%package hdfs
Summary: The Hadoop Distributed File System
Group: System/Daemons
Requires: %{name} = %{version}-%{release}, bigtop-groovy, bigtop-jsvc

%description hdfs
Hadoop Distributed File System (HDFS) is the primary storage system used by
Hadoop applications. HDFS creates multiple replicas of data blocks and distributes
them on compute nodes throughout a cluster to enable reliable, extremely rapid
computations.

%package yarn
Summary: The Hadoop NextGen MapReduce (YARN)
Group: System/Daemons
Requires: %{name} = %{version}-%{release}

%description yarn
YARN (Hadoop NextGen MapReduce) is a general purpose data-computation framework.
The fundamental idea of YARN is to split up the two major functionalities of the
JobTracker, resource management and job scheduling/monitoring, into separate daemons:
ResourceManager and NodeManager.

The ResourceManager is the ultimate authority that arbitrates resources among all
the applications in the system. The NodeManager is a per-node slave managing allocation
of computational resources on a single node. Both work in support of per-application
ApplicationMaster (AM).

An ApplicationMaster is, in effect, a framework specific library and is tasked with
negotiating resources from the ResourceManager and working with the NodeManager(s) to
execute and monitor the tasks.


%package mapreduce
Summary: The Hadoop MapReduce (MRv2)
Group: System/Daemons
Requires: %{name}-yarn = %{version}-%{release}

%description mapreduce
Hadoop MapReduce is a programming model and software framework for writing applications
that rapidly process vast amounts of data in parallel on large clusters of compute nodes.


%package hdfs-namenode
Summary: The Hadoop namenode manages the block locations of HDFS files
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-hdfs = %{version}-%{release}

%description hdfs-namenode
The Hadoop Distributed Filesystem (HDFS) requires one unique server, the
namenode, which manages the block locations of files on the filesystem.


%package hdfs-secondarynamenode
Summary: Hadoop Secondary namenode
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-hdfs = %{version}-%{release}

%description hdfs-secondarynamenode
The Secondary Name Node periodically compacts the Name Node EditLog
into a checkpoint.  This compaction ensures that Name Node restarts
do not incur unnecessary downtime.

%package hdfs-zkfc
Summary: Hadoop HDFS failover controller
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-hdfs = %{version}-%{release}

%description hdfs-zkfc
The Hadoop HDFS failover controller is a ZooKeeper client which also
monitors and manages the state of the NameNode. Each of the machines
which runs a NameNode also runs a ZKFC, and that ZKFC is responsible
for: Health monitoring, ZooKeeper session management, ZooKeeper-based
election.

%package hdfs-journalnode
Summary: Hadoop HDFS JournalNode
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}

%description hdfs-journalnode
The HDFS JournalNode is responsible for persisting NameNode edit logs.
In a typical deployment the JournalNode daemon runs on at least three
separate machines in the cluster.

%package hdfs-datanode
Summary: Hadoop Data Node
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-hdfs = %{version}-%{release}

%description hdfs-datanode
The Data Nodes in the Hadoop Cluster are responsible for serving up
blocks of data over the network to Hadoop Distributed Filesystem
(HDFS) clients.

%package httpfs
Summary: HTTPFS for Hadoop
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}, bigtop-tomcat
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-hdfs = %{version}-%{release}

%description httpfs
The server providing HTTP REST API support for the complete FileSystem/FileContext
interface in HDFS.

%package yarn-resourcemanager
Summary: YARN Resource Manager
Group: System/Daemons
Requires: %{name}-yarn = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-yarn = %{version}-%{release}

%description yarn-resourcemanager
The resource manager manages the global assignment of compute resources to applications

%package yarn-nodemanager
Summary: YARN Node Manager
Group: System/Daemons
Requires: %{name}-yarn = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-yarn = %{version}-%{release}

%description yarn-nodemanager
The NodeManager is the per-machine framework agent who is responsible for
containers, monitoring their resource usage (cpu, memory, disk, network) and
reporting the same to the ResourceManager/Scheduler.

%package yarn-proxyserver
Summary: YARN Web Proxy
Group: System/Daemons
Requires: %{name}-yarn = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-yarn = %{version}-%{release}

%description yarn-proxyserver
The web proxy server sits in front of the YARN application master web UI.

%package yarn-timelineserver
Summary: YARN Timeline Server
Group: System/Daemons
Requires: %{name}-yarn = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-yarn = %{version}-%{release}

%description yarn-timelineserver
Storage and retrieval of applications' current as well as historic information in a generic fashion is solved in YARN through the Timeline Server.

%package mapreduce-historyserver
Summary: MapReduce History Server
Group: System/Daemons
Requires: %{name}-mapreduce = %{version}-%{release}
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-mapreduce = %{version}-%{release}

%description mapreduce-historyserver
The History server keeps records of the different activities being performed on a Apache Hadoop cluster

%package client
Summary: Hadoop client side dependencies
Group: System/Daemons
Requires: %{name} = %{version}-%{release}
Requires: %{name}-hdfs = %{version}-%{release}
Requires: %{name}-yarn = %{version}-%{release}
Requires: %{name}-mapreduce = %{version}-%{release}

%description client
Installation of this package will provide you with all the dependencies for Hadoop clients.

%package conf-pseudo
Summary: Pseudo-distributed Hadoop configuration
Group: System/Daemons
Requires: %{name} = %{version}-%{release}
Requires: %{name}-hdfs-namenode = %{version}-%{release}
Requires: %{name}-hdfs-datanode = %{version}-%{release}
Requires: %{name}-hdfs-secondarynamenode = %{version}-%{release}
Requires: %{name}-yarn-resourcemanager = %{version}-%{release}
Requires: %{name}-yarn-nodemanager = %{version}-%{release}
Requires: %{name}-mapreduce-historyserver = %{version}-%{release}

%description conf-pseudo
Contains configuration files for a "pseudo-distributed" Hadoop deployment.
In this mode, each of the hadoop components runs as a separate Java process,
but all on the same machine.

%package doc
Summary: Hadoop Documentation
Group: Documentation
%description doc
Documentation for Hadoop

%package libhdfs
Summary: Hadoop Filesystem Library
Group: Development/Libraries
Requires: %{name}-hdfs = %{version}-%{release}
# TODO: reconcile libjvm
AutoReq: no

%description libhdfs
Hadoop Filesystem Library

%package hdfs-fuse
Summary: Mountable HDFS
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: %{name}-libhdfs = %{version}-%{release}
Requires: %{name}-client = %{version}-%{release}
Requires: fuse
AutoReq: no

%if %{?suse_version:1}0
Requires: libfuse2
%else
Requires: fuse-libs
%endif


%description hdfs-fuse
These projects (enumerated below) allow HDFS to be mounted (on most flavors of Unix) as a standard file system using


%prep
%setup -n %{hadoop_sname}-%{hadoop_base_version}-src

#BIGTOP_PATCH_COMMANDS
%build
# This assumes that you installed Java JDK 6 and set JAVA_HOME
# This assumes that you installed Forrest and set FORREST_HOME

env HADOOP_VERSION=%{hadoop_base_version} HADOOP_ARCH=%{hadoop_arch} bash %{SOURCE1}

%clean
%__rm -rf $RPM_BUILD_ROOT

%install
%__rm -rf $RPM_BUILD_ROOT

%__install -d -m 0755 $RPM_BUILD_ROOT/%{lib_hadoop}

env HADOOP_VERSION=%{hadoop_base_version} HDP_VERSION=%{hdp_version} bash %{SOURCE2} \
  --distro-dir=$RPM_SOURCE_DIR \
  --build-dir=$PWD/build \
  --httpfs-dir=$RPM_BUILD_ROOT%{lib_httpfs} \
  --system-include-dir=$RPM_BUILD_ROOT%{hadoop_base}/%{_includedir} \
  --system-libexec-dir=$RPM_BUILD_ROOT%{lib_hadoop}/libexec \
  --prefix=$RPM_BUILD_ROOT \
  --doc-dir=$RPM_BUILD_ROOT%{doc_hadoop} \
  --example-dir=$RPM_BUILD_ROOT%{doc_hadoop}/examples \
  --native-build-string=%{hadoop_arch} \
  --man-dir=$RPM_BUILD_ROOT%{man_hadoop} \
  --hadoop-dir=$RPM_BUILD_ROOT%{lib_hadoop} \
  --bin-dir=$RPM_BUILD_ROOT%{bin_hadoop} \
  --etc-dir=$RPM_BUILD_ROOT%{hadoop_base}/etc \

sed -i 's#HDP_PLACEHOLDER#%{hadoop_base}#g' $RPM_BUILD_ROOT/%{lib_hadoop}/libexec/init-hcfs.groovy

cat >> ${SYSTEM_LIBEXEC_DIR}/hadoop-config.sh <<EOF
if [[ -z \${IS_HIVE2} && -d "%{hadoop_base}/tez" ]]; then
  export HADOOP_CLASSPATH=\${HADOOP_CLASSPATH}:%{hadoop_base}/tez/*:%{hadoop_base}/tez/lib/*:%{hadoop_base}/tez/conf
  export CLASSPATH=\${CLASSPATH}:%{hadoop_base}/tez/*:%{hadoop_base}/tez/lib/*:%{hadoop_base}/tez/conf
fi

#Adding Ranger check to the hadoop-config.sh
[ -f "%{lib_hadoop}/conf/set-hdfs-plugin-env.sh" ] && . "%{lib_hadoop}/conf/set-hdfs-plugin-env.sh" ]

EOF

# Workaround for BIGTOP-583
%__rm -f $RPM_BUILD_ROOT/%{lib_hadoop}-*/lib/slf4j-log4j12-*.jar

# Install top level /etc/default files
%__install -d -m 0755 $RPM_BUILD_ROOT/%{hadoop_base}/etc/default
%__cp %{SOURCE3} $RPM_BUILD_ROOT/%{hadoop_base}/etc/default/%{hadoop_sname}

cat >> $RPM_BUILD_ROOT/%{hadoop_base}/etc/default/%{hadoop_sname} <<EOF
export HADOOP_HOME_WARN_SUPPRESS=true
export HADOOP_HOME=%{hadoop_home}
export HADOOP_PREFIX=%{hadoop_home}

export HADOOP_LIBEXEC_DIR=%{lib_hadoop}/libexec
export HADOOP_CONF_DIR=/etc/hadoop/conf

export HADOOP_COMMON_HOME=%{lib_hadoop}
export HADOOP_HDFS_HOME=%{lib_hdfs}
export HADOOP_MAPRED_HOME=%{lib_mapreduce}
export HADOOP_YARN_HOME=%{lib_yarn}
EOF
# FIXME: BIGTOP-463
echo 'export JSVC_HOME=%{libexecdir}/bigtop-utils' >> $RPM_BUILD_ROOT/%{hadoop_base}/etc/default/%{hadoop_sname}
%__cp %{SOURCE4} $RPM_BUILD_ROOT/%{hadoop_base}/etc/default/%{hadoop_sname}-fuse

# Generate the init.d scripts
for service in %{hadoop_services}
do
       %__install -d -m 0755 $RPM_BUILD_ROOT/%{hadoop_home}-${service/-*/}/%{initd_dir}/
       bash %{SOURCE11} $RPM_SOURCE_DIR/%{hadoop_sname}-${service}.svc rpm $RPM_BUILD_ROOT/%{hadoop_home}-${service/-*/}/%{initd_dir}/%{hadoop_sname}-${service}
       cp $RPM_SOURCE_DIR/${service/-*/}.default $RPM_BUILD_ROOT/%{hadoop_base}/etc/default/%{hadoop_sname}-${service}
       chmod 644 $RPM_BUILD_ROOT/%{hadoop_base}/etc/default/%{hadoop_sname}-${service}
done

# Install security limits
%__install -d -m 0755 $RPM_BUILD_ROOT/%{hadoop_base}/etc/security/limits.d
%__install -m 0644 %{SOURCE8} $RPM_BUILD_ROOT/%{hadoop_base}/etc/security/limits.d/hdfs.conf
%__install -m 0644 %{SOURCE9} $RPM_BUILD_ROOT/%{hadoop_base}/etc/security/limits.d/yarn.conf
%__install -m 0644 %{SOURCE10} $RPM_BUILD_ROOT/%{hadoop_base}/etc/security/limits.d/mapreduce.conf

# /var/lib/*/cache
%__install -d -m 1777 $RPM_BUILD_ROOT/%{state_yarn}/cache
%__install -d -m 1777 $RPM_BUILD_ROOT/%{state_hdfs}/cache
%__install -d -m 1777 $RPM_BUILD_ROOT/%{state_mapreduce}/cache
%__install -d -m 1777 $RPM_BUILD_ROOT/%{state_httpfs}/cache
# /var/log/*
%__install -d -m 0755 $RPM_BUILD_ROOT/%{log_yarn}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{log_hdfs}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{log_mapreduce}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{log_httpfs}
# /var/run/*
%__install -d -m 0755 $RPM_BUILD_ROOT/%{run_yarn}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{run_hdfs}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{run_mapreduce}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{run_httpfs}

%pre
getent group hadoop >/dev/null || groupadd -r hadoop

%pre hdfs
getent group hdfs >/dev/null   || groupadd -r hdfs
getent passwd hdfs >/dev/null || /usr/sbin/useradd --comment "Hadoop HDFS" --shell /bin/bash -M -r -g hdfs -G hadoop --home %{state_hdfs} hdfs

%pre httpfs
getent group httpfs >/dev/null   || groupadd -r httpfs
getent passwd httpfs >/dev/null || /usr/sbin/useradd --comment "Hadoop HTTPFS" --shell /bin/bash -M -r -g httpfs -G hadoop --home %{state_httpfs} httpfs

%pre yarn
getent group yarn >/dev/null   || groupadd -r yarn
getent passwd yarn >/dev/null || /usr/sbin/useradd --comment "Hadoop Yarn" --shell /bin/bash -M -r -g yarn -G hadoop --home %{state_yarn} yarn

%pre mapreduce
getent group mapred >/dev/null   || groupadd -r mapred
getent passwd mapred >/dev/null || /usr/sbin/useradd --comment "Hadoop MapReduce" --shell /bin/bash -M -r -g mapred -G hadoop --home %{state_mapreduce} mapred

%post
if [ !  -e "/etc/hadoop/conf" ]; then
    rm -f /etc/hadoop/conf
    mkdir -p /etc/hadoop/conf
    cp -rp %{etc_hadoop}/conf.empty/* /etc/hadoop/conf
fi
/usr/bin/hdp-select --rpm-mode set hadoop-client %{hdp_version}
/usr/bin/hdp-select --rpm-mode set hadoop-hdfs-datanode %{hdp_version}
/usr/bin/hdp-select --rpm-mode set hadoop-hdfs-journalnode %{hdp_version}
/usr/bin/hdp-select --rpm-mode set hadoop-hdfs-nfs3 %{hdp_version}
/usr/bin/hdp-select --rpm-mode set hadoop-hdfs-namenode %{hdp_version}
/usr/bin/hdp-select --rpm-mode set hadoop-hdfs-portmap %{hdp_version}
/usr/bin/hdp-select --rpm-mode set hadoop-hdfs-secondarynamenode %{hdp_version}
/usr/bin/hdp-select --rpm-mode set hadoop-mapreduce-historyserver %{hdp_version}
/usr/bin/hdp-select --rpm-mode set hadoop-yarn-resourcemanager %{hdp_version}
/usr/bin/hdp-select --rpm-mode set hadoop-yarn-nodemanager %{hdp_version}
/usr/bin/hdp-select --rpm-mode set hadoop-yarn-timelineserver %{hdp_version}

%post httpfs
if [ !  -e "/etc/hadoop-httpfs/conf" ]; then
    rm -f /etc/hadoop-httpfs/conf
    mkdir -p /etc/hadoop-httpfs/conf
    cp -rp %{etc_httpfs}/conf.empty/* /etc/hadoop-httpfs/conf

    rm -rf %{tomcat_deployment_httpfs}/conf
    mkdir -p %{tomcat_deployment_httpfs}/conf
    cp -rp %{etc_httpfs}/tomcat-conf.dist/conf/* %{tomcat_deployment_httpfs}/conf
fi
/usr/bin/hdp-select --rpm-mode set hadoop-httpfs %{hdp_version}

%files yarn
%defattr(-,root,root)
%config(noreplace) %{etc_hadoop}/conf.empty/yarn-env.sh
%config(noreplace) %{etc_hadoop}/conf.empty/yarn-site.xml
%config(noreplace) %{etc_hadoop}/conf.empty/capacity-scheduler.xml
%config(noreplace) %{etc_hadoop}/conf.empty/container-executor.cfg
%config(noreplace) %{hadoop_base}/etc/security/limits.d/yarn.conf
%{lib_hadoop}/libexec/yarn-config.sh
%{lib_yarn}
%attr(4754,root,yarn) %{lib_yarn}/bin/container-executor
%{bin_hadoop}/yarn
%attr(0775,yarn,hadoop) %{run_yarn}
%attr(0775,yarn,hadoop) %{log_yarn}
%attr(0755,yarn,hadoop) %{state_yarn}
%attr(1777,yarn,hadoop) %{state_yarn}/cache

%exclude %{lib_yarn}/%{initd_dir}/*

%files hdfs
%defattr(-,root,root)
%config(noreplace) %{etc_hadoop}/conf.empty/hdfs-site.xml
%config(noreplace) %{hadoop_base}/etc/security/limits.d/hdfs.conf
%{lib_hdfs}
%{lib_hadoop}/libexec/hdfs-config.sh
%{bin_hadoop}/hdfs
%attr(0775,hdfs,hadoop) %{run_hdfs}
%attr(0775,hdfs,hadoop) %{log_hdfs}
%attr(0755,hdfs,hadoop) %{state_hdfs}
%attr(1777,hdfs,hadoop) %{state_hdfs}/cache
%{lib_hadoop}/libexec/init-hdfs.sh
%{lib_hadoop}/libexec/init-hcfs.json
%{lib_hadoop}/libexec/init-hcfs.groovy

%exclude %{lib_hdfs}/%{initd_dir}/*

%files mapreduce
%defattr(-,root,root)
%config(noreplace) %{etc_hadoop}/conf.empty/mapred-site.xml
%config(noreplace) %{etc_hadoop}/conf.empty/mapred-env.sh
%config(noreplace) %{etc_hadoop}/conf.empty/mapred-queues.xml.template
%config(noreplace) %{etc_hadoop}/conf.empty/mapred-site.xml.template
%config(noreplace) %{hadoop_base}/etc/security/limits.d/mapreduce.conf
%{lib_mapreduce}
%{lib_hadoop}/libexec/mapred-config.sh
%{bin_hadoop}/mapred
%attr(0775,mapred,hadoop) %{run_mapreduce}
%attr(0775,mapred,hadoop) %{log_mapreduce}
%attr(0775,mapred,hadoop) %{state_mapreduce}
%attr(1777,mapred,hadoop) %{state_mapreduce}/cache


%files
%defattr(-,root,root)
%config(noreplace) %{etc_hadoop}/conf.empty/core-site.xml
%config(noreplace) %{etc_hadoop}/conf.empty/hadoop-metrics.properties
%config(noreplace) %{etc_hadoop}/conf.empty/hadoop-metrics2.properties
%config(noreplace) %{etc_hadoop}/conf.empty/log4j.properties
%config(noreplace) %{etc_hadoop}/conf.empty/slaves
%config(noreplace) %{etc_hadoop}/conf.empty/ssl-client.xml.example
%config(noreplace) %{etc_hadoop}/conf.empty/ssl-server.xml.example
%config(noreplace) %{etc_hadoop}/conf.empty/configuration.xsl
%config(noreplace) %{etc_hadoop}/conf.empty/hadoop-env.sh
%config(noreplace) %{etc_hadoop}/conf.empty/hadoop-policy.xml
%config(noreplace) %{etc_hadoop}/conf.empty/kms-acls.xml
%config(noreplace) %{etc_hadoop}/conf.empty/kms-env.sh
%config(noreplace) %{etc_hadoop}/conf.empty/kms-log4j.properties
%config(noreplace) %{etc_hadoop}/conf.empty/kms-site.xml
%config(noreplace) %{hadoop_base}/etc/default/hadoop
%{hadoop_base}/etc/bash_completion.d/hadoop
%{lib_hadoop}/*.jar
%{lib_hadoop}/lib
%{lib_hadoop}/sbin
%{lib_hadoop}/bin
%{lib_hadoop}/etc
%{lib_hadoop}/libexec/hadoop-config.sh
%{lib_hadoop}/libexec/hadoop-layout.sh
%{lib_hadoop}/libexec/kms-config.sh
%{lib_hadoop}/mapreduce.tar.gz
%{lib_hadoop}/conf
%{bin_hadoop}/hadoop
%{man_hadoop}/man1/hadoop.1.*
%{man_hadoop}/man1/yarn.1.*
%{man_hadoop}/man1/hdfs.1.*
%{man_hadoop}/man1/mapred.1.*

# Shouldn't the following be moved to hadoop-hdfs?
%exclude %{lib_hadoop}/bin/fuse_dfs
%exclude %{lib_hadoop}/lib/native/libhdfs.so*

%files doc
%defattr(-,root,root)
%doc %{doc_hadoop}

%files httpfs
%defattr(-,root,root)
%config(noreplace) %{etc_httpfs}
%config(noreplace) %{hadoop_base}/etc/default/%{hadoop_sname}-httpfs
%{lib_hadoop}/libexec/httpfs-config.sh
%{lib_hadoop}-httpfs/%{initd_dir}/%{hadoop_sname}-httpfs
%{lib_httpfs}
%attr(0775,httpfs,hadoop) %{run_httpfs}
%attr(0775,httpfs,hadoop) %{log_httpfs}
%attr(0775,httpfs,hadoop) %{state_httpfs}
%attr(1777,httpfs,hadoop) %{state_httpfs}/cache

# Service file management RPMs
%define service_macro() \
%files %1 \
%defattr(-,root,root) \
%{lib_hadoop}-%2/%{initd_dir}/%{hadoop_sname}-%1 \
%config(noreplace) %{hadoop_base}/etc/default/%{hadoop_sname}-%1 \
\
%post %1 \
ln -sf rc.d/init.d/ %{lib_hadoop}-%2/etc/init.d \
%postun %1 \
if [ "$1" -eq 0 ]; then \
    rm -f %{lib_hadoop}-%2/etc/init.d \
fi

%service_macro hdfs-namenode hdfs
%service_macro hdfs-secondarynamenode hdfs
%service_macro hdfs-zkfc hdfs
%service_macro hdfs-journalnode hdfs
%service_macro hdfs-datanode hdfs
%service_macro yarn-resourcemanager yarn
%service_macro yarn-nodemanager yarn
%service_macro yarn-proxyserver yarn
%service_macro yarn-timelineserver yarn
%service_macro mapreduce-historyserver mapreduce

%files conf-pseudo
%defattr(-,root,root)
%config(noreplace) %attr(755,root,root) %{etc_hadoop}/conf.pseudo

%files client
%defattr(-,root,root)
%{lib_hadoop}/client

%files libhdfs
%defattr(-,root,root)
%{lib_hadoop}/lib/native/libhdfs*
%{hadoop_base}/%{_includedir}/

%files hdfs-fuse
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{hadoop_base}/etc/default/hadoop-fuse
%attr(0755,root,root) %{lib_hadoop}/bin/fuse_dfs
%attr(0755,root,root) %{bin_hadoop}/hadoop-fuse-dfs


