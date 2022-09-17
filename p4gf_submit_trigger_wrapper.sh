#! /usr/bin/env bash
dash_config='--config-path='
if [ $# -gt 5 ]; then
 if [[ "$2" == change-* ]]; then
  if [[ "$3" == $dash_config* ]]; then 
   if [ "$5" == "git-fusion-user" ]; then
    exit 0
   fi
  else
   if [ "$4" == "git-fusion-user" ]; then
    exit 0
   fi
  fi
 else
  if [[ "$3" == change-* ]]; then
   if [[ "$4" == $dash_config* ]]; then 
    if [ "$6" == "git-fusion-user" ]; then
     exit 0
    fi
   else
    if [ "$5" == "git-fusion-user" ]; then
     exit 0
    fi
   fi
  fi
 fi
fi
"$@"
