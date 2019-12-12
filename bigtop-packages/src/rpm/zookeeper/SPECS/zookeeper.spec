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
%define zookeeper_sname zookeeper
%define zookeeper_home %{zookeeper_base}/%{zookeeper_sname}
%define etc_zookeeper %{zookeeper_base}/etc/%{zookeeper_sname}
%define bin_zookeeper %{zookeeper_home}/bin
%define lib_zookeeper %{zookeeper_home}/lib
%define log_zookeeper /var/log/%{zookeeper_sname}
%define run_zookeeper /var/run/%{zookeeper_sname}
#%define vlb_zookeeper /var/lib/%{name}
%define svc_zookeeper %{zookeeper_sname}-server
%define svc_zookeeper_rest %{zookeeper_sname}-rest
%define man_dir %{zookeeper_home}/man

%if  %{?suse_version:1}0

# Only tested on openSUSE 11.4. le'ts update it for previous release when confirmed
%if 0%{suse_version} > 1130
%define suse_check \# Define an empty suse_check for compatibility with older sles
%endif

# SLES is more strict anc check all symlinks point to valid path
# But we do point to a hadoop jar which is not there at build time
# (but would be at install time).
# Since our package build system does not handle dependencies,
# these symlink checks are deactivated
%define __os_install_post \
    %{suse_check} ; \
    /usr/lib/rpm/brp-compress ; \
    %{nil}


%define doc_zookeeper %{_docdir}/%{name}
%define alternatives_cmd update-alternatives
%define alternatives_dep update-alternatives
%define chkconfig_dep    aaa_base
%define service_dep      aaa_base
%global initd_dir %{_sysconfdir}/rc.d

%else

%define doc_zookeeper %{zookeeper_home}/doc
%define alternatives_cmd alternatives
%define alternatives_dep chkconfig 
%define chkconfig_dep    chkconfig
%define service_dep      initscripts
%global initd_dir %{zookeeper_home}%{_sysconfdir}/rc.d/init.d

%endif



Name: %{zookeeper_name}
Version: %{zookeeper_version}
Release: %{zookeeper_release}
Summary: A high-performance coordination service for distributed applications.
URL: http://zookeeper.apache.org/
Group: Development/Libraries
Buildroot: %{_topdir}/INSTALL/%{name}-%{version}
License: ASL 2.0
Source0: %{zookeeper_sname}-%{zookeeper_base_version}.tar.gz
Source1: do-component-build
Source2: install_zookeeper.sh
Source3: zookeeper-server.sh
Source4: zookeeper-server.sh.suse
Source5: zookeeper.1
Source6: zoo.cfg
Source7: zookeeper.default
Source8: init.d.tmpl
Source9: zookeeper-rest.svc
#BIGTOP_PATCH_FILES
BuildRequires: autoconf, automake, cppunit-devel
Requires(pre): coreutils, /usr/sbin/groupadd, /usr/sbin/useradd
Requires: bigtop-utils >= 0.7
Requires: hdp-select >= %{hdp_version}

%description 
ZooKeeper is a centralized service for maintaining configuration information, 
naming, providing distributed synchronization, and providing group services. 
All of these kinds of services are used in some form or another by distributed 
applications. Each time they are implemented there is a lot of work that goes 
into fixing the bugs and race conditions that are inevitable. Because of the 
difficulty of implementing these kinds of services, applications initially 
usually skimp on them ,which make them brittle in the presence of change and 
difficult to manage. Even when done correctly, different implementations of these services lead to management complexity when the applications are deployed.  

%package server
Summary: The Hadoop Zookeeper server
Group: System/Daemons
Requires: %{name} = %{version}-%{release}

%if  %{?suse_version:1}0
# Required for init scripts
Requires: insserv
%endif

%if  0%{?mgaversion}
# Required for init scripts
Requires: initscripts
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0
# Required for init scripts
Requires: /lib/lsb/init-functions
%endif


%description server
This package starts the zookeeper server on startup

%package rest
Summary: ZooKeeper REST Server
Group: System/Daemons
Requires: %{name} = %{version}-%{release}

%package native
Summary: C bindings for ZooKeeper clients
Group: Development/Libraries

