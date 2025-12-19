eststo clear

// Run PSM and store the result
capture eststo psm_results: psmatch2 $treatment $xlist, out($y_var) comm norepl logit

if _rc == 0 {
	// Store ATT and standard error
	estadd scalar att = r(att)
	estadd scalar seatt = r(seatt)

	// Calculate and store t-statistic and p-value
	scalar t_stat = r(att) / r(seatt)
	scalar p_value = 2 * ttail(e(df_r), abs(t_stat))

	estadd scalar t_stat = t_stat
	estadd scalar p_value = p_value

	// Count treated, untreated, matched
	count if _treated == 1
	scalar treated_total = r(N)
	estadd scalar treated_total = treated_total

	count if _treated == 0
	scalar untreated_total = r(N)
	estadd scalar untreated_total = untreated_total

	count if _treated == 1 & _weight > 0
	scalar matched_treated = r(N)
	estadd scalar matched_treated = matched_treated

	count if _treated == 0 & _weight > 0
	scalar matched_untreated = r(N)
	estadd scalar matched_untreated = matched_untreated

	count if _weight > 0
	scalar matched_total = r(N)
	estadd scalar matched_total = matched_total

	// Export results to CSV
	esttab psm_results using "${out_path}$y_var.csv", replace ///
		se star scalars(att seatt t_stat p_value treated_total untreated_total matched_treated matched_untreated matched_total) drop(_cons) obslast ///
		plain
}

else {
	display "									*											"
	display "									*											"
	display "									*											"
	display "																				"
    display " ** ** **   --> PSM estimation failed — skipping result export! <--   ** ** ** "
	display "																				"
	display "									*											"
	display "									*											"
	display "									*											"
}