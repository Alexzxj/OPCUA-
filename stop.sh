#!/bin/bash

# A function to stop a program.
killproc() {
    local RC killlevel= base pid pid_file= delay try binary=

    RC=0; delay=3; try=0
    # Test syntax.
    if [ "$#" -eq 0 ]; then
        echo $"Usage: killproc [-p pidfile] [ -d delay] {program} [-signal]"
        return 1
    fi
    if [ "$1" = "-p" ]; then
        pid_file=$2
        shift 2
    fi
    if [ "$1" = "-b" ]; then
        if [ -z $pid_file ]; then
            echo $"-b option can be used only with -p"
            echo $"Usage: killproc -p pidfile -b binary program"
            return 1
        fi
        binary=$2
        shift 2
    fi
    if [ "$1" = "-d" ]; then
        if [ "$?" -eq 1 ]; then
            echo $"Usage: killproc [-p pidfile] [ -d delay] {program} [-signal]"
            return 1
        fi
        shift 2
    fi


    # check for second arg to be kill level
    [ -n "${2:-}" ] && killlevel=$2

    # Save basename.
    base=${1##*/}

    # Find pid.
    __pids_var_run "$1" "$pid_file" "$binary"
    RC=$?
    if [ -z "$pid" ]; then
        if [ -z "$pid_file" ]; then
            pid="$(__pids_pidof "$1")"
        else
            [ "$RC" = "4" ] && { failure $"$base shutdown" ; return $RC ;}
        fi
    fi

    # Kill it.
    if [ -n "$pid" ] ; then
        [ "$BOOTUP" = "verbose" -a -z "${LSB:-}" ] && echo -n "$base "
        if [ -z "$killlevel" ] ; then
            __kill_pids_term_kill -d $delay $pid
            RC=$?
            [ "$RC" -eq 0 ] && success $"$base shutdown" || failure $"$base shutdown"
        # use specified level only
        else
            if checkpid $pid; then
                kill $killlevel $pid >/dev/null 2>&1
                RC=$?
                [ "$RC" -eq 0 ] && success $"$base $killlevel" || failure $"$base $killlevel"
            elif [ -n "${LSB:-}" ]; then
                RC=7 # Program is not running
            fi
        fi
    else
        if [ -n "${LSB:-}" -a -n "$killlevel" ]; then
            RC=7 # Program is not running
        else
            failure $"$base shutdown"
            RC=0
        fi
    fi

    # Remove pid file if any.
    if [ -z "$killlevel" ]; then
        rm -f "${pid_file:-/var/run/$base.pid}"
    fi
    return $RC
}
#检查PID进程
checkpid() {
    local i

    for i in $* ; do
        [ -d "/proc/$i" ] && return 0
    done
    return 1
}

#说明，模块开发必须按照模块的当前工作目录名称写入pid文件
pidPath="/var/run/";

#获取执行脚本的目录
workplace=$(dirname $0);
cd $workplace
#这两个不用修改，有程序自动判断
p=`pwd`;
array=(${p//// })  
length=${#array[@]}

if [ $length>0 ];then
    let index=$length-1;
    name=${array[$index]}
    pidfile=$pidPath$name".pid"
else
    echo "workPlace error!!!";
    exit -1
fi

if [  -f $pidfile ]; then

pid=`cat $pidfile`;

if checkpid $pid; then
        #echo "running"
        #此处根据pidfile路径杀掉进程
        #echo $pidfile
        #killproc -p $pidfile
        kill $pid
else
     #echo "stop"
     echo "errorCode=-1000"
     exit 0
fi
fi
#成功标识
echo "errorCode="$?