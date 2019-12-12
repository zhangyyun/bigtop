#!/bin/bash -x
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

set -ex

usage() {
  echo "
usage: $0 <options>
  Required not-so-options:
     --distro-dir=DIR            path to distro specific files (debian/RPM)
     --build-dir=DIR             path to hive/build/dist
     --prefix=PREFIX             path to install into

  Optional options:
     --native-build-string       eg Linux-amd-64 (optional - no native installed if not set)
     ... [ see source for more similar options ]
  "
  exit 1
}

OPTS=$(getopt \
  -n $0 \
  -o '' \
  -l 'prefix:' \
  -l 'distro-dir:' \
  -l 'build-dir:' \
  -l 'native-build-string:' \
  -l 'hadoop-dir:' \
  -l 'httpfs-dir:' \
  -l 'hdfs-dir:' \
  -l 'yarn-dir:' \
  -l 'mapreduce-dir:' \
  -l 'client-dir:' \
  -l 'system-include-dir:' \
  -l 'system-lib-dir:' \
  -l 'system-libexec-dir:' \
  -l 'hadoop-etc-dir:' \
  -l 'httpfs-etc-dir:' \
  -l 'doc-dir:' \
  -l 'man-dir:' \
  -l 'example-dir:' \
  -l 'apache-branch:' \
  -l 'bin-dir:' \
  -l 'etc-dir:' \
  -- "$@")

if [ $? != 0 ] ; then
    usage
fi

eval set -- "$OPTS"
while true ; do
    case "$1" in
        --prefix)
        PREFIX=$2 ; shift 2
        ;;
        --distro-dir)
        DISTRO_DIR=$2 ; shift 2
        ;;
        --httpfs-dir)
        HTTPFS_DIR=$2 ; shift 2
        ;;
        --hadoop-dir)
        HADOOP_DIR=$2 ; shift 2
        ;;
        --hdfs-dir)
        HDFS_DIR=$2 ; shift 2
        ;;
        --yarn-dir)
        YARN_DIR=$2 ; shift 2
        ;;
        --mapreduce-dir)
        MAPREDUCE_DIR=$2 ; shift 2
        ;;
        --client-dir)
        CLIENT_DIR=$2 ; shift 2
        ;;
        --system-include-dir)
        SYSTEM_INCLUDE_DIR=$2 ; shift 2
        ;;
        --system-lib-dir)
        SYSTEM_LIB_DIR=$2 ; shift 2
        ;;
        --system-libexec-dir)
        SYSTEM_LIBEXEC_DIR=$2 ; shift 2
        ;;
        --build-dir)
        BUILD_DIR=$2 ; shift 2
        ;;
        --native-build-string)
        NATIVE_BUILD_STRING=$2 ; shift 2
        ;;
        --doc-dir)
        DOC_DIR=$2 ; shift 2
        ;;
        --hadoop-etc-dir)
        HADOOP_ETC_DIR=$2 ; shift 2
        ;;
        --httpfs-etc-dir)
        HTTPFS_ETC_DIR=$2 ; shift 2
        ;;
        --man-dir)
        MAN_DIR=$2 ; shift 2
        ;;
        --example-dir)
        EXAMPLE_DIR=$2 ; shift 2
        ;;
        --bin-dir)
        BIN_DIR=$2 ; shift 2
        ;;
        --etc-dir)
        ETC_DIR=$2 ; shift 2
        ;;
        --)
        shift ; break
        ;;
        *)
        echo "Unknown option: $1"
        usage
        exit 1
        ;;
    esac
done

for var in PREFIX BUILD_DIR; do
  if [ -z "$(eval "echo \$$var")" ]; then
    echo Missing param: $var
    usage
  fi
done