%description native
Provides native libraries and development headers for C / C++ ZooKeeper clients. Consists of both single-threaded and multi-threaded implementations.

%description rest
This package starts the zookeeper REST server on startup

%prep
%setup -n %{zookeeper_sname}-%{zookeeper_base_version}

#BIGTOP_PATCH_COMMANDS

%build
#solve proxy issue
. /etc/profile
bash %{SOURCE1}

%install
%__rm -rf $RPM_BUILD_ROOT
cp $RPM_SOURCE_DIR/zookeeper.1 $RPM_SOURCE_DIR/zoo.cfg $RPM_SOURCE_DIR/zookeeper.default .
bash %{SOURCE2} \
          --build-dir=build/%{zookeeper_sname}-%{zookeeper_base_version} \
          --lib-dir=%{lib_zookeeper} \
          --bin-dir=%{bin_zookeeper} \
          --doc-dir=%{doc_zookeeper} \
          --home-dir=%{zookeeper_home} \
          --man-dir=%{man_dir} \
          --etc-dir=%{etc_zookeeper} \
          --prefix=$RPM_BUILD_ROOT \
          --system-include-dir=%{zookeeper_home}%{_includedir} \
          --system-lib-dir=%{zookeeper_home}%{_libdir}

%if  %{?suse_version:1}0
orig_init_file=%{SOURCE4}
%else
orig_init_file=%{SOURCE3}
%endif

%__install -d -m 0755 $RPM_BUILD_ROOT/%{initd_dir}/
init_file=$RPM_BUILD_ROOT/%{initd_dir}/%{svc_zookeeper}
%__cp $orig_init_file $init_file
chmod 755 $init_file

# Install Zookeeper REST server init script
init_file=$RPM_BUILD_ROOT/%{initd_dir}/zookeeper-rest
bash $RPM_SOURCE_DIR/init.d.tmpl $RPM_SOURCE_DIR/zookeeper-rest.svc rpm $init_file

%pre
getent group zookeeper >/dev/null || groupadd -r zookeeper
getent passwd zookeeper > /dev/null || useradd -c "ZooKeeper" -s /sbin/nologin -g zookeeper -r -d %{run_zookeeper} zookeeper 2> /dev/null || :

%__install -d -o zookeeper -g zookeeper -m 0755 %{run_zookeeper}
%__install -d -o zookeeper -g zookeeper -m 0755 %{log_zookeeper}

%post
/usr/bin/hdp-select --rpm-mode set zookeeper-client %{hdp_version}
/usr/bin/hdp-select --rpm-mode set zookeeper-server %{hdp_version}

if [ !  -e "/etc/zookeeper/conf" ]; then
    rm -f /etc/zookeeper/conf
    mkdir -p /etc/zookeeper/conf
    cp -rp %{etc_zookeeper}/conf.dist/* /etc/zookeeper/conf
fi

%files
%defattr(-,root,root)
%config(noreplace) %{etc_zookeeper}/conf.dist
%{lib_zookeeper}
%{zookeeper_home}/zookeeper*.jar
%{zookeeper_home}/contrib
%{zookeeper_home}/conf
%{bin_zookeeper}/zkServer.sh
%{bin_zookeeper}/zkEnv.sh
%{bin_zookeeper}/zkCli.sh
%{bin_zookeeper}/zkCleanup.sh
%{bin_zookeeper}/zkServer-initialize.sh
%{bin_zookeeper}/zookeeper-server
%{bin_zookeeper}/zookeeper-server-initialize
%{bin_zookeeper}/zookeeper-client
%{bin_zookeeper}/zookeeper-server-cleanup
%doc %{doc_zookeeper}
%{man_dir}/man1/zookeeper.1.*

%files server
%attr(0755,root,root) %{initd_dir}/%{svc_zookeeper}

%files rest
%attr(0755,root,root) %{initd_dir}/%{svc_zookeeper_rest}

%files native
%defattr(-,root,root)
%{lib_zookeeper}-native
%{bin_zookeeper}/cli_*
%{bin_zookeeper}/load_gen*
%{zookeeper_home}%{_includedir}/zookeeper
%{zookeeper_home}%{_libdir}/*

