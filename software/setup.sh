# uhal setup
export LD_LIBRARY_PATH=/opt/cactus/lib:$LD_LIBRARY_PATH
export PATH=/opt/cactus/bin:$PATH
# python setup
TEST_SOFTWARE_PATH=/scratch/ypiadyk/AMchip05_testbench/software
export PYTHONPATH=$TEST_SOFTWARE_PATH:$TEST_SOFTWARE_PATH/common:$TEST_SOFTWARE_PATH/wrappers
