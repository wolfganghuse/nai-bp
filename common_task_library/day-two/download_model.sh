#!/bin/bash


if [ '@@{calm_array_index}@@' != '0' ]; then
    echo "model download must be run from the first VM in the replica set"
    exit 0
fi

export PATH=$PATH:/home/ubuntu/.local/bin
export WORK_DIR="/home/ubuntu/nai-release-@@{NAI_LLM_REVISION}@@"

MODEL_NAME="@@{AI_MODEL_NAME}@@"
MODEL_REVISION="@@{AI_MODEL_REVISION}@@"

echo $MODEL_NAME
echo $MODEL_REVISION

if [ ! -d /mnt/llm/$MODEL_NAME ];
then
    mkdir -p /mnt/llm/$MODEL_NAME
    mkdir -p $WORK_DIR/models/$MODEL_NAME

    echo "bash python3 $WORK_DIR/llm/download.py --model_name $MODEL_NAME --model_path $WORK_DIR/models/$MODEL_NAME --mar_output /mnt/llm/$MODEL_NAME"
    nohup python3 $WORK_DIR/llm/download.py --model_name $MODEL_NAME --model_path $WORK_DIR/models/$MODEL_NAME --mar_output /mnt/llm/$MODEL_NAME

    rm -rf $WORK_DIR/models/$MODEL_NAME

elif [ -d /mnt/llm/$MODEL_NAME ];
then
    echo "Model: $MODEL_NAME is already present"
    exit 0
fi