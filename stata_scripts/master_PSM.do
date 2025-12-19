global res_path "results/dummy_reg/"
global data_path "data/"
global stata_scripts "stata_scripts/"

*#######################################################################################################
*************************************** Main PSM analysis **********************************************
*#######################################################################################################

*######### Green *#########
use "${data_path}panel_green_patents.dta", clear
drop if id==.
drop if ebit ==. | l_lab_prod == . | l_sales == . |  market_share ==. | l_cap_int == . | roce_sine ==. 

global treatment true_green //green is a dummy = 1 if that firm in that year got a green patent granted

* Drop who does not innovation*
drop if innov==0

global out_path "{res_path}res_psm/true_green/"
do "${stata_scripts}psm_manager_1.do"


*######### Green novelty vs brown novelty *#########
use "${data_path}panel_green_patents.dta", clear
drop if id==.
drop if ebit ==. | l_lab_prod == . | l_sales == . |  market_share ==. | l_cap_int == . | roce_sine ==. 

global treatment true_green_novelty //green is a dummy = 1 if that firm in that year got a green patent granted

* Drop who does not novelty innovation*
drop if innov_novelty == 0

global out_path "{res_path}res_psm/green_nov_brown/"
do "${stata_scripts}psm_manager_1.do"


*************************************** Robusteness check **********************************************

*#################################################################################################
*							Above median size vs. Below median size firms
*#################################################################################################

*######### Above median size *#########
use "${data_path}panel_green_patents.dta", clear
drop if id==.
drop if ebit ==. | l_lab_prod == . | l_sales == . |  market_share ==. | l_cap_int == . | roce_sine ==. 
* Drop who does not innovation*
drop if innov==0

* Step 1: Compute the median
bysort id : egen mean_size = mean(employee)
preserve
sum mean_size, detail
local mymedian = r(p50)
restore
* Step 2: Tag  and drop individuals whose value is below the median
gen below_median = 1
bysort id: replace below_median = 0 if mean_size >= `mymedian'
drop if below_median == 1
drop below_median

global treatment true_green //green is a dummy = 1 if that firm in that year got a green patent granted

global out_path "{res_path}res_psm/above/"
do "${stata_scripts}psm_manager_1.do"


*######### Below median size *#########
use "${data_path}panel_green_patents.dta", clear
drop if id==.
drop if ebit ==. | l_lab_prod == . | l_sales == . |  market_share ==. | l_cap_int == . | roce_sine ==. 
* Drop who does not innovation*
drop if innov==0

* Step 1: Compute the median
bysort id : egen mean_size = mean(employee)
preserve
sum mean_size, detail
local mymedian = r(p50)
restore
* Step 2: Tag  and drop individuals whose value is below the median
gen below_median = 1
bysort id: replace below_median = 0 if mean_size >= `mymedian'
drop if below_median == 0
drop below_median

global treatment true_green //green is a dummy = 1 if that firm in that year got a green patent granted

global out_path "{res_path}res_psm/below/"
do "${stata_scripts}psm_manager_1.do"


*#################################################################################################
*					ALL TRUE GREEN PATENTS (conventional false negatives)
*#################################################################################################

*######### Green *#########
use "${data_path}panel_green_patents.dta", clear
drop if id==.
drop if ebit ==. | l_lab_prod == . | l_sales == . |  market_share ==. | l_cap_int == . | roce_sine ==. 

global treatment true_green_all //green is a dummy = 1 if that firm in that year got a green patent granted

* Drop who does not innovation*
drop if innov==0

global out_path "{res_path}res_psm/true_all/"
do "${stata_scripts}psm_manager_1.do"


*#################################################################################################
*							High pollution vs. Low pollution firms (NACE)
*#################################################################################################


*######### High pollution *#########
use "${data_path}panel_green_patents.dta", clear
drop if id==.
* Drop who does not innovation*
drop if innov==0

* Step 1: Get polluting tag
merge m:1 nace using "${data_path}polluting_dummy.dta"
drop if _m == 1
drop _m
keep if pollut == 1

global treatment true_green //green is a dummy = 1 if that firm in that year got a green patent granted

global out_path "{res_path}res_psm/high_pollute/"
do "${stata_scripts}psm_manager_1.do"


*######### Low pollution *#########
use "${data_path}panel_green_patents.dta", clear
drop if id==.
* Drop who does not innovation*
drop if innov==0

* Step 1: Get polluting tag
merge m:1 nace using "${data_path}polluting_dummy.dta"
drop if _m == 1
drop _m
keep if pollut == 0

global treatment true_green //green is a dummy = 1 if that firm in that year got a green patent granted

* Drop who does not novelty innovation*
drop if innov == 0

global out_path "{res_path}res_psm/low_pollute/"
do "${stata_scripts}psm_manager_1.do"