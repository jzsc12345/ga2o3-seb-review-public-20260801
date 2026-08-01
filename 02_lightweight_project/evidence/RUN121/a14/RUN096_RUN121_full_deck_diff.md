diff --git "a/decks\\RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in" "b/decks\\RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_short500ns.in"
index 83028e0..f143154 100644
--- "a/decks\\RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in"
+++ "b/decks\\RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_short500ns.in"
@@ -1,18 +1,19 @@
 # =============================================================================
-# RUN096 -- HfO2 heat-capacity-only arm from completed RUN095
+# RUN121 -- z/[001] impact OFAT from frozen RUN096
 #
 # Goal:
-#   Quantify only the missing HfO2 heat-capacity model after RUN095 closed the
-#   HEAT.FULL root-cause branch. Geometry, electrical physics, source, thermal
-#   boundaries, heat-source equation and time schedule are frozen from RUN095.
+#   Quantify only the Wang Table II / material-library z-axis impact group
+#   relative to RUN096's y/[010] group. Geometry, mesh, material lifetime,
+#   mobility, source, thermal boundaries, heat-source equation, solver and the
+#   complete 0--500 ns time schedule are frozen from RUN096.
 #   Integrate PHOTOGEN and require the generated charge to agree with
 #   0.4529 pC/um * 5.35 um = 2.423015 pC within 5 percent.
 #
-# Contract relative to RUN092:
-#   The only physical change is lateral geometry: xdev 31->20 um,
-#   drain-left 29->18 um (Lgd 20->9 um), and removal of gate_fp.  The 5 um
-#   substrate, Fe trap, channel/UID, work functions, mobility, impact,
-#   thermal parameters/contacts, source, solver and time schedule are frozen.
+# Contract relative to frozen RUN096:
+#   The only physical change is the complete five-region electron/hole paired
+#   SELB group: A 2.16e6 -> 7.06e5 cm^-1 and B 1.77e7 -> 2.10e7 V/cm.
+#   BETAN=BETAP=1 and EGRAN=4e5 are unchanged. The post-500 ns execution tail
+#   is intentionally omitted and is not a physics change.
 #
 # Structure/contact lineage:
 #   RUN021: no-FP means source/drain/gate zero-area contacts only.
@@ -173,13 +174,13 @@ constr.mesh x1=$ion_roi_l y1=$y_buffer_b x2=$ion_roi_r y2=$y_sub_b \
             max.height=$ion_dy_sub max.width=$ion_dx
 
 mesh mode=MeshBuild
-structure outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_mesh.str"
+structure outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_mesh.str"
 
 # -----------------------------------------------------------------------------
 # Stage 2: frozen RUN047 equations with a low-field transfer sweep
 # -----------------------------------------------------------------------------
 go atlas simflags="-V 5.40.0.R -P 4"
-mesh infile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_mesh.str"
+mesh infile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_mesh.str"
 
 doping gauss n.type conc=$nd_sd char=1.0 lat.char=1.0 \
        x.min=$x_drn_l y.min=$y_surface y.max=$y_channel_b
@@ -267,20 +268,20 @@ mobility region=7 mu1n.caug=10 mu2n.caug=$mun_g \
          alphap.caug=0 betap.caug=0 gammap.caug=0 \
          vsatn=2.0e7 vsatp=2.0e7 betan=7.52 betap=7.52
 
-impact region=3 selb an1=2.16e6 an2=2.16e6 bn1=1.77e7 bn2=1.77e7 \
-       ap1=2.16e6 ap2=2.16e6 bp1=1.77e7 bp2=1.77e7 \
+impact region=3 selb an1=7.06e5 an2=7.06e5 bn1=2.10e7 bn2=2.10e7 \
+       ap1=7.06e5 ap2=7.06e5 bp1=2.10e7 bp2=2.10e7 \
        betan=1.0 betap=1.0 egran=4.0e5
-impact region=4 selb an1=2.16e6 an2=2.16e6 bn1=1.77e7 bn2=1.77e7 \
-       ap1=2.16e6 ap2=2.16e6 bp1=1.77e7 bp2=1.77e7 \
+impact region=4 selb an1=7.06e5 an2=7.06e5 bn1=2.10e7 bn2=2.10e7 \
+       ap1=7.06e5 ap2=7.06e5 bp1=2.10e7 bp2=2.10e7 \
        betan=1.0 betap=1.0 egran=4.0e5
-impact region=5 selb an1=2.16e6 an2=2.16e6 bn1=1.77e7 bn2=1.77e7 \
-       ap1=2.16e6 ap2=2.16e6 bp1=1.77e7 bp2=1.77e7 \
+impact region=5 selb an1=7.06e5 an2=7.06e5 bn1=2.10e7 bn2=2.10e7 \
+       ap1=7.06e5 ap2=7.06e5 bp1=2.10e7 bp2=2.10e7 \
        betan=1.0 betap=1.0 egran=4.0e5
-impact region=6 selb an1=2.16e6 an2=2.16e6 bn1=1.77e7 bn2=1.77e7 \
-       ap1=2.16e6 ap2=2.16e6 bp1=1.77e7 bp2=1.77e7 \
+impact region=6 selb an1=7.06e5 an2=7.06e5 bn1=2.10e7 bn2=2.10e7 \
+       ap1=7.06e5 ap2=7.06e5 bp1=2.10e7 bp2=2.10e7 \
        betan=1.0 betap=1.0 egran=4.0e5
