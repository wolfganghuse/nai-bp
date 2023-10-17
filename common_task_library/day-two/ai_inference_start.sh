#!/bin/bash

export PATH=$PATH:/home/ubuntu/.local/bin
export WORK_DIR="/home/ubuntu/nai-release-@@{NAI_LLM_REVISION}@@"

MODEL_NAME="@@{AI_MODEL_NAME}@@"
MODEL_REVISION="@@{AI_MODEL_REVISION}@@"

rm -rf nohup.out

if [ -z "$MODEL_REVISION" ]; then
    echo "bash $WORK_DIR/llm/run.sh -n $MODEL_NAME -a /mnt/llm/$MODEL_NAME -g 1"
    nohup $WORK_DIR/llm/run.sh -n $MODEL_NAME -a /mnt/llm/$MODEL_NAME -g 1
else
    echo "bash $WORK_DIR/llm/run.sh -n $MODEL_NAME -a /mnt/llm/$MODEL_NAME -g 1 -v $MODEL_REVISION"
    nohup $WORK_DIR/llm/run.sh -n $MODEL_NAME -a /mnt/llm/$MODEL_NAME -g 1 -v $MODEL_REVISION
fi

cat nohup.out