#!/bin/bash

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
     --build-dir=DIR             path to zookeeper dist.dir
     --prefix=PREFIX             path to install into

  Optional options:
     --doc-dir=DIR               path to install docs into [/usr/share/doc/zookeeper]
     --home-dir=DIR              home path to install into [/usr/lib/zookeeper]
     --man-dir=DIR               path to install manpages into [/usr/share/man]
     --etc-dir=DIR               path to install etc into [/etc]
     --lib-dir=DIR               path to install zookeeper home [/usr/lib/zookeeper]
     --bin-dir=DIR               path to install bins [/usr/bin]
     --examples-dir=DIR          path to install examples [doc-dir/examples]
     --system-include-dir=DIR    path to install development headers [/usr/include]
     --system-lib-dir=DIR        path to install native libraries [/usr/lib]
     ... [ see source for more similar options ]
  "
  exit 1
}

OPTS=$(getopt \
  -n $0 \
  -o '' \
  -l 'prefix:' \
  -l 'doc-dir:' \
  -l 'lib-dir:' \
  -l 'bin-dir:' \
  -l 'home-dir:' \
  -l 'man-dir:' \
  -l 'etc-dir:' \
  -l 'examples-dir:' \
  -l 'system-include-dir:' \
  -l 'system-lib-dir:' \
  -l 'build-dir:' -- "$@")

if [ $? != 0 ] ; then
    usage
fi

eval set -- "$OPTS"
while true ; do
    case "$1" in
        --prefix)
        PREFIX=$2 ; shift 2
        ;;
        --build-dir)
        BUILD_DIR=$2 ; shift 2
        ;;
        --home-dir)
        HOME_DIR=$2 ; shift 2
        ;;
        --man-dir)
        MAN_DIR=$2 ; shift 2
        ;;
        --etc-dir)
        ETC_DIR=$2 ; shift 2
        ;;
        --doc-dir)
        DOC_DIR=$2 ; shift 2
        ;;
        --lib-dir)
        LIB_DIR=$2 ; shift 2
        ;;
        --bin-dir)
        BIN_DIR=$2 ; shift 2
        ;;
        --examples-dir)
        EXAMPLES_DIR=$2 ; shift 2
        ;;
        --system-include-dir)
        SYSTEM_INCLUDE_DIR=$2 ; shift 2
        ;;
        --system-lib-dir)
        SYSTEM_LIB_DIR=$2 ; shift 2
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

for var in PREFIX BUILD_DIR ; do
  if [ -z "$(eval "echo \$$var")" ]; then
    echo Missing param: $var
    usage
  fi
done

HOME_DIR=${HOME_DIR:-/var/lib/zookeeper}
MAN_DIR=${MAN_DIR:-/usr/share/man}
DOC_DIR=${DOC_DIR:-/usr/share/doc/zookeeper}
LIB_DIR=${LIB_DIR:-/usr/lib/zookeeper}
BIN_DIR=${BIN_DIR:-/usr/bin}
CONF_DIR=/etc/zookeeper/conf
CONF_DIST_DIR=${ETC_DIR:-/etc/zookeeper}/conf.dist
SYSTEM_INCLUDE_DIR=${SYSTEM_INCLUDE_DIR:-/usr/include}
SYSTEM_LIB_DIR=${SYSTEM_LIB_DIR:-/usr/lib}

install -d -m 0755 $PREFIX/$LIB_DIR/
rm -f $BUILD_DIR/zookeeper-*-javadoc.jar $BUILD_DIR/zookeeper-*-bin.jar $BUILD_DIR/zookeeper-*-sources.jar $BUILD_DIR/zookeeper-*-test.jar
cp $BUILD_DIR/zookeeper*.jar $PREFIX/$HOME_DIR/
install -d -m 0755 ${PREFIX}/${HOME_DIR}/contrib
for module in rest; do
    cp -r ${BUILD_DIR}/contrib/${module} ${PREFIX}/${HOME_DIR}/contrib/
done

# Make a symlink of zookeeper.jar to zookeeper-version.jar
for x in $PREFIX/$HOME_DIR/zookeeper*jar ; do
  x=$(basename $x)
  ln -s $x $PREFIX/$HOME_DIR/zookeeper.jar
done

