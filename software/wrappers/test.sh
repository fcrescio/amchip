#!/bin/bash

echo "Test with random bank and threshold 0"

# Setup Clocks and GTXs
python ../test_serdes.py a 2 100
python configure_serdes.py

PATTERNS=2048
EVLEN=4096
OFFSET=0

# for bank in {0..19}
# do
    python gen_bank.py $PATTERNS bank_test_thr0
    python load_bank.py bank_test_thr0 $OFFSET
    # for data in {0..1}
    # do
	# # INJEVT=$(($data*1000))
	INJEVT=8000
	python gen_data.py 32768 bank_test_thr0 $INJEVT data_test_thr0
	python predict_stream.py bank_test_thr0 $OFFSET data_test_thr0 $EVLEN 0 stream_test_thr0 predicted_events_test_thr0 
	python load_predicted_patterns.py predicted_events_test_thr0 16384
	python load_hits_and_start.py data_test_thr0 $EVLEN 0
	# for trial in {0..1}
	# do
	    # python dump_predicted_patterns_extra.py 16000 extra_events_test_thr0
	    python dump_pattout_events.py 16384 events_test_thr0
	    #python dump_pattout_events_spybuffer.py events_test_thr0
	    python compare_events.py events_test_thr0 predicted_events_test_thr0 results_long_thr0_$INJEVT
	    python read_error_rate.py pattout_dump_test_thr0
	# done
    # done
# done
