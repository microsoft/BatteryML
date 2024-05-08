CONFIG_ROOT=configs
WORKSPACE_ROOT=./workspaces_new

for folder in configs/baselines/sklearn; do
    # find $folder -type f -exec $SCRIPT {} 8 \;
    for CONFIG in $(find $folder -type f); do        
        echo $CONFIG
        relpath=$(echo $CONFIG | sed "s|$CONFIG_ROOT/||")
        WORKSPACE=$WORKSPACE_ROOT/${relpath%.*}
        #echo $WORKSPACE
        mkdir -p $WORKSPACE
        seed=0
        batteryml run $CONFIG --workspace  $WORKSPACE --train --eval --skip_if_executed false | tee $WORKSPACE/log.$seed
    done
done


for folder in configs/baselines/nn_models; do  
    for CONFIG in $(find $folder -type f); do
        echo $CONFIG
        relpath=$(echo $CONFIG | sed "s|$CONFIG_ROOT/||")
        WORKSPACE=$WORKSPACE_ROOT/${relpath%.*}
        echo $WORKSPACE
        mkdir -p $WORKSPACE

        # for seed in 0 1 2 3 4 5 6 7 8 9; do  
        for seed in 0 1 2 3 4 5 6 7 8 9; do  
            echo "Processing seed $seed"  
            batteryml run $CONFIG --workspace  $WORKSPACE --train --eval --seed $seed --device cuda --skip_if_executed false | tee $WORKSPACE/log.$seed
        done 
    done
done