-impact region=7 selb an1=2.16e6 an2=2.16e6 bn1=1.77e7 bn2=1.77e7 \
-       ap1=2.16e6 ap2=2.16e6 bp1=1.77e7 bp2=1.77e7 \
+impact region=7 selb an1=7.06e5 an2=7.06e5 bn1=2.10e7 bn2=2.10e7 \
+       ap1=7.06e5 ap2=7.06e5 bp1=2.10e7 bp2=2.10e7 \
        betan=1.0 betap=1.0 egran=4.0e5
 
 # Physical Fe acceptor trap. REGION is numeric so the trap cannot spill into
@@ -312,12 +313,12 @@ output e.field impact flowlines e.mobility h.mobility band.param \
 
 solve init
 solve vgate=0 name=gate
-log outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_static.log"
+log outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_static.log"
 solve vdrain=0.1 name=drain
 solve name=drain vstep=0.5 vfinal=10 previous
 solve name=drain vstep=5.0 vfinal=$target_vds previous \
       compliance=1.6e-5 cname=drain
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_isothermal.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_isothermal.str"
 log off
 
 # Turn on the complete thermal equation in the same ATLAS process, preserving
@@ -333,7 +334,7 @@ probe name=Tbottom lat.temp x=10.0 y=$y_sub_b
 method block newton trap maxtraps=10 climit=1e-4 itlimit=50 max.temp=5000
 
 solve previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_prestrike.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_prestrike.str"
 
 singleeventupset entrypoint="$xion,$y_surface" exitpoint="$xion,$y_sub_b" \
                  radialgauss b.density=$qline pcunits radius=$ion_radius \
@@ -341,64 +342,52 @@ singleeventupset entrypoint="$xion,$y_surface" exitpoint="$xion,$y_sub_b" \
 probe integrated photogen name="GSEU_all" \
       x.min=0 x.max=$x_dev y.min=$y_sio2_top y.max=$y_sub_b
 
-log outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_transient.log"
+log outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_transient.log"
 solve tstop=2e-12 dt=2e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t2ps.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t2ps.str"
 solve tstop=6e-12 dt=1e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t6ps.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t6ps.str"
 solve tstop=9.8e-12 dt=1e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t9p8ps.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t9p8ps.str"
 solve tstop=14e-12 dt=1e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t14ps.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t14ps.str"
 solve tstop=20e-12 dt=2e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t20ps.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t20ps.str"
 
-# Long recovery window. The sequence through 1 us is inherited from the
-# previously verified RUN038 long-tail schedule; 10/100 us extend it to
-# the Wang-paper recovery horizon without changing the source or physics.
+# Recovery window through 500 ns is inherited byte-for-byte from RUN096.
+# The active plan intentionally stops before RUN096's 1--100 us tail.
 solve tstop=30e-12 dt=1e-12 previous
 solve tstop=50e-12 dt=1e-12 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t50ps.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t50ps.str"
 solve tstop=100e-12 dt=1e-11 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t100ps.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t100ps.str"
 solve tstop=400e-12 dt=1e-11 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t400ps.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t400ps.str"
 solve tstop=1e-9 dt=1e-11 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t1ns.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t1ns.str"
 solve tstop=2e-9 dt=1e-9 previous
 solve tstop=3e-9 dt=1e-9 previous
 solve tstop=4e-9 dt=1e-9 previous
 solve tstop=7e-9 dt=1e-9 previous
 solve tstop=9e-9 dt=1e-9 previous
 solve tstop=10e-9 dt=1e-9 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t10ns.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t10ns.str"
 solve tstop=20e-9 dt=1e-8 previous
 solve tstop=30e-9 dt=1e-8 previous
 solve tstop=40e-9 dt=1e-8 previous
 solve tstop=50e-9 dt=1e-8 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t50ns.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t50ns.str"
 solve tstop=100e-9 dt=1e-8 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t100ns.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t100ns.str"
 solve tstop=500e-9 dt=1e-8 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t500ns.str"
-solve tstop=1e-6 dt=1e-8 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t1us.str"
-solve tstop=2e-6 dt=1e-7 previous
-solve tstop=5e-6 dt=2e-7 previous
-solve tstop=10e-6 dt=5e-7 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t10us.str"
-solve tstop=20e-6 dt=1e-6 previous
-solve tstop=50e-6 dt=2e-6 previous
-solve tstop=100e-6 dt=5e-6 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t100us.str"
+save outfile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_t500ns.str"
+# RUN121 contract stops here. The frozen RUN096 1--100 us tail is not executed.
 log off
 
-extract init infile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_transient.log"
+extract init infile="RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_transient.log"
 # 2-D area integral has units cm^-1; multiply by 1e-4 cm for a 1 um width.
-extract name="AreaTimeInt_cmInv_RUN096" area from curve(time, probe."GSEU_all")
+extract name="AreaTimeInt_cmInv_RUN121" area from curve(time, probe."GSEU_all")
 
 quit
 
 
-
-
