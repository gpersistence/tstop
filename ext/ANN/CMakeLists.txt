INCLUDE_DIRECTORIES(${dynatopo_SOURCE_DIR}/ext/ANN)
SET(ann_sources
	ANN.cpp brute.cpp kd_tree.cpp kd_util.cpp kd_split.cpp
	kd_dump.cpp kd_search.cpp kd_pr_search.cpp kd_fix_rad_search.cpp
	bd_tree.cpp bd_search.cpp bd_pr_search.cpp bd_fix_rad_search.cpp
	perf.cpp
	kd_tree.h kd_split.h kd_util.h kd_search.h
	kd_pr_search.h kd_fix_rad_search.h pr_queue.h pr_queue_k.h
	)

ADD_LIBRARY(ann ${ann_sources})
