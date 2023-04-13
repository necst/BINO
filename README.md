# BINO Framework

Static analysis framework for recognition of inline binary functions from template classes.


## Installation:

1) `pip install -r requirements`
2) `./install.sh`
   This might generate an error if clang is not installed. You can install it through apt
   `sudo apt install clang-10`


## Fingerprint generation

In order to build new fingerprints, you must define a building_procedure.json in data/building_procedure/.
Samples of building procedure are available in the folder.
Then, to build the fingerprints, run the following scripts:
1) `./summaries_build_stage.py`
2) `./sources_builder_stage.py`
3) `./preprocessor_stage.py`
4) `./compiler_stage.py`
5) `./fingerprinter_stage.py`
6) `./storer_stage.py`

## Fingerprint matching

The matching is carried on by tester_stage.py.

`usage: tester_stage.py [-h] [-d] [-fp FINGERPRINTS_PATH] [-cs CLASSES_NAMES [CLASSES_NAMES ...]] [-o OUTPUT_FILE] [-mbb MIN_BB] [-ec] [-s SIMILARITY_THRESHOLD] [-efc] [-css] [-p PROCESSES] test_binary`

The optional parameters are:
* -d: enable debug
* -fp: custom fingerprints db path
* -cs: classes to test
* -o: output file
* -mbb: minimum number of basic blocks
* -ec: enable colors
* -s: similarity threshold(default: 0.88)
* -efc: enable function call information
* -css: check static symbols if available

A test binary sample is available in data/test_binaries/generic_binaries/

## Testing

### Dataset

Dataset can be downloaded at: https://mega.nz/file/eW5yhIJI#vsIjOz7_MNegW728R4KtN_KuZT2uJ18vWHo0_qTE0CI

### Building the images

Testing is performed through docker containers, one for each class under testing.
To create the images and containers, run the following script with the list of classes you want to test:

* `./install_testing.py -cs [List of classes]`

For instance:

* `./install_testing.py -cs std::map std::vector`

This command will create a Dockerfile and a docker-compose for testing the two classes.

### Running tests

Before running the tests, the dataset must be copied in the proper directory in the docker container. 
The files to be copied are inside the directory named as the class under testing. Such a directory contains a .csv and a .7z file that must be copied in the directory `data/github_testing`.
This operation must be repeat for each container by copying its relative dataset.
Finally, it is possibile start the testing by running:

`./run.sh`

Testing might take up to days, thus it is suggested to use tmux to keep the tests running.

### Results

Results are available under `data/github_testing`. Specifically, you can find a summary in the file `data/github_testing/git_testing_output.csv` and the result for each project in the file `*.dwarf.txt` in the directory `data/github_testing/projects`.