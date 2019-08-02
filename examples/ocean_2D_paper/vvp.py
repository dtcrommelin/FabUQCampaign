# This file contains prototype VVP implementations.
#
# These patterns should be purposed for specific settings.
# As such, they do not contain a @task descriptor.
import os


"""
validate_ensemble_output Validation Pattern.

Purpose: 
1. given an ensemble of validation output directories, it will:
2. operate a validation_function on each direction, and
3. print the outputs to screen, and
4. use an aggregation function to combine all outputs into a compound metric, 
   and
5. print the compound metric.


SPECS of the required validation_function:
- Should operate with a single argument (the simulation output directory).
- ASSUMPTION: There is no explicit argument to indicate where the validation 
  data resides (currently assumed to be packaged with the simulation output 
  and known by the function). -> we could choose to make this explicit.
- The validation function should return a set of metrics.

SPECS of the aggregation_function:
- Receives a Python list with the output of validation_function in each 
  element.
- Returns a data type that represents the compound validation outcome
  (.e.g, one or more error scores).
"""

"""
*******
CHANGES
*******
1) 'validate_ensemble_output' may not be a good name, this function will be 
   used for verification as well, changed it to 'ensemble_vvp'
2) 'validation_function': same comment, changed it to 'partition_function',
   being the opposite of 'aggregation_function', something that acts on a single sample only
3) print("AVERAGED VALIDATION SCORE ...) line is removed
4) added *argv in case the partition function takes more than the result_dir as argument
5) added the possibility of multiple results_dirs
"""

def ensemble_vvp(results_dirs, partition_function, aggregation_function, *argv):
    """
    Goes through all the output directories and calculates the scores.
    """

    #if a single result_dir is specified, still add it to a list
    if type(results_dirs) == str:
        tmp = []; tmp.append(results_dirs); results_dirs = tmp
        
    for results_dir in results_dirs:    

        scores = []
        
        for item in os.listdir("{}".format(results_dir)):
            print(item)
            if os.path.isdir(os.path.join(results_dir, item)):
                print(os.path.join(results_dir, item))
                scores.append(partition_function(os.path.join(results_dir, item), *argv))
    
        print("scores:", scores)
        aggregation_function(scores)