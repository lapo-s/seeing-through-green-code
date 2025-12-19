set more off
global res_path "results/dummy_reg/"
global data_path "data/"

use "${data_path}panel_green_patents.dta", clear

global outcomes l_sales market_share l_lab_prod l_cap_int roce_sine ebit log_np

* Set same comparable sample for each outcome
drop if ebit ==. | l_lab_prod == . | l_sales == . |  market_share ==. | l_cap_int == . | roce_sine ==. 

*** COVARIATES *****
global xlist2 true_green innov i.country_ i.nace employees i.i.year

foreach outcome of global outcomes {
	
	* GREEN + INNOVATION
    reg `outcome' $xlist2, vce(cluster id) noconstant
	estimates store reg_temp
	outreg2 reg_temp using "${res_path}dummy_reg_res.raw", append tex dec(3) label keep(true_green innov) 

	}