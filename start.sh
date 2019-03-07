#!/bin/bash
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
#获取程序工作目录
p=`pwd`;
array=(${p//// })  
length=${#array[@]}

if [ $length>0 ];then
    let index=$length-1;
    name=${array[$index]}
    pidfile=$pidPath$name".pid"
    echo $pidfile
else
    echo "workPlace error!!!";
    exit -1
fi

if [  -f $pidfile ]; then

pid=`cat $pidfile`;

if checkpid $pid; then

    #echo "running"
    echo "errorCode=-1000"
    exit 0;
else
    #echo "stop"
    python3 main.py 1,2>>/dev/null&
fi
else
    python3 main.py 1,2>>/dev/null&
fi
#成功标识
echo "errorCode="$? 