install -d -m 0755 $PREFIX/$LIB_DIR
cp $BUILD_DIR/lib/*.jar $PREFIX/$LIB_DIR

# Copy in the configuration files
install -d -m 0755 $PREFIX/$CONF_DIST_DIR
cp zoo.cfg $BUILD_DIR/conf/* $PREFIX/$CONF_DIST_DIR/
ln -s $CONF_DIR $PREFIX/$HOME_DIR/conf

install -d -m 0755 ${PREFIX}/${HOME_DIR}/contrib
for module in rest; do
    cp -r ${BUILD_DIR}/contrib/${module} ${PREFIX}/${HOME_DIR}/contrib/
    mv ${PREFIX}/${HOME_DIR}/contrib/${module}/conf ${PREFIX}/${CONF_DIST_DIR}/${module}
done

# Copy in the /usr/bin/zookeeper-server wrapper
install -d -m 0755 $PREFIX/${BIN_DIR}
# FIXME: a workaround in preparation for Zookeeper 3.5
echo '#!/bin/bash' > $BUILD_DIR/bin/zkServer-initialize.sh

for i in zkServer.sh zkEnv.sh zkCli.sh zkCleanup.sh zkServer-initialize.sh
	do cp $BUILD_DIR/bin/$i $PREFIX/${BIN_DIR}
	chmod 755 $PREFIX/${BIN_DIR}/$i
done

wrapper=$PREFIX/${BIN_DIR}/zookeeper-client
install -d -m 0755 `dirname $wrapper`
cat > $wrapper <<EOF
#!/bin/bash

# Autodetect JAVA_HOME if not defined
. /usr/lib/bigtop-utils/bigtop-detect-javahome

export ZOOKEEPER_HOME=\${ZOOKEEPER_HOME:-${HOME_DIR}}
export ZOOKEEPER_CONF=\${ZOOKEEPER_CONF:-/etc/zookeeper/conf}
export CLASSPATH=\$CLASSPATH:\$ZOOKEEPER_CONF:\$ZOOKEEPER_HOME/*:\$ZOOKEEPER_HOME/lib/*
export ZOOCFGDIR=\${ZOOCFGDIR:-\$ZOOKEEPER_CONF}
env CLASSPATH=\$CLASSPATH ${BIN_DIR}/zkCli.sh "\$@"
EOF
chmod 755 $wrapper

for pairs in zkServer.sh/zookeeper-server zkServer-initialize.sh/zookeeper-server-initialize zkCleanup.sh/zookeeper-server-cleanup ; do
  wrapper=$PREFIX/${BIN_DIR}/`basename $pairs`
  upstream_script=`dirname $pairs`
  cat > $wrapper <<EOF
#!/bin/bash

# Autodetect JAVA_HOME if not defined
. /usr/lib/bigtop-utils/bigtop-detect-javahome

export ZOOPIDFILE=\${ZOOPIDFILE:-/var/run/zookeeper/zookeeper_server.pid}
export ZOOKEEPER_HOME=\${ZOOKEEPER_HOME:-${HOME_DIR}}
export ZOOKEEPER_CONF=\${ZOOKEEPER_CONF:-/etc/zookeeper/conf}
export ZOOCFGDIR=\${ZOOCFGDIR:-\$ZOOKEEPER_CONF}
export CLASSPATH=\$CLASSPATH:\$ZOOKEEPER_CONF:\$ZOOKEEPER_HOME/*:\$ZOOKEEPER_HOME/lib/*
export ZOO_LOG_DIR=\${ZOO_LOG_DIR:-/var/log/zookeeper}
export ZOO_LOG4J_PROP=\${ZOO_LOG4J_PROP:-INFO,ROLLINGFILE}
export JVMFLAGS=\${JVMFLAGS:--Dzookeeper.log.threshold=INFO}
export ZOO_DATADIR_AUTOCREATE_DISABLE=\${ZOO_DATADIR_AUTOCREATE_DISABLE:-true}
env CLASSPATH=\$CLASSPATH ${BIN_DIR}/${upstream_script} "\$@"
EOF
  chmod 755 $wrapper
done

# Copy in the docs
install -d -m 0755 $PREFIX/$DOC_DIR
cp -a $BUILD_DIR/docs/* $PREFIX/$DOC_DIR
cp $BUILD_DIR/*.txt $PREFIX/$DOC_DIR/

install -d -m 0755 $PREFIX/$MAN_DIR/man1
gzip -c zookeeper.1 > $PREFIX/$MAN_DIR/man1/zookeeper.1.gz

# Zookeeper log and tx log directory
install -d -m 1766 $PREFIX/var/log/zookeeper
install -d -m 1766 $PREFIX/var/log/zookeeper/txlog

# ZooKeeper native libraries
install -d ${PREFIX}/$SYSTEM_INCLUDE_DIR
install -d ${PREFIX}/$SYSTEM_LIB_DIR
install -d ${PREFIX}/${LIB_DIR}-native

(cd ${BUILD_DIR}/.. && tar xzf zookeeper-*-lib.tar.gz)
cp -R ${BUILD_DIR}/../usr/include/* ${PREFIX}/${SYSTEM_INCLUDE_DIR}/
cp -R ${BUILD_DIR}/../usr/lib*/* ${PREFIX}/${SYSTEM_LIB_DIR}/
cp -R ${BUILD_DIR}/../usr/bin/* ${PREFIX}/${LIB_DIR}-native/
for binary in ${PREFIX}/${LIB_DIR}-native/*; do
  cat > ${PREFIX}/${BASE}/${BIN_DIR}/`basename ${binary}` <<EOF
#!/bin/bash

PREFIX=\$(dirname \$(readlink -f \$0))
export LD_LIBRARY_PATH=\${LD_LIBRARY_PATH}:\${PREFIX}/../lib:\${PREFIX}/../lib64
${LIB_DIR}-native/`basename ${binary}` \$@

EOF
done
chmod 755 ${PREFIX}/${BIN_DIR}/* ${PREFIX}/${LIB_DIR}-native/*