HADOOP_DIR=${HADOOP_DIR:-$PREFIX/usr/lib/hadoop}
HDFS_DIR=${HDFS_DIR:-${HADOOP_DIR}-hdfs}
YARN_DIR=${YARN_DIR:-${HADOOP_DIR}-yarn}
MAPREDUCE_DIR=${MAPREDUCE_DIR:-${HADOOP_DIR}-mapreduce}
CLIENT_DIR=${CLIENT_DIR:-${HADOOP_DIR}/client}
HTTPFS_DIR=${HTTPFS_DIR:-${HADOOP_DIR}-httpfs}
SYSTEM_LIB_DIR=${SYSTEM_LIB_DIR:-/usr/lib}
BIN_DIR=${BIN_DIR:-$PREFIX/usr/bin}
DOC_DIR=${DOC_DIR:-$PREFIX/usr/share/doc/hadoop}
MAN_DIR=${MAN_DIR:-$PREFIX/usr/man}
SYSTEM_INCLUDE_DIR=${SYSTEM_INCLUDE_DIR:-$PREFIX/usr/include}
SYSTEM_LIBEXEC_DIR=${SYSTEM_LIBEXEC_DIR:-$PREFIX/usr/libexec}
EXAMPLE_DIR=${EXAMPLE_DIR:-$DOC_DIR/examples}
ETC_DIR=${ETC_DIR:-$PREFIX/etc}
HADOOP_ETC_DIR=${HADOOP_ETC_DIR:-${ETC_DIR}/hadoop}
HTTPFS_ETC_DIR=${HTTPFS_ETC_DIR:-${ETC_DIR}/hadoop-httpfs}
BASH_COMPLETION_DIR=${BASH_COMPLETION_DIR:-${ETC_DIR}/bash_completion.d}

HADOOP_NATIVE_LIB_DIR=${HADOOP_DIR}/lib/native

##Needed for some distros to find ldconfig
export PATH="/sbin/:$PATH"

