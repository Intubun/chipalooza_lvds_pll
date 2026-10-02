source $::env(LAYOUT_SCRIPTS)/mkdev.tcl
mkdev sg13_lv_nmos dev_n_w0p6_l0p13_ng1_noguard_m1 {w 0.6 l 0.13 ng 1 m 1 guard 0 conn_gates 1 full_metal 1 doports 1 viasrc 0 viadrn 0 viagate 0}
mkdev sg13_lv_nmos dev_n_w0p6_l0p13_ng2_noguard_m1 {w 0.6 l 0.13 ng 2 m 1 guard 0 conn_gates 1 full_metal 1 doports 1 viasrc 0 viadrn 0 viagate 0}
mkdev sg13_lv_nmos dev_n_w0p6_l0p13_ng4_noguard_m1 {w 0.6 l 0.13 ng 4 m 1 guard 0 conn_gates 1 full_metal 1 doports 1 viasrc 0 viadrn 0 viagate 0}
mkdev sg13_lv_nmos dev_n_w0p6_l0p13_ng6_noguard_m1 {w 0.6 l 0.13 ng 6 m 1 guard 0 conn_gates 1 full_metal 1 doports 1 viasrc 0 viadrn 0 viagate 0}
mkdev sg13_lv_pmos dev_p_w0p6_l0p13_ng1_noguard_m1 {w 0.6 l 0.13 ng 1 m 1 guard 0 conn_gates 1 full_metal 1 doports 1 viasrc 0 viadrn 0 viagate 0}
mkdev sg13_lv_pmos dev_p_w0p6_l0p13_ng2_noguard_m1 {w 0.6 l 0.13 ng 2 m 1 guard 0 conn_gates 1 full_metal 1 doports 1 viasrc 0 viadrn 0 viagate 0}
mkdev sg13_lv_pmos dev_p_w0p6_l0p13_ng4_noguard_m1 {w 0.6 l 0.13 ng 4 m 1 guard 0 conn_gates 1 full_metal 1 doports 1 viasrc 0 viadrn 0 viagate 0}
writeall force
quit -noprompt
