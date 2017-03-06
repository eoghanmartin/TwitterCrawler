# Truth Finding using MLE

#### Requirements
* Python 2.7.10

##Running
The program can be ran using:
```
python main.py
```

## Output

####Task 1
* Matrix is read from `SCMatrix_Submit.txt`.
* MLE is calculated and results are written to `ResultsTask1.txt`.

####Task 2
* K-Means clusters are generated for the tweets from the file `Tweets.json` using the seeds in the file `InitialSeeds.txt`.
* Clusters are output in the clusters.json file.
* Each line corresponds to a cluster and contains the cluster id as well as tweet ids.
* A matrix is then built from those clusters using twitter users as the source and clusters as the measured variable.
* The MLE for that matrix is computed and results are output to `ResultsTask2`.