#libexec
install -d -m 0755 ${SYSTEM_LIBEXEC_DIR}
cp ${BUILD_DIR}/libexec/* ${SYSTEM_LIBEXEC_DIR}/
cp ${DISTRO_DIR}/hadoop-layout.sh ${SYSTEM_LIBEXEC_DIR}/
install -m 0755 ${DISTRO_DIR}/init-hdfs.sh ${SYSTEM_LIBEXEC_DIR}/
cat >> ${SYSTEM_LIBEXEC_DIR}/hadoop-layout.sh <<EOF
HADOOP_LIBEXEC_DIR=${SYSTEM_LIBEXEC_DIR#${PREFIX}}
HADOOP_CONF_DIR=${HADOOP_DIR#${PREFIX}}/conf
HADOOP_COMMON_HOME=${HADOOP_DIR#${PREFIX}}
HADOOP_HDFS_HOME=${HDFS_DIR#${PREFIX}}
HADOOP_MAPRED_HOME=${MAPREDUCE_DIR#${PREFIX}}
HADOOP_YARN_HOME=${YARN_DIR#${PREFIX}}
EOF
install -m 0755 ${DISTRO_DIR}/init-hcfs.json ${SYSTEM_LIBEXEC_DIR}/
install -m 0755 ${DISTRO_DIR}/init-hcfs.groovy ${SYSTEM_LIBEXEC_DIR}/
rm -rf ${SYSTEM_LIBEXEC_DIR}/*.cmd

# hadoop jar
install -d -m 0755 ${HADOOP_DIR}
cp ${BUILD_DIR}/share/hadoop/common/*.jar ${HADOOP_DIR}/
cp ${BUILD_DIR}/share/hadoop/common/lib/hadoop-auth*.jar ${HADOOP_DIR}/
cp ${BUILD_DIR}/share/hadoop/mapreduce/lib/hadoop-annotations*.jar ${HADOOP_DIR}/
install -d -m 0755 ${MAPREDUCE_DIR}
cp ${BUILD_DIR}/share/hadoop/mapreduce/hadoop-mapreduce*.jar ${MAPREDUCE_DIR}
cp ${BUILD_DIR}/share/hadoop/tools/lib/*.jar ${MAPREDUCE_DIR}
install -d -m 0755 ${HDFS_DIR}
cp ${BUILD_DIR}/share/hadoop/hdfs/*.jar ${HDFS_DIR}/
install -d -m 0755 ${YARN_DIR}
cp ${BUILD_DIR}/share/hadoop/yarn/hadoop-yarn*.jar ${YARN_DIR}/
chmod 644 ${HADOOP_DIR}/*.jar ${MAPREDUCE_DIR}/*.jar ${HDFS_DIR}/*.jar ${YARN_DIR}/*.jar

# lib jars
install -d -m 0755 ${HADOOP_DIR}/lib
cp ${BUILD_DIR}/share/hadoop/common/lib/*.jar ${HADOOP_DIR}/lib
install -d -m 0755 ${MAPREDUCE_DIR}/lib
cp ${BUILD_DIR}/share/hadoop/mapreduce/lib/*.jar ${MAPREDUCE_DIR}/lib
install -d -m 0755 ${HDFS_DIR}/lib 
cp ${BUILD_DIR}/share/hadoop/hdfs/lib/*.jar ${HDFS_DIR}/lib
install -d -m 0755 ${YARN_DIR}/lib
cp ${BUILD_DIR}/share/hadoop/yarn/lib/*.jar ${YARN_DIR}/lib
chmod 644 ${HADOOP_DIR}/lib/*.jar ${MAPREDUCE_DIR}/lib/*.jar ${HDFS_DIR}/lib/*.jar ${YARN_DIR}/lib/*.jar

# Install webapps
cp -ra ${BUILD_DIR}/share/hadoop/hdfs/webapps ${HDFS_DIR}/

# bin
install -d -m 0755 ${HADOOP_DIR}/bin
cp -a ${BUILD_DIR}/bin/{hadoop,rcc,fuse_dfs} ${HADOOP_DIR}/bin
install -d -m 0755 ${HDFS_DIR}/bin
cp -a ${BUILD_DIR}/bin/hdfs ${HDFS_DIR}/bin
install -d -m 0755 ${YARN_DIR}/bin
cp -a ${BUILD_DIR}/bin/{yarn,container-executor} ${YARN_DIR}/bin
install -d -m 0755 ${MAPREDUCE_DIR}/bin
cp -a ${BUILD_DIR}/bin/mapred ${MAPREDUCE_DIR}/bin
# FIXME: MAPREDUCE-3980
cp -a ${BUILD_DIR}/bin/mapred ${YARN_DIR}/bin

# sbin
install -d -m 0755 ${HADOOP_DIR}/sbin
cp -a ${BUILD_DIR}/sbin/{hadoop-daemon,hadoop-daemons,slaves}.sh ${HADOOP_DIR}/sbin
install -d -m 0755 ${HDFS_DIR}/sbin
cp -a ${BUILD_DIR}/sbin/{distribute-exclude,refresh-namenodes}.sh ${HDFS_DIR}/sbin
install -d -m 0755 ${YARN_DIR}/sbin
cp -a ${BUILD_DIR}/sbin/{yarn-daemon,yarn-daemons}.sh ${YARN_DIR}/sbin
install -d -m 0755 ${MAPREDUCE_DIR}/sbin
cp -a ${BUILD_DIR}/sbin/mr-jobhistory-daemon.sh ${MAPREDUCE_DIR}/sbin

# native libs
install -d -m 0755 ${HADOOP_NATIVE_LIB_DIR}

install -d -m 0755 ${SYSTEM_INCLUDE_DIR}
cp ${BUILD_DIR}/include/* ${SYSTEM_INCLUDE_DIR}/

cp ${BUILD_DIR}/lib/native/*.a ${HADOOP_NATIVE_LIB_DIR}/
for library in `cd ${BUILD_DIR}/lib/native ; ls libsnappy.so.1.* 2>/dev/null` libhadoop.so.1.0.0 libhdfs.so.0.0.0; do
  cp ${BUILD_DIR}/lib/native/${library} ${HADOOP_NATIVE_LIB_DIR}/
  ldconfig -vlN ${HADOOP_NATIVE_LIB_DIR}/${library}
  ln -s ${library} ${HADOOP_NATIVE_LIB_DIR}/${library/.so.*/}.so
