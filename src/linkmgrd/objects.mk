
USER_OBJS :=

LIBS := \
    -lswsscommon \
    -lboost_date_time \
    -lboost_thread \
    -lboost_log \
    -lboost_log_setup \
    -lboost_program_options \
    -lnl-3 \
    -lnl-route-3

LIBS_TEST := \
    -lgtest_main \
    -lgtest
