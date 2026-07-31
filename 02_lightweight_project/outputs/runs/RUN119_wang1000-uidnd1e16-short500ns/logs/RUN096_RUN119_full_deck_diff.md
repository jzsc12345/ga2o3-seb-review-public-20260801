# RUN096 → RUN119 完整 deck diff

> 生成日期：2026-07-31  
> 基线：`D:\SILVACO_LOCAL\decks\RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in`  
> 候选：`D:\SILVACO_LOCAL\decks\RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_short500ns.in`  
> 比对命令：`git diff --no-index --unified=3 --src-prefix=RUN096/ --dst-prefix=RUN119/`  
> 本文件记录原始文本差异；逻辑命令归一化裁决见 `RUN119_preflight_contract.md`。

```diff
diff --git "RUN096/D:\\SILVACO_LOCAL\\decks\\RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in" "RUN119/D:\\SILVACO_LOCAL\\decks\\RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_short500ns.in"
index 83028e0..15fc718 100644
--- "RUN096/D:\\SILVACO_LOCAL\\decks\\RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in"
+++ "RUN119/D:\\SILVACO_LOCAL\\decks\\RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_short500ns.in"
@@ -1,50 +1,23 @@
 # =============================================================================
-# RUN096 -- HfO2 heat-capacity-only arm from completed RUN095
+# RUN119 -- UID donor 2x sensitivity arm, frozen from RUN096
 #
-# Goal:
-#   Quantify only the missing HfO2 heat-capacity model after RUN095 closed the
-#   HEAT.FULL root-cause branch. Geometry, electrical physics, source, thermal
-#   boundaries, heat-source equation and time schedule are frozen from RUN095.
-#   Integrate PHOTOGEN and require the generated charge to agree with
-#   0.4529 pC/um * 5.35 um = 2.423015 pC within 5 percent.
+# A13 contract:
+#   The only physical change is Nd_UID 5.0e15 -> 1.0e16 cm^-3.
+#   UID thickness remains 0.20 um. Geometry, mesh commands, channel/substrate
+#   doping, Fe trap, materials, constant VSAT, impact, thermal model/boundary,
+#   ion source, solver, VDS and every time step through 500 ns are frozen.
+#   The 1-100 us execution tail is omitted; output names are mechanically
+#   isolated under RUN119. No interface charge/trap/barrier is added.
 #
-# Contract relative to RUN092:
-#   The only physical change is lateral geometry: xdev 31->20 um,
-#   drain-left 29->18 um (Lgd 20->9 um), and removal of gate_fp.  The 5 um
-#   substrate, Fe trap, channel/UID, work functions, mobility, impact,
-#   thermal parameters/contacts, source, solver and time schedule are frozen.
+# Production baseline:
+#   D:/SILVACO_LOCAL/decks/
+#   RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in
+#   SHA-256 786EA68542AA235621A2A2AD13DC81CB86666FD875577F00FF1FBFA5143D7CB5
 #
-# Structure/contact lineage:
-#   RUN021: no-FP means source/drain/gate zero-area contacts only.
-#   RUN093: exact 20 um/no-FP/Lgd9/xion11/5 um substrate DevEdit preflight,
-#   11672 points, 22992 triangles, 0 obtuse, 0 errors and 0 warnings.
-#
-# Physics lineage:
-#   RUN048 plus one new substrate region and one region-limited Fe acceptor trap.
-#   The lateral geometry, zero-area contacts, gate/FP common binding, channel,
-#   UID, materials, mobility, Fe trap and geometry are unchanged.
-#
-# Thermal evidence labels:
-#   kappa=0.27 W/(cm K) and C=3.332 J/(cm3 K): Wang 2026 Table I.
-#   Constant-kappa and HC.STD are the minimum-assumption ATLAS mapping because
-#   Wang does not report kappa(T) or heat-capacity temperature coefficients.
-#   SiO2/HfO2 kappa=0.014/0.023: project Silvaco surrogate, RUN035 validated.
-#   ext.temp=300 K, top alpha=1000 and bottom alpha=3:
-#   project thermal-boundary surrogates, not Wang-reported values.
-#
-# Existing electrical evidence labels:
-#   Fe trap parameters: Wang 2026 (5 um, Ec-0.8 eV, 2e18 cm-3, 5e-15 cm2).
-#   n-type substrate background 1.5e15 cm-3: project candidate; paper unreported.
-#   SIGP=SIGN and DEGEN.FAC=1: documented surrogate; paper unreported.
-#
-# Source evidence labels:
-#   LET75 -> B.DENSITY=0.4529 pC/um is the project conversion.
-#   RADIALGAUSS, radius=0.05 um and T0/TC=10/2 ps are project proxies.
-#   No RESCALE is frozen by RUN034. xion=11 remains gate-right+2 um exactly
-#   as in Wang; it is not moved with any former field-plate endpoint.
-#   Wang reports a vertical ion completely penetrating the device; mapping
-#   y=0..5.35 um to this geometry is a new project implementation and must pass
-#   the integrated-PHOTOGEN charge gate before a long transient is launched.
+# Authorization state:
+#   Deck/A14 preparation authorized 2026-07-31. Upload and launch are NOT
+#   authorized. Candidate mesh topology remains unverified until a separate
+#   DevEdit-only preflight is explicitly approved and executed.
 # =============================================================================
 
 set x_dev       = 20.0
@@ -63,7 +36,7 @@ set y_buffer_b  = 0.35
 set y_sub_b     = 5.35
 
 set nd_channel  = 5.0e16
-set nd_uid      = 5.0e15
+set nd_uid      = 1.0e16
 set nd_sd       = 1.0e19
 set nd_sub      = 1.5e15
 set nt_fe       = 2.0e18
@@ -100,7 +73,7 @@ set wf_drain    = 4.00
 set wf_gate     = 5.78
 
 # -----------------------------------------------------------------------------
-# Stage 1: frozen RUN029/RUN030 zero-area-electrode structure and mesh
+# Stage 1: frozen RUN096 zero-area-electrode structure and mesh commands
 # -----------------------------------------------------------------------------
 go devedit
 
@@ -173,13 +146,13 @@ constr.mesh x1=$ion_roi_l y1=$y_buffer_b x2=$ion_roi_r y2=$y_sub_b \
             max.height=$ion_dy_sub max.width=$ion_dx
 
 mesh mode=MeshBuild
-structure outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_mesh.str"
+structure outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_mesh.str"
 
 # -----------------------------------------------------------------------------
-# Stage 2: frozen RUN047 equations with a low-field transfer sweep
+# Stage 2: frozen RUN096 equations; only Nd_UID differs in Stage 1
 # -----------------------------------------------------------------------------
 go atlas simflags="-V 5.40.0.R -P 4"
-mesh infile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_mesh.str"
+mesh infile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_mesh.str"
 
 doping gauss n.type conc=$nd_sd char=1.0 lat.char=1.0 \
        x.min=$x_drn_l y.min=$y_surface y.max=$y_channel_b
@@ -312,12 +285,12 @@ output e.field impact flowlines e.mobility h.mobility band.param \
 
 solve init
 solve vgate=0 name=gate
-log outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_static.log"
+log outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_static.log"
 solve vdrain=0.1 name=drain
 solve name=drain vstep=0.5 vfinal=10 previous
 solve name=drain vstep=5.0 vfinal=$target_vds previous \
       compliance=1.6e-5 cname=drain
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_isothermal.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_isothermal.str"
 log off
 
 # Turn on the complete thermal equation in the same ATLAS process, preserving
@@ -333,7 +306,7 @@ probe name=Tbottom lat.temp x=10.0 y=$y_sub_b
 method block newton trap maxtraps=10 climit=1e-4 itlimit=50 max.temp=5000
 
 solve previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_prestrike.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_prestrike.str"
 
 singleeventupset entrypoint="$xion,$y_surface" exitpoint="$xion,$y_sub_b" \
                  radialgauss b.density=$qline pcunits radius=$ion_radius \
@@ -341,64 +314,49 @@ singleeventupset entrypoint="$xion,$y_surface" exitpoint="$xion,$y_sub_b" \
 probe integrated photogen name="GSEU_all" \
       x.min=0 x.max=$x_dev y.min=$y_sio2_top y.max=$y_sub_b
 
-log outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_transient.log"
+log outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_transient.log"
 solve tstop=2e-12 dt=2e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t2ps.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t2ps.str"
 solve tstop=6e-12 dt=1e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t6ps.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t6ps.str"
 solve tstop=9.8e-12 dt=1e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t9p8ps.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t9p8ps.str"
 solve tstop=14e-12 dt=1e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t14ps.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t14ps.str"
 solve tstop=20e-12 dt=2e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t20ps.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t20ps.str"
 
-# Long recovery window. The sequence through 1 us is inherited from the
-# previously verified RUN038 long-tail schedule; 10/100 us extend it to
-# the Wang-paper recovery horizon without changing the source or physics.
+# Short diagnostic window. The RUN096 schedule is frozen through 500 ns;
+# the 1-100 us execution tail is intentionally omitted by the RUN119 contract.
 solve tstop=30e-12 dt=1e-12 previous
 solve tstop=50e-12 dt=1e-12 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t50ps.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t50ps.str"
 solve tstop=100e-12 dt=1e-11 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t100ps.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t100ps.str"
 solve tstop=400e-12 dt=1e-11 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t400ps.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t400ps.str"
 solve tstop=1e-9 dt=1e-11 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t1ns.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t1ns.str"
 solve tstop=2e-9 dt=1e-9 previous
 solve tstop=3e-9 dt=1e-9 previous
 solve tstop=4e-9 dt=1e-9 previous
 solve tstop=7e-9 dt=1e-9 previous
 solve tstop=9e-9 dt=1e-9 previous
 solve tstop=10e-9 dt=1e-9 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t10ns.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t10ns.str"
 solve tstop=20e-9 dt=1e-8 previous
 solve tstop=30e-9 dt=1e-8 previous
 solve tstop=40e-9 dt=1e-8 previous
 solve tstop=50e-9 dt=1e-8 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t50ns.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t50ns.str"
 solve tstop=100e-9 dt=1e-8 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t100ns.str"
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t100ns.str"
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
+save outfile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_t500ns.str"
 log off
 
-extract init infile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_transient.log"
+extract init infile="RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_transient.log"
 # 2-D area integral has units cm^-1; multiply by 1e-4 cm for a 1 um width.
-extract name="AreaTimeInt_cmInv_RUN096" area from curve(time, probe."GSEU_all")
+extract name="AreaTimeInt_cmInv_RUN119" area from curve(time, probe."GSEU_all")
 
 quit
-
-
-
-
```