done

# Make bin wrappers
mkdir -p $BIN_DIR

install -m 0755 ${DISTRO_DIR}/kill-name-node.sh ${HDFS_DIR}/bin/kill-name-node
install -m 0755 ${DISTRO_DIR}/kill-secondary-name-node.sh ${HDFS_DIR}/bin/kill-secondary-name-node

for component in $HADOOP_DIR/bin/hadoop $HDFS_DIR/bin/hdfs $YARN_DIR/bin/yarn $MAPREDUCE_DIR/bin/mapred $YARN_DIR/bin/mapred ; do
  mv $component ${component}.distro
  wrapper=$BIN_DIR/${component#*/bin/}
  cat > $component <<EOF
#!/bin/bash

# Autodetect JAVA_HOME if not defined
. /usr/lib/bigtop-utils/bigtop-detect-javahome

export HADOOP_HOME=\${HADOOP_HOME:-${HADOOP_DIR#${PREFIX}}}
export HADOOP_MAPRED_HOME=\${HADOOP_MAPRED_HOME:-${HADOOP_DIR#${PREFIX}}-mapreduce}
export HADOOP_YARN_HOME=\${HADOOP_YARN_HOME:-${HADOOP_DIR#${PREFIX}}-yarn}
export HADOOP_LIBEXEC_DIR=\${HADOOP_HOME}/libexec
export HDP_VERSION=\${HDP_VERSION:-${HDP_VERSION}}
export HADOOP_OPTS="\${HADOOP_OPTS} -Dhdp.version=\${HDP_VERSION}"
export YARN_OPTS="\${YARN_OPTS} -Dhdp.version=\${HDP_VERSION}"

exec ${component#${PREFIX}}.distro "\$@"
EOF
  chmod 755 $component
  if [ $component != $wrapper ]; then
    cp -p $component $wrapper
  fi
done

# Install fuse wrapper
fuse_wrapper=${BIN_DIR}/hadoop-fuse-dfs
cat > $fuse_wrapper << EOF
#!/bin/bash

/sbin/modprobe fuse

# Autodetect JAVA_HOME if not defined
. /usr/lib/bigtop-utils/bigtop-detect-javahome

export HADOOP_HOME=\${HADOOP_HOME:-${HADOOP_DIR#${PREFIX}}}

BIGTOP_DEFAULTS_DIR=\${BIGTOP_DEFAULTS_DIR-/etc/default}
[ -n "\${BIGTOP_DEFAULTS_DIR}" -a -r \${BIGTOP_DEFAULTS_DIR}/hadoop-fuse ] && . \${BIGTOP_DEFAULTS_DIR}/hadoop-fuse

export HADOOP_LIBEXEC_DIR=\${HADOOP_HOME}/libexec

if [ "\${LD_LIBRARY_PATH}" = "" ]; then
  export JAVA_NATIVE_LIBS="libjvm.so"
  . /usr/lib/bigtop-utils/bigtop-detect-javalibs
  export LD_LIBRARY_PATH=\${JAVA_NATIVE_PATH}:/usr/lib
fi

# Pulls all jars from hadoop client package
for jar in \${HADOOP_HOME}/client/*.jar; do
  CLASSPATH+="\$jar:"
done
CLASSPATH="/etc/hadoop/conf:\${CLASSPATH}"

env CLASSPATH="\${CLASSPATH}" \${HADOOP_HOME}/bin/fuse_dfs \$@
EOF

chmod 755 $fuse_wrapper

# Bash tab completion
install -d -m 0755 $BASH_COMPLETION_DIR
install -m 0644 \
  hadoop-common-project/hadoop-common/src/contrib/bash-tab-completion/hadoop.sh \
  $BASH_COMPLETION_DIR/hadoop

# conf
install -d -m 0755 $HADOOP_ETC_DIR/conf.empty
cp ${DISTRO_DIR}/conf.empty/mapred-site.xml $HADOOP_ETC_DIR/conf.empty
# disable everything that's definied in hadoop-env.sh
# so that it can still be used as example, but doesn't affect anything
# by default
sed -i -e '/^[^#]/s,^,#,' ${BUILD_DIR}/etc/hadoop/hadoop-env.sh
cp ${BUILD_DIR}/etc/hadoop/* $HADOOP_ETC_DIR/conf.empty
rm -rf $HADOOP_ETC_DIR/conf.empty/*.cmd

# docs
install -d -m 0755 ${DOC_DIR}
cp -r ${BUILD_DIR}/share/doc/* ${DOC_DIR}/

# man pages
mkdir -p $MAN_DIR/man1
for manpage in hadoop hdfs yarn mapred; do
	gzip -c < $DISTRO_DIR/$manpage.1 > $MAN_DIR/man1/$manpage.1.gz
	chmod 644 $MAN_DIR/man1/$manpage.1.gz
done

# HTTPFS
install -d -m 0755 ${HTTPFS_DIR}/sbin

# Install httpfs wrapper
httpfs_wrapper=${HTTPFS_DIR}/sbin/httpfs.sh
cp ${BUILD_DIR}/sbin/httpfs.sh ${httpfs_wrapper}.distro

cat > ${httpfs_wrapper} <<EOF
#!/bin/bash

# Autodetect JAVA_HOME if not defined
. /usr/lib/bigtop-utils/bigtop-detect-javahome

export HADOOP_HOME=\${HADOOP_HOME:-${HADOOP_DIR#${PREFIX}}}
export HADOOP_LIBEXEC_DIR=\${HADOOP_HOME}/libexec

TOMCAT_DEPLOYMENT=\${TOMCAT_DEPLOYMENT:-/etc/hadoop-httpfs/tomcat-deployment}
HTTPFS_HOME=\${HTTPFS_HOME:-${HTTPFS_DIR#${PREFIX}}}

if [ ! -e "\${TOMCAT_DEPLOYMENT}" ]; then
  . \${HTTPFS_HOME}/tomcat-deployment.sh
fi

export CATALINA_BASE=\${TOMCAT_DEPLOYMENT}
export HTTPFS_CONFIG=/etc/hadoop-httpfs/conf

exec ${httpfs_wrapper#${PREFIX}}.distro "\$@"
EOF

chmod 755 $httpfs_wrapper

cp -r ${BUILD_DIR}/share/hadoop/httpfs/tomcat/webapps ${HTTPFS_DIR}/webapps
install -d -m 0755 ${PREFIX}/var/lib/hadoop-httpfs
install -d -m 0755 $HTTPFS_ETC_DIR/conf.empty

install -m 0755 ${DISTRO_DIR}/httpfs-tomcat-deployment.sh ${HTTPFS_DIR}/tomcat-deployment.sh

HTTP_DIRECTORY=$HTTPFS_ETC_DIR/tomcat-conf.dist
HTTPS_DIRECTORY=$HTTPFS_ETC_DIR/tomcat-conf.https

install -d -m 0755 ${HTTP_DIRECTORY}
cp -r ${BUILD_DIR}/share/hadoop/httpfs/tomcat/conf ${HTTP_DIRECTORY}
chmod 644 ${HTTP_DIRECTORY}/conf/*

cp -r ${HTTP_DIRECTORY} ${HTTPS_DIRECTORY}
mv ${HTTPS_DIRECTORY}/conf/ssl-server.xml ${HTTPS_DIRECTORY}/conf/server.xml
rm ${HTTP_DIRECTORY}/conf/ssl-server.xml

mv $HADOOP_ETC_DIR/conf.empty/httpfs* $HTTPFS_ETC_DIR/conf.empty
sed -i -e '/<\/configuration>/i\
  <property>\
    <name>httpfs.hadoop.config.dir</name>\
    <value>/etc/hadoop/conf</value>\
  </property>\
  <!-- HUE proxy user setting -->\
  <property>\
    <name>httpfs.proxyuser.hue.hosts</name>\
    <value>*</value>\
  </property>\
  <property>\
    <name>httpfs.proxyuser.hue.groups</name>\
    <value>*</value>\
  </property>' $HTTPFS_ETC_DIR/conf.empty/httpfs-site.xml

# Make the pseudo-distributed config
for conf in conf.pseudo ; do
  install -d -m 0755 $HADOOP_ETC_DIR/$conf
  # Install the upstream config files
  cp ${BUILD_DIR}/etc/hadoop/* $HADOOP_ETC_DIR/$conf
  # Remove the ones that shouldn't be installed
  rm -rf $HADOOP_ETC_DIR/$conf/httpfs*
  rm -rf $HADOOP_ETC_DIR/$conf/*.cmd
  # Overlay the -site files
  (cd $DISTRO_DIR/$conf && tar -cf - .) | (cd $HADOOP_ETC_DIR/$conf && tar -xf -)
  chmod -R 0644 $HADOOP_ETC_DIR/$conf/*
  # When building straight out of svn we have to account for pesky .svn subdirs 
  rm -rf `find $HADOOP_ETC_DIR/$conf -name .svn -type d` 
done
cp ${BUILD_DIR}/etc/hadoop/log4j.properties $HADOOP_ETC_DIR/conf.pseudo

# FIXME: Provide a convenience link for configuration (HADOOP-7939)
install -d -m 0755 ${HADOOP_DIR}/etc
ln -s /etc/hadoop/conf ${HADOOP_DIR}/conf
ln -s ../../hadoop/conf ${HADOOP_DIR}/etc/hadoop
install -d -m 0755 ${YARN_DIR}/etc
ln -s ../../hadoop/conf ${YARN_DIR}/etc/hadoop

# Create log, var and lib
install -d -m 0755 $PREFIX/var/{log,run,lib}/hadoop-hdfs
install -d -m 0755 $PREFIX/var/{log,run,lib}/hadoop-yarn
install -d -m 0755 $PREFIX/var/{log,run,lib}/hadoop-mapreduce

# Remove all source and create version-less symlinks to offer integration point with other projects
for DIR in ${HADOOP_DIR} ${HDFS_DIR} ${YARN_DIR} ${MAPREDUCE_DIR} ${HTTPFS_DIR} ; do
  (cd $DIR &&
   rm -fv *-sources.jar
   rm -fv lib/hadoop-*.jar
   for j in hadoop-*.jar; do
     if [[ $j =~ hadoop.*-${HADOOP_VERSION}.*.jar ]]; then
       ln -s $j ${j/-${HADOOP_VERSION}/}
     fi
   done)
done

# Now create a client installation area full of symlinks
install -d -m 0755 ${CLIENT_DIR}
for file in `cat ${BUILD_DIR}/hadoop-client.list` ; do
  for dir in ${HADOOP_DIR}/{lib,} ${HDFS_DIR}/{lib,} ${YARN_DIR}/{lib,} ${MAPREDUCE_DIR}/{lib,} ; do
    [ -e $dir/$file ] && \
    ln -fs ${dir#$PREFIX}/$file ${CLIENT_DIR}/${file} && \
    ln -fs ${dir#$PREFIX}/$file ${CLIENT_DIR}/${file/-[[:digit:]]*/.jar} && \
    continue 2
  done
  exit 1
done
cp ${BUILD_DIR}/../hadoop-dist/target/hadoop-${HADOOP_VERSION}.tar.gz ${HADOOP_DIR}/mapreduce.tar.gz

