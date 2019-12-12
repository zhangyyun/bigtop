i#!/bin/sh

# HDP configures the NameNode JVM process to call this script on
# OutOfMemoryError.  This will find and kill the NameNode process.  It's
# potentially dangerous to keep running the NameNode after an OutOfMemoryError.
# There is a risk that a file system change could be applied to the in-memory
# metadata but not made persistent to the edit log.  HDFS contains legacy code
# that catches OutOfMemoryError, so we need to use this script to kill it
# externally.

NNPID=$("$JAVA_HOME"/bin/jps | grep -E '^[0-9]+[ ]+NameNode$' | awk '{print $1}')

if [ $? -gt 0 ]; then
  echo "ERROR: Command failed while looking for NameNode PID."
  exit 1
fi

if [ -z "$NNPID" ];
then
  echo "ERROR: Could not find a NameNode PID."
  exit 1
fi

kill -9 "$NNPID"

if [ $? -gt 0 ]; then
  echo "ERROR: Kill command failed."
  exit 1
fi
