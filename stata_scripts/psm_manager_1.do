ssc install psmatch2, replace

* Propensity score matching with common support ONLY NP
*LOG SALES
global xlist lag_cap_int pretrend_capint lag_roce pretrend_roce i.country_ i.nace i.i.year l_age
global y_var l_sales
do "${stata_scripts}psm_executor_2.do"

*MARKET SHARE
global xlist lag_cap_int pretrend_capint lag_roce pretrend_roce i.country_ i.nace employees i.i.year l_age
global y_var market_share
do "${stata_scripts}psm_executor_2.do"

*LAB PROD
global y_var l_lab_prod
do "${stata_scripts}psm_executor_2.do"

*CAP INTENSITY
global y_var l_cap_int
do "${stata_scripts}psm_executor_2.do"

*LOG ROCE
global y_var roce_sine
do "${stata_scripts}psm_executor_2.do"

*EBIT
global y_var ebit
do "${stata_scripts}psm_executor_2.do"