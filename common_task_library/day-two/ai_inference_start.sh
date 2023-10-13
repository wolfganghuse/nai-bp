#!/bin/bash

export PATH=$PATH:/home/ubuntu/.local/bin
export WORK_DIR="/home/ubuntu/nai-release-@@{NAI_LLM_REVISION}@@"

MODEL_NAME="@@{AI_MODEL_NAME}@@"
MODEL_REVISION="@@{AI_MODEL_REVISION}@@"


echo "bash $WORK_DIR/llm/run.sh -n $MODEL_NAME -a /mnt/llm/$MODEL_NAME/$MODEL_NAME.mar -g 1 -k"
nohup $WORK_DIR/llm/run.sh -n $MODEL_NAME -a /mnt/llm/$MODEL_NAME/$MODEL_NAME.mar -g 1 -k