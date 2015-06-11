for VOLT in {800..1200..150}
do
	# for TIME in {0..20..1}
	# do
	for FREQ in {60..200..15}
	do
		python test_random.py ./random_test_results_20150603/random_test $FREQ $VOLT silent
	done 
	# done 
done
